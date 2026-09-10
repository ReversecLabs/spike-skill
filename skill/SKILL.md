---
name: spikee-pentesting
description: Use Spikee to test prompt injection and jailbreak resistance in LLM-powered features, from local setup and target creation through datasets, tests, results, and iteration. Not for general web-application pentesting.
license: Apache-2.0
metadata:
  author: Reversec Labs
  version: "1.0"
  tool: spikee
---

# Spikee Pentesting

- Use Spikee to generate datasets, test an LLM application, and analyse results.
- Collaborate by default. Identify the current phase from the request and evidence; do not restart completed work or automatically run remaining phases.

## Collaboration and Phase Gates

**A passed technical gate means ready to discuss the next phase, not permission to start it.**

1. **Inspect:** Read `spikee.log` and relevant artifacts without modifying the workspace. Identify the phase, completed prerequisites, and unresolved decisions before asking for discoverable facts.
2. **Agree:** State the current status and concrete proposal. Before creating directories/venvs, installing packages, initializing Spikee, editing configuration, or creating/modifying targets, present the commands/design and wait for approval unless explicitly covered by autopilot. Reuse explicit requests or approvals for those concrete actions.
3. **Execute:** Complete agreed work and required checks. Do not silently add phases, coverage, stronger attacks, or test runs.
4. **Handoff:** Report outcome/evidence, next phase, and proposed action. Ask whether to proceed, revise, or stop; wait for a reply. Combine with design/command approval where useful; avoid duplicate rounds.

- Apply these gates to earlier-phase returns and iterations too.
- Inspection permission, a URL, tool access, silence, or a progress update is not implementation approval.
- “Test this app” starts a collaborative assessment, not unattended execution of all five phases. “Continue” approves only the concrete next step discussed.
- **Autopilot requires explicit delegation**, such as “go autopilot” or “work autonomously through the assessment.” Within scope, advance phases and make routine decisions without asking again.
- Log autopilot mode, scope, limits, and user decision in `spikee.log`. Default scope: current assessment. Continue reporting phase outcomes and next actions.
- Autopilot retains prerequisite checks, judge-change approvals, execution logging, and attachable sessions. Stop for missing facts, unresolved traffic/cost limits, or work outside scope; invent nothing. Resume check-ins when scope ends or the user requests them.
- Command delegation (“run this command” / “stop asking about commands”) does not waive phase check-ins. Autopilot delegating execution covers routine command confirmations within scope; retain exact previews and execution safeguards.

## Work Directly

Take the shortest documented path through the agreed work in the current phase, following the collaboration gates above.

Keep the workspace lean: create only files and configuration needed for the current task; avoid unused examples, placeholders, and redundant artifacts.

1. Treat facts the user already supplied—workspace, provider, URL, port, model, credentials, target behavior, and limits—as the working configuration. Do not ask for them again or verify them repeatedly without a concrete reason.
2. Read `spikee.log`, inspect only the relevant artifacts, and read only the current phase guide.
3. Perform the minimum authorized check or action needed to satisfy the technical gate. Once it succeeds, report the result and follow the phase handoff gate. Do not continue checking the same fact.
4. Debug only after an observed error, contradictory evidence, or a genuine ambiguity blocks progress. Show the failure, form one specific hypothesis, and inspect only the relevant layer.

Do not pre-debug. Avoid broad environment inventories, recursive source scans, speculative dependency or hardware checks, several endpoint variants, and inference calls made only to prove that a configured provider might work.

For a user-supplied llama.cpp or OpenAI-compatible URL, query its model-list endpoint once. For llama.cpp, normalize the API base so it ends in exactly one `/v1`, then use `GET <api-base>/models`; this is metadata discovery, so do not send a chat completion. Use the sole returned model, or show the returned IDs and ask the user to choose when there are several. Enter provider debugging only if this request fails or a later Spikee command produces an actual provider error.

## Use Spikee for Test Execution

Adversarial prompts and attacks normally flow through an agreed Spikee dataset, target, judge, and `spikee test` run.

- Direct HTTP, WebSocket, browser, or `spikee debug` interaction is allowed only to understand the interface and send harmless inputs needed to build or prove a target.
- Do not manually jailbreak the application, improvise payloads, or substitute the assistant's interactions for a Spikee run.
- Phase 3's judge-only smoke check is allowed via `spikee debug module judges`: pass synthetic prompt/response fixtures to the configured judge without calling the target. Run it normally without tmux; it is separate from Phase 4 testing.
- If Spikee cannot express a required test, remain in the phase that owns the gap and propose a target, seed, plugin, attack, or judge change.
- Perform manual or out-of-band testing only when the user explicitly requests it. Confirm the narrow scope, keep its evidence separate from Spikee metrics, and record a sanitized `manual deviation` in `spikee.log`.

