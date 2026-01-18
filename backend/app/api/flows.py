"""Flows API router - Flow Studio endpoints."""

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models.core import IntentEnvelope, IntentLifecycleState

router = APIRouter()

# In-memory store for envelopes
ENVELOPES: dict[str, IntentEnvelope] = {}


class CreateEnvelopeRequest(BaseModel):
    """Request to create a new intent envelope."""

    protocol: str
    intent_type: str
    intent_data: dict[str, Any]


class ValidateIntentRequest(BaseModel):
    """Request to validate an intent."""

    protocol: str
    intent_type: str
    intent_data: dict[str, Any]


@router.post("/envelopes")
async def create_envelope(request: CreateEnvelopeRequest) -> dict[str, Any]:
    """Create a new intent envelope."""
    from app.api.protocols import PROFILES

    profile = PROFILES.get(request.protocol.upper())
    if not profile:
        raise HTTPException(
            status_code=400, detail=f"Unknown protocol: {request.protocol}"
        )

    # Validate intent
    is_valid, errors = profile.validate_intent(request.intent_type, request.intent_data)
    if not is_valid:
        raise HTTPException(status_code=400, detail={"errors": errors})

    envelope = IntentEnvelope(
        id=str(uuid.uuid4()),
        protocol=profile.name,
        protocol_version=profile.version,
        intent_type=request.intent_type,
        intent_data=request.intent_data,
    )
    ENVELOPES[envelope.id] = envelope

    return envelope.model_dump()


@router.get("/envelopes")
async def list_envelopes() -> list[dict[str, Any]]:
    """List all intent envelopes."""
    return [
        {
            "id": e.id,
            "protocol": e.protocol,
            "intent_type": e.intent_type,
            "current_state": e.current_state.value,
            "created_at": e.created_at.isoformat(),
        }
        for e in ENVELOPES.values()
    ]


@router.get("/envelopes/{envelope_id}")
async def get_envelope(envelope_id: str) -> dict[str, Any]:
    """Get envelope details."""
    envelope = ENVELOPES.get(envelope_id)
    if not envelope:
        raise HTTPException(status_code=404, detail=f"Envelope '{envelope_id}' not found")
    return envelope.model_dump()


@router.get("/envelopes/{envelope_id}/actions")
async def get_available_actions(envelope_id: str) -> list[dict[str, Any]]:
    """Get available actions for an envelope."""
    from app.api.protocols import PROFILES

    envelope = ENVELOPES.get(envelope_id)
    if not envelope:
        raise HTTPException(status_code=404, detail=f"Envelope '{envelope_id}' not found")

    profile = PROFILES.get(envelope.protocol)
    if not profile:
        raise HTTPException(status_code=500, detail="Protocol profile not found")

    return profile.get_available_actions(
        envelope.current_state,
        envelope.intent_type,
        envelope.execution_context,
    )


@router.post("/validate")
async def validate_intent(request: ValidateIntentRequest) -> dict[str, Any]:
    """Validate an intent without creating an envelope."""
    from app.api.protocols import PROFILES

    profile = PROFILES.get(request.protocol.upper())
    if not profile:
        raise HTTPException(
            status_code=400, detail=f"Unknown protocol: {request.protocol}"
        )

    is_valid, errors = profile.validate_intent(request.intent_type, request.intent_data)

    return {
        "is_valid": is_valid,
        "errors": errors,
        "protocol": profile.name,
        "intent_type": request.intent_type,
    }
