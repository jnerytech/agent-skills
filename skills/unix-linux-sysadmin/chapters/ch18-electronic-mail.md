# Chapter 18: Electronic Mail

## Core Idea
Email flows through a pipeline of cooperating agents speaking **SMTP/ESMTP**. The bulk of admin work is configuring the **MTA** (mail transport agent — sendmail/Postfix/Exim). Even cloud-hosted mail (Gmail/Office 365) requires understanding the architecture, reading headers to debug, and applying anti-spam (SPF/DKIM) and encryption (TLS/IMAPS). Because SMTP is text-based and standardized, heterogeneous MTAs interoperate freely.

## Frameworks Introduced
- **Mail-system components**: **MUA** (user agent — read/compose) → **MSA** (submission agent — accepts outbound from MUA, port 587, authenticates) → **MTA** (transport — routes via SMTP, port 25) → **DA/LDA** (delivery agent — writes to message store) → **AA** (access agent — IMAP/POP serves the store to clients).
- **Three parts of a message**: **envelope** (MTA-internal routing/return addresses, invisible to users) + **headers** (RFC5322 property/value pairs) + **body**. Envelope and From/To headers can disagree (mailing lists, spammers).
- **SMTP conversation**: `EHLO` (or `HELO`) → `MAIL FROM:` (envelope sender) → `RCPT TO:` (envelope recipient) → `DATA` (headers+body) → `QUIT`. Sender does most of the talking; receiver returns codes.
- **Anti-spam layers**: SPF (DNS lists authorized senders), DKIM (cryptographic signature in DNS), DSN error codes — plus the practical advice to *pay a cloud anti-spam service*.

## Key Concepts
- **MSA vs MTA**: MSA = "receptionist" on port 587, does header cleanup + authenticated/encrypted submission; often just the MTA on a different port/config. MSA→MTA relay must use **SMTP-AUTH** or you create an **open relay** (spammer-abused, blacklisted).
- **Message store formats**: **mbox** (all mail in one file `/var/mail/user`, `From ` separators) vs **Maildir** (one file per message — convenient but many tiny files).
- **Access protocols**: **IMAP** (better — per-message download, browse headers before fetching attachments, good for multiple devices) vs **POP** (downloads all at once). Use TLS versions: **IMAPS/POP3S** — never cleartext passwords.
- **SPF (Sender Policy Framework)**: DNS records naming a domain's official outbound servers; receivers reject mail not from them. **Fatal flaw: relayed/forwarded mail breaks SPF** (relay IP won't match). Be cautious acting on SPF failures.
- **DKIM**: crypto signature verifying sender identity *and* untampered transit, keys published in DNS — but real-world deployment is rare.
- **Aliases**: reroute mail; defined in `/etc/mail/aliases` (sysadmin, hashed via `newaliases`) or `~/.forward` (per-user). Recursive. Can target users, files, programs, or `:include:` files.

## Mental Models
- **Read Received headers bottom-up.** The oldest hop (sender) is at the bottom; trace upward through each MTA to the recipient. Timestamps show timezone offsets from UTC. **But headers can be forged — use with caution.**
- **Forging email is trivial** — any MUA lets you set the sender. Never use email alone to authorize door keys, money, or privilege changes; warn users about phishing.
- **One process per port.** MSA on 587, MTA on 25 — to run both on 25 they must be on different hosts. Configure MSA and MTA so they don't *duplicate* header rewriting.
- **Aliases supersede `/etc/passwd`.** An alias `david: david@elsewhere` stops local user david from ever receiving mail — adduser tools must check both files for name clashes.
- **Mailing to files/programs is a security hazard.** Only valid in `aliases`/`.forward`/`:include:` files, with strict permission/ownership rules — the message content is attacker-controlled.

## Anti-patterns
- **MSA→MTA relay without SMTP-AUTH**: an open relay — spam abuse + blacklisting.
- **Cleartext IMAP/POP**: passwords sent in the clear — require IMAPS/POP3S.
- **Acting harshly on SPF failures**: legitimate relayed mail fails SPF; relaying breaks both SPF and Sender ID.
- **Throwing away postmaster/abuse mail** (`postmaster: /dev/null`): humans with delivery problems write to postmaster — point it at a real person (`postmaster: root`, root→sysadmin).
- **Forgetting `newaliases`** after editing `/etc/mail/aliases` (sendmail/Postfix): the hashed `aliases.db` is stale until rebuilt (Exim detects changes automatically).
- **`/var/spool/mqueue` and `/var/log` on the same partition**: a queue blowup fills the disk and takes logging with it.
- **Letting external mail hit an `:include:` alias**: it becomes a spam expander.

