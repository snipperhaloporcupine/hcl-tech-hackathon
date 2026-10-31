"""
Evaluation Runner for Enterprise Documentation Q&A Assistant.

Measures:
  1. Retrieval Metrics: Recall@1, Recall@3, Recall@5, Mean Reciprocal Rank (MRR)
  2. Conflict Detection: Precision, Recall, F1 for FR-06
  3. Fallback / Guardrail Adherence: Correct rejection of unanswerable queries for FR-07
  4. Groundedness: Citation validity check for FR-05

Can be run in:
  - Benchmark / Mock mode (works immediately with built-in test fixtures)
  - Live mode (connects to real retriever & generator when ready)

Usage:
  python evaluation/evaluate.py
  python evaluation/evaluate.py --live
"""

import os
import sys
import json
import argparse
from pathlib import Path
from dataclasses import asdict

# Ensure project root is on sys.path
_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from app.models import DocumentChunk, RetrievedPassage, Citation, Answer


def load_test_set(test_set_path: str = None) -> list[dict]:
    """Load labelled test cases from JSON file."""
    if test_set_path is None:
        test_set_path = os.path.join(_project_root, "evaluation", "test_set.json")
    with open(test_set_path, "r", encoding="utf-8") as f:
        return json.load(f)


def check_source_match(retrieved_chunk: DocumentChunk, gold_source: dict) -> bool:
    """Check if a retrieved chunk matches a gold source expectation."""
    if gold_source.get("source_file"):
        if retrieved_chunk.source_file.lower() != gold_source["source_file"].lower():
            return False

    if gold_source.get("page_number") is not None:
        if retrieved_chunk.page_number != gold_source["page_number"]:
            return False

    if gold_source.get("section_heading"):
        gold_heading = gold_source["section_heading"].lower()
        chunk_heading = (retrieved_chunk.section_heading or "").lower()
        if gold_heading not in chunk_heading and chunk_heading not in gold_heading:
            return False

    return True


def evaluate_retrieval(passages: list[RetrievedPassage], gold_sources: list[dict]) -> dict:
    """
    Calculate Hit@1, Hit@3, Hit@5, and Reciprocal Rank for a single query.
    """
    if not gold_sources:
        return {"hit@1": None, "hit@3": None, "hit@5": None, "rr": None}

    hit_rank = None
    for rank, p in enumerate(passages, start=1):
        for gold in gold_sources:
            if check_source_match(p.chunk, gold):
                hit_rank = rank
                break
        if hit_rank is not None:
            break

    hit_1 = 1.0 if (hit_rank and hit_rank <= 1) else 0.0
    hit_3 = 1.0 if (hit_rank and hit_rank <= 3) else 0.0
    hit_5 = 1.0 if (hit_rank and hit_rank <= 5) else 0.0
    rr = (1.0 / hit_rank) if hit_rank else 0.0

    return {
        "hit@1": hit_1,
        "hit@3": hit_3,
        "hit@5": hit_5,
        "rr": rr,
        "first_hit_rank": hit_rank
    }


