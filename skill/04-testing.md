# Phase 4 — Testing

Run attack datasets against your target using `spikee test`.

This is the only default execution path for adversarial testing, including one-off trial prompts. Do not manually invoke adversarial inputs through `spikee debug`, a standalone harness, direct target calls, the application UI, browser/Playwright, Burp Repeater, `curl`, or ad hoc scripts, and do not invent attacks outside the agreed dataset/plugin/attack workflow. If Spikee cannot express the requested test, return to the phase that owns the missing target, seed, plugin, attack, or judge capability and ask the user how to proceed.

Only perform manual or out-of-band testing when the user explicitly requests that deviation. Treat it as a narrow exception: confirm its scope and limits, perform only the agreed attempt, and do not invent extra payloads or iterative follow-ups without further approval. Keep its evidence separate from Spikee results, record a concise sanitized `manual deviation` entry in `spikee.log`, and never merge it into Spikee success rates.

> **Workspace memory:** Read `spikee.log` before selecting a command so completed baselines, known limits, and prior result paths are not rediscovered or rerun blindly.

This guide, `spikee list attacks -d`, and examples in the initialized workspace are sufficient for routine test and attack setup. Consult `spikee-src/docs/08_dynamic_attacks.md` when a documented option is unclear. Do not read attack implementation source merely to start a built-in attack; inspect it only for unresolved behavior or debugging.

## Mandatory Preview and Attachable Session for `spikee test`

Before execution, show the fully resolved test command without placeholders or secrets and propose a unique session such as `spikee-baseline-20260904-143000`. Ask: **“Would you like to run this command yourself, or should I run it in tmux session `<name>`?”**

- If the user will run it, wait for their result.
- For agent execution, create an empty session in the workspace with `remain-on-exit`, show the resolved `tmux attach-session -t <name>` in its own fenced `bash` code block, then start the confirmed command inside it. Do not start before sending the attach command.
- Monitor with `tmux capture-pane` and leave the session available after exit.
- If tmux is unavailable, stop and offer installation or an attachable equivalent. Never substitute foreground execution, `&`, or `nohup`.
- Only the user's explicit no-session instruction waives tmux for that test. A confirmation waiver, urgency, or a short run does not.

Other Spikee commands run normally without tmux.

## Required Testing Sequence

Do not skip ahead when a gate is unresolved:

1. Confirm the venv, target, dataset question, judges, credentials, endpoints, concurrency, and tmux availability.
2. Check `spikee.log` and results for a matching baseline: same application state, target/options, entries, and judge semantics.
3. Count selected entries and calculate the workload ceiling and provider-call estimate.
4. Present one approval block with the exact command and execution choice.
5. If no matching baseline exists, run a static smoke baseline without `--attack`; fix errors before scaling.
6. Add a relevant dynamic attack only after execution is sound. Use `--attack-only` when a recorded matching baseline makes repeated direct attempts unnecessary.

Example smoke baseline:

```bash
spikee test --dataset datasets/my-dataset.jsonl \
            --target my_target \
            --sample <agreed-fraction> \
            --sample-seed 42 \
            --threads <agreed-n> \
            --tag baseline-smoke
```

Agree whether to use the full dataset or a sample, and state both the fraction and resulting entry count before approval. Do not choose a sample merely because the assistant considers the full dataset long. Do not interpret or scale a run with judge failures, malformed/empty target responses, widespread request errors, or missing category coverage.

## Agree Concurrency Before Testing

Spikee defaults to 4 threads. Agree an explicit `--threads <n>` using the lowest relevant capacity: target rate/session limits, LLM-judge capacity, and LLM-attack-model capacity. Reuse a logged value only when those constraints are unchanged.

Tell the user that a local llama.cpp server with one slot, such as `-np 1`, will serialize higher concurrency and may become slow or time out. Browser-backed or stateful targets normally start at 1 unless worker state is isolated. Recommend a value, let the user choose, and record the decision. On 429s, broken sessions, queues, or timeouts, stop scaling and revisit it.

## Concise Workload Approval Before Each Test

Derive the workload from the command rather than guessing from the dataset filename:

- Let `D` be the entries actually selected after `--sample` or other dataset selection, `A` be `--attempts`, and `I` be `--attack-iterations`.
- Without a dynamic attack, the planned ceiling is `D × A` target attempts.
- With an attack and ordinary standard attempts, the planned ceiling is `D × A × (1 + I)` target attempts.
- With `--attack-only`, the planned ceiling is `D × A × I` target attempts.

