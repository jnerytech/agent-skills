# Chapter 3: Encrypting Secrets the Kubernetes-Native Way

## Core Idea
kube-apiserver has a built-in **KMS framework** (`EncryptionConfiguration`) with four providers — `identity`, `aescbc`, `aesgcm`, `kms` — evaluated **in list order**; `kms` with envelope encryption (DEK/KEK) is the only option that keeps the key off the control-plane disk, and it must be layered on top of OS/disk/filesystem/transport hardening because etcd itself has **no encryption capability whatsoever** except on the wire.

## Frameworks Introduced

- **The EncryptionConfiguration provider list with precedence** — the core mechanic of native encryption.
  - When to use: enabling, changing, or rotating encryption at rest for `secrets` (and, since v1.25, ConfigMaps and custom resources).
  - How:
    1. **Write** — kube-apiserver uses the **first** provider in the list to encrypt new/updated objects.
    2. **Read** — kube-apiserver inspects the **Secret's header** to identify provider, version, and key. Match ⇒ decrypt. No match ⇒ error.
    3. **Migrate** — reorder the list (put the new provider first, keep the old one below it), then rewrite every Secret to a new revision. That is how you go from unencrypted to `aesgcm`, or rotate keys, with no downtime.
  - Why it works: keeping the old provider *below* the new one preserves read access to not-yet-rewritten objects. **Failure mode**: removing the old provider before rewriting all Secrets makes them permanently unreadable.

- **Envelope encryption (DEK / KEK)** — the two-key scheme behind the `kms` provider.
  - When to use: any compliance regime requiring external key management; any environment where control-plane disk access is a credible threat.
  - How: a **DEK** (data encryption key) encrypts the `data` payload and is generated locally by kube-apiserver; a **KEK** (key encryption key) encrypts the DEK and is generated and *hosted remotely on the KMS*. Only the encrypted DEK lands in etcd.
  - Why it works: the key that could decrypt etcd never sits on the node. **Recommended granularity**: one dedicated KEK **per cluster** — a shared KEK across clusters is a single point of failure and a shared blast radius. (Per-tenant KEKs would be ideal but were not implemented at time of writing.)

- **Onion-layer defense for etcd** — encryption at the API layer is one ring; the others must be hardened separately.
  - When to use: designing a production etcd posture, especially self-managed / on-prem / edge.
  - How, outermost to innermost: **Transport (TLS)** → **Linux system hardening (SCAP/CIS/NIST profiles + OpenSCAP scanning)** → **Disk encryption (FDE/SED)** → **Filesystem encryption (dm-crypt / LUKS / NBDE)** → **Kubernetes native encryption (EncryptionConfiguration)**.
  - Why it works: each ring fails to a different attacker. Native encryption does nothing against a wire tap; TLS does nothing against a stolen disk.

- **Risk-based selection of filesystem encryption** — choose by requirement, not by sophistication.
  - How: plain `dm-crypt` for deniable, header-less, disaster-resilient block encryption (but no key derivation, no rotation, no TRIM); **LUKS** when you need key rotation, key derivation, and multiple passphrases; **NBDE/Tang** when you need transparent reboot without a passphrase and without a vault to keep highly available.

## Key Concepts
- **EncryptionConfiguration** — `apiserver.config.k8s.io/v1` API object, deployed as a **file on every control-plane node**, listing `resources` and an ordered `providers` list.
- **`identity` provider** — the default; performs **no** transformation. Also the tool you use to *decrypt back* to plaintext.
- **`aescbc`** — AES-CBC: "considered weak but fast."
- **`aesgcm`** — AES-GCM: "faster and less weak **when key rotation is implemented**."
- **DEK (data encryption key)** — encrypts the payload; generated locally, tied to the cluster.
- **KEK (key encryption key)** — encrypts the DEK; generated and stored on the external KMS.
- **KMS provider plugin** — third-party shim connecting kube-apiserver to a KMS, deployed on control-plane nodes over a **local UNIX socket** (not the network). e.g. **Trousseau** (Vault, Azure Key Vault, AWS KMS).
- **KMSv1 vs KMSv2** — see table below. KMSv1 is **deprecated as of Kubernetes 1.28**.
- **FDE / SED** — full-disk / self-encrypting disk; offloaded, transparent, but boot needs a key and it has documented attacks.
- **LUKS** — universal disk encryption with secure password management: key derivation, rotation, multiple passphrases; composable with LVM and software RAID.
- **NBDE (network-bound disk encryption)** — a quorum of servers (e.g. **Tang**) over HTTP/HTTPS holds split symmetric key material; unlock only succeeds on the right network. No vault, no HA/backup burden for keys.
- **TPM** — can auto-unlock LUKS at boot, but a stolen server carries the TPM with it.
- **OpenSCAP** — scans an install base against SCAP profiles (PCI-DSS, CIS, NIST) and emits a risk-scored audit plus remediation as Shell/Puppet/Ansible.

