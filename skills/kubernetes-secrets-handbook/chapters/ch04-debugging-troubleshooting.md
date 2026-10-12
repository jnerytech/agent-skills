# Chapter 4: Debugging and Troubleshooting Kubernetes Secrets

## Core Idea
Secret bugs almost never surface as Secret errors — they surface as a *dependent component* failing — so debug **top-down** from the broken app to the Secret, then verify the Secret's content by **hashing it, never printing it**, because printing a Secret into stdout ships it to your org-wide logging platform and forces a rotation.

## Frameworks Introduced

- **The five-step Secret evaluation checklist** — run this once your top-down search reaches the Secret.
  - When to use: as soon as logs implicate a Secret.
  - How:
    1. Ensure the **existence** of the Secret.
    2. Check the **value** of the Secret.
    3. **Decode** it and confirm it's the desired one.
    4. Use **MD5 hashing** to compare rather than eyeballing plaintext.
    5. **Avoid downloading Secrets locally** — it can violate your infosec policy.

- **Isolate the Secret from the application** — the three-step rule-out.
  - When to use: when you suspect the *consumption* (mount/env wiring) rather than the value, and trial-and-error on the real deployment is producing noise.
  - How: take a **simple container** (busybox/alpine) — less complexity, less that can go wrong — and
    1. Mount the Secret as **environment variables** to a Pod.
    2. Mount the Secret as a **file** to a Pod.
    3. **Hash** the result and compare to the expected hash.
  - Why it works: "there are many things that can go wrong in an application. This translates to noise… Ruling out that the Secrets are not the problem brings us closer to a resolution."

- **Three principles that prevent Secret errors in the first place.**
  - **YAML files are structured and can create a source of truth** — reviewable in an editor, re-appliable after a fix.
  - **Reusability of Secrets minimizes errors** — the more times you re-create the same Secret, the more chances to fumble it.
  - **Automation removes human intervention, which is prone to error** — "most of the time, when an error is introduced, it is highly likely to be caused by human intervention."

- **Dry run before apply.** `--dry-run=client` validates syntax/type without touching the cluster; add `-o yaml` to inspect exactly what would be created. **Limit**: a dry run cannot catch a *successfully applied Secret with invalid content*.

## Key Concepts
- **`kubectl describe`** — the escalation from `kubectl get`; surfaces events, labels, annotations, and resource-specific properties. The primary Secret-debugging tool.
- **`ContainerCreating` (stuck)** — the symptom of a **missing Secret mounted as a volume**. Feedback is *not* immediate; the Deployment loops silently.
- **`CreateContainerConfigError`** — the symptom of a **missing Secret referenced via `envFrom`/`secretRef`**. Fails within seconds.
- **`FailedMount` warning** — `MountVolume.SetUp failed for volume "users-volume": secret "user-file" not found`.
- **Helm Secrets** — Helm plugin providing encryption/decryption of chart values via AWS KMS, GCP KMS, or **GPG/OpenPGP**; driven by a `.sops.yaml` `creation_rules` file.
- **PGP key pair** — public key encrypts (distributable), private key decrypts (kept secret). Generate with `gpg --generate-key` (or `--full-generate-key` for options).
- **The double-base64 trap** — a value that is *itself* already base64/hex-looking gets decoded by Kubernetes on injection, delivering **binary** to the container instead of the string you meant.

## Mental Models
- **Debug top-down, not Secret-first.** Start at the failing application; follow the logs; the misconfigured Secret is the terminus, not the entry point.
- **Think of a Secret's *type* as documentation, not validation.** Kubernetes validates `dockercfg` and rejects malformed JSON — but silently accepts a `kubernetes.io/tls` Secret with garbage certs and a `kubernetes.io/basic-auth` Secret with no `username` key at all.
- **Treat stdout as a publishing channel.** Container logs go to CloudWatch / Datadog / Google Cloud Monitoring — "more accessible in an organization than direct Secret access on a Kubernetes cluster." `echo $SECRET` is a data-leak incident.
- **Compare hashes, not values.** `md5sum` proves equality without ever revealing the secret.
- **An Ingress with a bad cert doesn't fail — it lies.** "If we don't provide a certificate by ourselves or we provide a bad certificate configuration, **Kubernetes will generate a certificate on its own**." The Ingress comes up healthy; only the controller logs tell the truth.