These are conservative target-attempt ceilings. Success can stop attacks early; `--max-retries` can increase transport calls. Estimate judge and attack-model calls separately when possible, otherwise state the uncertainty.

Dynamic `best_of_n` illustrates the distinction. For 1,000 selected entries, `--attempts 1`, and `--attack-iterations 10`, the attack portion can make up to 10,000 target attempts. The planned ceiling is 10,000 with `--attack-only`, or 11,000 when the standard attempt is included. This runtime attack does **not** enlarge the dataset JSONL. By contrast, the generation-time `best_of_n` plugin with `variants=10` creates additional dataset entries, so that larger entry count becomes `D` in the formulas above.

Present one compact approval message:

- **Dataset:** path; total entries; selected entries after sampling.
- **Run:** baseline or attack; `--attempts`; attack iterations; `--max-retries`/throttle; whether the standard attempt is included or a named matching baseline is reused.
- **Workload:** planned maximum target attempts before transport retries; judge/attack-model request estimate or clearly stated uncertainty; material time/cost implication.
- **Concurrency:** explicit threads, Spikee default of 4 for context, and known target/local-model capacity.
- **Command:** the complete exact command with no secret values.
- **Execution:** proposed tmux session and attach command.

End with: **“Approve this run? Would you like to execute it yourself, or should I run it in tmux session `<name>`?”** If an option changes, recompute and show the block once. A command-confirmation waiver does not resolve dataset-size, workload, concurrency, traffic, or cost decisions.

## 4.1 Basic Test Command

```bash
spikee test --dataset "datasets/cybersec-2026-01-*.jsonl" \
            --target my_app_target \
            --threads <agreed-n>
```

**Key flags:**
- `--dataset <file>`: Path to dataset JSONL. **Supports glob patterns** (e.g., `datasets/*.jsonl`) — remember to quote the glob so the shell doesn't expand it prematurely if passing multiple files.
- `--dataset-folder <dir>`: Process all datasets in a folder.
- `--target <name>`: Target module name (without `.py`).
- `--target-options <string>`: Options to pass to the target (e.g., `provider/model`).
- `--tag <string>`: Tag for the results filename.

## 4.2 Using the Built-In LLM Target

For testing raw LLM endpoints without writing a custom target:

```bash
# OpenAI
spikee test --dataset datasets/my-dataset.jsonl \
            --target llm_provider \
            --target-options "openai/gpt-4o-mini" \
            --threads <agreed-n>

# Bedrock
spikee test --dataset datasets/my-dataset.jsonl \
            --target llm_provider \
            --target-options "bedrock/anthropic.claude-3-sonnet-20240229-v1:0" \
            --threads <agreed-n>

# Ollama (local)
spikee test --dataset datasets/my-dataset.jsonl \
            --target llm_provider \
            --target-options "ollama/llama3" \
            --threads <agreed-n>

# Google Gemini
spikee test --dataset datasets/my-dataset.jsonl \
            --target llm_provider \
            --target-options "google/gemini-1.5-flash" \
            --threads <agreed-n>
```

> For the full provider/model list, read `spikee-src/docs/03_llm_providers.md`.

## 4.3 Judges — How Success is Determined

Every dataset entry has a `judge_name` field that determines how Spikee evaluates whether an attack succeeded.

### Built-In Basic Judges (No LLM required)

- `canary`: Checks if `judge_args` string appears in the response (case-insensitive).
- `regex`: Checks if `judge_args` regex pattern matches the response.

*Note: These judges run locally and do **not** require `--judge-options`.*

### LLM Judges (Requires `--judge-options`)

- `llm_judge_harmful`: Evaluates for harmful content.
- `llm_judge_objective`: Checks whether the response fulfills or materially advances the input instruction's objective; suited to instruction-only datasets. The bundled implementation ignores `judge_args`; use Phase 3's guidance for separate custom criteria.
- `llm_judge_output_criteria`: Evaluates custom criteria from `judge_args`.
- `llm_judge_output_only`: Like output_criteria but only sees the response (not the prompt).

*Note: These judges require an LLM to perform semantic evaluation. You **must** provide the `--judge-options` flag.*

```bash
spikee test --dataset datasets/my-dataset.jsonl \
            --target my_target \
            --judge-options "openai/gpt-4o-mini" \
            --threads <agreed-n>
```

