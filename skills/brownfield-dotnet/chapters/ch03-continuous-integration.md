# Chapter 3: Continuous Integration

## Core Idea
Continuous Integration closes the feedback loop on a brownfield project by automating the build (compile, test, release) so integration errors surface within minutes of a check-in instead of days or weeks later. The hard part is cultural, not technical: CI doesn't create more problems, it just exposes existing ones earlier.

## Frameworks Introduced

- **The Feedback Loop**: the time between when a problem is created and when it's discovered.
  - When to use: framing why CI matters — the longer the loop, the more expensive the fix (cost rises by an order of magnitude at each stage: dev → testing team → client).
  - How: shorten the loop by detecting problems as close to their creation as possible — compiler catches syntax instantly; CI catches integration errors on check-in; testers and clients are the worst-case discoverers.
  - Why it works / failure mode: brownfield defect lists are full of issues a regular integration process would have caught early. Failure mode is leaving discovery to the client.

- **The Updated Check-In Dance** (CI version): the disciplined sequence each developer follows before and after committing.
  - When to use: every check-in once a CI process exists.
  - How (7 steps): 1) Compile local copy, 2) Test local copy, 3) Get latest from source control and merge, 4) Compile merged version, 5) Test merged version, 6) Check code into source control, 7) Stop and wait for confirmation from the build server that there are no errors.
  - Why it works / failure mode: step 7 (build-server compile+test) catches a forgotten class or unreferenced third-party library that local builds miss. Steps 1-2 must run the *same way* as the server (build script, not IDE). Failure mode: skipping the merge step (3) and breaking the build for the next person.

- **Setting Up a CI Process (3 incremental steps)**: build out CI one capability at a time.
  - When to use: introducing CI to a team unfamiliar with it.
  - How: (1) Compile the application, (2) Run automated tests, (3) Create deployable releases. Introduce one step at a time — get compilation working and stable on the server, then add tests, then add releases. Distribute each build-file change initiator → build server → whole team via source control.
  - Why it works / failure mode: adding all three at once is overwhelming and demoralizing, and makes it hard to isolate which change broke the build.

## Key Concepts
- **Build (Integration) Server**: a clean, non-developer machine resembling production (no IDE, minimal third-party software) that acts as the *mainline* — code isn't "stable" until it builds there.
- **Mainline**: the authoritative build; passing on developer machines means nothing until the build server confirms it.
- **Broken Build**: the server can't compile, has failing tests, or is otherwise unstable — a serious offense meaning the app doesn't work right now.
- **The Metronome**: the steady rhythm of "edit, build, get, build, commit, integrate" that frequent check-ins + CI produce.
- **Releasable**: with CI in place, the app is at any moment confidently deployable to a test/prod environment (existing features work, even if not all features exist).
- **Release vs Deployment**: a *release* is the deliverable (MSI, xcopy folder); a *deployment* is the act of installing a release into an environment.
- **Build Components**: build script + supporting files (DDL/data SQL scripts, config templates) kept in source control, organized in a separate `build` folder.
- **Environment Templates**: .ini-like files holding environment-specific variables (connection strings, logging config, service endpoints) loaded by the build script per target environment.
- **Fast/Slow Build Split**: separating quick (compile + unit tests + release) from slow (integration/UI tests) so developers aren't blocked.

## Mental Models
- Use the **build server as an un-judging third party** when you want a broken build to add levity and team bonding rather than blame between developers.
- Use **each developer's machine as its own build server** (run the build script locally) when you want to close the feedback loop at maximum speed and catch issues before they reach the repository.
- Use **labels/tags in version control** instead of "wait until the feature is done" when deciding when to check in — code "works" for a developer simply if it does what you want and compiles (later: + passes tests, + meets metrics).
- Use **csc.exe/vbc.exe granular compilation** when deployment structure should differ from Solution Explorer layout — treat Solution Explorer as a file organizer, not a layering designer.

## Anti-patterns
- **Building in the IDE for CI**: Visual Studio's visual progress updates are slow on large solutions and IDE compilation can't be automated or matched to the server — risks errors that appear only on the build server.
- **Compiling/testing differently locally vs on the server**: configuration, included files, or tested assemblies diverge, causing build-server-only failures.
- **Checking in code while the build is broken** (unless fixing it), or **getting latest while the build is broken** — exacerbates an unstable state.
- **A manual "Build Person" with a printed script on the wall**: tedious, error-prone, repeated per-client; a title for a task is itself a sign of a pain point.
- **Testing the release/installation process for the first time on production deployment day**: recurring install issues never get fixed because reviewers rotate.
- **Adding the compile or release folders to version control**: compile output is re-creatable; releases belong on the server with a retention policy and nightly backup.
- **Deploying on every check-in** (early on): many no-op changes can make the acceptance environment look buggy — schedule deployments separately (nightly/weekly/manual).

## Rules for Broken Builds
1. Nobody shall check in code when the build is broken, unless it is specifically to fix the build.
2. Nobody shall retrieve the latest version of the code when the build is broken.
3. He who broke it, fixes it.

