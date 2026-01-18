"""AP2 Mock Server - Agent Payments Protocol (A2A Message Handler).

Implements a mock AP2-compliant merchant agent for testing.
Based on: https://github.com/google-agentic-commerce/AP2

AP2 uses A2A (Agent-to-Agent) protocol for message exchange.
Key flows: IntentMandate → CartMandate → PaymentMandate → PaymentReceipt
"""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()

# In-memory storage
_mandates: dict[str, dict[str, Any]] = {}
_sessions: dict[str, dict[str, Any]] = {}
_receipts: dict[str, dict[str, Any]] = {}

# Multi-agent simulation storage
_payment_methods: dict[str, dict[str, Any]] = {}  # Credentials Provider
_otp_challenges: dict[str, dict[str, Any]] = {}   # Payment Processor
_pending_payments: dict[str, dict[str, Any]] = {} # Payment Processor


# ============================================================================
# Models (A2A Message Format)
# ============================================================================


class A2AMessage(BaseModel):
    """A2A protocol message."""

    jsonrpc: str = "2.0"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    method: str
    params: dict[str, Any] = Field(default_factory=dict)


class A2AResponse(BaseModel):
    """A2A protocol response."""

    jsonrpc: str = "2.0"
    id: str
    result: dict[str, Any] | None = None
    error: dict[str, Any] | None = None


class IntentMandateRequest(BaseModel):
    """Request to create an IntentMandate."""

    intent_description: str
    max_amount_cents: int
    currency: str = "USD"
    allowed_merchants: list[str] = Field(default_factory=list)
    expiry_hours: int = 24


class CartRequest(BaseModel):
    """Request to create a cart/order."""

    items: list[dict[str, Any]]
    shipping_address: dict[str, Any] | None = None


class PaymentAuthorizationRequest(BaseModel):
    """Request to authorize payment."""

    cart_mandate_id: str
    payment_method: dict[str, Any]
    user_authorization: str  # Signature from user


# ============================================================================
# Mock Merchant Catalog
# ============================================================================

PRODUCTS: dict[str, dict[str, Any]] = {
    "laptop_pro": {
        "id": "laptop_pro",
        "name": "Pro Laptop 16\"",
        "price_cents": 249900,
        "currency": "USD",
    },
    "wireless_mouse": {
        "id": "wireless_mouse",
        "name": "Wireless Mouse",
        "price_cents": 7999,
        "currency": "USD",
    },
    "usb_hub": {
        "id": "usb_hub",
        "name": "USB-C Hub",
        "price_cents": 4999,
        "currency": "USD",
    },
}

MERCHANT_INFO = {
    "id": "mock_merchant_001",
    "name": "APS Mock Electronics",
    "agent_url": "http://localhost:8080/mock/ap2",
}

# Credentials Provider Agent - available payment methods in user's wallet
WALLET_PAYMENT_METHODS = [
    {
        "id": "pm_card_visa",
        "type": "card",
        "display_name": "Visa •••• 4242",
        "brand": "visa",
        "last4": "4242",
        "is_tokenized": True,
        "dpan": "tok_dpan_visa_4242",
    },
    {
        "id": "pm_card_mastercard",
        "type": "card",
        "display_name": "Mastercard •••• 5555",
        "brand": "mastercard",
        "last4": "5555",
        "is_tokenized": True,
        "dpan": "tok_dpan_mc_5555",
    },
    {
        "id": "pm_x402_usdc",
        "type": "x402",
        "display_name": "USDC Wallet",
        "network": "eip155:84532",
        "asset": "USDC",
        "balance_cents": 100000,
    },
]


# ============================================================================
# Helper Functions
# ============================================================================


def _compute_hash(data: dict[str, Any]) -> str:
    """Compute SHA-256 hash of data."""
    json_str = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(json_str.encode()).hexdigest()


def _mock_sign(data: dict[str, Any], signer: str) -> str:
    """Generate mock signature (JWT-like)."""
    # In production, this would be actual ES256K signing
    payload_hash = _compute_hash(data)
    return f"mock_sig_{signer}_{payload_hash[:16]}"


def _verify_mock_signature(signature: str, expected_signer: str) -> bool:
    """Verify mock signature."""
    return signature.startswith(f"mock_sig_{expected_signer}_")


# ============================================================================
# A2A Agent Card (Discovery)
# ============================================================================