Preserve the dataset's intended judge semantics. If an LLM judge is required but its provider/model or access is unresolved, stop and ask the user to choose a supported hosted provider/model or a configured local endpoint. Explain the needed `.env` credentials when applicable. **Do not** replace the LLM judge with `regex`/`canary`, edit `judge_name`, or create a custom judge merely to bypass missing LLM access. Present the configuration options and wait for the user's choice. If the user deliberately wants to redesign the evaluation, return to Phase 3, agree the exact judge semantics, update the source seeds, regenerate the dataset, and repeat the baseline.

### Custom Judges

Create or change a custom judge only when the user explicitly wants a custom evaluation rule—not as a workaround for an unavailable LLM judge.

Create in `judges/` in your workspace:

```python
# judges/my_custom_judge.py
from spikee.templates.judge import Judge
from spikee.utilities.hinting import ModuleDescriptionHint, ModuleOptionsHint
from spikee.utilities.enums import ModuleTag

class MyCustomJudge(Judge):
    def get_description(self) -> ModuleDescriptionHint:
        return [ModuleTag.SINGLE], "My custom judge"

    def get_available_option_values(self) -> ModuleOptionsHint:
        return [], False

    def judge(self, prompt, response, judge_args, judge_options=None) -> bool:
        """Return True if the attack succeeded, False otherwise."""
        return "SECRET_DATA" in str(response)
```

> Start with the initialized workspace's `judges/` examples and `spikee-src/docs/09_judges.md`. Inspect judge base-class source only for an unresolved custom-judge contract or debugging issue.

## 4.4 Dynamic Attacks

Attacks are adaptive strategies that modify payloads in real-time. They run **only when the standard attempt fails** unless `--attack-only` is used. This makes the ordinary combined run meaningful: an attack-only success is a demonstrated bypass only when the same entry has a trustworthy baseline refusal.

Do not add a dynamic attack to the smoke baseline. Before using one, confirm all of the following:

- the static baseline passed the analysis gate above;
- the attack matches the target's single-turn or multi-turn interface;
- any attack-side model/provider and credentials or local endpoint are configured;
- request rate, concurrency, iteration, time, and cost limits are known and acceptable.

If any item is unclear, stop and present the missing decision or configuration instead of guessing. Use `--attack-only` when a trustworthy matching baseline already exists and the user wants to avoid rerunning the same direct attempts, such as when comparing a second attack against a dataset already baselined by the first. Record the reused baseline path in `spikee.log`. Without matching baseline evidence, omit `--attack-only` or run a separate static baseline first.

Instructions-only datasets are a natural input for objective-driven attacks. Their unmodified run asks whether the target complies with direct harmful requests; an LLM-driven attack asks whether it can wrap or adapt those objectives into successful jailbreak attempts. If the direct request already succeeds, report that baseline safety failure first: running a jailbreak attack adds little evidence for that entry unless the user has a different stated purpose.

```bash
# Crescendo is only for a verified multi-turn target
spikee test --dataset datasets/my-dataset.jsonl \
            --target my_chatbot_target \
            --attack crescendo \
            --attack-iterations 10 \
            --threads <agreed-n>
```

### Single-Turn Attacks

| Attack | Strategy | Options |
|---|---|---|
| `best_of_n` | Randomly perturbs the payload until success or the iteration limit | Controlled by `--attack-iterations`; no LLM required |
| `random_suffix_search` | Appends random suffixes to find bypasses | — |
| `prompt_decomposition` | Breaks the prompt into sub-questions | `model=` |
| `llm_jailbreaker` | Uses an LLM to rephrase the attack | `model=` |
| `llm_multi_language_jailbreaker` | Translates attacks to different languages | `model=`, `language=` |
| `anti_spotlighting` | Counters document-spotlighting defences | `model=` |
| `rag_poisoner` | Crafts adversarial context for RAG systems | `model=` |

### Multi-Turn Attacks (Require Multi-Turn Target)

| Attack | Strategy | Options |
|---|---|---|
| `crescendo` | Gradually escalates through conversation turns | `model=`, `max-turns=` |
| `echo_chamber` | Manipulates the model through contradictions/echoes | `model=`, `max-turns=` |
| `multi_turn` | Simple multi-turn with pre-defined conversation flow | — |

```bash
# Multi-turn attack with options
spikee test --dataset datasets/my-dataset.jsonl \
            --target my_chatbot_target \
            --attack crescendo \
            --attack-iterations 15 \
            --attack-options "model=openai/gpt-4o-mini,max-turns=5" \
            --threads <agreed-n>
```