## Code Examples

Dry-run validation, with the generated manifest for inspection:

```bash
$ kubectl create secret generic opaque-example-from-literals \
    --from-literal=literal1=text-for-literal-1 --dry-run=client -o yaml
secret/opaque-example-from-literals created (dry run)
apiVersion: v1
data:
  literal1: dGV4dC1mb3ItbGl0ZXJhbC0x
kind: Secret
```

Verify a Secret reached the container intact — **without printing it**:

```yaml
apiVersion: v1
kind: Pod
spec:
  containers:
  - command: ["/bin/sh","-c"]
    args: ["echo $(key) | md5sum"]
    envFrom:
    - secretRef:
        name: aes-key
```
```bash
$ kubectl logs print-env-pod
6a59e95805ea05ff21a708038be9b130   # matches the source hash → value is correct
```
- **What it demonstrates**: the hash-compare pattern. Print the digest, never the value.

Ingress TLS failure — the only place the truth appears is the **controller** log:

```bash
$ kubectl get ing        # looks healthy: ADDRESS assigned, ports 80,443
$ kubectl describe ing   # only "Scheduled for sync" — no error
$ kubectl logs -f ingress-nginx-controller-755dfbfc65-vf7v6 -n ingress-nginx
W … backend_ssl.go:45] Error obtaining X.509 certificate: unexpected error
    creating SSL Cert: no valid PEM formatted block found
W … controller.go:1348] Unexpected error validating SSL certificate
    "default/ingress-tls" for server "bad-ssl": x509: certificate is not
    valid for any names, but wanted to match bad-ssl
```
- **What it demonstrates**: `get` and `describe` on the Ingress are both clean. Escalate to the **controller's** logs.

Helm Secrets + SOPS with a PGP key:

```yaml
# .sops.yaml
creation_rules:
  - pgp: >-
      <gpg-key-fingerprint>
```
```bash
$ gpg --generate-key          # leave the passphrase EMPTY or automation breaks
$ helm secrets enc values.yaml
```
```yaml
jwt-key:
  value: ENC[AES256_GCM,data:9/0gmkCNm2DbEw==,iv:dbthtzx…,tag:MLVXlruH…,type:str]
```
- **What it demonstrates**: values stay in Git in YAML shape, encrypted per-value, with the structure still reviewable.

## Reference Tables

| Symptom | Wiring | Speed of feedback | Where the truth is |
|---|---|---|---|
| Pod stuck `ContainerCreating` | Secret as **volume** | Slow / silent loop | `kubectl describe pod` → `FailedMount` |
| `CreateContainerConfigError` | Secret via **`envFrom`/`secretRef`** | Seconds | `kubectl describe pod` → `secret "…" not found` |
| Ingress serves a Kubernetes-generated cert | bad `kubernetes.io/tls` Secret | None — looks healthy | **Ingress controller logs** |
| Value arrives as binary garbage | already-encoded value in `data:` | Runtime only | hash-compare inside a test Pod |

| Secret type | Content validated on apply? | Failure mode if wrong |
|---|---|---|
| `kubernetes.io/tls` | **No** | Accepted; breaks at mount/use; Ingress substitutes its own cert |
| `kubernetes.io/basic-auth` | **No** | Accepted with wrong/missing keys entirely |
| `kubernetes.io/dockercfg` | **Yes** | `Invalid value: "<secret contents redacted>": invalid character 'R' looking for beginning of value` |
| `Opaque` | No (by design) | Runtime |

## Worked Example

**The double-base64 bug, reproduced end to end.** This is the chapter's signature trap:

