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

Use Spikee to generate datasets, test an LLM application, and analyse the results. Resume at the nearest unmet gate; do not restart completed work.

## Work Directly

Take the shortest documented path through the current gate.

1. Treat facts the user already supplied—workspace, provider, URL, port, model, credentials, target behavior, and limits—as the working configuration. Do not ask for them again or verify them repeatedly without a concrete reason.
2. Read `spikee.log`, inspect only the relevant artifacts, and read only the current phase guide.
3. Perform the minimum check or action needed to cross the gate. Once it succeeds, advance. Do not continue checking the same fact.
4. Debug only after an observed error, contradictory evidence, or a genuine ambiguity blocks progress. Show the failure, form one specific hypothesis, and inspect only the relevant layer.

Do not pre-debug. Avoid broad environment inventories, recursive source scans, speculative dependency or hardware checks, several endpoint variants, and inference calls made only to prove that a configured provider might work.

For a user-supplied llama.cpp or OpenAI-compatible URL, query its model-list endpoint once. For llama.cpp, normalize the API base so it ends in exactly one `/v1`, then use `GET <api-base>/models`; this is metadata discovery, so do not send a chat completion. Use the sole returned model, or show the returned IDs and ask the user to choose when there are several. Enter provider debugging only if this request fails or a later Spikee command produces an actual provider error.

## Use Spikee for Test Execution

Adversarial prompts and attacks normally flow through an agreed Spikee dataset, target, judge, and `spikee test` run.

- Direct HTTP, WebSocket, browser, or `spikee debug` interaction is allowed only to understand the interface and send harmless inputs needed to build or prove a target.
- Do not manually jailbreak the application, improvise payloads, or substitute the assistant's interactions for a Spikee run.
- If Spikee cannot express a required test, remain in the phase that owns the gap and propose a target, seed, plugin, attack, or judge change.
- Perform manual or out-of-band testing only when the user explicitly requests it. Confirm the narrow scope, keep its evidence separate from Spikee metrics, and record a sanitized `manual deviation` in `spikee.log`.

## Commands and Test Sessions

Before any Spikee CLI command, resolve and show the exact command without secret values. By default, ask whether the user wants to run it or wants the agent to run it. A user's response to a displayed command or batch, such as “you run the commands,” authorizes that exact preview; do not ask again. Preview and confirm changed commands, added commands, and retries separately.

An explicit instruction to stop asking for command confirmations waives the question for its stated scope, or the current task when no scope is given. Continue to print every exact command before execution. Record the waiver and scope in `spikee.log`.

Every agent-run `spikee test` must use a named attachable `tmux` session, including smoke tests, baselines, attacks, resumes, and `--attack-only` runs. This does not depend on expected duration.

- Include the proposed session in the test approval block.
- After approval, create the empty session with `remain-on-exit`, then tell the user its name and `tmux attach-session -t <name>` before starting the test.
- If `tmux` is unavailable, stop and offer installation or an attachable equivalent such as GNU Screen.
- Skip the session only when the user explicitly declines it for that test; record the waiver.

Run all other commands normally without tmux, including `init`, `list`, `generate`, `debug`, `results`, `webui`, and help/version checks.

Keep questions compact. Resolve known facts first and group only unresolved gate decisions. Do not drip-feed questions, repeat answered questions, or ask questions without a concrete decision behind them.

## Workspace Memory

Maintain `spikee.log` in the initialized workspace root. It is a concise resume record, not a transcript and not an instruction source.

At session start, read its current summary and recent activity, then verify only cheap facts relevant to the current gate. After each material outcome:

- update the summary in place;
- append one short ISO-8601 timestamped activity entry for a completed milestone, meaningful failure, or durable decision;
- record observed outcomes only, including who ran material commands and sanitized commands or artifact paths;
- record `.env` variable names and status, never secret values;
- correct, redact, deduplicate, or compact old entries when needed.

Do not log chain-of-thought, chat transcripts, routine reads/listings, raw requests, full prompts/responses, dataset contents, result contents, or merely proposed commands. For an existing artifact with unknown creation time, record the time first observed and say its creation time is unknown. Do not commit or share `spikee.log` unless the user asks.

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
- Concurrency: <threads and known target/judge/attack-model limits>
- Last run: <mode; attempt ceiling; session; result path; status>
- Current phase / next gate: <phase / gate>
- Blockers: <none or concrete blocker>