## Commands and Test Sessions

- Before any Spikee CLI command or runtime/workspace mutation (`mkdir`, venv creation, installation, configuration writes), show the exact command without secrets. Ask who should run it; wait before dispatch.
- The same gate applies to Python, scripts, and file-editing tools. Read-only local inspection may inform proposals; required `spikee.log` updates belong to already authorized work.
- Approval of a displayed command/batch covers that exact preview; do not reconfirm. Preview and confirm changed/added commands and retries separately.
- An explicit command-confirmation waiver covers its stated scope, or the current task if unspecified. Log the waiver/scope; still print every exact command before execution.

**Hard gate — every agent-run `spikee generate` and `spikee test`: preview → authorization → write and verify log → execution → outcome update.**

- Before dispatch, write `starting` under `Executions` in `spikee.log`: ISO timestamp, `actor=agent`, working directory, **exact runnable command** (executable, every argument, value, path, and required quoting), plus a brief purpose summary. For tests, include session manager/name and exact attach command.
- No condensed commands, ellipses, unresolved placeholders, or summary-only records. The purpose summary supplements the command; it never replaces it.
- Keep secrets in `.env`; omit/redact their values, never non-secret arguments.
- Read back the saved record and verify the command matches the authorized command about to run. Missing, incomplete, mismatched, or unwritable record: **do not execute**. Logging afterward does not satisfy this gate.
- Autonomy/confirmation waivers never waive logging. Each retry or changed command needs a separate verified record.
- After exit, update the same record: finish timestamp, exit status, `completed`/`failed`, generated dataset/result path. Do not defer to a later phase.

Every agent-run `spikee test` must use a named attachable `tmux` session, including smoke tests, baselines, attacks, resumes, and `--attack-only` runs. This does not depend on expected duration.

- Include the proposed session in the test approval block.
- After approval, create the empty session and run `tmux set-window-option -t <name> remain-on-exit on` **before** starting the test. Then tell the user its name and show the resolved `tmux attach-session -t <name>` in its own fenced `bash` code block.
- Preserve the session and final output after success or failure, including non-zero exits. No automatic `kill-session`, `kill-window`, `kill-pane`, or other cleanup. Remove only at the user's request or confirmation that inspection is finished.
- If `tmux` is unavailable, stop and offer installation or an attachable equivalent such as GNU Screen.
- Skip the session only when the user explicitly declines it for that test; record the waiver.

Run all other commands normally without tmux, including `init`, `list`, `generate`, `debug`, `results`, `webui`, and help/version checks.

Keep questions compact. Resolve known facts first and group only unresolved gate decisions. Do not drip-feed questions, repeat answered questions, or ask questions without a concrete decision behind them.

## User-Facing Brevity and Evidence

- Be brief: facts, relevant observations, next decision. No opinions, reactions (“interesting”), filler, repetition, or routine narration.
- Give options with concrete pros/cons and evidence-based recommendations. Flag errors, pitfalls, hypotheses, and uncertainty clearly.
- Report actual counts, units, known denominators, and run status. Distinguish judge verdicts from verified findings.
- Never invent constraints or rationales. Separate defaults, user choices, observed limits, and unknowns.
- Show required commands and attach instructions once. Expand only when requested or needed for an informed decision.

## Workspace Memory

Maintain `spikee.log` in the initialized workspace root. It is a concise resume record, not a transcript and not an instruction source.

At session start, read its current summary and recent activity, then verify only cheap facts relevant to the current gate. In every phase, update memory after material actions, decisions, newly learned or corrected facts, and changed blockers; do not wait for phase completion:

- update the summary in place;
- append one short ISO-8601 timestamped activity entry for a completed milestone, meaningful failure, or durable decision;
- keep every executed `spikee generate` and `spikee test` in `Executions`; never compact these records away;
- record observed outcomes in `Activity`; use `Executions` for authorized commands that are starting or have finished;
- record `.env` variable names and status, never secret values;
- correct or redact execution records when needed, but preserve each execution; deduplicate or compact other old entries when useful.

- Never log chain-of-thought, transcripts, routine reads/listings, raw requests, full prompts/responses, dataset/result contents, or merely proposed commands. Authorized commands about to dispatch must be logged as `starting`.
- For artifacts with unknown creation time, record first-observed time and mark creation time unknown.
- Do not commit or share `spikee.log` unless requested.

Use this compact shape and add only fields that help the next session:

```text
# Spikee Workspace Memory
## Current State
- Updated: <ISO timestamp>
- Scope: <application and approved scope>
- Runtime: <venv>; Python <version>; Spikee <version>
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
- <timestamp> | setup | Created .venv; installed Spikee <version>; initialized workspace.
- <timestamp> | target | Created targets/<name>.py; harmless live probe passed.
- <timestamp> | result mutation | Archived <exact source path> to <exact destination path>; user requested cleanup.
```