@router.get("/.well-known/a2a")
async def get_agent_card() -> dict[str, Any]:
    """Return A2A Agent Card with AP2 extension."""
    return {
        "name": MERCHANT_INFO["name"],
        "description": "Mock merchant for AP2 protocol testing",
        "url": MERCHANT_INFO["agent_url"],
        "version": "1.0.0",
        "capabilities": {
            "streaming": False,
            "pushNotifications": False,
            "extensions": [
                {
                    "uri": "https://github.com/google-agentic-commerce/ap2/tree/v0.1",
                    "params": {
                        "roles": ["merchant"],
                        "supported_mandates": [
                            "IntentMandate",
                            "CartMandate",
                            "PaymentMandate",
                        ],
                    },
                }
            ],
        },
        "skills": [
            {
                "id": "shop",
                "name": "Shopping",
                "description": "Browse products and make purchases",
            }
        ],
        "authentication": {
            "schemes": ["bearer", "signature"],
        },
        "signing_keys": [
            {
                "kid": "merchant_key_001",
                "kty": "EC",
                "crv": "secp256k1",
                "use": "sig",
                "alg": "ES256K",
            }
        ],
    }


# ============================================================================
# A2A Message Handler
# ============================================================================


@router.post("/message")
async def handle_message(message: A2AMessage) -> A2AResponse:
    """Handle A2A protocol messages."""
    method = message.method
    params = message.params

    try:
        if method == "ap2/createIntentMandate":
            result = await _create_intent_mandate(params)
        elif method == "ap2/browseProducts":
            result = await _browse_products(params)
        elif method == "ap2/createCart":
            result = await _create_cart(params)
        elif method == "ap2/authorizePayment":
            result = await _authorize_payment(params)
        elif method == "ap2/getReceipt":
            result = await _get_receipt(params)
        elif method == "ap2/getMandateStatus":
            result = await _get_mandate_status(params)
        # Credentials Provider Agent methods
        elif method == "ap2/listPaymentMethods":
            result = await _list_payment_methods(params)
        elif method == "ap2/selectPaymentMethod":
            result = await _select_payment_method(params)
        # Payment Processor Agent methods
        elif method == "ap2/initiatePayment":
            result = await _initiate_payment(params)
        elif method == "ap2/submitOtp":
            result = await _submit_otp(params)
        else:
            return A2AResponse(
                id=message.id,
                error={"code": -32601, "message": f"Method not found: {method}"},
            )

        return A2AResponse(id=message.id, result=result)

    except HTTPException as e:
        return A2AResponse(
            id=message.id,
            error={"code": e.status_code, "message": e.detail},
        )
    except Exception as e:
        return A2AResponse(
            id=message.id,
            error={"code": -32603, "message": str(e)},
        )


# ============================================================================
# AP2 Method Handlers
# ============================================================================