## Mental Models
- **Think of encryption at rest as one ring of an onion, not a checkbox.** "Encrypting the data contained in the payload will protect from the aforementioned protection mechanisms, but **not replace them**."
- **Use `aesgcm`/`aescbc` as the fast on-ramp, `kms` as the destination.** Local AES is trivial to enable and immediately raises the bar — but the key is base64 in a YAML file on the control-plane disk. A disk or filesystem breach hands the attacker both the ciphertext and the key.
- **Read the provider list top-down for writes, header-driven for reads.** That asymmetry is why migrations work and why premature key removal is fatal.
- **Assume one compromised etcd compromises the fleet.** In hybrid multi-cloud, a breached etcd holds the fleet-management token — "a viral attack infecting every connected endpoint."
- **Security is not a finite game.** Regular audits and scans produce a rolling backlog of mitigations, not a one-time pass.

## Code Examples

The explicit form of the Kubernetes default (no encryption) — the safe starting file:

```yaml
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
- resources:
  - secrets
  - configmaps
  providers:
  - identity: {}
```

Turning on local AES-GCM, with `identity` kept **below** it so pre-existing plaintext Secrets stay readable:

```yaml
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
- resources:
  - secrets
  providers:
  - aesgcm:
      keys:
      - name: key-20230616
        secret: DlZbD9Vc9ADLjAxKBaWxoevlKdsMMIY68DxQZVabJM8=
  - identity: {}
```
- **What it demonstrates**: `aesgcm` first ⇒ new writes are encrypted; `identity` second ⇒ old plaintext still decodes. The key is a **32-byte (or more) random value, base64-encoded**.

Wiring it into the kube-apiserver static Pod:

```yaml
apiVersion: v1
kind: Pod
spec:
  containers:
  - command:
    - kube-apiserver
    - --encryption-provider-config=/etc/kubernetes/encryption/configuration.yaml
    - --encryption-provider-config-automatic-reload=true   # Kubernetes 1.26+
```
- **What it demonstrates**: the config file must exist on **every** control-plane node at that exact path. Auto-reload avoids restarting the apiserver on every key change.

## Reference Tables

| Provider | External dependency | Where the key lives | Strength | Use when |
|---|---|---|---|---|
| `identity` | none | n/a | none — base64 only | Default; also used to *revert* to plaintext |
| `aescbc` | none | base64 in YAML on control-plane disk | weak but fast | Legacy / speed-only; avoid new use |
| `aesgcm` | none | base64 in YAML on control-plane disk | better, **requires key rotation** | Quick win, no KMS available |
| `kms` (v2) | KMS + provider plugin | KEK remote on KMS; DEK cached in apiserver memory | strongest; meets external-key-management regs | Production / regulated |

| | KMSv1 | KMSv2 |
|---|---|---|
| DEK generation | One **per Secret creation** | One at **startup / config reload** |
| KMS calls | Every transaction | Only at restart and key rotation |
| Crypto operations | Round-trip to plugin | From **cached DEK in memory** |
| Large-cluster performance | Degrades | Greatly improved |
| Network partition tolerance | Poor | Resilient |
| Status | **Deprecated in v1.28** | Current |

| Filesystem encryption | Key rotation | Deniable | TRIM safe | Complexity |
|---|---|---|---|---|
| plain `dm-crypt` | ✗ (single passphrase, no KDF) | ✓ (no header/UUID/LABEL) | ✗ (leaks freed-block pattern) | High mastery required |
| **LUKS** | ✓ (KDF + multiple passphrases) | ✗ (header at device start) | ✓ *if* passphrase rotated | Moderate |
| **LVM on LUKS** | single key, all volumes | ✗ | — | Easy partitioning, protects layout |
| **LUKS on LVM** | per-volume | ✗ | — | Complex, **exposes volume layout** |
| **NBDE (Tang)** | ✓ via re-distributable public key | ✗ | — | Surprisingly easy; needs quorum |

