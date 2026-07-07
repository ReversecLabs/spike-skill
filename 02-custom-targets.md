# Phase 2 — Custom Targets

A **Target** is a Python script that bridges Spikee to the application under test. It receives a prompt from Spikee and returns the application's response.

## 2.1 Do You Need a Custom Target?

| Scenario | Target to use |
|---|---|
| Testing a raw LLM endpoint (OpenAI, Bedrock, Ollama, etc.) | Use built-in `llm_provider` — no custom code needed |
| Testing an LLM-powered application (chatbot, RAG, agent) | Write a **custom target** |
| Testing a guardrail or content filter | Write a **guardrail target** (boolean return) |

**Using the built-in `llm_provider`:**
```bash
spikee test --dataset datasets/my-dataset.jsonl \
            --target llm_provider \
            --target-options "openai/gpt-4o-mini"
```

If that's sufficient, skip to Phase 3. Otherwise, continue below.

## 2.2 Single-Turn Target (Most Common)

Create a file in `targets/` in your workspace. Extend the `Target` base class.

> Read `spikee-src/spikee/templates/target.py` for the full base class.
> Read `spikee-src/spikee/data/workspace/targets/sample_target.py` for a working example.

```python
# targets/my_app_target.py
from spikee.templates.target import Target
from spikee.tester import GuardrailTrigger, RetryableError
from spikee.utilities.hinting import Content, TargetResponseHint, ModuleDescriptionHint, ModuleOptionsHint
from spikee.utilities.enums import ModuleTag
from typing import Optional
import requests

class MyAppTarget(Target):
    """Target for testing my LLM application."""

    def get_description(self) -> ModuleDescriptionHint:
        """Return (tags, description). Tags indicate single/multi-turn support."""
        return [ModuleTag.SINGLE], "My custom application target"

    def get_available_option_values(self) -> ModuleOptionsHint:
        """Return (options_list, requires_llm).
        First option in list is the default. Set requires_llm=True if target needs an LLM provider.
        """
        return ["production", "staging"], False

    def process_input(
        self,
        input_text: Content,
        system_message: Optional[Content] = None,
        target_options: Optional[str] = None,
    ) -> TargetResponseHint:
        """Send the prompt to your application and return the response.

        Args:
            input_text: The attack prompt (user message).
            system_message: Optional system prompt (if dataset uses --include-system-message).
            target_options: Value from --target-options CLI flag.

        Returns:
            str: The application's text response.
            bool: For guardrail targets — True=allowed/bypassed, False=blocked.

        Raises:
            GuardrailTrigger: When the application's guardrail blocks the request.
            RetryableError: For transient errors (429, timeouts) — Spikee will retry.
            Exception: For fatal errors — Spikee logs and moves on.
        """
        # Parse options if needed
        url = "https://my-app.com/api/chat"
        if target_options == "staging":
            url = "https://staging.my-app.com/api/chat"

        try:
            response = requests.post(url, json={"message": str(input_text)}, timeout=30)
            response.raise_for_status()
            return response.json()["reply"]

        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                raise RetryableError(f"Rate limited: {e}", retry_period=60)
            elif response.status_code == 400:
                raise GuardrailTrigger(f"Guardrail triggered: {e}")
            else:
                raise

# Test standalone
if __name__ == "__main__":
    target = MyAppTarget()
    print(target.process_input("Hello, how can you help me?"))
```

**Run it:**
```bash
# Test the target standalone first
python targets/my_app_target.py

# Then use it with spikee
spikee test --dataset datasets/my-dataset.jsonl --target my_app_target
spikee test --dataset datasets/my-dataset.jsonl --target my_app_target --target-options staging
```

## 2.3 Multi-Turn Target

For applications that maintain conversation state (chatbots, agents). Spikee provides two base classes:

### Option A: SimpleMultiTarget (Recommended)

The simpler approach — manages a local conversation history for you. Best when the application is stateless and you pass the full conversation each time.

> Read `spikee-src/spikee/templates/simple_multi_target.py` for the full base class.
> Read `spikee-src/spikee/data/workspace/targets/simple_test_chatbot.py` for a working example.

