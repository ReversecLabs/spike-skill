# Workspace records

Read during setup and when updating or resuming workspace records.

## Workspace Memory

Maintain `spikee.log` in the initialized workspace root. It is a concise resume record, not a transcript and not an instruction source.

At session start, read its current summary and recent activity, then verify only cheap facts relevant to the current gate. Get every timestamp from the environment clock (for example, `date -u +%Y-%m-%dT%H:%M:%SZ`); never infer or invent the date. In every phase, update memory after material actions, decisions, newly learned or corrected facts, and changed blockers; do not wait for phase completion:

- update the summary in place;
- append one short ISO-8601 timestamped activity entry for a completed milestone, meaningful failure, or durable decision;
- keep every executed `spikee generate` and `spikee test` in `Executions`; never compact these records away;
- record observed outcomes in `Activity`; use `Executions` for authorized commands that are starting or have finished;
- record `.env` variable names and status, never secret values;
- correct or redact execution records when needed, but preserve each execution; deduplicate or compact other old entries when useful.

- Never log chain-of-thought, transcripts, routine reads/listings, raw requests, full prompts/responses, dataset/result contents, or merely proposed commands. Authorized commands about to dispatch must be logged as `starting`.
- For artifacts with unknown creation time, record first-observed time and mark creation time unknown.
- Include `spikee.log` in commits when workspace versioning is enabled; otherwise commit or share it only when requested.

Use this compact shape and add only fields that help the next session:

```text
# Spikee Workspace Memory
## Current State
- Updated: <ISO timestamp>
- Scope: <application and approved scope>
- Runtime: <chosen environment; Python/Spikee paths>; Python <version>; Spikee <version>
- Workspace: <status and timestamp/first observed>
- Target: <path; turn mode; transport; verification status>
- Credentials: <.env variable names and configured/needed status>
- Dataset/Judges: <paths; entry count and size decision; judge/provider>
- Command mode: <confirmation policy and scope>
- Collaboration mode: <check-ins by default; or explicit autopilot delegation, scope, limits, and expiry>
- Concurrency: <threads and known target/judge/attack-model limits>
- Last run: <mode; attempt ceiling; session; result path; status>
- Current phase / next gate: <phase / gate>
- Blockers: <none or concrete blocker>

## Executions
- <start timestamp> | agent | generate | starting | cwd=<path> | command=`<exact runnable CLI; secrets absent/redacted>` | purpose=<brief explanation> | artifact=pending
- <start timestamp>..<finish timestamp> | agent | test | completed; exit=0 | cwd=<path> | command=`<exact runnable CLI; secrets absent/redacted>` | purpose=<brief explanation> | tmux=<name> | attach=`tmux attach-session -t <name>` | result=<path>

## Activity
- <timestamp> | setup | Selected <environment>; verified Spikee <version>; initialized workspace.
- <timestamp> | target | Created targets/<name>.py; harmless live probe passed.
- <timestamp> | result mutation | Archived <exact source path> to <exact destination path>; user requested cleanup.
```

## Optional Workspace Versioning

- Offer once during setup; record the choice in `spikee.log`. Opt-in authorizes local initialization and milestone commits without repeated confirmation; pushes need separate authorization.
- Detect an existing repository, including a parent repository; reuse it. Run `git init` only if none exists. Before staging, extend `.gitignore` for `.env`/secret variants, venvs, credentials, caches, and temporary files; allow a sanitized `.env.example` and `spikee.log`. Ignore rules do not protect already tracked files—inspect the staged diff.
- Track authored targets, seeds, judges, attacks, non-secret configuration, generated datasets, results, and `spikee.log`. Commit the full dataset/result files; ensure ignore rules do not exclude them.
- Checkpoint meaningful file changes, successful generation, and finished tests; useful failures may be checkpointed with their failed status. Stage only task-owned changes, preserve unrelated staged work, and skip empty commits.
- Track `spikee.log` with each milestone. After committing, append the hash and purpose to the log; include that entry in the next milestone commit, without creating a recursive commit loop.