def run_mock_query(test_case: dict) -> tuple[Answer, list[RetrievedPassage]]:
    """
    Simulated pipeline response matching the expected behavior of test fixtures.
    Allows verifying evaluation logic before full model inference runs.
    """
    cat = test_case["category"]
    gold = test_case.get("gold_sources", [])

    passages = []
    # Build simulated ranked passages
    for i, g in enumerate(gold):
        chunk = DocumentChunk(
            chunk_id=f"sim_chunk_{i}",
            text=f"Sample text snippet corresponding to {g.get('section_heading', 'Section')} in {g.get('source_file')}.",
            source_file=g.get("source_file", "unknown.pdf"),
            doc_title=g.get("source_file", "unknown").replace(".pdf", "").replace("_", " ").title(),
            page_number=g.get("page_number"),
            section_heading=g.get("section_heading")
        )
        passages.append(RetrievedPassage(chunk=chunk, relevance_score=round(0.95 - (i * 0.1), 2), excerpt=chunk.text))

    # Add 2 distractor chunks
    if not test_case.get("unanswerable"):
        passages.append(RetrievedPassage(
            chunk=DocumentChunk(
                chunk_id="distractor_1",
                text="General enterprise terms and conditions apply to all service agreements.",
                source_file="billing_policy_2024.pdf",
                doc_title="Billing & Payments Policy",
                page_number=2,
                section_heading="General Provisions"
            ),
            relevance_score=0.45,
            excerpt="General terms apply."
        ))

    # Simulate Answer
    citations = [
        Citation(
            source_file=p.chunk.source_file,
            doc_title=p.chunk.doc_title,
            page_number=p.chunk.page_number,
            section_heading=p.chunk.section_heading,
            excerpt=p.excerpt
        )
        for p in passages if p.chunk.chunk_id != "distractor_1"
    ]

    if test_case["unanswerable"]:
        answer = Answer(
            text="I do not have enough information in the provided documentation to answer this question.",
            citations=[],
            confidence="LOW",
            has_conflict=False,
            conflict_details=None
        )
    elif cat == "conflict":
        answer = Answer(
            text=f"The available sources disagree: {test_case['ground_truth_answer']}",
            citations=citations,
            confidence="MEDIUM",
            has_conflict=True,
            conflict_details="Discrepancy identified between cited sources."
        )
    elif cat == "ambiguous":
        answer = Answer(
            text=f"{test_case['ground_truth_answer']} Please specify your edition or error code.",
            citations=citations,
            confidence="MEDIUM",
            has_conflict=False,
            conflict_details=None
        )
    else:
        answer = Answer(
            text=test_case["ground_truth_answer"],
            citations=citations,
            confidence="HIGH",
            has_conflict=False,
            conflict_details=None
        )

    return answer, passages


def run_live_query(question: str) -> tuple[Answer, list[RetrievedPassage]]:
    """Connect to the real RAG modules once active."""
    try:
        from app.retrieval.retriever import retrieve_passages
        from app.generation.conflict_detector import detect_conflicts
        from app.generation.answerer import generate_grounded_answer

        passages = retrieve_passages(question, top_k=5)
        has_conflict, details = detect_conflicts(passages)
        answer = generate_grounded_answer(question, passages, has_conflict, details)
        return answer, passages
    except ImportError:
        print("[Notice] Real RAG modules not yet fully wired. Falling back to mock test execution.")
        from app.dummy_data import dummy_ask_question
        return dummy_ask_question(question)