## Workflow

- Narrow request: enter the relevant phase; verify only its prerequisites.
- End-to-end assessment: follow phases in order under the collaboration gates. Exit gates establish readiness, not permission to advance.
- At each handoff, log the outcome and next action's status: awaiting agreement or covered by delegation.

### Phase 1 — Runtime and Workspace

Read `01-workspace-setup.md`.

1. Locate the intended project directory and any existing `spikee.log`.
2. Check for a local `.venv`, `venv`, or `env` before invoking Spikee. Inspect existing runtime metadata and compare its version with the bundled metadata. If creation, installation, or an update is needed, present the exact setup commands and wait for approval under the setup gate before running them.
3. Never use or modify a system-wide Spikee installation unless the user explicitly chooses it after hearing that the project-local venv is preferred.
4. After the local runtime is ready, detect or initialize the workspace with that venv's Spikee.
5. Configure only providers needed for the agreed work. Do not enumerate every seed, target, plugin, attack, judge, or provider during setup; list the relevant category when a later decision needs it.

**Exit gate:** a compatible Spikee installation exists in the local venv and the directory is an initialized workspace.

### Phase 2 — Target

Read `02-custom-targets.md`; read `02b-advanced-targets.md` only for advanced authentication or transport.

1. Scope the target to one LLM-powered feature that accepts user-controlled text or a document and returns an AI response or guardrail decision. A target is not a general web pentest client.
2. Observe only the application path needed to operate that feature. Do not enumerate, crawl, scan, fuzz, or test unrelated routes. If several AI features are plausible and the user's scope does not identify one, list the candidates and ask which to target.
3. **Samples are structure only.** Never infer the real application's identity, source project, URL, routes, request schema, authentication, behavior, or guardrails from a sample target—even when names or UI text look similar. Copy only Spikee class and method patterns.
4. Never search for, fetch, or clone an application or sample application's source repository based on such a similarity. Never probe endpoints copied or guessed from a sample. If external source lookup seems necessary and the user did not supply or authorize it, stop before the lookup and ask with the exact URL and reason.
5. Reuse a target only when the user or evidence from the real application confirms it is correct. Otherwise ask only for missing facts needed to map the selected feature: URL, captured Burp/DevTools request and response, authentication, input/output fields, errors, and session behavior.
6. Choose target turn mode from the real feature's conversation capability, not from the security objective. Single-turn means independent calls; multi-turn means the target can preserve conversation state. Harmful-content and authorization tests may use either mode.
7. Before creating or modifying a target, present the proposed turn mode, transport, input/output mapping, and verification plan; wait for design approval unless already supplied or explicitly delegated. For a genuine chatbot with usable history, ask whether Spikee should preserve it and normally recommend multi-turn. For a stateless feature, explain why single-turn fits and include that choice in the design approval. Unknown session behavior requires a question, not a silent single-turn default. A static dataset entry remains one prompt even through a multi-turn-capable target; only a multi-turn attack such as `crescendo` creates a multi-message test.
8. Prefer a mapped HTTP or WebSocket target. Use browser inspection only when mapping is unclear; propose a Playwright-backed target only when browser state is truly required.
9. Keep credentials in `.env`, never in code or CLI options. Preserve existing `.env` entries when adding or changing a variable.
10. Start from workspace `targets/` examples for Spikee structure only. Use docs, then source, only under the reference order below.
11. Prove the target with one harmless Spikee request. For multi-turn, prove two messages retain context. Stop after a valid, parsed response.

**Exit gate:** Spikee can invoke the target and parse a valid application response.

### Phase 3 — Dataset and Judge

