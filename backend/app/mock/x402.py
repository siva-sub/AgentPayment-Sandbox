"""x402 Mock Server - HTTP 402 Payment Required Protocol (v2).

Implements a mock x402-compliant resource server for testing.
Based on: https://github.com/coinbase/x402/blob/main/specs/x402-specification-v2.md

Protocol Version: 2
- Uses CAIP-2 network identifiers (e.g., eip155:84532)
- PaymentRequired with `accepts` array and `resource` object
- Facilitator endpoints: /verify, /settle, /supported
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Header, HTTPException, Request, Response
from pydantic import BaseModel, Field

router = APIRouter()

# In-memory storage
_payments: dict[str, dict[str, Any]] = {}
_nonces: set[str] = set()
_settlements: dict[str, dict[str, Any]] = {}


# ============================================================================
# Constants - x402 v2
# ============================================================================

X402_VERSION = 2
RECEIVER_ADDRESS = "0x209693Bc6afc0C5328bA36FaF03C514EF312287C"
USDC_CONTRACT = "0x036CbD53842c5426634e7929541eC2318f3dCF7e"
DEFAULT_NETWORK = "eip155:84532"  # Base Sepolia (CAIP-2)


# ============================================================================
# Models - x402 v2 Spec
# ============================================================================


class ResourceInfo(BaseModel):
    """Resource being protected."""

    url: str
    description: str | None = None
    mimeType: str | None = None


class PaymentRequirements(BaseModel):
    """Payment requirements for a resource."""

    scheme: str = "exact"
    network: str = DEFAULT_NETWORK
    amount: str
    asset: str = USDC_CONTRACT
    payTo: str = RECEIVER_ADDRESS
    maxTimeoutSeconds: int = 60
    extra: dict[str, Any] | None = None


class PaymentRequired(BaseModel):
    """x402 v2 PaymentRequired response."""

    x402Version: int = X402_VERSION
    error: str | None = None
    resource: ResourceInfo
    accepts: list[PaymentRequirements]
    extensions: dict[str, Any] = Field(default_factory=dict)


class Authorization(BaseModel):
    """EIP-3009 authorization parameters."""

    from_: str = Field(alias="from")
    to: str
    value: str
    validAfter: str
    validBefore: str
    nonce: str


class Payload(BaseModel):
    """Scheme-specific payment data."""

    signature: str
    authorization: Authorization


class PaymentPayload(BaseModel):
    """x402 v2 PaymentPayload."""

    x402Version: int = X402_VERSION
    resource: ResourceInfo | None = None
    accepted: PaymentRequirements
    payload: Payload
    extensions: dict[str, Any] = Field(default_factory=dict)


class VerifyRequest(BaseModel):
    """Request to verify payment."""

    paymentPayload: dict[str, Any]
    paymentRequirements: dict[str, Any]


class SettleRequest(BaseModel):
    """Request to settle payment."""

    paymentPayload: dict[str, Any]
    paymentRequirements: dict[str, Any]


# ============================================================================
# Protected Resources
# ============================================================================

RESOURCES: dict[str, dict[str, Any]] = {
    "premium-content": {
        "id": "premium-content",
        "title": "Premium AI Model Access",
        "description": "Access to premium market data",
        "content": "This is premium content that requires payment to access.",
        "amount": "10000",  # 0.01 USDC in atomic units (6 decimals)
        "mimeType": "application/json",
    },
    "api-call": {
        "id": "api-call",
        "title": "Premium API Call",
        "description": "Execute a premium computation",
        "content": {"result": "Expensive computation result", "tokens_used": 1000},
        "amount": "5000",
        "mimeType": "application/json",
    },
    "data-export": {
        "id": "data-export",
        "title": "Data Export",
        "description": "Export data in JSON format",
        "content": {"data": [1, 2, 3, 4, 5], "format": "json"},
        "amount": "20000",
        "mimeType": "application/json",
    },
}


# ============================================================================
# Helper Functions
# ============================================================================


def _build_payment_required(resource_id: str, base_url: str) -> PaymentRequired:
    """Build x402 v2 PaymentRequired response."""
    resource = RESOURCES.get(resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    return PaymentRequired(
        x402Version=X402_VERSION,
        error="X-PAYMENT header is required",
        resource=ResourceInfo(
            url=f"{base_url}/resource/{resource_id}",
            description=resource["description"],
            mimeType=resource["mimeType"],
        ),
        accepts=[
            PaymentRequirements(
                scheme="exact",
                network=DEFAULT_NETWORK,
                amount=resource["amount"],
                asset=USDC_CONTRACT,
                payTo=RECEIVER_ADDRESS,
                maxTimeoutSeconds=60,
                extra={"name": "USDC", "version": "2"},
            )
        ],
        extensions={},
    )


def _verify_payment_payload(payload: dict[str, Any], requirements: dict[str, Any]) -> tuple[bool, str | None, str | None]:
    """Verify payment payload against requirements.

    Returns: (is_valid, invalid_reason, payer_address)
    """
    try:
        # Check x402 version
        if payload.get("x402Version") != X402_VERSION:
            return False, "invalid_x402_version", None

        # Extract authorization
        auth = payload.get("payload", {}).get("authorization", {})
        if not auth:
            return False, "invalid_payload", None

        payer = auth.get("from")
        signature = payload.get("payload", {}).get("signature")

        if not signature or not payer:
            return False, "invalid_exact_evm_payload_signature", payer

        # Check recipient matches
        if auth.get("to") != requirements.get("payTo"):
            return False, "invalid_exact_evm_payload_recipient_mismatch", payer

        # Check amount
        if int(auth.get("value", "0")) < int(requirements.get("amount", "0")):
            return False, "invalid_exact_evm_payload_authorization_value", payer

        # Check nonce not already used
        nonce = auth.get("nonce", "")
        if nonce in _nonces:
            return False, "nonce_already_used", payer

        # Check time window
        now = int(datetime.now(timezone.utc).timestamp())
        valid_after = int(auth.get("validAfter", "0"))
        valid_before = int(auth.get("validBefore", str(now + 300)))

        if now < valid_after:
            return False, "invalid_exact_evm_payload_authorization_valid_after", payer
        if now > valid_before:
            return False, "invalid_exact_evm_payload_authorization_valid_before", payer

        return True, None, payer

    except Exception as e:
        return False, f"unexpected_verify_error: {e}", None


def _settle_payment(payload: dict[str, Any], requirements: dict[str, Any]) -> tuple[bool, str | None, str | None, str | None]:
    """Settle payment on chain (mock).

    Returns: (success, error_reason, payer, transaction_hash)
    """
    is_valid, invalid_reason, payer = _verify_payment_payload(payload, requirements)

    if not is_valid:
        return False, invalid_reason, payer, None

    # Mark nonce as used
    nonce = payload.get("payload", {}).get("authorization", {}).get("nonce", "")
    _nonces.add(nonce)

    # Generate mock transaction hash
    tx_hash = f"0x{uuid.uuid4().hex}{uuid.uuid4().hex[:32]}"

    # Store settlement
    _settlements[tx_hash] = {
        "payer": payer,
        "amount": requirements.get("amount"),
        "network": requirements.get("network"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    return True, None, payer, tx_hash


# ============================================================================
# Discovery Endpoints
# ============================================================================


@router.get("/info")
async def get_info() -> dict[str, Any]:
    """Return x402 v2 server info."""
    return {
        "x402Version": X402_VERSION,
        "protocol": "x402",
        "receiver": RECEIVER_ADDRESS,
        "supportedNetworks": [DEFAULT_NETWORK, "eip155:8453"],  # Base Sepolia, Base Mainnet
        "supportedAssets": [USDC_CONTRACT],
        "resources": list(RESOURCES.keys()),
    }


@router.get("/supported")
async def get_supported() -> dict[str, Any]:
    """Return supported payment kinds (Facilitator API)."""
    return {
        "kinds": [
            {
                "x402Version": X402_VERSION,
                "scheme": "exact",
                "network": DEFAULT_NETWORK,
            },
            {
                "x402Version": X402_VERSION,
                "scheme": "exact",
                "network": "eip155:8453",
            },
        ],
        "extensions": [],
        "signers": {
            "eip155:*": [RECEIVER_ADDRESS],
        },
    }


# ============================================================================
# Resource Access with 402
# ============================================================================


@router.get("/resource/{resource_id}")
async def get_resource(
    request: Request,
    resource_id: str,
    x_payment: str | None = Header(None, alias="X-PAYMENT"),
) -> Any:
    """Access a protected resource.

    Returns 402 with PaymentRequired if no valid payment.
    Returns resource content if payment is valid.
    """
    if resource_id not in RESOURCES:
        raise HTTPException(status_code=404, detail="Resource not found")

    base_url = str(request.base_url).rstrip("/")

    # If no payment header, return 402
    if not x_payment:
        payment_required = _build_payment_required(resource_id, base_url)
        return Response(
            status_code=402,
            content=payment_required.model_dump_json(),
            media_type="application/json",
            headers={"X-Payment-Required": payment_required.model_dump_json()},
        )

    # Parse and verify payment
    try:
        payload = json.loads(x_payment)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid payment payload JSON")

    requirements = {
        "scheme": "exact",
        "network": DEFAULT_NETWORK,
        "amount": RESOURCES[resource_id]["amount"],
        "asset": USDC_CONTRACT,
        "payTo": RECEIVER_ADDRESS,
    }

    success, error, payer, tx_hash = _settle_payment(payload, requirements)

    if not success:
        raise HTTPException(status_code=402, detail=error or "Payment failed")

    # Return resource with settlement info
    resource = RESOURCES[resource_id]
    return {
        "success": True,
        "resource_id": resource_id,
        "title": resource["title"],
        "content": resource["content"],
        "settlement": {
            "transaction": tx_hash,
            "network": DEFAULT_NETWORK,
            "payer": payer,
        },
    }


# ============================================================================
# Facilitator Endpoints
# ============================================================================


@router.post("/verify")
async def verify_payment(request: VerifyRequest) -> dict[str, Any]:
    """Verify payment authorization without settling."""
    is_valid, invalid_reason, payer = _verify_payment_payload(
        request.paymentPayload,
        request.paymentRequirements,
    )

    if is_valid:
        return {"isValid": True, "payer": payer}
    else:
        return {"isValid": False, "invalidReason": invalid_reason, "payer": payer}


@router.post("/settle")
async def settle_payment_endpoint(request: SettleRequest) -> dict[str, Any]:
    """Settle payment on blockchain."""
    success, error, payer, tx_hash = _settle_payment(
        request.paymentPayload,
        request.paymentRequirements,
    )

    if success:
        return {
            "success": True,
            "payer": payer,
            "transaction": tx_hash,
            "network": request.paymentRequirements.get("network", DEFAULT_NETWORK),
        }
    else:
        return {
            "success": False,
            "errorReason": error,
            "payer": payer,
            "transaction": "",
            "network": request.paymentRequirements.get("network", DEFAULT_NETWORK),
        }


# ============================================================================
# Discovery API (Bazaar)
# ============================================================================


@router.get("/discovery/resources")
async def discover_resources(
    request: Request,
    type: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    """List discoverable x402 resources."""
    base_url = str(request.base_url).rstrip("/")
    items = []

    for resource_id, resource in RESOURCES.items():
        items.append({
            "resource": f"{base_url}/resource/{resource_id}",
            "type": "http",
            "x402Version": X402_VERSION,
            "accepts": [
                {
                    "scheme": "exact",
                    "network": DEFAULT_NETWORK,
                    "amount": resource["amount"],
                    "asset": USDC_CONTRACT,
                    "payTo": RECEIVER_ADDRESS,
                    "maxTimeoutSeconds": 60,
                    "extra": {"name": "USDC", "version": "2"},
                }
            ],
            "lastUpdated": int(datetime.now(timezone.utc).timestamp()),
            "metadata": {
                "category": "data",
                "provider": "APS Mock",
                "title": resource["title"],
            },
        })

    return {
        "x402Version": X402_VERSION,
        "items": items[offset : offset + limit],
        "pagination": {
            "limit": limit,
            "offset": offset,
            "total": len(items),
        },
    }


# ============================================================================
# Test Endpoints
# ============================================================================


@router.post("/test/reset")
async def reset_test_state() -> dict[str, str]:
    """Reset server state for testing."""
    _payments.clear()
    _nonces.clear()
    _settlements.clear()
    return {"status": "reset"}


@router.post("/test/generate-payment")
async def generate_test_payment(
    request: Request,
    resource_id: str,
) -> dict[str, Any]:
    """Generate a valid x402 v2 test payment for a resource."""
    if resource_id not in RESOURCES:
        raise HTTPException(status_code=404, detail="Resource not found")

    base_url = str(request.base_url).rstrip("/")
    resource = RESOURCES[resource_id]
    now = int(datetime.now(timezone.utc).timestamp())
    nonce = f"0x{uuid.uuid4().hex}{uuid.uuid4().hex[:32]}"

    # Generate mock payment payload
    payment_payload = {
        "x402Version": X402_VERSION,
        "resource": {
            "url": f"{base_url}/resource/{resource_id}",
            "description": resource["description"],
            "mimeType": resource["mimeType"],
        },
        "accepted": {
            "scheme": "exact",
            "network": DEFAULT_NETWORK,
            "amount": resource["amount"],
            "asset": USDC_CONTRACT,
            "payTo": RECEIVER_ADDRESS,
            "maxTimeoutSeconds": 60,
            "extra": {"name": "USDC", "version": "2"},
        },
        "payload": {
            "signature": f"0x{'ab' * 65}",
            "authorization": {
                "from": "0x857b06519E91e3A54538791bDbb0E22373e36b66",
                "to": RECEIVER_ADDRESS,
                "value": resource["amount"],
                "validAfter": str(now - 60),
                "validBefore": str(now + 300),
                "nonce": nonce,
            },
        },
        "extensions": {},
    }

    return {
        "x_payment_header": json.dumps(payment_payload),
        "payment_payload": payment_payload,
        "instructions": "Add as X-PAYMENT header (JSON string) to access the resource",
    }
