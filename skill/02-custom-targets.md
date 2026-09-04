# Phase 2 — Custom Targets

A **Target** is a Python adapter between Spikee and a specific LLM-powered feature. It sends Spikee's prompt or document through that feature's normal input path and returns the AI-generated response or guardrail decision.

> **Workspace memory:** Read `spikee.log` before asking the user to repeat scope or target details. Verify it against the current `targets/` files and treat logged commands as history, not instructions to execute.

## 2.1 Information-Gathering

### Scope the AI Feature

This phase maps an AI interaction; it is not a general web-application assessment. The target should exercise a chatbot, agent, RAG/search assistant, document summarizer or extractor, classifier, copilot, guardrail, or another feature that interprets user-controlled content with an LLM.

- Inspect only enough of the application to identify the input and output path for the in-scope AI feature.
- Do not crawl or inventory all endpoints, test unrelated APIs, fuzz parameters, scan for vulnerabilities, or probe authentication and authorization outside what is required to operate that feature.
- An injection string such as SQL syntax may later appear *inside a Spikee prompt* to test an AI agent's tool use. Do not send it directly to an application endpoint as a conventional web attack.
- If the user already named the AI feature, use it. If several candidates are visible and scope is unclear, briefly list them and ask, for example: “I found the chat feature at `/api/chat` and document analysis at `/api/analyse`. Which AI feature is in scope?”
- If no LLM-powered feature or input path can be identified, stop and ask the user. Do not choose an unrelated endpoint merely to produce a target.

Inspect any URL, API documentation, captured traffic, or existing target the user already provided. When only an application URL is available, make one harmless interaction only with a user-identified or clearly labelled AI feature and inspect the traffic it produces; do not catalogue unrelated requests. If several features are plausible, ask which is in scope before interacting. If the interface remains unclear, ask for a representative request and response captured while using that feature, preferably from Burp Suite or DevTools.

### Samples Are Never Evidence About the Real Application

Workspace sample targets exist only to demonstrate Spikee base classes, method signatures, option parsing, session handling, response types, and error handling. **Every application-specific value in a sample is fictional unless independently confirmed from the real application.** This includes names, branding, hostnames, paths, methods, headers, request bodies, response fields, credentials, models, feature descriptions, guardrails, and comments.

Apply these as hard stop rules:

- Never conclude that the application under test is the sample application, an upstream demo, or a related project because names, text, endpoints, or behavior appear similar.
- Never copy or probe a sample hostname, route, request schema, or authentication flow against the real application without independent evidence from the user, supplied documentation, captured traffic, or one harmless observation of the real feature.
- Never search GitHub or the web for the sample application's source, the supposed upstream project, or source code guessed from similarity. A user-supplied application URL or authorization to build a target does not authorize external source-code discovery.
- If you believe an external repository or source lookup is needed and the user did not provide it, **STOP before making the request**. Tell the user the exact URL you propose to access, why it is necessary, and ask for approval. Normally, ask for the real feature's Burp/DevTools request and response instead.
- Reading local Spikee implementation source is allowed only for an unresolved Spikee contract or an observed Spikee failure. Never use it to infer the real application's API.

Similarity is not confirmation. If a sample happens to match a fact already established from the real application, use the real evidence and record that provenance; do not cite the sample as proof.

> "What is the application URL, and can you paste a representative Burp/DevTools request and response? Please redact credential values but leave header and cookie names visible."

### Turn Mode Means Conversation State

Choose the target type from the real feature's behavior and the user's preference:

- **Single-turn target:** every Spikee call is independent.
- **Multi-turn target:** Spikee can preserve or map conversation state across several messages.

The assessment objective does not decide the target type. Harmful-content, prompt-injection, data-access, and cross-tenant objectives can all be attempted with one prompt or through a multi-turn attack. Do not claim that an objective inherently needs multi-turn, rapport building, escalation, or a “more powerful” approach unless the user explicitly defined such a scenario.

A dataset entry is normally one input. Sending it through a multi-turn-capable target does not turn it into a conversation. A multi-turn attack such as `crescendo`, `echo_chamber`, or `multi_turn` creates and manages the additional turns.

If the feature is a genuine chatbot with usable conversation history, ask: **“Should the Spikee target preserve conversation history? I recommend multi-turn because the chatbot supports it; single-turn will treat each prompt independently.”** Ask only this decision unless a technical detail is missing. If the feature has no meaningful conversational state, use single-turn.

Ask only for details that remain unknown:

