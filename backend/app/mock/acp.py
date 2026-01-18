"""ACP Mock Server - OpenAI Agentic Commerce Protocol Endpoints.

Implements a mock ACP-compliant merchant server for testing.
Based on: https://github.com/agentic-commerce-protocol/agentic-commerce-protocol
Spec: spec/openapi/openapi.agentic_checkout.yaml (v2026-01-16)
"""

import uuid
from datetime import datetime, timezone, timedelta
from typing import Any

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

router = APIRouter()

# API Version from OpenAPI spec
API_VERSION = "2026-01-16"

# In-memory storage
_sessions: dict[str, dict[str, Any]] = {}
_idempotency_cache: dict[str, dict[str, Any]] = {}


# ============================================================================
# Models
# ============================================================================


class ItemRequest(BaseModel):
    """Item in checkout request."""

    id: str
    quantity: int = 1


class CreateSessionRequest(BaseModel):
    """Request to create a checkout session."""

    items: list[ItemRequest]
    fulfillment_address: dict[str, Any] | None = None


class UpdateSessionRequest(BaseModel):
    """Request to update a checkout session."""

    items: list[ItemRequest] | None = None
    fulfillment_address: dict[str, Any] | None = None
    selected_fulfillment_option_id: str | None = None


class CompleteSessionRequest(BaseModel):
    """Request to complete checkout."""

    payment_data: dict[str, Any]


# ============================================================================
# Mock Catalog
# ============================================================================

ITEMS: dict[str, dict[str, Any]] = {
    "item_123": {
        "id": "item_123",
        "title": "Premium Widget",
        "description": "A high-quality widget",
        "price_cents": 1999,
    },
    "item_456": {
        "id": "item_456",
        "title": "Deluxe Gadget",
        "description": "The best gadget money can buy",
        "price_cents": 4999,
    },
    "item_789": {
        "id": "item_789",
        "title": "Basic Tool",
        "description": "A reliable everyday tool",
        "price_cents": 999,
    },
}


# ============================================================================
# Discovery
# ============================================================================


@router.get("/.well-known/checkout")
async def get_discovery() -> dict[str, Any]:
    """Return ACP discovery profile."""
    return {
        "name": "APS Mock Store",
        "version": API_VERSION,
        "checkout_url": "/mock/acp/checkout_sessions",
        "payment_providers": [
            {"provider": "stripe", "supported_payment_methods": ["card"]},
            {"provider": "delegated", "supported_payment_methods": ["delegated_token"]},
        ],
        "api_version": API_VERSION,
    }


# ============================================================================
# Checkout Sessions
# ============================================================================


def _build_line_items(items: list[ItemRequest]) -> list[dict[str, Any]]:
    """Build line items with pricing."""
    line_items = []
    for item_req in items:
        item_data = ITEMS.get(item_req.id, {"id": item_req.id, "title": item_req.id, "price_cents": 0})
        base_amount = item_data.get("price_cents", 0) * item_req.quantity
        tax = int(base_amount * 0.10)  # 10% tax
        line_items.append({
            "id": f"li_{uuid.uuid4().hex[:8]}",
            "item": {
                "id": item_req.id,
                "title": item_data.get("title", item_req.id),
                "quantity": item_req.quantity,
            },
            "base_amount": base_amount,
            "discount": 0,
            "subtotal": base_amount,
            "tax": tax,
            "total": base_amount + tax,
        })
    return line_items


