# Account and Limit Settings

Document ID: PROD002
Source: https://docs.gitlab.com/administration/settings/account_and_limit_settings/

# Account and limit settings

- Tier: Free, Premium, Ultimate
- Offering: GitLab Self-Managed, GitLab Dedicated

GitLab administrators can configure project and account limits on their instance, like:

- The number of projects a user can create.
- Size limits on attachments, pushes, and repositories.
- Session duration and expiration.
- Access token settings, such as expiration and prefixes.
- User privacy and deletion settings.
- Creation rules for organizations and top-level groups.

## Default projects limit

You can configure the default maximum number of projects new users can create in their
personal namespace. This limit affects only new user accounts created after you change
the setting. This setting is not retroactive for existing users, but you can separately edit
the [project limits for existing users](/administration/settings/account_and_limit_settings/#projects-limit-for-a-user).

To configure the maximum number of projects in personal namespaces for new users:

1. In the upper-right corner, select **Admin**.
2. In the left sidebar, select **Settings** > **General**.
3. Expand **Account and limit**.
4. Increase or decrease that **Default projects limit** value.

If you set **Default projects limit** to 0, users are not allowed to create projects
in their personal namespace. However, projects can still be created in a group.

### Projects limit for a user

You can edit a specific user, and change the maximum number of projects this user can create in their personal namespace:

1. In the upper-right corner, select **Admin**.
2. In the left sidebar, select **Overview** > **Users**.
3. From the list of users, select a user.
4. Select **Edit**.
5. Increase or decrease the **Projects limit** value.

## Max attachment size

The maximum file size for attachments in GitLab comments and replies is 100 MB. This limit also applies to files you upload to a repository through the GitLab UI. To change the maximum attachment size:

1. In the upper-right corner, select **Admin**.
2. In the left sidebar, select **Settings** > **General**.
3. Expand **Account and limit**.
4. Increase or decrease by changing the value in **Maximum attachment size (MiB)**.

If you choose a size larger than the configured value for the web server,
you may receive errors. For more information, see the [troubleshooting section](/administration/settings/account_and_limit_settings/#troubleshooting).

For GitLab.com repository size limits, see [accounts and limit settings](/user/gitlab_com/#account-and-limit-settings).

## Max push size

You can change the maximum push size for your instance:

1. In the upper-right corner, select **Admin**.
2. In the left sidebar, select **Settings** > **General**.
3. Expand **Account and limit**.
4. Increase or decrease by changing the value in **Maximum push size (MiB)**.

For GitLab.com push size limits, see [accounts and limit settings](/user/gitlab_com/#account-and-limit-settings).

When you [add files to a repository](/user/project/repository/web_editor/#create-a-file)
through the web UI, the maximum attachment size is the limiting factor. This happens
because the web server
must receive the file before GitLab can generate the commit.
Use [Git LFS](/topics/git/lfs/) to add large files to a repository.
This setting does not apply when pushing Git LFS objects.

## Repository size limit

- Tier: Premium, Ultimate
- Offering: GitLab Self-Managed, GitLab Dedicated

Repositories in your GitLab instance can grow quickly, especially if you are using LFS. Their size can grow exponentially, rapidly consuming available storage. To prevent this from happening, you can set a hard limit for your repositories’ size. This limit can be set globally, per group, or per project, with per project limits taking the highest priority.

The repository size limit applies to both private and public projects. It includes repository files and Git LFS objects (even when stored in external object storage), but does not include:

- Artifacts
- Containers
- Packages
- Snippets
- Uploads
- Wikis

Numerous use cases exist where you might set up a limit for repository size. For instance, consider the following workflow:

1. Your team develops apps which require large files to be stored in the application repository.
2. Although you have enabled [Git LFS](/topics/git/lfs/) for your project, your storage has grown significantly.
3. Before you exceed available storage, you set up a limit of 10 GB per repository.

On GitLab Self-Managed and GitLab Dedicated, only a GitLab administrator can set those limits. Setting the limit to `0` means
there are no restrictions. For GitLab.com repository size limits, see
[accounts and limit settings](/user/gitlab_com/#account-and-limit-settings).

These settings can be found in:

- Each project’s settings:
  1. From the Project’s homepage, go to **Settings** > **General**.
  2. Fill in the **Repository size limit (MiB)** field in the **Naming, topics, avatar** section.
  3. Select **Save changes**.
- Each group’s settings:
  1. From the Group’s homepage, go to **Settings** > **General**.
  2. Fill in the **Repository size limit (MiB)** field in the **Naming, visibility** section.
  3. Select **Save changes**.
- GitLab global settings:
  1. In the upper-right corner, select **Admin**.
  2. Select **Settings** > **General**.
  3. Expand the **Account and limit** section.
  4. Fill in the **Size limit per repository (MiB)** field.
  5. Select **Save changes**.

The first push of a new project, including LFS objects, is checked for size. If the sum of their sizes exceeds the maximum allowed repository size, the push is rejected.

### Check repository size

To determine if a project is nearing its configured repository size limit:

1. [View your storage usage](/user/storage_usage_quotas/#view-storage).
The **Repository** size includes both Git repository files and [Git LFS](/topics/git/lfs/) objects.
2. Compare the current usage to your configured repository size limit to estimate remaining capacity.

You can also use the [Projects API](/api/projects/) to retrieve repository
statistics.

To reduce repository size, see
[methods to reduce repository size](/user/project/repository/repository_size/#methods-to-reduce-repository-size).

## Session duration

### Customize the default session duration

You can change how long users can remain signed in without activity.

1. In the upper-right corner, select **Admin**.
2. In the left sidebar, select **Settings** > **General**.
3. Expand **Account and limit**.
4. Fill in the **Session duration (minutes)** field. Setting **Session duration (minutes)** to `0` breaks your GitLab instance.
For more information, see [issue 19469](https://gitlab.com/gitlab-org/gitlab/-/issues/19469).
5. Select **Save changes**.
6. Restart GitLab to apply the changes. For GitLab Dedicated, submit a [support ticket](https://support.gitlab.com/hc/en-us/requests/new?ticket_form_id=4414917877650) to request a restart of your instance.

If the [**Remember me** option](/administration/settings/account_and_limit_settings/#configure-the-remember-me-option) is enabled, users’ sessions can remain active for an indefinite period of time.

For details, see [cookies used for sign-in](/user/profile/#cookies-used-for-sign-in).

### Set sessions to expire from creation date

By default, sessions expire a set amount of time after the session becomes inactive. Instead, you can configure sessions to expire a set amount of time after the session is created.

When the session duration is met, the session ends and the user is signed out even if:

- The user is still actively using the session.
- The user selected [**Remember me**](/administration/settings/account_and_limit_settings/#configure-the-remember-me-option) during sign in.

1. In the upper-right corner, select **Admin**.
2. In the left sidebar, select **Settings** > **General**.
3. Expand **Account and limit**.
4. Select the **Expire session from creation date** checkbox.

After a session ends, a window prompts the user to sign in again.

### Configure the Remember me option

Users can select the **Remember me** checkbox on sign-in. Their session remains active for an indefinite
period of time when accessed from that specific browser. Turn off this setting to expire sessions for
security or compliance purposes. Turning off this setting ensures users’ sessions expire after the
number of minutes of inactivity set when you [customize your session duration](/administration/settings/account_and_limit_settings/#customize-the-default-session-duration).

1. In the upper-right corner, select **Admin**.
2. In the left sidebar, select **Settings** > **General**.
3. Expand **Account and limit**.
4. Select or clear the **Remember me** checkbox to turn this setting on or off.

### Customize session duration for Git Operations when 2FA is enabled

- Tier: Premium, Ultimate
- Offering: GitLab Self-Managed

The availability of this feature is controlled by a feature flag. For more information, see the history. This feature is not ready for production use.

GitLab administrators can choose to customize the session duration (in minutes) for Git operations when 2FA is enabled. The default is 15 and this can be set to a value between 1 and 10080.

To set a limit on how long these sessions are valid:

1. In the upper-right corner, select **Admin**.
2. In the left sidebar, select **Settings** > **General**.
3. Expand the **Account and limit** section.
4. Fill in the **Session duration for Git operations when 2FA is enabled (minutes)** field.
5. Select **Save changes**.

## Allow top-level group Owners to create service accounts

- Tier: Premium, Ultimate
- Offering: GitLab Self-Managed, GitLab Dedicated

By default, only administrators can create service accounts. You can configure GitLab to also allow top-level group Owners to create service accounts.

Prerequisites:

- You must have administrator access.

To allow top-level group Owners to create service accounts:

1. In the upper-right corner, select **Admin**.
2. In the left sidebar, select **Settings** > **General**.
3. Expand **Account and limit**.
4. Under **Service account creation**, select the **Allow top-level group owners to create Service accounts** checkbox.
5. Select **Save changes**.

## Require expiration dates for new access tokens

- Tier: Free, Premium, Ultimate
- Offering: GitLab.com, GitLab Self-Managed, GitLab Dedicated

Prerequisites:

- You must be an administrator.

You can require all new access tokens to have an expiration date. This setting is turned on by default and applies to:

- Personal access tokens for non-service account users.
- Group access tokens.
- Project access tokens.
- Impersonation tokens.

For personal access tokens for service accounts, use the `service_access_tokens_expiration_enforced`
setting in the [Application settings API](/api/settings/).

To require expiration dates for new access tokens:

1. In the upper-right corner, select **Admin**.
2. In the left sidebar, select **Settings** > **General**.
3. Expand **Account and limit**.
4. Select the **Require expiration date** checkbox.
5. Select **Save changes**.

When you require expiration dates for new access tokens:

- Users must set an expiration date that does not exceed the allowed lifetime for new access tokens.
- To control the maximum access token lifetime, use the [**Limit the lifetime of access tokens** setting](/administration/settings/account_and_limit_settings/#limit-the-lifetime-of-access-tokens).

## Inactive project and group access token retention period

- Offering: GitLab Self-Managed, GitLab Dedicated

By default, GitLab deletes group and project access tokens and their [token family](/api/personal_access_tokens/#automatic-reuse-detection)
30 days after the last active token in the token family becomes inactive. This deletion removes all
tokens in the token family and the associated bot user, and moves any bot contributions to a
[ghost user](/user/profile/account/delete_account/#associated-records).

Prerequisites:

- Administrator access.

To modify the retention period for inactive tokens:

1. In the upper-right corner, select **Admin**.
2. In the left sidebar, select **Settings** > **General**.
3. Expand **Account and limit**.
4. In the **Inactive project and group access token retention period** text box, modify the retention period.
  - If a number is defined, all group and project access tokens are deleted after they are inactive for the specified number of days.
  - If the field is blank, inactive tokens are never deleted.
5. Select **Save changes**.

You can also use the [application settings API](/api/settings/) to modify the `inactive_resource_access_tokens_delete_after_days` attribute.

## Personal access token prefix

You can specify a prefix for personal access tokens. Benefits of using a custom prefix include:

- Tokens are distinct and identifiable.
- Leaked tokens are more easily identifiable during security scans.
- Reduced risk of token confusion between different instances.

The default prefix for personal access tokens is `glpat-` but administrators can change it.
[Project access tokens](/user/project/settings/project_access_tokens/) and
[group access tokens](/user/group/settings/group_access_tokens/) also inherit this prefix.

By default, client-side secret detection, secret push protection, and pipeline secret detection do
not detect tokens that have a custom prefix. This might result in an increase in false negatives.
However, you can
[customize pipeline secret detection](/user/application_security/secret_detection/pipeline/configure/#customize-analyzer-rulesets)
to detect these tokens.

### Set a prefix

To change the default global prefix:

1. In the upper-right corner, select **Admin**.
2. In the left sidebar, select **Settings** > **General**.
3. Expand the **Account and limit** section.
4. Fill in the **Personal access token prefix** field.
5. Select **Save changes**.

You can also configure the prefix by using the
[settings API](/api/settings/).

## Instance token prefix

The availability of this feature is controlled by a feature flag. For more information, see the history. This feature is available for testing, but not ready for production use.

You can set a custom prefix that is prepended to all tokens generated on your instance. Benefits of using a custom prefix include:

- Tokens are distinct and identifiable.
- Leaked tokens are more easily identifiable during security scans.
- Reduced risk of token confusion between different instances.

By default, client-side secret detection, secret push protection, and pipeline secret detection do
not detect tokens that have a custom prefix. This might result in an increase in false negatives.
However, you can
[customize pipeline secret detection](/user/application_security/secret_detection/pipeline/configure/#customize-analyzer-rulesets)
to detect these tokens.

Custom token prefixes apply only to the following tokens:

Prerequisites:

- You must have administrator access to the instance.

To set a custom token prefix:

1. In the upper-right corner, select **Admin**.
2. In the left sidebar, select **Settings** > **General**.
3. Expand the **Account and limit** section.
4. In the **Instance token prefix** field, enter your custom prefix.
5. Select **Save changes**.

`gl` is a reserved prefix.
Instances that saved their application settings before GitLab changed the default instance token prefix from `gl` to no prefix still have `gl` stored as the value.
GitLab now treats a stored `gl` value the same as no prefix, so you cannot set the instance token prefix to `gl`.

## Limit the lifetime of access tokens

- Tier: Ultimate
- Offering: GitLab Self-Managed, GitLab Dedicated

The availability of the extended maximum allowable lifetime limit is controlled by a feature flag. For more information, see the history. The feature flag is not available on GitLab Dedicated.

Users can optionally specify a maximum lifetime in days for
access tokens. This includes [personal](/user/profile/personal_access_tokens/),
[group](/user/group/settings/group_access_tokens/), and [project](/user/project/settings/project_access_tokens/) access tokens.
This lifetime is not a requirement, and can be set to any value greater than 0 and less than or equal to:

- 365 days by default.
- 400 days, if you enable the `buffered_token_expiration_limit` feature flag.
This extended limit is not available on GitLab Dedicated.

If this setting is left blank, the default allowable lifetime of access tokens is:

- 365 days by default.
- 400 days, if you enable the `buffered_token_expiration_limit` feature flag.
This extended limit is not available on GitLab Dedicated.

Access tokens are the only tokens needed for programmatic access to GitLab. However, organizations with security requirements may want to enforce more protection by requiring the regular rotation of these tokens.

### Set a lifetime

Only a GitLab administrator can set a lifetime. Leaving it empty means there are no restrictions.

To set a lifetime on how long access tokens are valid:

1. In the upper-right corner, select **Admin**.
2. In the left sidebar, select **Settings** > **General**.
3. Expand the **Account and limit** section.
4. Fill in the **Maximum allowable lifetime for access tokens (days)** field.
5. Select **Save changes**.

After a lifetime for access tokens is set, GitLab:

- Applies the lifetime for new personal access tokens, and requires users to set an expiration date and a date no later than the allowed lifetime.
- After three hours, revokes old tokens with no expiration date or with a lifetime longer than the allowed lifetime. Three hours is given to allow administrators to change the allowed lifetime, or remove it, before revocation takes place.

## Limit the lifetime of SSH keys

- Tier: Ultimate
- Offering: GitLab Self-Managed, GitLab Dedicated

Users can optionally specify a lifetime for
[SSH keys](/user/ssh/).
This lifetime is not a requirement, and can be set to any arbitrary number of days.

SSH keys are user credentials to access GitLab. However, organizations with security requirements may want to enforce more protection by requiring the regular rotation of these keys.

### Set a lifetime

Only a GitLab administrator can set a lifetime. Leaving it empty means there are no restrictions.

To set a lifetime on how long SSH keys are valid:

1. In the upper-right corner, select **Admin**.
2. In the left sidebar, select **Settings** > **General**.
3. Expand the **Account and limit** section.
4. Fill in the **Maximum allowable lifetime for SSH keys (days)** field.
5. Select **Save changes**.

After a lifetime for SSH keys is set, GitLab:

- Requires users to set an expiration date that is no later than the allowed lifetime on new SSH keys. The maximum allowed lifetime is:
  - 365 days by default.
  - 400 days, if you enable the `buffered_token_expiration_limit` feature flag.
This extended limit is not available on GitLab Dedicated.
- Applies the lifetime restriction to existing SSH keys. Keys with no expiry or a lifetime greater than the maximum immediately become invalid.

When a user’s SSH key becomes invalid they can delete and re-add the same key again.

## User OAuth applications setting

- Tier: Free, Premium, Ultimate
- Offering: GitLab Self-Managed, GitLab Dedicated

Prerequisites:

- You must be an administrator.

The **User OAuth applications** setting controls whether users can register applications to use GitLab
as an OAuth provider. This setting affects OAuth applications owned by users, but does not affect OAuth
applications owned by groups.

To turn the **User OAuth applications** setting on or off:

1. In the upper-right corner, select **Admin**.
2. In the left sidebar, select **Settings** > **General**.
3. Expand the **Account and limit** section.
4. Select or clear the **User OAuth applications** checkbox.
5. Select **Save changes**.

### Limit the lifetime of OAuth access tokens

By default, OAuth access tokens expire after two hours (7200 seconds). Instance administrators can configure a custom lifetime for OAuth access tokens.

The minimum value is 300 seconds (5 minutes). When unset, the default of 7200 seconds (2 hours) applies. This setting applies to all new OAuth access tokens issued by the instance.

Prerequisites:

- You must be an administrator.

To set a lifetime for OAuth access tokens:

1. In the upper-right corner, select **Admin**.
2. In the left sidebar, select **Settings** > **General**.
3. Expand the **Account and limit** section.
4. Fill in the **OAuth access token lifetime (seconds)** field.
5. Select **Save changes**.

You can also configure this setting by using the
[application settings API](/api/settings/) with the `oauth_access_token_expires_in` attribute.

### Turn off OAuth dynamic client registration

- Tier: Free, Premium, Ultimate
- Offering: GitLab Self-Managed, GitLab Dedicated

OAuth clients, such as MCP clients and AI tools, use OAuth dynamic client registration (DCR)
to automatically register applications by sending a request to `POST /oauth/register`.
By default, DCR is enabled.

When you turn off DCR, the following outcomes apply to OAuth clients:

- OAuth clients cannot register applications automatically. Clients must use a pre-registered OAuth application instead.
- GitLab deletes dynamically registered OAuth applications and revokes their access tokens and grants.

Prerequisites:

- You must be an administrator.

To turn off OAuth dynamic client registration, use the
[application settings API](/api/settings/) to set the
`dynamic_client_registration_enabled` attribute to `false`.

## Disable user profile name changes

- Tier: Premium, Ultimate
- Offering: GitLab Self-Managed, GitLab Dedicated

To maintain integrity of user details in [audit events](/administration/compliance/audit_event_reports/),
GitLab administrators can prevent users from changing their profile name.

To do this:

1. In the upper-right corner, select **Admin**.
2. In the left sidebar, select **Settings** > **General**.
3. Expand **Account and limit**.
4. Select **Prevent users from changing their profile name**.

When selected, GitLab administrators can still update usernames in the
[**Admin** area](/administration/admin_area/#administering-users) or the
[API](/api/users/#modify-a-user).

## Prevent users from creating organizations

- Status: Experiment

On GitLab Self-Managed, by default this feature is not available. To make it available, an administrator
can [enable the feature flag](/administration/feature_flags/) named `ui_for_organizations`. On GitLab.com and GitLab Dedicated,
this feature is not available. This feature is not ready for production use.

By default, users can create organizations. GitLab administrators can prevent users from creating organizations.

1. In the upper-right corner, select **Admin**.
2. In the left sidebar, select **Settings** > **General**.
3. Expand **Account and limit**.
4. Clear the **Allow users to create organizations** checkbox.

## Prevent new users from creating top-level groups

By default, new users can create top-level groups. GitLab administrators can prevent new users from creating top-level groups:

- In the GitLab UI, with the steps in this section.
- With the [Application settings API](/api/settings/#update-application-settings).

1. In the upper-right corner, select **Admin**.
2. In the left sidebar, select **Settings** > **General**.
3. Expand **Account and limit**.
4. Clear the **Allow new users to create top-level groups** checkbox.

This setting applies only to users added after you turn off the setting. Existing users can still create top-level groups.

## Prevent non-members from creating projects and groups

By default, users with the Guest role can create projects and groups. GitLab administrators can prevent this behavior:

1. In the upper-right corner, select **Admin**.
2. In the left sidebar, select **Settings** > **General**.
3. Expand **Account and limit**.
4. Clear the **Allow users with up to Guest role to create groups and personal projects** checkbox.
5. Select **Save changes**.

## Prevent users from making their profiles private

- Tier: Premium, Ultimate
- Offering: GitLab Self-Managed, GitLab Dedicated

By default, users can make their profiles private.
GitLab administrators can disable this setting to require all user profiles to be public.
This setting does not affect [internal users](/administration/internal_users/) (sometimes referred to as “bots”).

To prevent users from making their profiles private:

1. In the upper-right corner, select **Admin**.
2. In the left sidebar, select **Settings** > **General**.
3. Expand **Account and limit**.
4. Clear the **Allow users to make their profiles private** checkbox.
5. Select **Save changes**.

When you turn off this setting:

- All private user profiles become public.
- The option to [set profiles of new users to private by default](/administration/settings/account_and_limit_settings/#set-profiles-of-new-users-to-private-by-default) is also turned off.

When you re-enable this setting, the user’s
[previously set profile visibility](/user/profile/#make-your-user-profile-page-private) is selected.

## Set profiles of new users to private by default

By default, newly created users have a public profile. GitLab administrators can set new users to have a private profile by default:

1. In the upper-right corner, select **Admin**.
2. In the left sidebar, select **Settings** > **General**.
3. Expand **Account and limit**.
4. Select the **Make new users’ profiles private by default** checkbox.
5. Select **Save changes**.

If [**Allow users to make their profiles private**](/administration/settings/account_and_limit_settings/#prevent-users-from-making-their-profiles-private) is disabled, this setting is also disabled.

## Prevent users from deleting their accounts

- Tier: Premium, Ultimate
- Offering: GitLab Self-Managed, GitLab Dedicated

By default, users can delete their own accounts. GitLab administrators can prevent users from deleting their own accounts:

1. In the upper-right corner, select **Admin**.
2. In the left sidebar, select **Settings** > **General**.
3. Expand **Account and limit**.
4. Clear the **Allows users to delete their own accounts** checkbox.

## Automatically accept achievements for all users

- Tier: Free, Premium, Ultimate
- Offering: GitLab Self-Managed, GitLab Dedicated

By default, users must explicitly accept an [achievement](/user/profile/achievements/) before it appears on
their user profile. Instead, you can configure a setting to automatically accept newly awarded achievements for all
users on the instance.

When turned on, new achievements are accepted immediately and displayed on the recipient’s user profile. GitLab still sends an email notification for the achievement, but the email no longer contains an acceptance link. This setting does not apply to achievements awarded before the setting was turned on.

Recipients can still [hide the achievement from their profile](/user/profile/achievements/#change-visibility-of-specific-achievements).

To automatically accept achievements for all users:

1. In the upper-right corner, select **Admin**.
2. In the left sidebar, select **Settings** > **General**.
3. Expand **Account and limit**.
4. Select the **Automatically accept achievements for all users** checkbox.
5. Select **Save changes**.

## Troubleshooting

- Offering: GitLab Self-Managed

### 413 Request Entity Too Large

When attaching a file to a comment or reply in GitLab, the [max attachment size](/administration/settings/account_and_limit_settings/#max-attachment-size)
is probably larger than the web server’s allowed value.

To increase the max attachment size to 200 MB in a Linux package install:

1. Add this line to `/etc/gitlab/gitlab.rb`:
`nginx['client_max_body_size'] = "200m"`
2. Increase the max attachment size.

### This repository has exceeded its size limit

If you receive intermittent push errors in your [Rails exceptions log](/administration/logs/#exceptions_jsonlog), like this:

`Your push to this repository cannot be completed because this repository has exceeded the allocated storage for your project.`
[Housekeeping](/administration/housekeeping/) tasks may be causing your repository size to grow.
To resolve this problem, either of these options helps in the short- to middle-term:

- Increase the [repository size limit](/administration/settings/account_and_limit_settings/#repository-size-limit).
- [Reduce the repository size](/user/project/repository/repository_size/#methods-to-reduce-repository-size).
