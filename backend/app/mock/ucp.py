"""UCP Mock Server - Discovery and Checkout Endpoints.

Implements a mock UCP-compliant merchant server for testing agents.
Based on: https://github.com/Upsonic/ucp-client/tree/main/ucp-server
"""

import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel, Field

router = APIRouter()

# In-memory storage
_checkouts: dict[str, dict[str, Any]] = {}
_orders: dict[str, dict[str, Any]] = {}
_idempotency_cache: dict[str, dict[str, Any]] = {}


# ============================================================================
# Models
# ============================================================================


class Product(BaseModel):
    """Product in the catalog."""

    id: str
    title: str
    description: str
    price_cents: int
    currency: str = "USD"
    available: bool = True


class LineItemRequest(BaseModel):
    """Line item in a checkout request."""

    item: dict[str, Any]
    quantity: int = 1


class CheckoutCreateRequest(BaseModel):
    """Request to create a checkout session."""

    currency: str = "USD"
    line_items: list[LineItemRequest]
    payment: dict[str, Any] | None = None
    buyer: dict[str, Any] | None = None
    fulfillment: dict[str, Any] | None = None


class CheckoutUpdateRequest(BaseModel):
    """Request to update a checkout session."""

    line_items: list[dict[str, Any]] | None = None
    payment: dict[str, Any] | None = None
    buyer: dict[str, Any] | None = None
    fulfillment: dict[str, Any] | None = None
    discounts: dict[str, Any] | None = None


class CompleteRequest(BaseModel):
    """Request to complete a checkout."""

    payment_data: dict[str, Any]
    risk_signals: dict[str, Any] | None = None


# ============================================================================
# Mock Product Catalog
# ============================================================================

PRODUCTS: dict[str, Product] = {
    "bouquet_roses": Product(
        id="bouquet_roses",
        title="Bouquet of Red Roses",
        description="A beautiful bouquet of fresh red roses",
        price_cents=3500,
    ),
    "pot_ceramic": Product(
        id="pot_ceramic",
        title="Ceramic Pot",
        description="Handcrafted ceramic flower pot",
        price_cents=1500,
    ),
    "bouquet_sunflowers": Product(
        id="bouquet_sunflowers",
        title="Sunflower Bundle",
        description="Bright and cheerful sunflower arrangement",
        price_cents=2500,
    ),
    "bouquet_tulips": Product(
        id="bouquet_tulips",
        title="Spring Tulips",
        description="Fresh colorful spring tulips",
        price_cents=3000,
    ),
    "orchid_white": Product(
        id="orchid_white",
        title="White Orchid",
        description="Elegant white orchid plant",
        price_cents=4500,
    ),
    "gardenias": Product(
        id="gardenias",
        title="Gardenias",
        description="Fragrant gardenia flowers",
        price_cents=2000,
    ),
}


# ============================================================================
# Discovery Endpoint
# ============================================================================


@router.get("/.well-known/ucp")
async def get_discovery_profile(request: Request) -> dict[str, Any]:
    """Return the UCP discovery profile.

    This endpoint tells agents what capabilities this merchant supports.
    """
    base_url = str(request.base_url).rstrip("/")

    return {
        "name": "APS Mock Flower Shop",
        "version": "2026-01-11",
        "description": "A mock UCP-compliant flower shop for testing",
        "endpoint": f"{base_url}/mock/ucp",
        "payment": {
            "handlers": [
                {"id": "mock_payment_handler", "name": "Mock Payment"},
                {"id": "stripe", "name": "Stripe"},
            ]
        },
        "capabilities": [
            {"name": "dev.ucp.shopping.checkout", "version": "2026-01-11"},
            {"name": "dev.ucp.shopping.fulfillment", "version": "2026-01-11"},
        ],
        "signing_keys": [
            {
                "kid": "mock_shop_key_001",
                "kty": "EC",
                "crv": "P-256",
                "x": "mock_x_coordinate",
                "y": "mock_y_coordinate",
                "use": "sig",
                "alg": "ES256",
            }
        ],
    }


# ============================================================================
# Products Endpoint
# ============================================================================


@router.get("/products")
async def list_products() -> dict[str, Any]:
    """List available products."""
    return {
        "products": [p.model_dump() for p in PRODUCTS.values()],
        "count": len(PRODUCTS),
    }


@router.get("/products/{product_id}")
async def get_product(product_id: str) -> dict[str, Any]:
    """Get a specific product."""
    if product_id not in PRODUCTS:
        raise HTTPException(status_code=404, detail="Product not found")
    return PRODUCTS[product_id].model_dump()


