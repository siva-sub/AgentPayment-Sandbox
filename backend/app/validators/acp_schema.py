"""ACP Schema Validator - Validates ACP OpenAPI-based messages.

Based on: agentic-commerce-protocol/spec/openapi/openapi.agentic_checkout.yaml
API Version: 2026-01-16
"""

from typing import Any

from pydantic import BaseModel, Field, field_validator


# ============================================================================
# Session Status Enum
# ============================================================================

VALID_STATUSES = {
    "not_ready_for_payment",
    "ready_for_payment",
    "completed",
    "canceled",
}


# ============================================================================
# LineItem Schema
# ============================================================================


class ItemSchema(BaseModel):
    """Item within a line item."""

    id: str
    title: str | None = None
    quantity: int = Field(ge=1)


class LineItemSchema(BaseModel):
    """ACP LineItem with totals breakdown."""

    id: str
    item: ItemSchema
    base_amount: int = Field(ge=0)
    discount: int = Field(ge=0, default=0)
    subtotal: int = Field(ge=0)
    tax: int = Field(ge=0)
    total: int = Field(ge=0)


# ============================================================================
# Total Schema
# ============================================================================


class TotalSchema(BaseModel):
    """ACP Total (items_base_amount, subtotal, tax, total)."""

    type: str
    display_text: str
    amount: int

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        allowed = {"items_base_amount", "subtotal", "tax", "total", "shipping", "discount"}
        if v not in allowed:
            raise ValueError(f"Total type must be one of: {allowed}")
        return v


# ============================================================================
# FulfillmentOption Schema
# ============================================================================


class FulfillmentOptionSchema(BaseModel):
    """ACP FulfillmentOption (shipping or digital)."""

    type: str
    id: str
    title: str
    subtitle: str | None = None
    carrier: str | None = None
    subtotal: int = Field(ge=0)
    tax: int = Field(ge=0, default=0)
    total: int = Field(ge=0)
    earliest_delivery_time: str | None = None
    latest_delivery_time: str | None = None

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        allowed = {"shipping", "digital", "pickup"}
        if v not in allowed:
            raise ValueError(f"FulfillmentOption type must be one of: {allowed}")
        return v


# ============================================================================
# PaymentProvider Schema
# ============================================================================


class PaymentProviderSchema(BaseModel):
    """ACP PaymentProvider."""

    provider: str
    supported_payment_methods: list[str]


# ============================================================================
# CheckoutSession Schema
# ============================================================================


class CheckoutSessionSchema(BaseModel):
    """ACP CheckoutSession full validation."""

    id: str
    status: str
    currency: str = Field(min_length=3, max_length=3)
    line_items: list[LineItemSchema]
    totals: list[TotalSchema]
    fulfillment_address: dict[str, Any] | None = None
    fulfillment_options: list[FulfillmentOptionSchema] = Field(default_factory=list)
    selected_fulfillment_option_id: str | None = None
    payment_provider: PaymentProviderSchema | None = None
    messages: list[dict[str, Any]] = Field(default_factory=list)
    links: list[dict[str, Any]] = Field(default_factory=list)
    created_at: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in VALID_STATUSES:
            raise ValueError(f"Status must be one of: {VALID_STATUSES}")
        return v

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        return v.lower()


# ============================================================================
# Discovery Schema
# ============================================================================


class DiscoverySchema(BaseModel):
    """ACP Discovery (.well-known/checkout) validation."""

    name: str
    version: str
    checkout_url: str
    payment_providers: list[PaymentProviderSchema]
    api_version: str | None = None


# ============================================================================
# Request Schemas
# ============================================================================


class CreateSessionRequestSchema(BaseModel):
    """ACP CreateCheckoutSession request."""

    items: list[dict[str, Any]] = Field(min_length=1)
    fulfillment_address: dict[str, Any] | None = None


class CompleteSessionRequestSchema(BaseModel):
    """ACP CompleteSession request."""

    payment_data: dict[str, Any]


# ============================================================================
# Validation Functions
# ============================================================================


def validate_checkout_session(data: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate CheckoutSession response against ACP OpenAPI schema."""
    errors = []
    try:
        CheckoutSessionSchema(**data)
        return True, []
    except Exception as e:
        errors.append(str(e))
        return False, errors


def validate_discovery(data: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate Discovery response against ACP OpenAPI schema."""
    errors = []
    try:
        DiscoverySchema(**data)
        return True, []
    except Exception as e:
        errors.append(str(e))
        return False, errors


def validate_line_item(data: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate a single LineItem."""
    errors = []
    try:
        LineItemSchema(**data)
        return True, []
    except Exception as e:
        errors.append(str(e))
        return False, errors


def validate_fulfillment_option(data: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate a FulfillmentOption."""
    errors = []
    try:
        FulfillmentOptionSchema(**data)
        return True, []
    except Exception as e:
        errors.append(str(e))
        return False, errors


def validate_api_version_header(header: str | None) -> tuple[bool, str | None]:
    """Validate API-Version header format."""
    if not header:
        return True, None  # Optional header
    # Expected format: YYYY-MM-DD
    import re
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", header):
        return False, f"API-Version must be YYYY-MM-DD format, got: {header}"
    return True, None