## Code Examples

Compile via the built-in `<msbuild>` task (NAnt), Debug configuration:
```
<target name="compile">
  <msbuild project="...sln">
    <property name="Configuration" value="Debug" />
  </msbuild>
</target>
```
- **What it demonstrates**: compiling the app the same way Visual Studio does, but scriptably — "a pretty benign event."

Granular compile of all `.cs` files into one assembly via `csc.exe`:
```
<csc target="library" output="${compiled.assembly}" debug="true">
  <sources>
    <include name="BrownfieldAppRoot\**\*.cs"/>
  </sources>
  <references>
    <include name="${thirdparty.nhibernate}"/>
  </references>
</csc>
```
- **What it demonstrates**: controlling final assembly contents at a finer grain than .sln/.csproj, so deployment can follow physical layering rather than project structure.

Run NUnit and fail the build if any test fails:
```
<target name="test" depends="test.compile">
  <exec program="nunit-console.exe"
    basedir="${dir.tools}\nunit\bin"
    workingdir="${dir.compile}"
    commandline="${dir.compile}\MyProject.Test.dll /xml=${dir.compile}\MyProject.Test-Results.xml"
    failonerror="true" />
</target>
```
- **What it demonstrates**: `failonerror="true"` makes an NUnit test failure fail the whole build — otherwise the build only checks whether NUnit *ran*, not whether tests passed.

## Reference Tables

| Folder | Purpose | In version control? |
|---|---|---|
| `build` | Build script + supporting files | Yes |
| `build/config` | Config files + templates for release | Yes |
| `build/sql/ddl` | Scripts to create DB, tables, keys, security | Yes |
| `build/sql/data` | Scripts to prime DB with lookup/config data | Yes |
| `compile` | Build artifacts (assemblies/exes); test working dir | No (re-creatable) |
| `release` | Deployable release packages | No (server only; nightly backup + retention) |

## Worked Example

**Removing the pain — a check-in walkthrough.** Michael renames the `Person.LastName` property to `Surname` and diligently updates all references. Jackson, working on a Person-edit screen, finishes and checks in — but forgets step 3 (get latest + merge), so his code still references the now-defunct `LastName`.

With CI in place: the moment Jackson checks in, the automated build (a) gets latest, (b) compiles, (c) emails the result. Compilation fails at (b). The team gets an email naming Jackson as the last check-in. The Rules for Broken Builds kick in — everyone stops, wanders over for good-natured ribbing (the "fail duck"). Jackson immediately realizes he skipped getting latest, makes the quick fix, runs the proper check-in dance, and the build goes green — often before the first colleague reaches his cubicle. The defect was discovered seconds after creation rather than surfacing days later when another developer pulled broken code. The build server, as a neutral third party, turned a potential blame incident into team bonding.

## Versioning Safety Check
Default the application version to **0.0.0.0** in the build process. Locally-built assemblies stay tagged 0.0.0.0; only the build server overwrites it with the real version number. This doesn't prevent a developer from accidentally deploying a locally-compiled assembly, but makes such an assembly easy to identify when problems arise. Prefer having the CI tool (TeamCity, Hudson, CruiseControl.NET) generate the build/version number.

## Handling Long-Running Tests
Split the build into a **fast** part (compile + unit tests + release, always quick) and a **slow** part (adds integration/UI tests). Expose both paths from the build script (e.g. separate batch files). The CI server runs the fast build on every check-in; on success it triggers the slow build. Developers wait only for the fast build, confident that integration-test failures are usually environmental/network issues. Concurrent check-ins during a slow run get queued — choose CI software with native build queuing.

## Key Takeaways
1. CI's purpose is to **close the feedback loop** — find problems quickly, not to find more problems; the resistance is cultural, not technical.
2. The cornerstone is an **automated build** runnable at any time; once it exists, CI is just scheduling or triggering it on check-in.
3. Run the build the **same way locally and on the server** — via build script (NAnt/Rake/PSake/MSBuild), not the IDE.
4. Add CI **incrementally**: compile, then tests, then releases — and keep the build script in source control as a first-class artifact.
5. A **clean, production-like build server** acts as the mainline; code isn't stable until it builds there.
6. Frequent check-ins + CI create the **Metronome effect**, keeping the app continuously releasable and check-ins a near non-event.
7. CI can be added at **any point** in a project's lifecycle — for brownfield it's largely automating what the team already does daily.

## Connects To
- **Ch 2**: builds on the self-contained folder/version-control structure set up earlier (the "check-in dance" originated there; Edit-Merge-Commit VCS); that structure makes CI run more smoothly.
- **Ch 4 (Automated Testing)**: expands "working code" to include passing automated tests; this chapter's test step (NUnit, unit vs integration) is a precursor that Ch 4 fleshes out.
- **Ch 5 (Software Metrics)**: further expands "working code" to include code metrics layered onto the CI process.
- **Ch 8 (Layering)**: returns to logical/physical layering and why deployment structure (granular compilation) need not mirror Solution Explorer.