1. Generate a key that is *already* printable-ASCII-encoded:
   ```bash
   $ secretKey=$(openssl rand -hex 32)
   $ echo "$secretKey"        # 80a3284da641…552e11
   $ echo "$secretKey" | md5sum
   6a59e95805ea05ff21a708038be9b130          # ← the reference hash
   ```
2. **Correct path** — create via `--from-literal`, letting Kubernetes do the encoding:
   ```bash
   $ kubectl create secret generic aes-key --from-literal=key=$secretKey
   # stored as data.key: ODBhMzI4NGRhNjQx…  (base64 of the hex string)
   ```
   Mount it with `envFrom.secretRef` and hash it in the Pod → `6a59e95805ea05ff21a708038be9b130`. **Match.**
3. **Broken path** — hand-write the YAML and put the hex string straight into `data:` without base64-encoding it:
   ```yaml
   data:
     key: 80a3284da641ac728b5585fd913b0e60e9c4f61ffe2cfb6f456c16a312552e11
   ```
   This *applies successfully*. But Kubernetes treats `data:` as base64, **decodes it**, and delivers the resulting **binary** as the environment variable.
   ```bash
   $ kubectl logs -f print-env-pod
   fc7d115eb58e428c53b346659e7604d6          # ← different hash
   ```
4. Diagnosis: the value was decoded once too many. Fix by either base64-encoding it for `data:` or moving it to `stringData:`.

The authors' framing: this "can create confusion and hours of debugging" — and note that they deliberately compared **MD5 hashes rather than printing the variable**, "Printing variables in a live environment might lead to a data leak."

## Anti-patterns
- **`kubectl exec` into a Pod and `echo $SECRET`** — writes the secret to stdout → the org's logging platform → mandatory revocation and rotation.
- **Downloading Secrets to your laptop for inspection** — likely an infosec-policy violation.
- **Trial-and-error editing of the real deployment** — application noise masks the Secret problem; isolate in a minimal container instead.
- **Trusting Secret `type` to validate content** — only `dockercfg` is validated; TLS and basic-auth are not.
- **Putting an already-encoded value in `data:`** — double-decode; use `stringData:` or encode it properly.
- **Setting a passphrase on the GPG key used by Helm Secrets** — "it will be required at every step of decryption making operations difficult to automate."
- **Creating Secrets ad hoc from the CLI each time** — no source of truth, no reusability, maximum human error.
- **Stopping at `kubectl describe ing`** when TLS misbehaves — the Ingress reports healthy; go to the controller logs.

## Key Takeaways
1. Debug **top-down**: failing app → logs → dependent component → Secret. Secrets rarely announce themselves.
2. `kubectl describe` is the workhorse; escalate to **controller logs** when the resource itself reports healthy.
3. `--dry-run=client -o yaml` catches syntax/type errors but never bad *content*.
4. Volume-mounted missing Secrets hang in `ContainerCreating`; env-referenced ones fail fast with `CreateContainerConfigError`.
5. Only `dockercfg` Secrets are content-validated. Invalid TLS certs and malformed basic-auth apply cleanly and fail later.
6. **Hash, don't print.** MD5-compare inside a throwaway Pod proves the value without leaking it.
7. Watch for the **double-base64 trap** with hex/base64-shaped values.
8. Prevention beats debugging: YAML as source of truth + Secret reuse + automation (Helm/Helm Secrets/SOPS).

## Connects To
- **Ch 2**: Secret types and `stringData` vs `data` — the source of the double-encoding trap.
- **Ch 3**: encryption at rest; troubleshooting must not undo it by dumping plaintext to logs.
- **Ch 5**: audit and compliance — leaked Secrets in logs are a reportable incident.
- **Ch 8/9/10**: CloudWatch, Azure Monitor, and Google Cloud Monitoring as the observability path that replaces `kubectl`.
- **Ch 12/13**: SOPS, Sealed Secrets, and CI/CD pipeline patterns that automate away human error.
