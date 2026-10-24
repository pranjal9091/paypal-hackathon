import base64
import time
import uuid
from typing import Dict, Any, Optional
import httpx
from app.config import settings

class PayPalClientError(Exception):
    def __init__(self, message: str, status_code: int = 502, details: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details

class PayPalClient:
    """
    Official PayPal REST API v2 Client for Authorize & Delayed Capture.
    Implements:
    - OAuth2 token caching
    - Orders v2 with intent=AUTHORIZE
    - Order authorization hold: POST /v2/checkout/orders/{id}/authorize
    - Authorized payment capture: POST /v2/payments/authorizations/{id}/capture
    - Authorization void: POST /v2/payments/authorizations/{id}/void
    - Idempotency using PayPal-Request-Id
    - Transparent, clearly labeled fallback mocks when sandbox credentials are not configured.
    """

    def __init__(self):
        self.base_url = settings.paypal_base_url
        self.client_id = settings.paypal_client_id.strip()
        self.client_secret = settings.paypal_client_secret.strip()
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0.0

    @property
    def is_live_configured(self) -> bool:
        return settings.has_real_paypal_credentials

    async def get_access_token(self) -> str:
        if not self.is_live_configured:
            return "mock-access-token"

        now = time.time()
        if self._access_token and now < self._token_expires_at - 60:
            return self._access_token

        auth_header = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {"grant_type": "client_credentials"}

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(f"{self.base_url}/v1/oauth2/token", headers=headers, data=data)
            if resp.status_code != 200:
                raise PayPalClientError(
                    f"PayPal OAuth token exchange failed: HTTP {resp.status_code}",
                    status_code=resp.status_code,
                    details=resp.text,
                )
            payload = resp.json()
            self._access_token = payload["access_token"]
            self._token_expires_at = now + payload.get("expires_in", 3600)
            return self._access_token

    async def create_order(self, amount: str, currency: str, reference_id: str, idempotency_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Creates an order with intent=AUTHORIZE.
        Places hold intent without capturing funds.
        """
        idempotency_key = idempotency_key or str(uuid.uuid4())

        if not self.is_live_configured:
            return {
                "id": f"MOCK-ORDER-{uuid.uuid4().hex[:12].upper()}",
                "status": "CREATED",
                "intent": "AUTHORIZE",
                "is_mock": True,
                "links": [
                    {"rel": "approve", "href": f"https://www.sandbox.paypal.com/checkoutnow?token=MOCK-{reference_id}"}
                ]
            }

        token = await self.get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "PayPal-Request-Id": idempotency_key,
        }
        body = {
            "intent": "AUTHORIZE",
            "purchase_units": [
                {
                    "reference_id": reference_id,
                    "description": f"Outcome Exchange Contract #{reference_id[:8]}",
                    "amount": {
                        "currency_code": currency,
                        "value": amount
                    }
                }
            ],
            "application_context": {
                "user_action": "CONTINUE",
                "shipping_preference": "NO_SHIPPING"
            }
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(f"{self.base_url}/v2/checkout/orders", headers=headers, json=body)
            if resp.status_code not in (200, 201):
                raise PayPalClientError(
                    f"Failed to create PayPal order: HTTP {resp.status_code}",
                    status_code=resp.status_code,
                    details=resp.text
                )
            result = resp.json()
            result["is_mock"] = False
            return result

    async def authorize_order(self, order_id: str, idempotency_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Authorizes an approved order, placing the authorization hold.
        POST /v2/checkout/orders/{id}/authorize
        """
        idempotency_key = idempotency_key or str(uuid.uuid4())

        if not self.is_live_configured or order_id.startswith("MOCK-"):
            auth_id = f"MOCK-AUTH-{uuid.uuid4().hex[:12].upper()}"
            return {
                "id": order_id,
                "status": "COMPLETED",
                "is_mock": True,
                "authorization_id": auth_id,
                "authorization_status": "CREATED",
                "raw": {
                    "purchase_units": [
                        {
                            "payments": {
                                "authorizations": [
                                    {"id": auth_id, "status": "CREATED"}
                                ]
                            }
                        }
                    ]
                }
            }

        token = await self.get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "PayPal-Request-Id": idempotency_key,
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(f"{self.base_url}/v2/checkout/orders/{order_id}/authorize", headers=headers, json={})
            if resp.status_code not in (200, 201):
                raise PayPalClientError(
                    f"Failed to authorize PayPal order: HTTP {resp.status_code}",
                    status_code=resp.status_code,
                    details=resp.text
                )
            data = resp.json()
            try:
                auth_unit = data["purchase_units"][0]["payments"]["authorizations"][0]
                auth_id = auth_unit["id"]
                auth_status = auth_unit["status"]
            except (KeyError, IndexError):
                raise PayPalClientError("PayPal authorize response missing expected authorization object", details=data)

            return {
                "id": order_id,
                "status": data.get("status", "COMPLETED"),
                "authorization_id": auth_id,
                "authorization_status": auth_status,
                "is_mock": False,
                "raw": data
            }

    async def capture_authorization(self, authorization_id: str, amount: str, currency: str, idempotency_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Captures an existing authorization hold after deterministic verification & buyer approval.
        POST /v2/payments/authorizations/{authorization_id}/capture
        """
        idempotency_key = idempotency_key or str(uuid.uuid4())

        if not self.is_live_configured or authorization_id.startswith("MOCK-"):
            cap_id = f"MOCK-CAP-{uuid.uuid4().hex[:12].upper()}"
            return {
                "capture_id": cap_id,
                "status": "COMPLETED",
                "amount": {"value": amount, "currency_code": currency},
                "is_mock": True,
                "raw": {"id": cap_id, "status": "COMPLETED"}
            }

        token = await self.get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "PayPal-Request-Id": idempotency_key,
        }
        body = {
            "amount": {
                "value": amount,
                "currency_code": currency
            },
            "final_capture": True
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(
                f"{self.base_url}/v2/payments/authorizations/{authorization_id}/capture",
                headers=headers,
                json=body
            )
            if resp.status_code not in (200, 201):
                raise PayPalClientError(
                    f"Failed to capture PayPal authorization: HTTP {resp.status_code}",
                    status_code=resp.status_code,
                    details=resp.text
                )
            data = resp.json()
            return {
                "capture_id": data.get("id"),
                "status": data.get("status", "COMPLETED"),
                "amount": data.get("amount", {"value": amount, "currency_code": currency}),
                "is_mock": False,
                "raw": data
            }

    async def void_authorization(self, authorization_id: str, idempotency_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Voids (cancels) an existing authorization hold, returning held funds immediately.
        POST /v2/payments/authorizations/{authorization_id}/void
        """
        idempotency_key = idempotency_key or str(uuid.uuid4())

        if not self.is_live_configured or authorization_id.startswith("MOCK-"):
            return {"status": "VOIDED", "authorization_id": authorization_id, "is_mock": True}

        token = await self.get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "PayPal-Request-Id": idempotency_key,
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(
                f"{self.base_url}/v2/payments/authorizations/{authorization_id}/void",
                headers=headers,
                json={}
            )
            if resp.status_code not in (200, 204):
                raise PayPalClientError(
                    f"Failed to void PayPal authorization: HTTP {resp.status_code}",
                    status_code=resp.status_code,
                    details=resp.text
                )
            return {"status": "VOIDED", "authorization_id": authorization_id, "is_mock": False}

paypal_client = PayPalClient()
