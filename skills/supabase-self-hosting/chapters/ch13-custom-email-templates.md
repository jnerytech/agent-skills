# Chapter 13: Custom Email Templates

## Core Idea
Supabase Auth does NOT read email templates from mounted volumes — it fetches each template from a **URL** returning a valid Golang HTML template. The standard pattern is a small private `templates-server` (Caddy file-server) on the Docker network that Auth reaches by hostname.

## Frameworks Introduced
- **URL-based templates**: set `GOTRUE_MAILER_TEMPLATES_<FLOW>` to a URL (and `GOTRUE_MAILER_SUBJECTS_<FLOW>` for subject). Falls back to default if unset or invalid.
  - When to use: customizing any auth or notification email.
  - How: serve HTML via a `templates-server`; Auth GETs `http://templates-server/<file>.html`.
- **Private templates-server**: a `caddy:2-alpine` `file-server` over `./volumes/templates`, no published ports → reachable only inside the Docker network. `auth` `depends_on` it.
- **Two template categories**:
  - Auth flow templates: `GOTRUE_MAILER_TEMPLATES_<FLOW>` / `_SUBJECTS_<FLOW>`.
  - Notification templates: also need `GOTRUE_MAILER_NOTIFICATIONS_<TYPE>_ENABLED='true'`, plus `_TEMPLATES_<TYPE>_NOTIFICATION` / `_SUBJECTS_<TYPE>_NOTIFICATION`.

## Key Concepts
- **URL requirements**: needn't be public, must be reachable from `auth`, must return a valid Golang HTML template.
- **Graceful fallback**: unreachable/invalid template → Auth uses its default (so a typo won't break sign-up emails, just revert them).
- **Notifications are opt-in**: the `_ENABLED='true'` flag is mandatory to send the notification at all.

## Mental Models
- Think "Auth pulls, you don't push": you don't mount templates into Auth; you stand up a server Auth can GET from.
- Keep the template server portless → it's private to the compose network by construction.

## Anti-patterns
- **Mounting templates into the auth container**: ignored — Auth only fetches via URL.
- **Setting a notification template without `_ENABLED='true'`**: nothing sends.
- **Publishing the templates-server's port**: unnecessary exposure; keep it network-internal.

## Code Examples
```yml name=docker-compose.yml
services:
  auth:
    depends_on:
      db: { condition: service_healthy }
      templates-server: { condition: service_started }
    environment:
      GOTRUE_MAILER_TEMPLATES_INVITE: 'http://templates-server/invite.html'
      GOTRUE_MAILER_SUBJECTS_INVITE: 'You have been invited'
  templates-server:
    image: caddy:2-alpine
    command: ['caddy','file-server','-r','/templates','--listen',':80']
    volumes:
      - ./volumes/templates:/templates
```
```sh
docker compose up -d --force-recreate --no-deps auth templates-server
```
- **What it demonstrates**: the private file-server + Auth dependency + invite template wiring.

## Reference Tables
Auth flow templates (`GOTRUE_MAILER_TEMPLATES_<FLOW>`):
| Flow | Sent when |
|---|---|
| `CONFIRMATION` | signup email verification |
| `RECOVERY` | password reset |
| `MAGIC_LINK` | passwordless login |
| `INVITE` | user invited |
| `EMAIL_CHANGE` | email change |
| `REAUTHENTICATION` | re-auth for sensitive ops |

Notification types (`<TYPE>_NOTIFICATION`, need `_ENABLED`): `PASSWORD_CHANGED`, `EMAIL_CHANGED`, `PHONE_CHANGED`, `MFA_FACTOR_ENROLLED`, `MFA_FACTOR_UNENROLLED`, `IDENTITY_LINKED`, `IDENTITY_UNLINKED`.

## Worked Example — enable the "password changed" notification
Directory: `volumes/templates/password_changed_notification.html`. Then:
```yml name=docker-compose.yml
auth:
  environment:
    GOTRUE_MAILER_NOTIFICATIONS_PASSWORD_CHANGED_ENABLED: 'true'   # required
    GOTRUE_MAILER_TEMPLATES_PASSWORD_CHANGED_NOTIFICATION: 'http://templates-server/password_changed_notification.html'
    GOTRUE_MAILER_SUBJECTS_PASSWORD_CHANGED_NOTIFICATION: 'Your password was changed'
```
Recreate `auth` + `templates-server`. The `_ENABLED` flag is what actually turns the notification on; the template/subject just customize it.

## Key Takeaways
1. Auth fetches templates from URLs — it never reads mounted template files.
2. Stand up a portless `templates-server` (Caddy file-server) on the Docker network.
3. Template URL must be Auth-reachable and return valid Golang HTML; else it falls back to default.
4. Notifications require `_ENABLED='true'` in addition to template/subject vars.
5. Recreate `auth` + `templates-server` to apply.

## Connects To
- **Ch 4**/**Ch 10**: same `GOTRUE_*` passthrough discipline.
- **Ch 1**: SMTP server config (`SMTP_*`) is what actually delivers these emails.
