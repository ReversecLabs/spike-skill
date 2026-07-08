# Phase 4 — Testing

Run attack datasets against your target using `spikee test`.

## 4.1 Basic Test Command

```bash
spikee test --dataset "datasets/cybersec-2026-01-*.jsonl" \
            --target my_app_target
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
            --target-options "openai/gpt-4o-mini"

# Bedrock
spikee test --dataset datasets/my-dataset.jsonl \
            --target llm_provider \
            --target-options "bedrock/anthropic.claude-3-sonnet-20240229-v1:0"

# Ollama (local)
spikee test --dataset datasets/my-dataset.jsonl \
            --target llm_provider \
            --target-options "ollama/llama3"

# Google Gemini
spikee test --dataset datasets/my-dataset.jsonl \
            --target llm_provider \
            --target-options "google/gemini-1.5-flash"
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
- `llm_judge_objective`: Evaluates if the specific objective in `judge_args` was achieved.
- `llm_judge_output_criteria`: Evaluates custom criteria from `judge_args`.
- `llm_judge_output_only`: Like output_criteria but only sees the response (not the prompt).

*Note: These judges require an LLM to perform semantic evaluation. You **must** provide the `--judge-options` flag.*

```bash
spikee test --dataset datasets/my-dataset.jsonl \
            --target my_target \
            --judge-options "openai/gpt-4o-mini"
```

### Custom Judges

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

> Read `spikee-src/spikee/templates/judge.py` and `spikee-src/spikee/templates/llm_judge.py` for base classes.
> Read `spikee-src/spikee/data/workspace/judges/` for LLM judge examples.

## 4.4 Dynamic Attacks

Attacks are adaptive strategies that modify payloads in real-time. They run **only when the standard attempt fails** (unless `--attack-only` is used).

```bash
spikee test --dataset datasets/my-dataset.jsonl \
            --target my_target \
            --attack crescendo \
            --attack-iterations 10
```

### Single-Turn Attacks

| Attack | Strategy | Options |
|---|---|---|
| `best_of_n` | Randomly perturbs the payload N times | `model=`, `variants=` |
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
            --attack-options "model=openai/gpt-4o-mini,max-turns=5"
```

> List available attacks: `spikee list attacks -d`
> Read `spikee-src/docs/08_dynamic_attacks.md` for full attack documentation.
> Read `spikee-src/spikee/templates/attack.py` for the attack base class.
> **Advanced:** To configure a custom GOAT (Generative Offensive Adversarial Toolkit) attack with specific guardrail mapping, refer to **`04b-goat-attack.md`**.

### Attack-Only Mode

Skip the initial standard attempt and only run the dynamic attack:
```bash
spikee test --dataset datasets/my-dataset.jsonl \
            --target my_target \
            --attack crescendo \
            --attack-only
```

## 4.5 Runtime Parameters

- `--threads <n>`: Parallel threads (default: 4)
- `--attempts <n>`: Retry attempts per entry (default: 1)
- `--max-retries <n>`: Retries for 429/transient errors (default: 3)
- `--throttle <seconds>`: Wait time between requests per thread
- `--sample <percentage>`: Sample percentage of dataset (e.g., `0.15` for 15%)
- `--sample-seed <n>`: Seed for reproducible sampling (default: 42, or "random")

## 4.6 Resume and Re-run

Spikee auto-detects previous results files and offers to resume:

```bash
# Auto-resume from latest matching results file
spikee test --dataset datasets/my-dataset.jsonl --target my_target --auto-resume

# Resume from a specific file
spikee test --dataset datasets/my-dataset.jsonl --target my_target \
            --resume-file results/results_my_target_cybersec-2026-01_1234567890.jsonl

# Force fresh start (no resume)
spikee test --dataset datasets/my-dataset.jsonl --target my_target --no-auto-resume
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

> Read `spikee-src/spikee/data/workspace/attacks/sample_attack.py` for a working example.
> Read `spikee-src/spikee/attacks/crescendo.py` to see a complex multi-turn attack.

## 4.8 Next Step

Once your test run completes, proceed to **Phase 5** to analyse the results.