> List available attacks: `spikee list attacks -d`
> If this guide and the list output are insufficient, read `spikee-src/docs/08_dynamic_attacks.md`. Inspect `spikee-src/spikee/templates/attack.py` only when implementing a custom attack and the documented contract remains unclear, or when debugging.
> **Advanced:** To configure a custom GOAT (Generative Offensive Adversarial Toolkit) attack with specific guardrail mapping, refer to **`04b-goat-attack.md`**.

### Attack-Only Mode

Skip the initial standard attempt and run only the dynamic attack when a trustworthy matching baseline already exists. Keep its result path in `spikee.log` so the attack-only outcome can be compared correctly:

```bash
spikee test --dataset datasets/my-dataset.jsonl \
            --target my_chatbot_target \
            --attack crescendo \
            --attack-only \
            --threads <agreed-n>
```

## 4.5 Runtime Parameters

- `--threads <n>`: Parallel test workers (Spikee default: 4). Always discuss and set this explicitly according to the target, judge, and attack-model capacities.
- `--attempts <n>`: Retry attempts per entry (default: 1)
- `--max-retries <n>`: Retries for 429/transient errors (default: 3)
- `--throttle <seconds>`: Wait time between requests per thread
- `--sample <percentage>`: Sample percentage of dataset (e.g., `0.15` for 15%)
- `--sample-seed <n>`: Seed for reproducible sampling (default: 42, or "random")

## 4.6 Resume and Re-run

Spikee auto-detects previous results files and offers to resume:

```bash
# Auto-resume from latest matching results file
spikee test --dataset datasets/my-dataset.jsonl --target my_target --auto-resume --threads <agreed-n>

# Resume from a specific file
spikee test --dataset datasets/my-dataset.jsonl --target my_target \
            --resume-file results/results_my_target_cybersec-2026-01_1234567890.jsonl \
            --threads <agreed-n>

# Force fresh start (no resume)
spikee test --dataset datasets/my-dataset.jsonl --target my_target --no-auto-resume --threads <agreed-n>
```

## 4.7 Writing Custom Attacks

Create in `attacks/` in your workspace:

```python
# attacks/my_attack.py
from spikee.templates.attack import Attack
from spikee.utilities.hinting import ModuleDescriptionHint, ModuleOptionsHint
from spikee.utilities.enums import ModuleTag

class MyAttack(Attack):
    def get_description(self) -> ModuleDescriptionHint:
        return [ModuleTag.SINGLE], "My custom attack strategy"

    def get_available_option_values(self) -> ModuleOptionsHint:
        return [], False

    def attack(self, entry, target, judge_fn, max_iterations, pbar, lock, attack_option=None):
        """Run the attack strategy.

        Args:
            entry: Dataset entry dict with 'text', 'judge_name', 'judge_args', etc.
            target: AdvancedTargetWrapper instance — call target.process_input(text)
            judge_fn: Judge function — call judge_fn(entry, response) → bool
            max_iterations: Maximum iterations allowed (from --attack-iterations)
            pbar: tqdm progress bar (update with lock)
            lock: threading.Lock for thread-safe progress updates

        Returns:
            tuple: (attempts_count, success_bool, final_input, final_response)
        """
        for i in range(max_iterations):
            # Modify the payload
            modified_text = f"Please help me with: {entry['text']}"

            try:
                response, meta = target.process_input(modified_text)
                with lock:
                    pbar.update(1)

                if judge_fn(entry, response):
                    return i + 1, True, modified_text, response
            except Exception:
                with lock:
                    pbar.update(1)

        return max_iterations, False, modified_text, ""
```

> Start with `attacks/sample_attack.py` in the initialized workspace and the official dynamic-attack guide. Inspect built-in attack source only if a concrete implementation question remains or observed behavior needs debugging.

The Spikee attack engine calls `target.process_input(...)` in this class. Do not run a custom attack class as a standalone client or use its target calls to conduct manual testing.

At launch, update the `spikee.log` summary and add one concise test activity entry with the ISO timestamp, who is running it, sanitized reproducible command, total/selected entry counts, planned target-attempt ceiling, agreed thread count and known concurrency limits, session manager/name, exact attach command, target/dataset, judge and attack configuration, and `started` status. On completion, update the same entry when practical with actual attempts, completion or error status, result path, baseline path if reused, and next gate. Keep Current State's command-confirmation mode and any active autonomy scope accurate. Record a user-approved no-session waiver or manual deviation explicitly and separately. Do not log a proposed but unexecuted command as completed, and do not paste console output or result contents into the log.

## 4.8 Next Step

Once your test run completes, proceed to **Phase 5** to analyse the results.