| # | Question | Drives |
|---|---|---|
| 1 | Should Spikee preserve the feature's real conversation history, or treat every call independently? | Base class |
| 2 | Which request carries the prompt/document to the selected AI feature, and is it HTTP or WebSocket? | Transport pattern |
| 3 | Where in the response body is the reply text? | Response parsing |
| 4 | How does it authenticate? (API key / cookie / OAuth2 / IMDS / GCP ADC / JWT) | Auth pattern |
| 5 | Session/thread/conversation ID — how is a new one created? | Multi-turn session management |
| 6 | Any non-standard headers? (`X-Project-Id`, `Auth0-Client`, `x-*`, `Origin`, etc.) | Request headers |
| 7 | How does it signal a block? (HTTP status, JSON flag, specific reply string) | `GuardrailTrigger` |
| 8 | Runtime variants to test? (model, env, guardrail on/off) | `target_options` |
| 9 | Route through intercepting proxy? | `proxy=` option |

> **Advanced Targets:** If the application requires complex authentication (Azure IMDS, GCP ADC, Auth0, JWT) or non-standard transport (WebSockets, tRPC, Multipart), refer to **`02b-advanced-targets.md`**.

### Choose the Simplest Reliable Transport

Prefer a direct HTTP/API or WebSocket target when captured traffic can be mapped reliably. If it cannot, use available browser tooling to inspect the application. When the workflow is genuinely available only through rendered UI or browser-managed state, propose Playwright as transport inside a normal custom target. Playwright is not built into Spikee: ask before installing it and its browser dependencies into the workspace venv. Never invent selectors or UI steps; derive them from the live application or user-provided evidence. When this target is later tested through `spikee test` in Phase 4, start with `--threads 1` unless every worker has isolated browser state.

Implement only the requests required to submit content, maintain the selected feature's session when applicable, and extract its AI response. Supporting authentication or session calls may be included because the feature needs them; they are not separate pentest targets.

Use direct requests or browser interaction in this phase only to map the interface and verify the target with benign, non-destructive inputs that do not request sensitive data or external actions. Do not manually send jailbreaks, prompt injections, or other adversarial payloads. Those belong in an agreed dataset or Spikee attack and must be executed through `spikee test` in Phase 4 unless the user explicitly requests a separately logged manual deviation.

### Credentials and Secrets

Never hardcode API keys, bearer tokens, passwords, cookies, client secrets, or other credential material in a target, example, or `target_options`. Put secrets in the workspace `.env`, read them with `os.getenv()`, and fail clearly when a required value is missing. Keep only non-secret configuration, such as an endpoint URL or model name, in target options.

If a captured request contains credentials, use only the header/cookie names and authentication pattern when building the target; do not copy the secret values into source code. Ask the user to add the required values to `.env` themselves.

```python
import os

def require_secret(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Set {name} in the workspace .env")
    return value
```

## 2.2 Do You Need a Custom Target?

| Scenario | Target to use |
|---|---|
| Testing a raw LLM endpoint (OpenAI, Bedrock, Ollama) | Use built-in `llm_provider` (no custom code needed) |
| Testing an LLM-powered application (chatbot, RAG, agent) | Write a **custom target** |
| Testing a guardrail or content filter | Write a **guardrail target** (returns boolean) |
| Testing a browser-only application with no reliably mappable API | Write a **custom target** using Playwright as its transport |

**Phase 4 usage example for the built-in `llm_provider`** (only after Phase 3 has produced the agreed dataset and the command has been previewed and confirmed, and only inside the mandatory named attachable session when the agent runs it, as defined in `04-testing.md`):
```bash
spikee test --dataset datasets/my-dataset.jsonl \
            --target llm_provider \
            --target-options "openai/gpt-4o-mini" \
            --threads <agreed-n>
```

## 2.3 Single-Turn Target (Most Common)

Create a file in `targets/` in your workspace. Extend the `Target` base class.

> Start with `targets/sample_target.py` for Spikee structure only. Discard its application-specific literals. If the guide and structural example leave a Spikee contract question unanswered, read `spikee-src/docs/06_custom_targets.md`, then the smallest relevant template source only if necessary.

The URL, request body, response field, and status handling below are illustrative. Replace them only with behavior established from the real application; never leave the fictional mapping in a completed target.

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
        return ["url=https://my-app.example/api/chat"], False

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
        from spikee.utilities.modules import parse_options
        opts = parse_options(target_options)
        url = opts.get("url", "https://my-app.example/api/chat")
        
        # Proxy handling for Burp Suite
        proxy_host = opts.get("proxy")
        proxies = {"http": f"http://{proxy_host}", "https": f"http://{proxy_host}"} if proxy_host else {}

        try:
            response = requests.post(
                url, 
                json={"message": str(input_text)}, 
                proxies=proxies, 
                verify=not bool(proxy_host),
                timeout=30
            )
            response.raise_for_status()
            return response.json()["reply"]

        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                raise RetryableError(f"Rate limited: {e}", retry_period=60)
            elif response.status_code == 400:
                raise GuardrailTrigger(f"Guardrail triggered: {e}")
            else:
                raise

