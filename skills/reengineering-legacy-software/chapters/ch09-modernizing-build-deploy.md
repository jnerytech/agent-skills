# Chapter 9: Modernizing the Development, Building, and Deployment of Legacy Software

## Core Idea
Legacy software is released so rarely that the knowledge of how to build, release, and deploy it rots and ends up locked in one person's head ("Bob is on holiday"). Modernizing the toolchain (a mainstream build tool) and automating every step from local dev to PROD deployment removes the stigma of legacy code and future-proofs it against developer turnover.

## Frameworks Introduced

- **Build-tool migration (Ant → Gradle)**: Replace a bespoke/older build tool with the same modern tool the rest of the org uses, so legacy projects feel like every other project.
  - When to use: A legacy codebase uses a different/older build tool than your mainstream stack, raising context-switching costs and developer reluctance.
  - How: (1) Rearrange the project to the new tool's standard directory conventions (`src/main/java`, `src/main/webapp/WEB-INF`) so it works "for free"; (2) write the minimal `build.gradle` (apply `java` + `war` plugins, declare repos/deps); (3) convert `lib/*.jar` into declared dependencies; (4) add convenience plugins (`jetty` → `gradle jettyRun`); (5) get developer buy-in *before* switching, train them, and confirm afterward — otherwise two build scripts must be kept in sync.

- **Jenkins CI baseline + one-click TEST deploy**: Minimum CI jobs every codebase must have.
  - When to use: Always; legacy apps often predate the CI server and have *no* jobs, which is itself a black mark.
  - How: (1) A standard CI job that runs tests and builds a package on every push to version control; (2) a parameterized job for one-click deploy to TEST — add a `branch` build parameter, a shell build step that SSHes to the TEST server and does `git fetch && git checkout origin/$branch`, and an Email Extension (or Slack/HipChat) notification to all developers. Optional extras: overnight slow tests, continuous inspection (ch2).

- **Automated rolling PROD deployment with Fabric**: Zero-downtime, repeatable production deploy driven by a Python `fabfile`.
  - When to use: Deploying to a load-balanced fleet where deployments must be invisible to users; shell-in-Jenkins would be too unwieldy.
  - How (per server, one at a time): (1) detach server from load balancer; (2) stop Apache; (3) `git checkout` the **tag** (not a branch); (4) start Apache; (5) poll the healthcheck endpoint until OK (give up after 10 attempts); (6) reattach to the load balancer, then move to the next server. Wrap `fab deploy_to_prod:tag=$tag` in a parameterized Jenkins job.

