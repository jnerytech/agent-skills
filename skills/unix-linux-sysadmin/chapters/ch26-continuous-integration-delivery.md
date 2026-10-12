# Chapter 26: Continuous Integration and Delivery

## Core Idea
CI/CD automates the path from code commit to running software. **Continuous integration** = developers merge frequently to a shared branch, each merge auto-builds and auto-tests. **Continuous delivery** = auto-deploy passing builds to non-production environments. **Continuous deployment** = auto-deploy all the way to production with no human intervention. The payoff: small, frequent, low-risk changes — deploy multiple times a day, isolate regressions fast (small deltas), fix bugs in hours not weeks. CI/CD is the bedrock of DevOps and squarely a sysadmin responsibility.

## Frameworks Introduced
- **The CI/CD pipeline** (sequential stages): **build** (compile/package → an *artifact*) → **test** (multiple kinds) → **deploy** (to dev → staging → production). A build that passes tests = "release candidate"; a deployed one = "release."
- **Build once, deploy often**: the build produces *one* artifact that flows unchanged through every environment — the only way to confirm a build is production-ready is to test *that exact artifact*.
- **The test pyramid**: static analysis (syntax/security/complexity, no execution) → unit tests (per function, developer's view) → integration tests (app + real dependencies/DB/APIs) → acceptance tests (user's view, e.g. Selenium) → performance/stress tests (production clone, real traffic) → infrastructure tests (Serverspec — verify provisioning).
- **Zero-downtime deployment strategies**: **blue/green** (stage new on standby, test, switch load-balancer traffic), **rolling** (update one node at a time through the LB), **canary** (route a small % to the new release first, watch telemetry, back out if bad). **Immutable deployment** = never mutate a server; build new servers with the new artifact baked in (cattle, not pets).

## Key Concepts
- **Environments** (ascending importance): **dev** (integrate changes, reset often, technical staff), **staging/test** (manual+automated testing, stakeholders, pen-testing), **production** (real users, HA/security, outages are emergencies). Software is promoted through them in succession, filtering errors.
- **Environment parity**: lower environments must match production closely (OS versions, redundancy, data scale) or you get "works in dev, breaks in prod" surprises (missing library functionality, slow queries on prod-scale data). Anonymize sensitive data when copying prod data down.
- **Build artifact**: the build's output — `.jar`/`.war`, static binary, `.rpm`/`.deb`, pip/gem package, container image, machine image. Stored in an artifact repository (S3, yum/APT repo, image registry) accessible to all deploy targets.
- **Feature flags**: config toggles that enable/disable a feature per environment — ship code dark, activate via a low-risk config change (not a release), disable instantly if buggy.
- **Jenkins**: the dominant open-source automation server — a *coordinator* (the real work is done by external tools: compilers, test harnesses, deployers); **Pipeline-as-code** via a `Jenkinsfile` (Groovy DSL) committed alongside the app.

## Mental Models
- **Fixing a broken pipeline is the top priority** — like halting a factory assembly line. No new code merges until it's green. But keep it **blame-free**: a broken build carries no stigma, the goal is just to get it running.
- **Build fast, fix fast.** Feedback within minutes keeps the failing change fresh in the developer's mind. Slow builds are counterproductive — add agents, parallelize tests, cut redundant steps.
- **Version control is the single source of truth** — nothing managed manually or off the record, including infrastructure code, docs, and config.
- **Never suppress a failing test "because it's harmless."** That erodes trust in the whole system — enforce technically that production deploys can't happen with any broken test.
- **Secrets never go in version control.** Read them from Jenkins' encrypted credential store into environment variables at pipeline runtime — embedding an API token in a committed Packer/Terraform file is a security antipattern.

## Anti-patterns
- **Building from work-in-progress / random branches**: only commits to the *integration branch* trigger builds; developers initiate integration when ready.
- **Rebuilding the artifact per environment**: violates "build once, deploy often" — you can no longer trust that what you tested is what ships.
- **Environment drift** (dev/staging on a newer OS than prod): causes production-only failures — keep environments in sync.
- **Suppressing/ignoring broken tests**: dangerous; make it technically impossible to deploy with failures.
- **Storing API tokens in committed Terraform/Packer configs**: pass them as variables from a credential store instead.
- **Home-grown ssh-loop deploy scripts at scale**: don't scale past a handful of hosts — use config management, a container orchestrator, or a dedicated deploy tool.
- **Rolling deployment when the app can't tolerate two versions running simultaneously**: causes problems — use blue/green instead.