async def _create_intent_mandate(params: dict[str, Any]) -> dict[str, Any]:
    """Create an IntentMandate (user's spending authorization)."""
    intent_id = f"intent_{uuid.uuid4().hex[:12]}"

    contents = {
        "intent_id": intent_id,
        "intent_description": params.get("intent_description", "General shopping"),
        "limits": {
            "max_amount_cents": params.get("max_amount_cents", 100000),
            "currency": params.get("currency", "USD"),
            "expiry": datetime.now(timezone.utc).isoformat(),
        },
        "allowed_merchants": params.get("allowed_merchants", [MERCHANT_INFO["id"]]),
    }

    mandate = {
        "type": "IntentMandate",
        "contents": contents,
        "user_authorization": params.get("user_authorization", "pending"),
        "status": "active" if params.get("user_authorization") else "pending_signature",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    _mandates[intent_id] = mandate

    return {
        "intent_mandate": mandate,
        "message": "IntentMandate created. User must sign to activate.",
    }


async def _browse_products(params: dict[str, Any]) -> dict[str, Any]:
    """Browse available products."""
    query = params.get("query", "").lower()
    category = params.get("category")

    products = list(PRODUCTS.values())
    if query:
        products = [p for p in products if query in p["name"].lower()]

    return {
        "products": products,
        "count": len(products),
        "merchant": MERCHANT_INFO,
    }


async def _create_cart(params: dict[str, Any]) -> dict[str, Any]:
    """Create a CartMandate (merchant's price commitment)."""
    intent_id = params.get("intent_id")
    items = params.get("items", [])

    # Validate intent mandate exists
    if intent_id and intent_id not in _mandates:
        raise HTTPException(status_code=404, detail="IntentMandate not found")

    # Calculate cart totals
    cart_id = f"cart_{uuid.uuid4().hex[:12]}"
    line_items = []
    subtotal = 0

    for item_req in items:
        product_id = item_req.get("product_id")
        quantity = item_req.get("quantity", 1)

        if product_id not in PRODUCTS:
            raise HTTPException(status_code=404, detail=f"Product not found: {product_id}")

        product = PRODUCTS[product_id]
        item_total = product["price_cents"] * quantity
        subtotal += item_total

        line_items.append({
            "product_id": product_id,
            "name": product["name"],
            "quantity": quantity,
            "unit_price_cents": product["price_cents"],
            "total_cents": item_total,
        })

    # Check against intent limits
    if intent_id:
        intent_mandate = _mandates[intent_id]
        max_amount = intent_mandate["contents"]["limits"]["max_amount_cents"]
        if subtotal > max_amount:
            raise HTTPException(
                status_code=400,
                detail=f"Cart total {subtotal} exceeds intent limit {max_amount}",
            )

    # Build CartMandate
    contents = {
        "id": cart_id,
        "merchant_name": MERCHANT_INFO["name"],
        "merchant_id": MERCHANT_INFO["id"],
        "intent_id": intent_id,
        "line_items": line_items,
        "payment_request": {
            "subtotal_cents": subtotal,
            "tax_cents": int(subtotal * 0.10),  # 10% tax
            "total_cents": subtotal + int(subtotal * 0.10),
            "currency": "USD",
        },
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": datetime.now(timezone.utc).isoformat(),  # +30 min in prod
    }

    # Merchant signs the cart
    merchant_authorization = _mock_sign(contents, "merchant")

    cart_mandate = {
        "type": "CartMandate",
        "contents": contents,
        "merchant_authorization": merchant_authorization,
        "content_hash": _compute_hash(contents),
        "status": "awaiting_user_approval",
    }

    _mandates[cart_id] = cart_mandate

    return {
        "cart_mandate": cart_mandate,
        "message": "CartMandate created and signed by merchant. Awaiting user approval.",
    }


async def _authorize_payment(params: dict[str, Any]) -> dict[str, Any]:
    """Process PaymentMandate (user authorizes payment)."""
    cart_id = params.get("cart_mandate_id")
    user_authorization = params.get("user_authorization", "")
    payment_method = params.get("payment_method", {})

    if cart_id not in _mandates:
        raise HTTPException(status_code=404, detail="CartMandate not found")

    cart_mandate = _mandates[cart_id]

    if cart_mandate["type"] != "CartMandate":
        raise HTTPException(status_code=400, detail="Invalid mandate type")

    # Verify user signature (mock verification)
    if not user_authorization.startswith("mock_sig_user_"):
        # Accept any signature for testing
        user_authorization = _mock_sign({"cart_id": cart_id}, "user")

    # Create PaymentMandate
    payment_mandate_id = f"pm_{uuid.uuid4().hex[:12]}"
    payment_mandate_contents = {
        "payment_mandate_id": payment_mandate_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payment_details_id": cart_id,
        "payment_details_total": cart_mandate["contents"]["payment_request"],
        "cart_mandate_hash": cart_mandate["content_hash"],
        "payment_response": {
            "method": payment_method.get("type", "card"),
            "token": payment_method.get("token", "mock_token"),
        },
        "merchant_agent": MERCHANT_INFO["id"],
    }

    payment_mandate = {
        "type": "PaymentMandate",
        "payment_mandate_contents": payment_mandate_contents,
        "user_authorization": user_authorization,
        "status": "processing",
    }

    _mandates[payment_mandate_id] = payment_mandate

    # Simulate payment processing
    receipt_id = f"rcpt_{uuid.uuid4().hex[:12]}"
    receipt = {
        "type": "PaymentReceipt",
        "receipt_id": receipt_id,
        "payment_mandate_id": payment_mandate_id,
        "cart_mandate_id": cart_id,
        "status": "SUCCESS",
        "amount": cart_mandate["contents"]["payment_request"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "transaction_id": f"txn_{uuid.uuid4().hex[:16]}",
    }

    _receipts[receipt_id] = receipt
    payment_mandate["status"] = "completed"
    payment_mandate["receipt_id"] = receipt_id

    return {
        "payment_mandate": payment_mandate,
        "receipt": receipt,
        "message": "Payment processed successfully.",
    }


async def _get_receipt(params: dict[str, Any]) -> dict[str, Any]:
    """Get payment receipt."""
    receipt_id = params.get("receipt_id")
    if not receipt_id or receipt_id not in _receipts:
        raise HTTPException(status_code=404, detail="Receipt not found")

    return {"receipt": _receipts[receipt_id]}


async def _get_mandate_status(params: dict[str, Any]) -> dict[str, Any]:
    """Get mandate status."""
    mandate_id = params.get("mandate_id")
    if not mandate_id or mandate_id not in _mandates:
        raise HTTPException(status_code=404, detail="Mandate not found")

    return {"mandate": _mandates[mandate_id]}


# ============================================================================
# Credentials Provider Agent Methods
# ============================================================================


async def _list_payment_methods(params: dict[str, Any]) -> dict[str, Any]:
    """List available payment methods in user's wallet (Credentials Provider)."""
    user_id = params.get("user_id", "default_user")
    filter_type = params.get("type")  # "card", "x402", etc.

    methods = WALLET_PAYMENT_METHODS
    if filter_type:
        methods = [m for m in methods if m["type"] == filter_type]

    return {
        "payment_methods": methods,
        "count": len(methods),
        "message": "Select a payment method to continue checkout.",
    }


async def _select_payment_method(params: dict[str, Any]) -> dict[str, Any]:
    """Select a payment method for checkout (Credentials Provider)."""
    payment_method_id = params.get("payment_method_id")
    cart_mandate_id = params.get("cart_mandate_id")

    # Find payment method
    method = next((m for m in WALLET_PAYMENT_METHODS if m["id"] == payment_method_id), None)
    if not method:
        raise HTTPException(status_code=404, detail="Payment method not found")

    # Verify cart mandate
    if cart_mandate_id and cart_mandate_id not in _mandates:
        raise HTTPException(status_code=404, detail="Cart mandate not found")

    # Store selection
    selection_id = f"sel_{uuid.uuid4().hex[:12]}"
    _payment_methods[selection_id] = {
        "id": selection_id,
        "payment_method": method,
        "cart_mandate_id": cart_mandate_id,
        "selected_at": datetime.now(timezone.utc).isoformat(),
        "status": "ready",
    }

    return {
        "selection_id": selection_id,
        "payment_method": method,
        "message": "Payment method selected. Ready to initiate payment.",
    }


# ============================================================================
# Payment Processor Agent Methods
# ============================================================================


async def _initiate_payment(params: dict[str, Any]) -> dict[str, Any]:
    """Initiate payment with OTP challenge (Payment Processor).

    This simulates the Merchant Payment Processor Agent requesting
    an OTP challenge for card payments.
    """
    selection_id = params.get("selection_id")
    cart_mandate_id = params.get("cart_mandate_id")
    user_authorization = params.get("user_authorization", "")

    # Verify selection
    selection = _payment_methods.get(selection_id)
    if not selection:
        raise HTTPException(status_code=404, detail="Payment selection not found")

    # Verify cart mandate
    cart_mandate = _mandates.get(cart_mandate_id)
    if not cart_mandate:
        raise HTTPException(status_code=404, detail="Cart mandate not found")

    payment_method = selection["payment_method"]
    payment_id = f"pay_{uuid.uuid4().hex[:12]}"

    # For card payments, require OTP challenge
    if payment_method["type"] == "card":
        otp_challenge_id = f"otp_{uuid.uuid4().hex[:12]}"
        _otp_challenges[otp_challenge_id] = {
            "payment_id": payment_id,
            "expected_otp": "123",  # Mock OTP
            "expires_at": datetime.now(timezone.utc).isoformat(),
            "attempts": 0,
            "max_attempts": 3,
        }

        # Store pending payment
        _pending_payments[payment_id] = {
            "id": payment_id,
            "selection_id": selection_id,
            "cart_mandate_id": cart_mandate_id,
            "user_authorization": user_authorization,
            "payment_method": payment_method,
            "amount": cart_mandate["contents"]["payment_request"],
            "status": "otp_required",
            "otp_challenge_id": otp_challenge_id,
        }

        return {
            "payment_id": payment_id,
            "status": "otp_required",
            "otp_challenge_id": otp_challenge_id,
            "message": "OTP challenge required. Use otp '123' for testing.",
        }

    # For x402 payments, process immediately
    elif payment_method["type"] == "x402":
        receipt_id = f"rcpt_{uuid.uuid4().hex[:12]}"
        receipt = {
            "type": "PaymentReceipt",
            "receipt_id": receipt_id,
            "payment_id": payment_id,
            "cart_mandate_id": cart_mandate_id,
            "payment_method_type": "x402",
            "status": "SUCCESS",
            "amount": cart_mandate["contents"]["payment_request"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "transaction_id": f"0x{uuid.uuid4().hex}{uuid.uuid4().hex[:32]}",
        }
        _receipts[receipt_id] = receipt

        return {
            "payment_id": payment_id,
            "status": "completed",
            "receipt": receipt,
            "message": "x402 payment completed.",
        }

    raise HTTPException(status_code=400, detail=f"Unsupported payment type: {payment_method['type']}")


async def _submit_otp(params: dict[str, Any]) -> dict[str, Any]:
    """Submit OTP to complete payment (Payment Processor)."""
    otp_challenge_id = params.get("otp_challenge_id")
    otp_code = params.get("otp")

    challenge = _otp_challenges.get(otp_challenge_id)
    if not challenge:
        raise HTTPException(status_code=404, detail="OTP challenge not found")

    # Check attempts
    challenge["attempts"] += 1
    if challenge["attempts"] > challenge["max_attempts"]:
        raise HTTPException(status_code=400, detail="Too many OTP attempts")

    # Verify OTP
    if otp_code != challenge["expected_otp"]:
        return {
            "status": "invalid",
            "attempts_remaining": challenge["max_attempts"] - challenge["attempts"],
            "message": "Invalid OTP. Try again.",
        }

    # Find pending payment
    payment = next(
        (p for p in _pending_payments.values() if p.get("otp_challenge_id") == otp_challenge_id),
        None
    )
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    # Complete payment
    payment["status"] = "completed"
    receipt_id = f"rcpt_{uuid.uuid4().hex[:12]}"
    receipt = {
        "type": "PaymentReceipt",
        "receipt_id": receipt_id,
        "payment_id": payment["id"],
        "cart_mandate_id": payment["cart_mandate_id"],
        "payment_method_type": "card",
        "status": "SUCCESS",
        "amount": payment["amount"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "transaction_id": f"txn_{uuid.uuid4().hex[:16]}",
    }
    _receipts[receipt_id] = receipt

    # Cleanup
    del _otp_challenges[otp_challenge_id]

    return {
        "status": "completed",
        "receipt": receipt,
        "message": "Payment completed successfully.",
    }


# ============================================================================
# REST Convenience Endpoints (for testing)
# ============================================================================


@router.get("/products")
async def list_products() -> dict[str, Any]:
    """List available products (REST convenience)."""
    return {"products": list(PRODUCTS.values()), "count": len(PRODUCTS)}


@router.post("/cart")
async def create_cart_rest(request: CartRequest) -> dict[str, Any]:
    """Create cart via REST (convenience wrapper)."""
    return await _create_cart({"items": request.items})


@router.post("/authorize")
async def authorize_rest(request: PaymentAuthorizationRequest) -> dict[str, Any]:
    """Authorize payment via REST (convenience wrapper)."""
    return await _authorize_payment({
        "cart_mandate_id": request.cart_mandate_id,
        "payment_method": request.payment_method,
        "user_authorization": request.user_authorization,
    })


# ============================================================================
# Test Helpers
# ============================================================================


@router.post("/test/reset")
async def reset_state() -> dict[str, str]:
    """Reset mock server state."""
    _mandates.clear()
    _sessions.clear()
    _receipts.clear()
    return {"status": "reset"}


@router.get("/test/generate-user-signature")
async def generate_test_signature(cart_id: str) -> dict[str, str]:
    """Generate a mock user signature for testing."""
    return {
        "user_authorization": _mock_sign({"cart_id": cart_id}, "user"),
        "instructions": "Use this signature in the authorize_payment call",
    }