## Key Concepts
- **Release**: Build artifact(s), label with a version, tag the VCS snapshot, and (usually) publish. **Releases are immutable** — fix anything by releasing a new version, never re-releasing.
- **Deployment**: Installing a released artifact onto a machine and running it.
- **Deployment ≠ Release**: You must build an artifact to deploy, but you need not formally release it. Continuous deployment (e.g. the Guardian's RiffRaff) builds on merge-to-master and auto-deploys to PROD with no version numbers or release step.
- **Continuous integration (CI)**: Server (Jenkins) that builds + tests on every push.
- **Rolling deployment**: Gracefully restart one server at a time behind a load balancer so end users see no downtime.
- **Connection draining**: After deregistering an instance from the load balancer, wait for in-flight requests to finish before stopping the server.
- **Healthcheck endpoint**: Trivial endpoint returning `OK`; proves the machine/port/web server are alive. A "good to go" endpoint additionally verifies DB, caches, and downstream APIs.
- **Infrastructure-as-code is still code**: A Fabric/deploy script is itself potential legacy code and will bit-rot if not exercised.

## Mental Models
- **Use a script-in-the-repo over a README note when** documenting a manual step — developers distrust docs ("assume the worst") but trust a committed `deploy-to-local-tomcat.sh` they can read.
- **Use standardized build tooling across all codebases when** you want developers to transfer skills and move freely between projects (90% on Gradle → the lone Ant project is the painful outlier).
- **Use automation over instructions when** a manual step is error-prone (e.g. "comment out one line for TEST, uncomment another for PROD") — tired humans following steps eventually slip.
- **Use a scheduled "dummy" deploy when** an app deploys rarely — run the deploy weekly even with no code changes, to keep the deploy script from rotting.

## Anti-patterns
- **Manual, undocumented deploy steps**: Knowledge lost when the one person who knows leaves; app becomes undeployable.
- **Privately automated, unshared solutions**: Every developer reinvents WAR-to-Tomcat deploy slightly differently (IDE plugin / shell script / manual copy dozens of times a day).
- **Trusting documentation alone**: It isn't guaranteed up to date and developers won't trust it; prefer executable scripts.
- **Switching the build tool without buy-in**: Unhappy developers keep using the old tool → two scripts to maintain.
- **Re-releasing a version**: Violates release immutability.
- **Deploying to PROD like TEST**: Skipping load-balancer detach/healthcheck/rolling restart causes visible outages.

## Code Examples

```groovy
// build.gradle — the entire build for a Java web app, vs a much longer build.xml
apply plugin: 'java'
apply plugin: 'war'
apply plugin: 'jetty'        // adds `gradle jettyRun` for local dev

repositories {
    mavenCentral()
}

dependencies {
    providedCompile "javax.servlet:servlet-api:2.5"
}
```
- **What it demonstrates**: A modern build tool gives clean/compile/package "for free" once you follow its directory conventions — `gradle build` produces the WAR; `gradle jettyRun` runs it locally.

```python
# fabfile.py — rolling PROD deploy, one server at a time
from fabric.api import *
env.hosts = ['ubuntu@ec2-...amazonaws.com', ...]

def stop_apache():  sudo("service httpd stop")
def start_apache(): sudo("service httpd start")

def git_checkout(tag):
    with cd('/var/www/htdocs/my-php-app'):
        run('git fetch --tags')
        run("git checkout %s" % tag)

def healthcheck():
    attempts = 10
    while "OK" not in run('curl localhost/my-php-app/healthcheck.php'):
        attempts -= 1
        if attempts == 0:
            abort("Healthcheck failed for 10 seconds")
        time.sleep(1)

def deploy_to_prod(tag):
    detach_from_lb(); stop_apache(); git_checkout(tag)
    start_apache(); healthcheck(); attach_to_lb()
```
- **What it demonstrates**: One Python function per deploy step, a `deploy_to_prod(tag)` entry point Fabric runs against every host in turn (`fab deploy_to_prod:tag=v5`); `run`/`sudo` execute remotely, `local` executes on the host running Fabric.

## Reference Tables

| | Release | Deployment |
|---|---|---|
| Action | Build + version-label + tag + publish artifact | Install a built artifact and run it |
| Immutable? | Yes — never re-release a version | N/A |
| Implies the other? | No | No — can deploy a build without a formal release (continuous deployment) |
| Automate via | Extend the CI build job to also create Git tags | Fabric/Jenkins job, `git checkout <tag>` |

| Build tool | Typical language |
|---|---|
| Rake | Ruby |
| MSBuild | C# |
| Gradle / Maven | Java (modern) |
| Ant | Java (older) |

## Worked Example
Author inherits a load-balanced PHP app served by Apache + `mod_php5` across three EC2 instances behind an Elastic Load Balancer (ELB), deployed by hand.

1. **TEST first**: Create a parameterized Jenkins job with a `branch` parameter; a shell build step SSHes to the TEST box and runs `cd /apps/my-php-app && git fetch && git checkout origin/$branch`; the Email Extension plugin notifies all developers. Now *anyone* can deploy to TEST, today and years from now.
2. **PROD is riskier** — must be invisible to users, so use a rolling deploy. Shell-in-Jenkins would be unwieldy, so use **Fabric** (Python remote-execution over SSH).
3. Write a `fabfile` skeleton with one stub function per step, plus a `deploy_to_prod(tag)` entry point; Fabric runs it against each host in turn.
4. Fill in the stubs: `stop_apache`/`start_apache` via `sudo`; `git_checkout(tag)` via `git fetch --tags` + `git checkout <tag>`; `healthcheck` polling `curl .../healthcheck.php` up to 10 times; `detach_from_lb`/`attach_to_lb` via the AWS CLI (`aws elb deregister/register-instances...`), waiting on connection draining and on the ELB reporting 3 healthy instances (parsing JSON with `jq`).
5. **Wrap in Jenkins**: parameterized build takes a `tag`, checks out the fabfile repo, runs `fab deploy_to_prod:tag=$tag`. Result: one-click PROD deploy for any dev or ops member, future-proofed.
6. **Guard the deploy script**: it's code and will rot — add a weekly scheduled Jenkins job that deploys even with no app changes.

## Key Takeaways
1. Small changes (swapping an outdated build tool for the org standard) remove barriers to entry and end the "second-class citizen" stigma of legacy code.
2. The longer/more complex the legacy build script, the *more* value in converting it to a maintainable modern one.
3. Modern build tools give clean/compile/package and local-run plugins almost for free once you adopt their directory conventions.
4. Every codebase needs at minimum a CI test/build job and a one-click TEST deploy; legacy apps often have neither.
5. Manual deploy knowledge is fragile and walks out the door; automate it so the app stays deployable across generations of developers.
6. Release and deployment are distinct — releases are immutable; deployment doesn't require a formal release.
7. Deploy scripts *are* code (potential legacy); exercise them on a schedule to prevent bit-rot.

## Connects To
- **Ch2**: Jenkins CI server and continuous inspection introduced earlier; this chapter adds deploy jobs on top.
- **Ch7/Ch8**: Provisioning/environment automation built the TEST and PROD machines (the UAD app); this pipeline deploys onto them.
- **Continuous Delivery (Humble & Farley)**: This chapter's release-vs-deployment distinction, immutable artifacts, rolling deploys, and healthchecks are the practical core of their deployment-pipeline model.
- **Fabric / RiffRaff / AWS ELB + jq**: concrete tools — Fabric for SSH orchestration, the Guardian's RiffRaff for continuous deployment, ELB for rolling restarts, `jq` for parsing CLI JSON.