## Code Examples
```groovy
// Jenkinsfile — pipeline as code (commit alongside the app)
pipeline {
  agent any
  environment {
    DO_TOKEN = credentials('do-token')          // from encrypted credential store, NOT git
    SSH_FINGERPRINT = credentials('ssh-fingerprint')
  }
  stages {
    stage('Checkout')   { steps { checkout scm } }
    stage('Unit tests') { steps { sh 'go test' } }
    stage('Build')      { steps { sh 'go build' } }
    stage('Build image'){ steps { sh 'packer build pipeline/packer/ulsahgo.json' } }
    stage('Deploy')     { steps { sh 'bash pipeline/testing/tf_testing.sh' } }
  }
}
```
```sh
# Go unit test (developer's view: input -> expected output)
func TestOrdinal(t *testing.T) {
  if ordinal(1) != "1st" { t.Error("expected 1st") }
}
go test                          # PASS  -> pipeline continues

# Terraform: declare desired infra; secrets passed as -var, not embedded
terraform apply -var do_image="$(<do_image.txt)" -var do_token="${DO_TOKEN}"
# Try Jenkins quickly:
docker run -p 8080:8080 --name jenkins jenkinsci/jenkins
```

## Reference Tables
**Test types** (fast→slow, narrow→broad): static analysis (no execution) · unit (functions, dev view) · integration (app + dependencies) · acceptance (user paths, browsers) · performance/stress (prod clone, real traffic) · infrastructure (Serverspec).

**Deployment strategies**: blue/green (standby→switch via LB, full rollback) · rolling (one node at a time; needs version coexistence) · canary (small % first + telemetry) · immutable (new servers per release, cloud/API-driven).

**Artifact types & repos**: jar/war, static binary, rpm/deb, pip/gem, container image, machine image → stored in SFTP/NFS dir, yum/APT repo, image registry, or S3.

## Worked Example
**A real pipeline: commit → tested DigitalOcean deployment (UlsahGo).** Jenkins polls GitHub (real life: a web hook). On a new commit to the integration branch, the `Jenkinsfile` runs: (1) `checkout scm`; (2) **unit tests** `go test` — if they fail the pipeline stops here, isolating the bug to the latest small commit; (3) **build** `go build` → a single static Go binary (no deps — copy-to-install); (4) **build image** — Packer takes a vanilla Ubuntu image, a *file* provisioner uploads the binary + a systemd unit, a *shell* provisioner updates the OS and creates a service user; the resulting machine-image ID is grepped out and saved to `do_image.txt` (the deployment artifact); (5) **deploy** — Terraform reads `ulsahgo.tf`, requisitions a droplet from that image, and writes its IP for the next stage. Crucially, the DigitalOcean token isn't in the repo — it's read from Jenkins' credential store as `DO_TOKEN` and passed via `terraform -var`. Each stage's STDOUT lands in the Jenkins console for debugging; a "weather" icon (sun/storm) shows recent build health. This is "build once" (one image flows on), "automate end-to-end," and "infrastructure as code" (Packer + Terraform committed in a `pipeline/` subdir) all at once.

## Key Takeaways
1. CI integrates and tests every commit; CD/continuous deployment automate delivery to staging and production — small frequent changes = low risk, fast regression isolation.
2. Build once into a single artifact and promote that exact artifact through dev → staging → prod; keep environments at parity.
3. Test in layers (static → unit → integration → acceptance → performance → infra), run them in parallel, and never let a deploy proceed with a failing test.
4. A broken pipeline is everyone's #1 priority to fix (blame-free); build fast for fast feedback; version control is the single source of truth.
5. Deploy with zero downtime via blue/green, rolling, or canary; prefer immutable infrastructure (new servers per release) where possible.
6. Jenkins coordinates the pipeline; use Pipeline-as-code (`Jenkinsfile`) and a credential store for secrets — never commit secrets.

## Connects To
- **Ch 23**: configuration management (environments, deployment orchestration, provisioning).
- **Ch 24**: virtualization (Packer images, immutable infrastructure).
- **Ch 25**: containers (image artifacts, Kubernetes/Swarm orchestrated deploys).
- **Ch 19**: load balancers (blue/green, rolling, canary all route through the LB).
- **Ch 31**: DevOps philosophy (CI/CD as its central practice).