# ============================================================================
# Checkout Session Endpoints
# ============================================================================


def _calculate_totals(
    line_items: list[dict[str, Any]], discounts: dict[str, Any] | None = None
) -> list[dict[str, Any]]:
    """Calculate checkout totals."""
    subtotal = 0
    for item in line_items:
        product_id = item.get("item", {}).get("id")
        quantity = item.get("quantity", 1)
        if product_id in PRODUCTS:
            subtotal += PRODUCTS[product_id].price_cents * quantity
        else:
            # Unknown product, use provided price or 0
            price = item.get("item", {}).get("price", 0)
            subtotal += price * quantity

    discount_amount = 0
    if discounts and discounts.get("codes"):
        # Apply 10% discount for "10OFF" code
        if "10OFF" in discounts.get("codes", []):
            discount_amount = int(subtotal * 0.10)

    total = subtotal - discount_amount

    return [
        {"type": "subtotal", "display_text": "Subtotal", "amount": subtotal},
        {"type": "discount", "display_text": "Discount", "amount": -discount_amount},
        {"type": "total", "display_text": "Total", "amount": total},
    ]


@router.post("/checkout-sessions", status_code=201)
async def create_checkout(
    request: CheckoutCreateRequest,
    idempotency_key: str | None = Header(None, alias="Idempotency-Key"),
    ucp_agent: str | None = Header(None, alias="UCP-Agent"),
) -> dict[str, Any]:
    """Create a new checkout session."""
    # Check idempotency
    if idempotency_key and idempotency_key in _idempotency_cache:
        return _idempotency_cache[idempotency_key]

    checkout_id = f"chk_{uuid.uuid4().hex[:12]}"

    # Build line items with prices
    line_items = []
    for li in request.line_items:
        product_id = li.item.get("id")
        product = PRODUCTS.get(product_id)
        line_items.append(
            {
                "id": f"li_{uuid.uuid4().hex[:8]}",
                "item": {
                    "id": product_id,
                    "title": li.item.get("title") or (product.title if product else product_id),
                    "price": product.price_cents if product else 0,
                },
                "quantity": li.quantity,
            }
        )

    checkout = {
        "id": checkout_id,
        "status": "in_progress",
        "currency": request.currency,
        "line_items": line_items,
        "totals": _calculate_totals(line_items),
        "payment": request.payment or {"handlers": [], "instruments": []},
        "buyer": request.buyer,
        "fulfillment": None,
        "discounts": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "ucp": {
            "version": "2026-01-11",
            "capabilities": [{"name": "dev.ucp.shopping.checkout", "version": "2026-01-11"}],
        },
    }

    _checkouts[checkout_id] = checkout

    if idempotency_key:
        _idempotency_cache[idempotency_key] = checkout

    return checkout


@router.get("/checkout-sessions/{checkout_id}")
async def get_checkout(checkout_id: str) -> dict[str, Any]:
    """Get a checkout session by ID."""
    if checkout_id not in _checkouts:
        raise HTTPException(status_code=404, detail="Checkout session not found")
    return _checkouts[checkout_id]


@router.put("/checkout-sessions/{checkout_id}")
async def update_checkout(
    checkout_id: str,
    request: CheckoutUpdateRequest,
    idempotency_key: str | None = Header(None, alias="Idempotency-Key"),
) -> dict[str, Any]:
    """Update a checkout session."""
    if checkout_id not in _checkouts:
        raise HTTPException(status_code=404, detail="Checkout session not found")

    checkout = _checkouts[checkout_id]

    if checkout["status"] == "completed":
        raise HTTPException(status_code=400, detail="Cannot modify completed checkout")

    # Update line items
    if request.line_items:
        line_items = []
        for li in request.line_items:
            product_id = li.get("item", {}).get("id")
            product = PRODUCTS.get(product_id)
            line_items.append(
                {
                    "id": li.get("id") or f"li_{uuid.uuid4().hex[:8]}",
                    "item": {
                        "id": product_id,
                        "title": li.get("item", {}).get("title")
                        or (product.title if product else product_id),
                        "price": product.price_cents if product else 0,
                    },
                    "quantity": li.get("quantity", 1),
                }
            )
        checkout["line_items"] = line_items

    # Update buyer
    if request.buyer:
        checkout["buyer"] = request.buyer

    # Update fulfillment
    if request.fulfillment:
        checkout["fulfillment"] = _process_fulfillment(request.fulfillment, checkout)

    # Update discounts
    if request.discounts:
        checkout["discounts"] = request.discounts

    # Recalculate totals
    checkout["totals"] = _calculate_totals(
        checkout["line_items"], checkout.get("discounts")
    )

    checkout["updated_at"] = datetime.now(timezone.utc).isoformat()

    return checkout