## Worked Example

**Migrating a cluster from plaintext to encrypted Secrets, then verifying it in etcd** (the ch03 Kind walkthrough):

1. Stand up a **Kind** cluster (Podman or Docker) with a cluster config file that both sets the two kube-apiserver flags and **mounts a host folder into the apiserver Pod** — the config lands at `/etc/kubernetes/encryption/configuration.yaml`. This mount-plus-flags pattern transfers to any distribution.
2. Start with the explicit `identity`-only file. Create some Secrets. They are base64 in etcd.
3. Generate a 32-byte random key, base64-encode it, and rewrite the config with `aesgcm` **first** and `identity` **second**. With auto-reload on, no apiserver restart is needed.
4. **Rewrite** the existing Secrets (create the new revision). Because `aesgcm` is first, each rewritten Secret is now stored encrypted; unrewritten ones still read via `identity`.
5. **Verify by dumping the entries directly from the etcd data store** — confirm each Secret carries the expected provider/key/version header and that the payload is no longer readable. This is the only proof that matters; `kubectl get` looks identical either way.
6. Repeat with the `kms` provider to see the same migration path work against an external KMS via a plugin such as Trousseau over a local UNIX socket.

The generalizable lesson: **provider changes are non-disruptive because of list precedence, but they only take effect on objects you rewrite.**

## Anti-patterns
- **Deploying the EncryptionConfiguration to only one control-plane node** — every control-plane node needs the file at the flagged path.
- **Removing the old provider before rewriting all Secrets** — reads fail with no match and the data is unrecoverable.
- **Using `aescbc`/`aesgcm` without an automated key-rotation strategy** — vulnerable to padding-oracle attacks, birthday attacks, and key-guessing based on how many payloads were written with a key.
- **Sharing one KEK across multiple clusters** — single point of failure and shared blast radius.
- **Assuming a managed Kubernetes service handles it** — "not all services are equal"; verify the provider encrypts at rest *and* lets you enable native encryption. All major providers advise doing both.
- **Terminating TLS only at an external load balancer** — that secures the user→apiserver hop and leaves **internal** cluster traffic, including etcd, readable on the wire.
- **Treating FDE as sufficient** — attacks succeed both with and without stealing the machine; layer filesystem encryption on top.
- **Enabling TRIM under plain `dm-crypt` when deniability matters** — freed blocks leak enough to expose the encryption pattern.

## Key Takeaways
1. `EncryptionConfiguration` + two apiserver flags is the entire native mechanism: `--encryption-provider-config` and `--encryption-provider-config-automatic-reload=true` (1.26+).
2. **Provider order is write-order; reads are header-driven.** Migration = reorder + rewrite, never reorder alone.
3. `aesgcm`/`aescbc` put the key on the control-plane disk — a real improvement, but the key and ciphertext share a breach.
4. `kms` + envelope encryption (DEK local, KEK remote) is the recommended production pattern and the one that satisfies external-key-management regulations.
5. **KMSv1 is deprecated in 1.28**; KMSv2's cached DEK is both faster at scale and tolerant of network partitions.
6. One KEK per cluster, minimum. Never one KEK for the fleet.
7. etcd offers **no** at-rest encryption of its own — the data file is readable; so disk + filesystem encryption and OS hardening are not optional extras.
8. TLS everywhere: external termination alone leaves internal Kubernetes flows exposed.

## Connects To
- **Ch 1**: the five exposures — this chapter closes the etcd-file and (partially) the backup one.
- **Ch 2**: `resources` in the config covers both `secrets` and `configmaps`, closing the ConfigMap gap.
- **Ch 6**: encrypted backups depend on these keys surviving; losing the KEK loses the restore.
- **Ch 8/9/10**: AWS KMS, Azure Key Vault, and GCP KMS are the concrete KEK hosts.
- **Ch 11**: HashiCorp Vault as the KMS behind Trousseau.
- **CIS Benchmarks, NIST, PCI-DSS, SCAP/OpenSCAP** — the compliance frameworks driving the hardening layer.