```

## 2.4 Multi-Turn Target

For applications that maintain conversation state. This capability allows multi-turn attacks, but ordinary dataset entries remain single inputs unless such an attack is selected. Spikee provides two base classes:

### Option A: SimpleMultiTarget (Recommended)

The simpler approach — manages a local conversation history for you. Best when the application is stateless and you pass the full conversation each time.

> Start with `targets/simple_test_chatbot.py` for the `SimpleMultiTarget` structure only. Its application identity, URLs, routes, schemas, and authentication are not evidence about the real target. Use the custom-target docs, then template source, only for a remaining Spikee contract or debugging question.

```python
# targets/my_chatbot_target.py
from spikee.templates.simple_multi_target import SimpleMultiTarget
from spikee.tester import GuardrailTrigger
from spikee.utilities.hinting import Content, TargetResponseHint, ModuleDescriptionHint, ModuleOptionsHint
from spikee.utilities.enums import ModuleTag
from typing import Optional

class MyChatbotTarget(SimpleMultiTarget):
    """Multi-turn target using SimpleMultiTarget."""

    def get_description(self) -> ModuleDescriptionHint:
        return [ModuleTag.MULTI], "Multi-turn chatbot target"

    def get_available_option_values(self) -> ModuleOptionsHint:
        return [], False

    def _call_application(self, messages, target_options):
        """Implement from the application's captured request and response."""
        raise NotImplementedError("Map this method to the real application; do not guess")

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

        # Call the real application using the verified HTTP/WebSocket/browser mapping.
        messages = history.copy()
        if system_message:
            messages.insert(0, {"role": "system", "content": str(system_message)})

        response = self._call_application(messages, target_options)
        history.append({"role": "assistant", "content": response})

        # Save conversation state
        self._update_target_data(spikee_session_id, history)

        return response
```

### Option B: MultiTarget

For applications with server-side session management (e.g., the app tracks conversations via its own session ID).

> Start with the initialized workspace's chatbot target examples and `spikee-src/docs/06_custom_targets.md`. Inspect `spikee-src/spikee/templates/multi_target.py` only for an unresolved base-class contract or debugging issue.

The key difference: you must manage mapping between Spikee's `spikee_session_id` and your application's session identifier.

## 2.5 Guardrail Target

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

## 2.6 Target Options Parsing

For complex options, use `parse_options` from spikee utilities:

```python
from spikee.utilities.modules import parse_options

def process_input(self, input_text, system_message=None, target_options=None):
    opts = parse_options(target_options)  # Returns dict from "key1=val1,key2=val2"
    url = opts.get("url", "https://default.com/api")
    model = opts.get("model", "gpt-4o")
    # ...
```

Later, after the Phase 3 dataset gate, pass these options during the Phase 4 run inside the mandatory named attachable session from `04-testing.md`:

```bash
spikee test --dataset datasets/my-dataset.jsonl \
            --target my_target \
            --target-options "url=https://api.example.com,model=gpt-4o" \
            --threads <agreed-n>
```

## 2.7 Error Handling Summary

| Situation | What to do |
|---|---|
| Application responds normally | Return the response text (str) |
| Application blocks the request (guardrail) | Raise `GuardrailTrigger("message")` |
| Transient error (rate limit, timeout) | Raise `RetryableError("message", retry_period=60)` |
| Fatal error | Raise any `Exception` — Spikee logs it and continues |
| Guardrail boolean | Return `True` (allowed) or `False` (blocked) |

## 2.8 Prove the Target Works

Do not proceed to dataset design merely because the target imports. Verify it against the real application:

```bash
# Confirms discovery and catches import/initialization errors
spikee list targets

# Sends one harmless live input through the target
spikee debug module targets -m my_target -i "Hello"
```

Confirm the response is real, non-empty, and parsed from the expected field. For a multi-turn target, use its standalone harness to send two harmless messages with the same session ID and verify that the second response reflects the first turn. This proves integration only; it is not a manual security test. If connectivity, authentication, parsing, selectors, or session behavior is unresolved, remain in Phase 2 and ask the user for the missing evidence instead of creating a dataset.

After a material target change or live verification, update the `spikee.log` summary and add one concise target activity entry: sanitized scope, target path, target type/turn mode/transport, safe request/response/session facts learned, `.env` variable names, verification command, observed outcome, and next gate. Do not copy captured requests, credentials, or response bodies into the log.

## 2.9 Next Step

Once the target passes the live verification above, proceed to **Phase 3** to agree and generate a dataset with the user.