## Code Examples
```sh
# Debug SMTP by hand — telnet to the MTA and speak the protocol
telnet mail-relay.example.com 25
  EHLO myhost.example.com           # server advertises extensions + AUTH mechanisms
  MAIL FROM:<me@example.com>
  RCPT TO:<you@example.org>
  DATA
  Subject: test
  <blank line> body... .            # lone "." ends the message
  QUIT

# sendmail diagnostics
sendmail -d0.1 -bt < /dev/null      # print version + compiled features
sendmail -bp        # == mailq : print the queue
sendmail -bv addr   # verify an address without sending
kill -HUP $(head -1 /var/run/sendmail.pid)   # reload config (started with absolute path)
newaliases          # rebuild aliases.db after editing /etc/mail/aliases
```
```
# /etc/mail/aliases
mailer-daemon: postmaster
postmaster:    root              # -> forward to a human/sysadmin, NOT /dev/null
sa-book:       :include:/usr/local/mail/ulsah.authors   # list from a file
owner-sa-book: evi               # bounces go to the list owner
cron-status:   /usr/local/admin/cron-status-messages    # append to a file
autolog:       "|/usr/local/bin/autologger"             # pipe to a program
```

## Reference Tables
**SMTP commands**: `EHLO`/`HELO` (identify, ESMTP/SMTP), `MAIL FROM:` (envelope sender), `RCPT TO:` (envelope recipient), `DATA` (body), `VRFY`/`EXPN` (verify/expand), `RSET`, `QUIT`, `HELP`.

**DSN error codes** (`X.X.X`, first digit: 2 success / 4 temporary / 5 permanent): `4.2.2`/`5.2.2` mailbox full, `4.4.1`/`5.4.1` no answer from host, `4.7.1`/`5.7.1` delivery not authorized/refused.

**MTA market share (2017)**: Exim 56% (Debian default), Postfix 33% (Red Hat/Ubuntu), sendmail 5% (FreeBSD default), Exchange 1%. Choosing: Postfix = simpler/faster/security-focused; Exim = powerful but complex; sendmail = legacy, m4-configured.

## Worked Example
**Spot a forged spam from its headers.** A message claims `From: "alert@atrust.com" <alert@atrust.com>` and `To: <ned@atrust.com>`. But the **Return-Path** (a copy of the envelope sender) reads `<smotheringl39@sherman.dp.ua>` — Ukraine, not atrust.com. Reading Received lines bottom-up, the *first* MTA to touch it is at `187.10.167.249` — Brazil. And it actually reached the mailbox `sailingevi@gmail.com`, so the envelope recipient must have been `evi@`, not the `ned@` in the To header. Google's `Received-SPF: neutral` shows the Ukrainian domain has no SPF record to check against. Three independent signals (From≠Return-Path, geographically impossible relay, To≠envelope recipient) expose the forgery — though remember any of those header lines could itself be forged. This is exactly why email must never be a trust/authorization vehicle.

## Key Takeaways
1. Mail = MUA→MSA→MTA→LDA→AA pipeline over SMTP/ESMTP; the MTA config is the bulk of the work.
2. Read Received headers bottom-up to trace a message — but treat all headers as potentially forged.
3. Require SMTP-AUTH on submission (no open relays) and TLS everywhere (IMAPS/POP3S, MTA-to-MTA STARTTLS).
4. SPF/DKIM help but SPF breaks on relayed mail — don't reject solely on SPF failure; offload spam fighting to a cloud service.
5. Forging email is trivial — warn users about phishing; never authorize anything via email alone.
6. Aliases supersede passwd, are recursive, and rebuild via `newaliases`; keep postmaster/abuse pointed at humans; mailing to files/programs is a security-restricted feature.

## Connects To
- **Ch 16**: DNS — MX records route mail; SPF/DKIM published as DNS records.
- **Ch 17**: SMTP-AUTH / SASL ties into the authentication stack.
- **Ch 19**: web hosting (similar TLS/cert concerns; HAProxy load balancing).
- **Ch 27**: security (encryption, DLP, phishing, TLS chain of trust).
- **Ch 4/10**: signals (HUP to reload), logging (mail logs, queue monitoring).