def run_evaluation(live: bool = False):
    test_cases = load_test_set()
    print("=" * 80)
    print(f"  RUNNING ENTERPRISE Q&A EVALUATION ({len(test_cases)} Test Cases)")
    print(f"  Mode: {'LIVE PIPELINE' if live else 'BENCHMARK VALIDATION'}")
    print("=" * 80)

    results = []
    retrieval_hits_1 = []
    retrieval_hits_3 = []
    retrieval_hits_5 = []
    reciprocal_ranks = []

    conflict_true_positives = 0
    conflict_false_positives = 0
    conflict_false_negatives = 0
    conflict_true_negatives = 0

    fallback_correct = 0
    fallback_total = 0

    grounded_citations_correct = 0
    total_citations_checked = 0

    for tc in test_cases:
        qid = tc["id"]
        cat = tc["category"]
        q = tc["question"]

        if live:
            answer, passages = run_live_query(q)
        else:
            answer, passages = run_mock_query(tc)

        # 1. Retrieval Eval (only for answerable/conflict/ambiguous with gold sources)
        gold_sources = tc.get("gold_sources", [])
        if gold_sources:
            ret_metrics = evaluate_retrieval(passages, gold_sources)
            retrieval_hits_1.append(ret_metrics["hit@1"])
            retrieval_hits_3.append(ret_metrics["hit@3"])
            retrieval_hits_5.append(ret_metrics["hit@5"])
            reciprocal_ranks.append(ret_metrics["rr"])
        else:
            ret_metrics = {"hit@1": None, "hit@3": None, "hit@5": None, "rr": None}

        # 2. Conflict Handling Eval
        exp_conflict = tc.get("expected_conflict", False)
        act_conflict = answer.has_conflict
        if exp_conflict and act_conflict:
            conflict_true_positives += 1
        elif not exp_conflict and act_conflict:
            conflict_false_positives += 1
        elif exp_conflict and not act_conflict:
            conflict_false_negatives += 1
        else:
            conflict_true_negatives += 1

        # 3. Fallback Eval (Unanswerable Guardrail)
        if tc.get("unanswerable"):
            fallback_total += 1
            # Must return LOW confidence and no false claims
            if answer.confidence == "LOW" and (not answer.citations or "not have enough information" in answer.text.lower()):
                fallback_correct += 1

        # 4. Citation Groundedness Check
        # Check that each returned citation corresponds to a retrieved passage
        retrieved_sources = {(p.chunk.source_file, p.chunk.page_number) for p in passages}
        for cit in answer.citations:
            total_citations_checked += 1
            if (cit.source_file, cit.page_number) in retrieved_sources:
                grounded_citations_correct += 1

        results.append({
            "id": qid,
            "category": cat,
            "question": q,
            "retrieval": ret_metrics,
            "confidence": answer.confidence,
            "expected_confidence": tc.get("expected_confidence"),
            "has_conflict": answer.has_conflict,
            "expected_conflict": exp_conflict,
            "citations_count": len(answer.citations)
        })

    # Summary Calculations
    r1 = (sum(retrieval_hits_1) / len(retrieval_hits_1)) if retrieval_hits_1 else 0.0
    r3 = (sum(retrieval_hits_3) / len(retrieval_hits_3)) if retrieval_hits_3 else 0.0
    r5 = (sum(retrieval_hits_5) / len(retrieval_hits_5)) if retrieval_hits_5 else 0.0
    mrr = (sum(reciprocal_ranks) / len(reciprocal_ranks)) if reciprocal_ranks else 0.0

    c_precision = (conflict_true_positives / (conflict_true_positives + conflict_false_positives)) if (conflict_true_positives + conflict_false_positives) > 0 else 1.0
    c_recall = (conflict_true_positives / (conflict_true_positives + conflict_false_negatives)) if (conflict_true_positives + conflict_false_negatives) > 0 else 1.0
    c_f1 = (2 * c_precision * c_recall / (c_precision + c_recall)) if (c_precision + c_recall) > 0 else 0.0

    fallback_acc = (fallback_correct / fallback_total) if fallback_total > 0 else 1.0
    citation_groundedness = (grounded_citations_correct / total_citations_checked) if total_citations_checked > 0 else 1.0

    print("\n" + "-" * 80)
    print("  SUMMARY EVALUATION METRICS")
    print("-" * 80)
    print(f"  Retrieval Recall@1 (Hit@1):             {r1 * 100:6.1f}%")
    print(f"  Retrieval Recall@3 (Hit@3):             {r3 * 100:6.1f}%")
    print(f"  Retrieval Recall@5 (Hit@5):             {r5 * 100:6.1f}%")
    print(f"  Retrieval MRR (Mean Reciprocal Rank):   {mrr:6.3f}")
    print(f"  Conflict Detection F1 Score:            {c_f1 * 100:6.1f}% (Precision: {c_precision:.2f}, Recall: {c_recall:.2f})")
    print(f"  Fallback Adherence (FR-07):             {fallback_acc * 100:6.1f}% ({fallback_correct}/{fallback_total})")
    print(f"  Citation Groundedness (FR-05):          {citation_groundedness * 100:6.1f}% ({grounded_citations_correct}/{total_citations_checked})")
    print("-" * 80)

    # Save detailed JSON output
    output_path = os.path.join(_project_root, "evaluation", "results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "metrics": {
                "recall@1": r1,
                "recall@3": r3,
                "recall@5": r5,
                "mrr": mrr,
                "conflict_f1": c_f1,
                "fallback_accuracy": fallback_acc,
                "citation_groundedness": citation_groundedness
            },
            "detailed_results": results
        }, f, indent=2)

    print(f"\n[Artifact Saved] Full results written to: {output_path}")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run RAG Evaluation Suite")
    parser.add_argument("--live", action="store_true", help="Run against active live model rather than benchmark fixtures")
    args = parser.parse_args()
    run_evaluation(live=args.live)

