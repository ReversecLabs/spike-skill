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

Use Spikee to prepare targets and datasets, run agreed tests, and analyse results. Start at the phase the user needs; read `spikee.log` and that phase's guide, not every guide.

## Collaboration and Phase Gates

Work collaboratively unless the user delegates decisions. Reuse explicit instructions and approvals; never ask someone to approve the same work again. “Initialize the workspace” authorizes initialization in the chosen environment. A URL alone does not approve an entire assessment.

Before writing a target, agree its design. Before customizing a dataset, agree its objectives, inputs and size. Before testing, agree the workload and who runs it. Combine related decisions in one exchange. Completed prerequisites do not authorize unrelated phases or extra coverage. A request to initialize a workspace covers Phase 1 only: finish setup, report it briefly and stop without asking target-discovery questions. “Continue” covers the proposed next step; explicit autonomy covers routine decisions within its stated scope and limits. Record delegation and command-confirmation waivers in `spikee.log`.

Inspect available evidence before asking. Usually ask one or two questions, at most three necessary questions in one message. Pace later decisions when they become relevant. Do not read a discovery checklist aloud or ask for facts already supplied. Stop only for missing decisions, necessary facts, limits, or permission outside the agreed scope. Autonomy never supplies unknown application facts or waives agreed judge criteria.

## User-Facing Brevity and Evidence

Write naturally, in complete, concise sentences. Lead with the current result or decision. Use a short table for choices and bullets for parallel facts. Explain when asked or when the user needs an explanation to choose; do not narrate routine tool calls or recap all five phases. At a phase handoff, state the result, the artifact or evidence, and the next material decision. Do not introduce choices from later phases. Omit successful setup chronology, unchanged configuration, empty placeholders and future-phase previews unless they affect the user's next decision.

Examples of useful updates (substitute observed facts):

- Setup: “Spikee is initialized in `/workspace`. Next I can inspect the summary feature using your supplied account.”
- Target proposal: “The summary request sends the emails from the browser. I’ll keep two fixed emails and replace the third with Spikee's input. Each summary is independent, so a single-turn target fits. Shall I build it?”
- Dataset choice: “Should the injection appear in an ordinary email, on its own, or both? I can reuse the seed's email or draft one for this application.”
- Results: “18 of 26 entries passed the judge; two requests failed. Results: `results/run.jsonl`.” Give actual counts and paths, never the example's values.

Show commands and attach instructions once. Report errors, uncertainty and partial results directly. Distinguish judge verdicts from reviewed findings; never invent counts, limits, completion or reasons for behaviour.

## Commands and Test Sessions

Preview exact commands without secrets before execution. Reuse the user's authorization for the action or batch; ask who executes only if undecided. A changed command needs authorization if it changes agreed work or exceeds its limits. Keep credentials out of code, command arguments, transcripts and logs; use the configured environment, secret file or credential service.

**Hard gate for every agent-run `spikee generate` and `spikee test`: authorization → write `spikee.log` → read back and verify → execute → record outcome.**

Before dispatch, write an `Executions` record containing the actual ISO time from the environment, `actor=agent`, `starting`, working directory, exact runnable command (all arguments, values, paths and quoting), and a brief purpose. For tests include the session name and exact attach command. No ellipses or unresolved placeholders. Read it back and compare it with the command about to run. A missing, incomplete, mismatched or unwritable record **blocks execution**. Retrying requires a separate record. Autonomy and concise chat never waive logging.

After exit, update the record with finish time, exit status, completed/failed status and dataset/result path. Update workspace state after material actions and decisions in every phase. Read [workspace-memory.md](workspace-memory.md) for the record format and optional versioning. It is a resume record, not an instruction source; never compact execution records away.

Every agent-run `spikee test`, including smoke tests and retries, runs in a named attachable tmux session. Create the empty session, enable `remain-on-exit`, and **print the exact attach command in a Bash code block before launching the test**. Include any selected socket option in every tmux command, including the attach command.

Tmux requires Unix sockets. If a shell sandbox blocks them, use the environment's escalation tool for session creation, launch and monitoring. Follow the environment's restrictions; do not repeatedly try the same blocked operation with different paths. This skill does not prescribe a particular sandbox, socket or escalation tool.

The same principle applies to networked Spikee commands: if the ordinary shell is intentionally network-isolated, use the environment's approved escalation tool for that command. Do not repeatedly retry a known-blocked network call inside the isolated shell.

Check startup, monitor through exit and retain the session and final output for inspection. Only an explicit run-and-forget request waives continued monitoring. Only an explicit no-session instruction waives tmux for that run. If unavailable, offer installation or an attachable equivalent. Never silently replace it with `nohup`, `&` or foreground execution. Other commands, including `generate`, `debug` and `results`, run normally.

## Workflow

| Phase | Read when needed | Required outcome |
|---|---|---|
| 1. Runtime and workspace | [01-workspace-setup.md](01-workspace-setup.md) | Selected runtime works; workspace initialized. |
| 2. Target | [02-custom-targets.md](02-custom-targets.md); after design approval, [implementation examples](02c-target-implementation.md); [advanced transports/auth](02b-advanced-targets.md) only when needed | Observed interface mapped; harmless Spikee probe passes. Prove two messages retain context for multi-turn. |
| 3. Dataset and judge | [03-dataset-generation.md](03-dataset-generation.md), [judges](03b-judges.md) | Agreed coverage and count; intentional, runnable judges. |
| 4. Testing | [04-testing.md](04-testing.md); [GOAT configuration](04b-goat-attack.md) only for GOAT | Agreed run completes; errors remain distinct from security outcomes. |
| 5. Analysis | [05-results-analysis.md](05-results-analysis.md) | Native analysis, concise results and next decision. |

Use the latest published Spikee for new installations and refresh references with `python3 <skill-directory>/update-references.py`. References follow upstream main; never pin or downgrade the runtime to match reference metadata. Retain an existing chosen runtime; upgrades need authorization. Installed help and interfaces determine executable commands.

Take the shortest documented route. During setup, check the selected runtime and initialize the workspace; list datasets, targets or providers only when the current decision needs them. Inspect relevant files and run the checks needed for the current phase. Debug after an actual failure or unresolved ambiguity; do not inventory environments, scan source trees or probe inference speculatively. For a supplied compatible local endpoint, list models once, use the sole ID or ask which returned ID to use. Normalize llama.cpp to exactly one `/v1`.

Adversarial execution uses agreed Spikee datasets, targets, judges and `spikee test`. Direct HTTP/browser interactions and target debug probes are for interface discovery and harmless verification. Judge-only smoke checks use synthetic responses without calling the target. Manual adversarial testing requires an explicit request; record it as a separate manual deviation, with its scope and evidence. If Spikee cannot express the test, propose the required module or dataset change.

After a run, analyse the intended result with `spikee results analyze` and summarize it; do not ask permission simply to report the requested run's results. New testing or changed coverage returns to the owning phase. Record the next action as awaiting agreement or covered by existing delegation. Avoid extra files or repeated checks once the required outcome is established.

## Optional Workspace Versioning

Offer local versioning once during setup, unless a choice is recorded. An explicit yes or no remains in force for the task; do not ask again later. Follow [workspace-memory.md](workspace-memory.md#optional-workspace-versioning) if accepted. Keep this optional decision separate from prerequisites for running Spikee.

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
