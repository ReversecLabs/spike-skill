# Target Implementation Examples

Read this only after the Phase 2 target design is approved. The examples show Spikee structure; application names, URLs, schemas and authentication are not evidence about the real target.

## Single-Turn Target

Create a file in `targets/` and extend `Target`. Start with `targets/sample_target.py` for structure only. If this guide leaves a Spikee contract question unanswered, read `spikee-src/docs/06_custom_targets.md`, then the smallest relevant template source only if necessary.

The URL, request body, response field and status handling below are illustrative. Replace them with behavior established from the real application. `process_input` receives the dataset entry in `input_text`, an optional dataset system message and the selected `target_options`. Return the application's text response. Guardrail targets may return a boolean. Raise `RetryableError` for transient failures and ordinary exceptions for fatal failures so Spikee records them. In `get_available_option_values`, the first option is the default; set the second tuple value to `True` only when the target itself needs an LLM provider.

```python
from spikee.templates.target import Target
from spikee.tester import RetryableError
from spikee.utilities.hinting import Content, TargetResponseHint, ModuleDescriptionHint, ModuleOptionsHint
from spikee.utilities.enums import ModuleTag
from typing import Optional
import requests

class MyAppTarget(Target):
    def get_description(self) -> ModuleDescriptionHint:
        return [ModuleTag.SINGLE], "My custom application target"

    def get_available_option_values(self) -> ModuleOptionsHint:
        return ["url=https://my-app.example/api/chat"], False

    def process_input(
        self,
        input_text: Content,
        system_message: Optional[Content] = None,
        target_options: Optional[str] = None,
    ) -> TargetResponseHint:
        from spikee.utilities.modules import parse_options
        opts = parse_options(target_options)
        url = opts.get("url", "https://my-app.example/api/chat")
        proxy_host = opts.get("proxy")
        proxies = {"http": f"http://{proxy_host}", "https": f"http://{proxy_host}"} if proxy_host else {}

        try:
            response = requests.post(
                url,
                json={"message": str(input_text)},
                proxies=proxies,
                verify=opts.get("ca_bundle", True),
                timeout=30,
            )
            response.raise_for_status()
            return response.json()["reply"]
        except requests.exceptions.HTTPError as error:
            if response.status_code == 429:
                raise RetryableError(f"Rate limited: {error}", retry_period=60)
            raise
```

## Multi-Turn Targets

Multi-turn capability allows conversation attacks, but ordinary dataset entries remain single inputs unless an attack creates additional turns.

### `SimpleMultiTarget`

Use this when the application is stateless and the target sends the full conversation each time. Start with `targets/simple_test_chatbot.py` for structure only.

```python
from spikee.templates.simple_multi_target import SimpleMultiTarget
from spikee.utilities.hinting import Content, TargetResponseHint, ModuleDescriptionHint, ModuleOptionsHint
from spikee.utilities.enums import ModuleTag
from typing import Optional

class MyChatbotTarget(SimpleMultiTarget):
    def get_description(self) -> ModuleDescriptionHint:
        return [ModuleTag.MULTI], "Multi-turn chatbot target"

    def get_available_option_values(self) -> ModuleOptionsHint:
        return [], False

    def _call_application(self, messages, target_options):
        raise NotImplementedError("Map this method to the observed application")

    def process_input(
        self,
        input_text: Content,
        system_message: Optional[Content] = None,
        target_options: Optional[str] = None,
        spikee_session_id: Optional[str] = None,
        backtrack: bool = False,
    ) -> TargetResponseHint:
        history = self._get_target_data(spikee_session_id) or []
        if backtrack and len(history) >= 2:
            history = history[:-2]

        history.append({"role": "user", "content": str(input_text)})
        messages = history.copy()
        if system_message:
            messages.insert(0, {"role": "system", "content": str(system_message)})

        response = self._call_application(messages, target_options)
        history.append({"role": "assistant", "content": response})
        self._update_target_data(spikee_session_id, history)
        return response
```

### `MultiTarget`

Use this when the application manages conversations through its own session or thread ID. Start with the initialized workspace examples and `spikee-src/docs/06_custom_targets.md`. Read `spikee-src/spikee/templates/multi_target.py` only for an unresolved base-class contract or debugging question.

Map each `spikee_session_id` to its application conversation identifier. Keep the associated turns for backtracking. If the application has no undo endpoint but can start a new conversation, create one and replay the retained turns up to the requested earlier state before sending the next input. Recommend `backtrack=True` when that reconstruction is reliable and verify it. Use `backtrack=False` only when the earlier state cannot be restored or replayed reliably; no native undo endpoint is not enough by itself. Never pass `None` to a base-class session reset unless that contract explicitly accepts it.

## Guardrail Target

A guardrail target returns `True` when a prompt was allowed and `False` when it was blocked.

```python
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
        return result == "ALLOWED"
```

For a full guardrail workflow with attack and benign datasets, read `spikee-src/docs/10_guardrail_testing.md` during the relevant later phase.

## Options and Errors

Parse complex target options with `parse_options`:

```python
from spikee.utilities.modules import parse_options

def process_input(self, input_text, system_message=None, target_options=None):
    opts = parse_options(target_options)
    url = opts.get("url", "https://default.com/api")
    model = opts.get("model", "gpt-4o")
```

Pass agreed options during Phase 4:

```bash
spikee test --dataset datasets/my-dataset.jsonl \
            --target my_target \
            --target-options "url=https://api.example.com,model=gpt-4o" \
            --threads <agreed-n>
```

Only map an explicit application block signal, such as a documented HTTP status or JSON flag, to `GuardrailTrigger`. A model refusal is ordinary response text unless the application contract marks it as a guardrail result. HTTP 400 alone can mean a malformed request. Supply a trusted CA bundle for an intercepting proxy; do not disable TLS verification by default.

| Situation | What to do |
|---|---|
| Application responds normally | Return response text |
| Application returns an explicit guardrail block signal | Raise `GuardrailTrigger("message")` |
| Rate limit or timeout | Raise `RetryableError("message", retry_period=60)` |
| Fatal error | Raise an exception so Spikee records an error |
| Guardrail boolean | Return `True` for allowed, `False` for blocked |
