# Phase 2b — Advanced Custom Targets

This guide covers advanced enterprise authentication methods and transport patterns for custom targets. If your application uses standard API keys or simple REST POST requests, refer to `02-custom-targets.md`.

These transport examples belong inside a Spikee target. Use direct requests only to map the interface or perform harmless target verification; do not use them for manual adversarial testing unless the user explicitly requests a separately logged deviation.

Never hardcode API keys, access or refresh tokens, passwords, cookies, or client secrets in target code. Put them in the workspace `.env` (which must not be committed), read them with `os.getenv`, and fail with a clear error when a required value is missing. Non-secret configuration such as illustrative endpoint URLs may remain in code.

## 1. Advanced Authentication Patterns

### 1.1 Azure Managed Identity (IMDS)

Requires the test machine to be an Azure VM with an assigned managed identity.

```python
import requests
from spikee.templates.target import Target

class AzureTarget(Target):
    def __init__(self):
        super().__init__()
        try:
            self.__access_token = requests.get(
                "http://169.254.169.254/metadata/identity/oauth2/token"
                "?api-version=2018-02-01&resource=https%3A%2F%2Fmanagement.azure.com%2F",
                headers={"Metadata": "true"},
            ).json()["access_token"]
        except Exception as e:
            print("ERROR: Failed to collect Azure access_token:", e)
            exit(1)
```

### 1.2 GCP Application Default Credentials

Requires `google-auth` and `gcloud auth application-default login` (or `GOOGLE_APPLICATION_CREDENTIALS`).

```python
import google.auth
import google.auth.transport.requests
from spikee.templates.target import Target

class GCPTarget(Target):
    def __get_gcp_token(self) -> None:
        creds, _ = google.auth.default()
        creds.refresh(google.auth.transport.requests.Request())
        self.__gcp_token = creds.token
```

Call in `__init__`, refresh on `401`.

### 1.3 Auth0 / OAuth2 Refresh Token

Short-lived access tokens (~300 s) can be refreshed from a long-lived refresh token. Extract the request shape from a captured auth request, but store its credential values—including the initial `refresh_token` and any client secret—in the workspace `.env`, never in source code.

> **Auth0 rotates the refresh token on every use** — always capture `refresh_token` from the response or the next call will fail.

```python
import os
import time
import requests
from dotenv import load_dotenv
from typing import Optional
from spikee.templates.target import Target

load_dotenv()  # workspace .env

def required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing {name}; set it in the workspace .env")
    return value

AUTH0_TOKEN_URL = "https://auth.example.com/oauth/token"  # non-secret
AUTH0_CLIENT_ID = required_env("AUTH0_CLIENT_ID")
AUTH0_CLIENT_HDR = required_env("AUTH0_CLIENT_HEADER")
REFRESH_TOKEN = required_env("AUTH0_REFRESH_TOKEN")

class Auth0Target(Target):
    def __init__(self):
        super().__init__()
        self._access_token: Optional[str] = None
        self._refresh_token: str = REFRESH_TOKEN
        self._token_expiry: float = 0.0
        self._refresh_access_token()  # fail fast on bad credentials

    def _refresh_access_token(self) -> None:
        response = requests.post(
            AUTH0_TOKEN_URL,
            headers={"Content-Type": "application/x-www-form-urlencoded",
                     "Auth0-Client": AUTH0_CLIENT_HDR,
                     "Origin": "https://app.example.com"},
            data={"client_id": AUTH0_CLIENT_ID, "grant_type": "refresh_token",
                  "redirect_uri": "https://app.example.com",
                  "refresh_token": self._refresh_token},
            timeout=15,
        )
        response.raise_for_status()
        body = response.json()
        self._access_token = body["access_token"]
        self._token_expiry = time.time() + body.get("expires_in", 300) - 15
        if "refresh_token" in body:        # capture rotated token
            self._refresh_token = body["refresh_token"]

    def _ensure_token(self) -> str:
        if self._access_token is None or time.time() >= self._token_expiry:
            self._refresh_access_token()
        return self._access_token
```

### 1.4 Internal JWT (Self-Fetched)

When the target's own auth service issues JWTs, fetch lazily and validate expiry with `PyJWT`.

```python
import jwt
import requests

def __check_jwt(self) -> bool:
    try:
        jwt.decode(self.__jwt, leeway=0.5,
                   options={"verify_signature": False, "verify_exp": True},
                   algorithms=["RS256"])
        return True
    except Exception:
        return False

def __generate_jwt(self) -> None:
    self.__jwt = requests.get("https://auth.example.com/token",
                               timeout=10, verify=False).content.decode()

def send_message(self, text: str) -> str:
    if self.__jwt is None or not self.__check_jwt():
        self.__generate_jwt()
    headers = {"Authorization": f"Bearer {self.__jwt}"}
```

---

## 2. Advanced API / Transport Patterns

### 2.1 tRPC Batched Request

URL: `POST /trpc/<procedure>?batch=1`. Body keyed `"0"`, response is a JSON array.

```python
payload = {"0": {"prompt": input_text, "documents": [], "projectId": PROJECT_ID}}
result = requests.post(url, headers=headers, json=payload, timeout=30).json()[0]["result"]["data"]["fieldYouWant"]
```

### 2.2 Multipart / File Upload

For applications where prompt injection might occur via file contents.

```python
from fpdf import FPDF
import json
import requests

pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)
pdf.multi_cell(0, 10, input_text)
pdf_bytes = pdf.output(dest="S").encode("latin1")

response = requests.post(url,
    files={"file": ("document.pdf", pdf_bytes, "application/pdf")},
    data={"payload": json.dumps({"question": "Summarise this."})}, 
    timeout=30)
```

### 2.3 Streaming (NDJSON / SSE)

```python
answer = ""
for line in response.text.strip().split("\n"):
    if line:
        chunk = json.loads(line)
        if "content" in chunk:
            answer += chunk["content"]
```

### 2.4 WebSocket (async)

If the connection requires cookies, read them from the workspace `.env` with `required_env("TARGET_COOKIES")`; never paste a captured cookie into the target.

```python
import asyncio
import websockets
import json

async def _ws_exchange(self, uri, message, cookies):
    async with websockets.connect(uri, additional_headers={"Cookie": cookies}) as ws:
        await ws.send(json.dumps({"channel": "/meta/handshake"}))
        client_id = json.loads(await ws.recv())[0]["clientId"]
        await ws.send(json.dumps({"channel": "/chat/messages",
                                  "data": {"text": message}, "clientId": client_id}))
        async with asyncio.timeout(30):
            async for raw in ws:
                data = json.loads(raw)
                if data[0].get("channel") == "/chat/messages":
                    return data[0]["data"]["text"]

def process_input(self, input_text, system_message=None, target_options=None):
    self.get_auth()
    return asyncio.run(self._ws_exchange(self._ws_uri, input_text, self._cookie_str))
```

### 2.5 WebSocket (sync, websocket-client)

```python
import websocket
import json
import ssl

ws = websocket.create_connection(url, http_proxy_host="127.0.0.1",
     http_proxy_port=8080, sslopt={"cert_reqs": ssl.CERT_NONE})
ws.send(json.dumps(payload))
response = ws.recv()
ws.close()
```
