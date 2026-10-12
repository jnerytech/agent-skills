# Chapter 10: Configure Phone Login & MFA

## Core Idea
Phone auth is enabled by default but useless without an SMS provider — wire up Twilio (or another) via `GOTRUE_SMS_*` passthroughs, tune OTP settings, and opt into MFA factor types. Same two-layer `.env` + passthrough discipline as OAuth.

## Frameworks Introduced
- **SMS provider setup**: `.env` (`SMS_PROVIDER=twilio`, OTP settings, Twilio creds) → `GOTRUE_SMS_*` passthroughs in `docker-compose.yml` → recreate `auth`.
  - When to use: any phone login or phone-based MFA — without it, OTP codes can't be delivered.
- **Three MFA factor types**:
  - TOTP (app authenticator): **enabled by default**, no config (Google Authenticator/Authy). Disable via `MFA_TOTP_ENROLL_ENABLED/VERIFY_ENABLED=false`.
  - Phone MFA: **disabled by default** (opt-in), reuses the SMS provider config. Enable `MFA_PHONE_ENROLL_ENABLED/VERIFY_ENABLED=true`.
  - (Max factors per user: `MFA_MAX_ENROLLED_FACTORS`, default 10.)
- **Test OTP mapping**: `SMS_TEST_OTP=phone:code,...` skips real SMS for listed numbers — dev only, remove before prod (or expire with `SMS_TEST_OTP_VALID_UNTIL`).

## Key Concepts
- **`ENABLE_PHONE_SIGNUP=true`**: phone auth on by default; SMS provider is the missing piece.
- **OTP knobs**: `SMS_OTP_EXP` (seconds, default 60 — often too short), `SMS_OTP_LENGTH` (6–10, default 6), `SMS_MAX_FREQUENCY` (min interval/number, default 60s).
- **E.164 phone format**: `+1234567890` — wrong format = delivery failure.
- **Global SMS rate limit**: `GOTRUE_RATE_LIMIT_SMS_SENT` (default 30/hour) separate from per-number `SMS_MAX_FREQUENCY`.

## Mental Models
- Same pattern as Ch 4: value in `.env`, passthrough in `docker-compose.yml`, then recreate `auth`. "Not working" almost always = missing passthrough.
- TOTP is free and on; phone MFA costs SMS and is opt-in.

## Anti-patterns
- **Leaving default 60 s OTP expiry**: too short for production — bump `SMS_OTP_EXP` (e.g. 300).
- **Test OTPs in production**: remove `SMS_TEST_OTP` (or set `SMS_TEST_OTP_VALID_UNTIL`).
- **`.env` creds without passthrough**: SMS silently undelivered — verify with `docker compose exec auth env | grep GOTRUE_SMS`.
- **Non-E.164 numbers**: rejected by provider.

## Code Examples
```sh name=.env
SMS_PROVIDER=twilio
SMS_OTP_EXP=300
SMS_OTP_LENGTH=6
SMS_MAX_FREQUENCY=60s
SMS_TEMPLATE=Your code is {{ .Code }}
SMS_TWILIO_ACCOUNT_SID=...
SMS_TWILIO_AUTH_TOKEN=...
SMS_TWILIO_MESSAGE_SERVICE_SID=...
```
```yaml name=docker-compose.yml
auth:
  environment:
    GOTRUE_SMS_PROVIDER: ${SMS_PROVIDER}
    GOTRUE_SMS_OTP_EXP: ${SMS_OTP_EXP}
    GOTRUE_SMS_TWILIO_ACCOUNT_SID: ${SMS_TWILIO_ACCOUNT_SID}
    # ... + auth token, message service sid, otp length, max frequency, template
```
```sh
docker compose up -d --force-recreate --no-deps auth
docker compose exec auth env | grep GOTRUE_SMS    # verify
```
- **What it demonstrates**: the SMS provider two-layer setup + verify.

## Reference Tables
| Setting | Default | Notes |
|---|---|---|
| `SMS_OTP_EXP` | 60 s | raise for prod (e.g. 300) |
| `SMS_OTP_LENGTH` | 6 | 6–10 |
| `SMS_MAX_FREQUENCY` | 60s | per-number min interval |
| `GOTRUE_RATE_LIMIT_SMS_SENT` | 30/hr | global |
| `MFA_TOTP_*` | enabled | app authenticator |
| `MFA_PHONE_*` | disabled | opt-in, uses SMS |
| `MFA_MAX_ENROLLED_FACTORS` | 10 | per user |

## Worked Example — test OTPs without sending SMS
```sh name=.env
SMS_TEST_OTP=16505551234:123456,16505555678:654321
```
Plus uncomment `GOTRUE_SMS_TEST_OTP: ${SMS_TEST_OTP}` in `docker-compose.yml`. Now those two numbers accept only their mapped codes and skip SMS delivery; all other numbers still use the real provider. Add `SMS_TEST_OTP_VALID_UNTIL=2026-12-31T23:59:59Z` so they auto-expire — and remove them before production.

## Key Takeaways
1. Phone auth is on by default; an SMS provider is required to deliver OTPs.
2. Two layers: `.env` creds + `GOTRUE_SMS_*` passthroughs; recreate `auth`.
3. Default 60 s OTP expiry is usually too short — raise it.
4. TOTP MFA is on by default; phone MFA is opt-in and reuses the SMS config.
5. Use `SMS_TEST_OTP` for dev; never ship it.
6. Phone numbers must be E.164; mind both per-number and global SMS rate limits.

## Connects To
- **Ch 4**: identical `.env` + passthrough + recreate-`auth` pattern.
- **Ch 1**: `auth` service recreate workflow.