def _process_fulfillment(
    fulfillment_req: dict[str, Any], checkout: dict[str, Any]
) -> dict[str, Any]:
    """Process fulfillment request and generate options."""
    methods = fulfillment_req.get("methods", [])
    processed_methods = []

    for method in methods:
        method_type = method.get("type", "shipping")
        processed_method = {
            "id": method.get("id") or f"method_{uuid.uuid4().hex[:8]}",
            "type": method_type,
            "line_item_ids": [li["id"] for li in checkout["line_items"]],
            "selected_destination_id": method.get("selected_destination_id"),
        }

        # Add destinations if shipping
        if method_type == "shipping":
            destinations = method.get("destinations", [])
            if not destinations:
                # Add default destination for known buyer
                if checkout.get("buyer"):
                    destinations = [
                        {
                            "id": "dest_default",
                            "street_address": "123 Main St",
                            "address_locality": "San Francisco",
                            "address_region": "CA",
                            "postal_code": "94102",
                            "address_country": "US",
                        }
                    ]
            processed_method["destinations"] = destinations

            # Generate shipping options if destination selected
            if method.get("selected_destination_id"):
                processed_method["groups"] = [
                    {
                        "id": "group_default",
                        "line_item_ids": [li["id"] for li in checkout["line_items"]],
                        "options": [
                            {
                                "id": "opt_standard",
                                "title": "Standard Shipping",
                                "price": 500,
                                "estimated_days": "5-7 business days",
                            },
                            {
                                "id": "opt_express",
                                "title": "Express Shipping",
                                "price": 1500,
                                "estimated_days": "2-3 business days",
                            },
                        ],
                        "selected_option_id": method.get("groups", [{}])[0].get(
                            "selected_option_id"
                        )
                        if method.get("groups")
                        else None,
                    }
                ]

        processed_methods.append(processed_method)

    return {"methods": processed_methods}


@router.post("/checkout-sessions/{checkout_id}/complete")
async def complete_checkout(
    checkout_id: str,
    request: CompleteRequest,
    idempotency_key: str | None = Header(None, alias="Idempotency-Key"),
) -> dict[str, Any]:
    """Complete a checkout session."""
    if checkout_id not in _checkouts:
        raise HTTPException(status_code=404, detail="Checkout session not found")

    checkout = _checkouts[checkout_id]

    if checkout["status"] == "completed":
        raise HTTPException(status_code=400, detail="Checkout already completed")

    # Validate payment
    payment_data = request.payment_data
    token = payment_data.get("credential", {}).get("token", "")

    if token == "fail_token":
        raise HTTPException(status_code=402, detail="Payment declined")

    # Create order
    order_id = f"ord_{uuid.uuid4().hex[:12]}"
    order = {
        "id": order_id,
        "checkout_id": checkout_id,
        "status": "confirmed",
        "line_items": checkout["line_items"],
        "totals": checkout["totals"],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _orders[order_id] = order

    # Update checkout
    checkout["status"] = "completed"
    checkout["order"] = {
        "id": order_id,
        "permalink_url": f"https://mock-shop.example/orders/{order_id}",
    }
    checkout["completed_at"] = datetime.now(timezone.utc).isoformat()

    return checkout


@router.post("/checkout-sessions/{checkout_id}/cancel")
async def cancel_checkout(checkout_id: str) -> dict[str, Any]:
    """Cancel a checkout session."""
    if checkout_id not in _checkouts:
        raise HTTPException(status_code=404, detail="Checkout session not found")

    checkout = _checkouts[checkout_id]

    if checkout["status"] == "completed":
        raise HTTPException(status_code=400, detail="Cannot cancel completed checkout")

    checkout["status"] = "cancelled"
    checkout["cancelled_at"] = datetime.now(timezone.utc).isoformat()

    return checkout


# ============================================================================
# Orders Endpoint
# ============================================================================


@router.get("/orders/{order_id}")
async def get_order(order_id: str) -> dict[str, Any]:
    """Get an order by ID."""
    if order_id not in _orders:
        raise HTTPException(status_code=404, detail="Order not found")
    return _orders[order_id]