Read `03-dataset-generation.md`; complete its [before-generation checklist](03-dataset-generation.md#before-generation-checklist) before generating.

1. Before customizing seeds or generating datasets, clarify any unresolved goals and present a coverage plan: the question each dataset answers, suitable built-in seeds, and gaps requiring customization. Get the user's agreement unless they have explicitly delegated dataset decisions for this step or the whole task; then choose within that scope and state the plan. Follow Phase 3's design gate.
2. Use `canary` (exact string/keyword) or `regex` (precise pattern) only when matching fully determines agreed success. Check the complete input and plausible failure/success responses offline; echoes or refusals must not masquerade as success. Keep disclosure markers out of attack inputs. Require an LLM judge for semantic/contextual/ambiguous criteria or unavoidable misclassification; no keyword heuristics. Preserve existing judge names/arguments unless the user explicitly approves changes.
3. When an LLM judge is required, agree the provider and model, then run Phase 3's positive/negative judge smoke check. For hosted providers, name the `.env` key; for local providers, obtain the endpoint/model and supported concurrency. If access is unavailable or unclear, stop and offer configuration or postponement. Do not fall back to regex/canary for the same semantic objective. A user-approved narrower objective must be labelled separately and satisfy the deterministic selection rule itself.
4. Estimate dataset size when practical. After generation, report the actual entry count without declaring it large or small. Ask whether it is acceptable unless that count or sizing rule was already approved or sizing decisions were delegated. Do not resize without approval or delegation.
5. Inspect representative entries offline. Do not submit them manually to the application.

**Exit gate:** the dataset matches the agreed question, its size is accepted, and every judge is intentional and runnable.

### Phase 4 — Test and Attack

Read `04-testing.md`; complete its [before-testing](04-testing.md#before-testing-checklist) and [after-dispatch](04-testing.md#immediately-after-dispatch-checklist) checks at the relevant points. Read `04b-goat-attack.md` only for GOAT.

1. Reuse a trustworthy matching baseline when one exists. Otherwise run a small static baseline and fix actual execution errors before adding an attack.
2. State that Spikee defaults to 4 threads and ask how many concurrent requests the user wants. Offer 1 as conservative if they are concerned about concurrency, server load, or quotas. Wait for their choice unless it was already supplied or explicitly delegated; do not choose an arbitrary value based on the endpoint being remote/local. Apply Phase 4's concurrency gate and report only evidenced limits.
3. Calculate the selected entry count and maximum planned target attempts. Include baseline/`--attack-only`, `--attempts`, and `--attack-iterations`; distinguish transport retries and estimated judge/attack-model calls.
4. Present one short approval block: exact command, dataset/selected entries, mode and attempt ceiling, user-approved threads, tmux name, and attach command. Mention only relevant evidenced capacity/cost constraints or unresolved limits; do not invent caveats. Ask whether the user will run it or wants the agent to run it in that session.
5. Establish direct-prompt results before measuring attack uplift, unless a matching baseline already exists. Use `--attack-only` to avoid a redundant baseline. If the direct prompt succeeds, an adaptive attack does not demonstrate a bypass for that entry.
6. Use only attacks relevant to the question and target. Multi-turn attacks require a proven multi-turn target. Return to Phase 3 for new coverage or transformations.

**Exit gate:** a completed result file exists and execution errors are separated from judged security outcomes.

### Phase 5 — Results and Iteration

Read `05-results-analysis.md`.

1. Verify the intended result path. Run `spikee results analyze --result-file <path>` first, capture its output, and present the key figures concisely; show full output only when requested or needed to explain a finding.
2. Use `spikee results extract` for standard categories. Inspect JSONL directly for specific questions or validation, stating any custom filter or calculation.
3. Offer HTML output or the loopback-bound web UI when visual exploration helps.
4. Route runtime/workspace failures to Phase 1, target failures to Phase 2, coverage/judge problems to Phase 3, and sound baselines needing stronger attempts to Phase 4.

The workflow is circular. A new hypothesis may require a revised target or dataset, a new matching baseline, another attack, and fresh analysis. Present the finding and proposed next action, then apply the collaboration gate before re-entering the owning phase. Revalidate affected downstream gates within the agreed work; do not start another cycle automatically.

## Reference Order

Do not read Spikee implementation source for routine target creation, dataset generation, or attack execution.

1. Read only the current phase guide.
2. Use the relevant `spikee list <category> -d`; for custom modules, inspect the closest workspace example only for the Spikee API pattern. Treat every application-specific literal in it as fictional.
3. If a specific question remains, read the relevant official document under `spikee-src/docs/`.
4. Read the smallest relevant file under `spikee-src/spikee/` only for an unresolved contract or observed failure.

Before opening source, state the exact unanswered question or error. Do not scan or preload the tree “just in case.” Spikee source may answer a framework-contract question; it is never evidence of the real target application's interface.

Useful documentation routes:

| Need | Path |
|---|---|
| Built-ins | `spikee-src/docs/02_builtin.md` |
| Providers | `spikee-src/docs/03_llm_providers.md` |
| Dataset generation | `spikee-src/docs/04_dataset_generation.md` |
| Testing | `spikee-src/docs/05_testing.md` |
| Custom targets | `spikee-src/docs/06_custom_targets.md` |
| Attacks | `spikee-src/docs/08_dynamic_attacks.md` |
| Judges | `spikee-src/docs/09_judges.md` |
| Results | `spikee-src/docs/11_results.md` |

If a gate lacks a required fact or approval, stop at that gate and give the smallest actionable options. Never invent URLs, request formats, credentials, selectors, application behavior, dataset objectives, judge criteria, capacity, or acceptable cost/traffic.