def _calculate_totals(line_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Calculate order totals."""
    items_base = sum(li["base_amount"] for li in line_items)
    subtotal = sum(li["subtotal"] for li in line_items)
    tax = sum(li["tax"] for li in line_items)
    total = sum(li["total"] for li in line_items)

    return [
        {"type": "items_base_amount", "display_text": "Item(s) total", "amount": items_base},
        {"type": "subtotal", "display_text": "Subtotal", "amount": subtotal},
        {"type": "tax", "display_text": "Tax", "amount": tax},
        {"type": "total", "display_text": "Total", "amount": total},
    ]


def _determine_status(session: dict[str, Any]) -> str:
    """Determine session status."""
    if session.get("completed"):
        return "completed"
    if session.get("cancelled"):
        return "canceled"
    if session.get("fulfillment_address") and session.get("selected_fulfillment_option_id"):
        return "ready_for_payment"
    return "not_ready_for_payment"


@router.post("/checkout_sessions", status_code=201)
async def create_session(
    request: CreateSessionRequest,
    idempotency_key: str | None = Header(None, alias="Idempotency-Key"),
    api_version: str | None = Header(API_VERSION, alias="API-Version"),
) -> dict[str, Any]:
    """Create a new checkout session."""
    if idempotency_key and idempotency_key in _idempotency_cache:
        return _idempotency_cache[idempotency_key]

    session_id = f"cs_{uuid.uuid4().hex[:16]}"
    line_items = _build_line_items(request.items)

    session = {
        "id": session_id,
        "status": "not_ready_for_payment",
        "currency": "usd",
        "line_items": line_items,
        "totals": _calculate_totals(line_items),
        "fulfillment_address": request.fulfillment_address,
        "fulfillment_options": [],
        "selected_fulfillment_option_id": None,
        "payment_provider": {"provider": "stripe", "supported_payment_methods": ["card"]},
        "messages": [],
        "links": [{"type": "terms_of_use", "url": "https://mock-store.example/terms"}],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    # Generate fulfillment options if address provided (OpenAPI spec format)
    if request.fulfillment_address:
        now = datetime.now(timezone.utc)
        session["fulfillment_options"] = [
            {
                "type": "shipping",
                "id": "fo_standard",
                "title": "Standard Shipping",
                "subtitle": "5-7 business days",
                "subtotal": 500,
                "tax": 50,
                "total": 550,
                "earliest_delivery_time": (now + timedelta(days=5)).isoformat(),
                "latest_delivery_time": (now + timedelta(days=7)).isoformat(),
            },
            {
                "type": "shipping",
                "id": "fo_express",
                "title": "Express Shipping",
                "subtitle": "2-3 business days",
                "carrier": "FedEx",
                "subtotal": 1500,
                "tax": 150,
                "total": 1650,
                "earliest_delivery_time": (now + timedelta(days=2)).isoformat(),
                "latest_delivery_time": (now + timedelta(days=3)).isoformat(),
            },
            {
                "type": "digital",
                "id": "fo_digital",
                "title": "Digital Delivery",
                "subtitle": "Instant access via email",
                "subtotal": 0,
                "tax": 0,
                "total": 0,
            },
        ]

    session["status"] = _determine_status(session)
    _sessions[session_id] = session

    if idempotency_key:
        _idempotency_cache[idempotency_key] = session

    return session


@router.get("/checkout_sessions/{session_id}")
async def get_session(session_id: str) -> dict[str, Any]:
    """Get a checkout session."""
    if session_id not in _sessions:
        raise HTTPException(status_code=404, detail="Checkout session not found")
    return _sessions[session_id]


@router.post("/checkout_sessions/{session_id}")
async def update_session(
    session_id: str,
    request: UpdateSessionRequest,
    idempotency_key: str | None = Header(None, alias="Idempotency-Key"),
) -> dict[str, Any]:
    """Update a checkout session."""
    if session_id not in _sessions:
        raise HTTPException(status_code=404, detail="Checkout session not found")

    session = _sessions[session_id]

    if session.get("completed") or session.get("cancelled"):
        raise HTTPException(status_code=400, detail="Cannot update finalized session")

    if request.items:
        session["line_items"] = _build_line_items(request.items)
        session["totals"] = _calculate_totals(session["line_items"])

    if request.fulfillment_address:
        session["fulfillment_address"] = request.fulfillment_address
        session["fulfillment_options"] = [
            {
                "id": "fo_standard",
                "type": "shipping",
                "title": "Standard Shipping",
                "price": 500,
                "estimated_delivery": "5-7 business days",
            },
            {
                "id": "fo_express",
                "type": "shipping",
                "title": "Express Shipping",
                "price": 1500,
                "estimated_delivery": "2-3 business days",
            },
        ]

    if request.selected_fulfillment_option_id:
        session["selected_fulfillment_option_id"] = request.selected_fulfillment_option_id

    session["status"] = _determine_status(session)
    session["updated_at"] = datetime.now(timezone.utc).isoformat()

    return session


@router.post("/checkout_sessions/{session_id}/complete")
async def complete_session(
    session_id: str,
    request: CompleteSessionRequest,
    idempotency_key: str | None = Header(None, alias="Idempotency-Key"),
) -> dict[str, Any]:
    """Complete a checkout session."""
    if session_id not in _sessions:
        raise HTTPException(status_code=404, detail="Checkout session not found")

    session = _sessions[session_id]

    if session["status"] != "ready_for_payment":
        raise HTTPException(
            status_code=400,
            detail=f"Session not ready for payment. Status: {session['status']}",
        )

    # Validate payment token
    token = request.payment_data.get("token", "")
    if token == "fail_token":
        raise HTTPException(status_code=402, detail="Payment declined")

    # Create order
    order_id = f"ord_{uuid.uuid4().hex[:12]}"
    session["completed"] = True
    session["status"] = "completed"
    session["order"] = {
        "id": order_id,
        "permalink_url": f"https://mock-store.example/orders/{order_id}",
    }
    session["completed_at"] = datetime.now(timezone.utc).isoformat()

    return session


@router.post("/checkout_sessions/{session_id}/cancel")
async def cancel_session(session_id: str) -> dict[str, Any]:
    """Cancel a checkout session."""
    if session_id not in _sessions:
        raise HTTPException(status_code=404, detail="Checkout session not found")

    session = _sessions[session_id]

    if session.get("completed"):
        raise HTTPException(status_code=400, detail="Cannot cancel completed session")

    session["cancelled"] = True
    session["status"] = "canceled"
    session["cancelled_at"] = datetime.now(timezone.utc).isoformat()

    return session