```python
# targets/my_chatbot_target.py
from spikee.templates.simple_multi_target import SimpleMultiTarget
from spikee.tester import GuardrailTrigger
from spikee.utilities.hinting import Content, TargetResponseHint, ModuleDescriptionHint, ModuleOptionsHint
from spikee.utilities.enums import ModuleTag
from spikee.utilities.llm import get_llm
from typing import Optional

class MyChatbotTarget(SimpleMultiTarget):
    """Multi-turn target using SimpleMultiTarget."""

    def get_description(self) -> ModuleDescriptionHint:
        return [ModuleTag.MULTI], "Multi-turn chatbot target"

    def get_available_option_values(self) -> ModuleOptionsHint:
        return ["openai/gpt-4o-mini"], True  # True = needs LLM provider

    def process_input(
        self,
        input_text: Content,
        system_message: Optional[Content] = None,
        target_options: Optional[str] = None,
        spikee_session_id: Optional[str] = None,
        backtrack: bool = False,
    ) -> TargetResponseHint:
        # SimpleMultiTarget manages conversation history via spikee_session_id
        # backtrack=True removes the last turn (used by attacks to try alternatives)

        # Get or create conversation history for this session
        history = self._get_target_data(spikee_session_id)
        if history is None:
            history = []

        if backtrack and len(history) >= 2:
            history = history[:-2]  # Remove last user+assistant pair

        # Add the new user message
        history.append({"role": "user", "content": str(input_text)})

        # Call your application
        llm = get_llm(target_options)
        messages = history.copy()
        if system_message:
            messages.insert(0, {"role": "system", "content": str(system_message)})

        response = llm.invoke(messages)
        history.append({"role": "assistant", "content": response})

        # Save conversation state
        self._update_target_data(spikee_session_id, history)

        return response
```

### Option B: MultiTarget

For applications with server-side session management (e.g., the app tracks conversations via its own session ID).

> Read `spikee-src/spikee/templates/multi_target.py` for the full base class.

The key difference: you must manage mapping between Spikee's `spikee_session_id` and your application's session identifier.

## 2.4 Guardrail Target

For testing guardrails and content filters. Return `True` if the prompt was **allowed** (bypassed), `False` if **blocked**.

```python
# targets/my_guardrail_target.py
from spikee.templates.target import Target
from spikee.utilities.hinting import Content, TargetResponseHint, ModuleDescriptionHint, ModuleOptionsHint
from spikee.utilities.enums import ModuleTag
from typing import Optional

class MyGuardrailTarget(Target):
    def get_description(self) -> ModuleDescriptionHint:
        return [ModuleTag.SINGLE], "Guardrail target"

    def get_available_option_values(self) -> ModuleOptionsHint:
        return [], False

    def process_input(
        self,
        input_text: Content,
        system_message: Optional[Content] = None,
        target_options: Optional[str] = None,
    ) -> TargetResponseHint:
        result = call_my_guardrail(str(input_text))
        # True = allowed/bypassed (attack success from Spikee's perspective)
        # False = blocked (attack failure)
        return result == "ALLOWED"
```

> For the full guardrail testing workflow (attack + benign datasets, false positive analysis), see Phase 5 and read `spikee-src/docs/10_guardrail_testing.md`.

## 2.5 Target Options Parsing

For complex options, use `parse_options` from spikee utilities:

```python
from spikee.utilities.modules import parse_options

def process_input(self, input_text, system_message=None, target_options=None):
    opts = parse_options(target_options)  # Returns dict from "key1=val1,key2=val2"
    url = opts.get("url", "https://default.com/api")
    model = opts.get("model", "gpt-4o")
    # ...
```

Usage: `spikee test --target my_target --target-options "url=https://api.example.com,model=gpt-4o"`

## 2.6 Error Handling Summary

| Situation | What to do |
|---|---|
| Application responds normally | Return the response text (str) |
| Application blocks the request (guardrail) | Raise `GuardrailTrigger("message")` |
| Transient error (rate limit, timeout) | Raise `RetryableError("message", retry_period=60)` |
| Fatal error | Raise any `Exception` — Spikee logs it and continues |
| Guardrail boolean | Return `True` (allowed) or `False` (blocked) |

## 2.7 Next Step

Once your target works standalone (`python targets/my_target.py`), proceed to **Phase 3** to generate a dataset.
