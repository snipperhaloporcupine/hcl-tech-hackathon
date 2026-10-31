
import requests
import trafilatura
import zipfile
import json
from pathlib import Path    

docs = [
    {
        "id": "IT001",
        "title": "Account Management",
        "url": "https://docs.gitlab.com/user/profile/"
    },
    {
        "id": "IT002",
        "title": "Project Settings",
        "url": "https://docs.gitlab.com/user/project/settings/"
    },
    {
        "id": "PROD001",
        "title": "Manage Subscription",
        "url": "https://docs.gitlab.com/subscriptions/manage_subscription/"
    },
    {
        "id": "PROD002",
        "title": "Account and Limit Settings",
        "url": "https://docs.gitlab.com/administration/settings/account_and_limit_settings/"
    },
    {
        "id": "IT003",
        "title": "GitLab Issues",
        "url": "https://docs.gitlab.com/user/project/issues/"
    },
    {
        "id": "IT004",
        "title": "Merge Requests",
        "url": "https://docs.gitlab.com/user/project/merge_requests/"
    },
    {
        "id": "IT005",
        "title": "GitLab Repository",
        "url": "https://docs.gitlab.com/user/project/repository/"
    },
    {
        "id": "IT006",
        "title": "GitLab CI/CD Pipelines",
        "url": "https://docs.gitlab.com/ci/pipelines/"
    },
    {
        "id": "IT007",
        "title": "GitLab Runners",
        "url": "https://docs.gitlab.com/ci/runners/"
    },
    {
        "id": "IT008",
        "title": "GitLab User Permissions",
        "url": "https://docs.gitlab.com/user/permissions/"
    }
]

output = Path("dataset")
output.mkdir(exist_ok=True)

metadata = []

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (compatible; EnterpriseRAGDemo/1.0)"
})

for doc in docs:
    print(f"\nDownloading {doc['title']}...")

    try:
        response = session.get(doc["url"], timeout=30)
        response.raise_for_status()

        final_url = response.url.lower()

        if "users/sign_in" in final_url or "login" in final_url:
            print("SKIPPED: Redirected to login page")
            continue

        if "text/html" not in response.headers.get(
            "Content-Type", ""
        ).lower():
            print("SKIPPED: Not an HTML page")
            continue

        content = trafilatura.extract(
            response.text,
            output_format="markdown",
            include_tables=True,
            include_links=True
        )

        if not content or len(content.strip()) < 100:
            print("SKIPPED: Insufficient extracted content")
            continue

        filename = f"{doc['id']}.md"

        text = (
            f"# {doc['title']}\n\n"
            f"Document ID: {doc['id']}\n"
            f"Source: {doc['url']}\n\n"
            f"{content}\n"
        )

        (output / filename).write_text(
            text, encoding="utf-8"
        )

        metadata.append({
            "id": doc["id"],
            "title": doc["title"],
            "url": doc["url"],
            "filename": filename
        })

        print("SUCCESS:", filename)

    except requests.RequestException as error:
        print("DOWNLOAD FAILED:", error)

with open(output / "metadata.json", "w") as file:
    json.dump(metadata, file, indent=4)

# Create ZIP
with zipfile.ZipFile(
    "enterprise_documents.zip", "w"
) as archive:
    for file in output.glob("*"):
        if file.is_file():
            archive.write(file, file.name)

print("\nCompleted!")
print("Successfully downloaded:", len(metadata))
print("ZIP: enterprise_documents.zip")