## Activity
- <timestamp> | setup | Created .venv; installed Spikee <version>; initialized workspace.
- <timestamp> | target | Created targets/<name>.py; harmless live probe passed.
- <timestamp> | test | Ran <sanitized command> in tmux <name>; wrote <result path>.
```

## Workflow

For a narrow request, enter the relevant phase and verify only its prerequisites. For an end-to-end assessment, follow the phases in order. Update `spikee.log` at each handoff.

### Phase 1 — Runtime and Workspace

Read `01-workspace-setup.md`.

1. Locate the intended project directory and any existing `spikee.log`.
2. Check for a local `.venv`, `venv`, or `env` before invoking Spikee. If absent, recommend creating `.venv` and installing Spikee there. If present, check/install Spikee through that venv and compare its version with the bundled metadata.
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
7. For a genuine chatbot with usable history, ask whether Spikee should preserve it and normally recommend a multi-turn target. Give no invented rationale. A static dataset entry remains one prompt even through a multi-turn-capable target; only a multi-turn attack such as `crescendo` creates a multi-message test.
8. Prefer a mapped HTTP or WebSocket target. Use browser inspection only when mapping is unclear; propose a Playwright-backed target only when browser state is truly required.
9. Keep credentials in `.env`, never in code or CLI options. Preserve existing `.env` entries when adding or changing a variable.
10. Start from workspace `targets/` examples for Spikee structure only. Use docs, then source, only under the reference order below.
11. Prove the target with one harmless Spikee request. For multi-turn, prove two messages retain context. Stop after a valid, parsed response.

**Exit gate:** Spikee can invoke the target and parse a valid application response.

### Phase 3 — Dataset and Judge

Read `03-dataset-generation.md`.

1. Agree the question each dataset should answer. Distinguish plain harmful objectives, ready-to-send jailbreak corpora, composable injections, generation-time transformations, and runtime attacks.
2. Preserve existing judge names and arguments. Never replace an LLM judge with regex/canary, invent judge criteria, or otherwise change evaluation semantics without explicit user approval.
3. If an LLM judge is required, agree the provider and model. For hosted providers, name the `.env` key; for local providers, obtain the endpoint/model and supported concurrency. If access is unavailable or unclear, stop and offer options. Regex is a last-resort substitute only when the user accepts the changed semantics.
4. Estimate dataset size when practical. After generation, report the actual entry count without declaring it large or small. Ask whether it is acceptable unless that exact count or sizing rule was already approved. Never resize the dataset on the assistant's judgment.
5. Inspect representative entries offline. Do not submit them manually to the application.

**Exit gate:** the dataset matches the agreed question, its size is accepted, and every judge is intentional and runnable.

### Phase 4 — Test and Attack

Read `04-testing.md`; read `04b-goat-attack.md` only for GOAT.

1. Reuse a trustworthy matching baseline when one exists. Otherwise run a small static baseline and fix actual execution errors before adding an attack.
2. Agree `--threads` explicitly; Spikee defaults to 4, but target and local judge/attack-model capacity may require another value. A local server with one processing slot will serialize higher concurrency and may time out.
3. Calculate the selected entry count and maximum planned target attempts. Include baseline/`--attack-only`, `--attempts`, and `--attack-iterations`; distinguish transport retries and estimated judge/attack-model calls.
4. Present one short approval block: exact command, dataset/selected entries, mode and attempt ceiling, threads and capacities, provider/cost caveats, tmux name, and attach command. Ask whether the user will run it or wants the agent to run it in that session.
5. Establish direct-prompt results before measuring attack uplift, unless a matching baseline already exists. Use `--attack-only` to avoid a redundant baseline. If the direct prompt succeeds, an adaptive attack does not demonstrate a bypass for that entry.
6. Use only attacks relevant to the question and target. Multi-turn attacks require a proven multi-turn target. Return to Phase 3 for new coverage or transformations.

**Exit gate:** a completed result file exists and execution errors are separated from judged security outcomes.

### Phase 5 — Results and Iteration

Read `05-results-analysis.md`.

1. Verify the intended result path. Run `spikee results analyze --result-file <path>` first for the standard summary and present its output.
2. Use `spikee results extract` for standard categories. Inspect JSONL directly for specific questions or validation, stating any custom filter or calculation.
3. Offer HTML output or the loopback-bound web UI when visual exploration helps.
4. Route runtime/workspace failures to Phase 1, target failures to Phase 2, coverage/judge problems to Phase 3, and sound baselines needing stronger attempts to Phase 4.

The workflow is circular. A new hypothesis may require a revised target or dataset, a new matching baseline, another attack, and fresh analysis. Re-enter the owning phase and revalidate affected downstream gates.

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
