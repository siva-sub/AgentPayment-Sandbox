"""Protocols API router."""

from typing import Any

from fastapi import APIRouter, HTTPException

from protocols.acp import ACPProfile
from protocols.ap2 import AP2Profile
from protocols.ucp import UCPProfile
from protocols.x402 import X402Profile

router = APIRouter()

# Protocol registry - Major companies/standards only
PROFILES = {
    "AP2": AP2Profile(),      # Google
    "x402": X402Profile(),    # Coinbase
    "ACP": ACPProfile(),      # OpenAI/Stripe
    "UCP": UCPProfile(),      # Open standard
}




@router.get("")
async def list_protocols() -> list[dict[str, Any]]:
    """List all available protocol profiles."""
    return [profile.get_metadata() for profile in PROFILES.values()]


@router.get("/{protocol_name}")
async def get_protocol(protocol_name: str) -> dict[str, Any]:
    """Get protocol profile details."""
    profile = PROFILES.get(protocol_name.upper())
    if not profile:
        raise HTTPException(status_code=404, detail=f"Protocol '{protocol_name}' not found")
    return profile.get_metadata()


@router.get("/{protocol_name}/schema/{intent_type}")
async def get_intent_schema(protocol_name: str, intent_type: str) -> dict[str, Any]:
    """Get JSON schema for an intent type."""
    profile = PROFILES.get(protocol_name.upper())
    if not profile:
        raise HTTPException(status_code=404, detail=f"Protocol '{protocol_name}' not found")

    schema = profile.get_intent_schema(intent_type)
    if not schema:
        raise HTTPException(
            status_code=404,
            detail=f"Intent type '{intent_type}' not found in {protocol_name}",
        )
    return schema


@router.get("/{protocol_name}/controls")
async def get_security_controls(protocol_name: str) -> list[dict[str, Any]]:
    """Get security controls assessment for a protocol."""
    profile = PROFILES.get(protocol_name.upper())
    if not profile:
        raise HTTPException(status_code=404, detail=f"Protocol '{protocol_name}' not found")

    controls = profile.get_security_controls()
    return [control.model_dump() for control in controls]


@router.get("/{protocol_name}/errors")
async def get_error_patterns(protocol_name: str) -> list[dict[str, Any]]:
    """Get error patterns for a protocol."""
    profile = PROFILES.get(protocol_name.upper())
    if not profile:
        raise HTTPException(status_code=404, detail=f"Protocol '{protocol_name}' not found")

    return profile.get_error_patterns()
