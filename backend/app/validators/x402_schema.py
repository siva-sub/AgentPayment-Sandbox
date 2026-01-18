"""x402 Schema Validator - Validates x402 v2 protocol messages.

Based on: x402-specification-v2.md
"""

import re
from typing import Any

from pydantic import BaseModel, Field, field_validator


# ============================================================================
# CAIP-2 Network Validation
# ============================================================================

CAIP2_PATTERN = re.compile(r"^[a-z0-9]+:[a-zA-Z0-9]+$")

SUPPORTED_NETWORKS = {
    "eip155:84532",  # Base Sepolia
    "eip155:8453",   # Base Mainnet
    "eip155:43113",  # Avalanche Fuji
    "eip155:43114",  # Avalanche Mainnet
    "solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp",  # Solana Mainnet
    "solana:EtWTRABZaYq6iMfeYKouRu166VU2xqa1",  # Solana Devnet
}


def validate_caip2_network(network: str) -> tuple[bool, str | None]:
    """Validate CAIP-2 network identifier format."""
    if not CAIP2_PATTERN.match(network):
        return False, f"Invalid CAIP-2 format: {network}"
    return True, None


# ============================================================================
# PaymentRequirements Schema
# ============================================================================


class PaymentRequirementsSchema(BaseModel):
    """x402 v2 PaymentRequirements validation."""

    scheme: str
    network: str
    amount: str
    asset: str
    payTo: str
    maxTimeoutSeconds: int = Field(ge=1, le=3600)
    extra: dict[str, Any] | None = None

    @field_validator("scheme")
    @classmethod
    def validate_scheme(cls, v: str) -> str:
        allowed = {"exact", "deferred"}
        if v not in allowed:
            raise ValueError(f"Scheme must be one of: {allowed}")
        return v

    @field_validator("network")
    @classmethod
    def validate_network(cls, v: str) -> str:
        valid, error = validate_caip2_network(v)
        if not valid:
            raise ValueError(error)
        return v

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: str) -> str:
        try:
            int(v)
        except ValueError:
            raise ValueError("Amount must be a numeric string")
        return v

    @field_validator("asset")
    @classmethod
    def validate_asset(cls, v: str) -> str:
        # EVM address or currency code
        if v.startswith("0x"):
            if len(v) != 42:
                raise ValueError("EVM asset address must be 42 characters")
        elif len(v) != 3:
            raise ValueError("Currency code must be 3 characters (ISO 4217)")
        return v

    @field_validator("payTo")
    @classmethod
    def validate_pay_to(cls, v: str) -> str:
        if v.startswith("0x"):
            if len(v) != 42:
                raise ValueError("EVM payTo address must be 42 characters")
        return v


# ============================================================================
# ResourceInfo Schema
# ============================================================================


class ResourceInfoSchema(BaseModel):
    """x402 v2 ResourceInfo validation."""

    url: str
    description: str | None = None
    mimeType: str | None = None

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v


# ============================================================================
# PaymentRequired Schema
# ============================================================================


class PaymentRequiredSchema(BaseModel):
    """x402 v2 PaymentRequired response validation."""

    x402Version: int = Field(eq=2)
    error: str | None = None
    resource: ResourceInfoSchema
    accepts: list[PaymentRequirementsSchema] = Field(min_length=1)
    extensions: dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# Authorization Schema (EIP-3009)
# ============================================================================


class AuthorizationSchema(BaseModel):
    """EIP-3009 authorization parameters."""

    from_: str = Field(alias="from")
    to: str
    value: str
    validAfter: str
    validBefore: str
    nonce: str

    @field_validator("from_", "to")
    @classmethod
    def validate_address(cls, v: str) -> str:
        if not v.startswith("0x") or len(v) != 42:
            raise ValueError("Must be valid EVM address (0x + 40 hex)")
        return v

    @field_validator("nonce")
    @classmethod
    def validate_nonce(cls, v: str) -> str:
        if not v.startswith("0x") or len(v) != 66:
            raise ValueError("Nonce must be 32-byte hex (0x + 64 chars)")
        return v


# ============================================================================
# PaymentPayload Schema
# ============================================================================


class PayloadSchema(BaseModel):
    """x402 v2 Payload (scheme-specific data)."""

    signature: str
    authorization: AuthorizationSchema

    @field_validator("signature")
    @classmethod
    def validate_signature(cls, v: str) -> str:
        if not v.startswith("0x"):
            raise ValueError("Signature must be hex string starting with 0x")
        return v


class PaymentPayloadSchema(BaseModel):
    """x402 v2 PaymentPayload validation."""

    x402Version: int = Field(eq=2)
    resource: ResourceInfoSchema | None = None
    accepted: PaymentRequirementsSchema
    payload: PayloadSchema
    extensions: dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# Validation Functions
# ============================================================================


def validate_payment_required(data: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate PaymentRequired response against x402 v2 schema."""
    errors = []
    try:
        PaymentRequiredSchema(**data)
        return True, []
    except Exception as e:
        errors.append(str(e))
        return False, errors


def validate_payment_payload(data: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate PaymentPayload against x402 v2 schema."""
    errors = []
    try:
        PaymentPayloadSchema(**data)
        return True, []
    except Exception as e:
        errors.append(str(e))
        return False, errors


def validate_payment_requirements(data: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate PaymentRequirements against x402 v2 schema."""
    errors = []
    try:
        PaymentRequirementsSchema(**data)
        return True, []
    except Exception as e:
        errors.append(str(e))
        return False, errors
