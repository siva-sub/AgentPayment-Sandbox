"""Core data models for AgentPayment Sandbox.

These models represent the fundamental entities used across all protocol profiles.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class IntentLifecycleState(str, Enum):
    """Canonical lifecycle states for intents across all protocols."""

    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    EXECUTING = "executing"
    AWAITING_SETTLEMENT = "awaiting_settlement"
    SETTLED = "settled"
    FAILED = "failed"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"


class ControlStatus(str, Enum):
    """Security control assessment status."""

    PRESENT = "present"
    PARTIAL = "partial"
    ABSENT = "absent"


class CaseType(str, Enum):
    """Operations case types mapped to ISO 20022 concepts."""

    RECALL = "recall"  # camt.056
    RETURN = "return"  # pacs.004
    COMPENSATION = "compensation"
    DISPUTE = "dispute"


class CaseStatus(str, Enum):
    """Lifecycle status for operations cases."""

    OPEN = "open"
    PENDING_RESPONSE = "pending_response"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CLOSED = "closed"
    EXPIRED = "expired"


# =============================================================================
# Core Domain Models
# =============================================================================


class SignatureRecord(BaseModel):
    """Record of a cryptographic signature."""

    signer: str = Field(..., description="Identity of the signer")
    field: str = Field(..., description="What was signed (e.g., 'cart_mandate')")
    signature: str = Field(..., description="The signature value")
    algorithm: str = Field(default="ecdsa-secp256k1", description="Signing algorithm")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class StateTransition(BaseModel):
    """Record of a state transition in the intent lifecycle."""

    from_state: IntentLifecycleState
    to_state: IntentLifecycleState
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    actor: str = Field(..., description="Who triggered the transition")
    reason: str | None = None


class IntentEnvelope(BaseModel):
    """Wrapper for any protocol intent with execution context.

    This is the universal container that wraps protocol-specific intents
    (CartMandate, PaymentPayload, CheckoutSession, etc.) with common metadata.
    """

    id: str = Field(..., description="Unique envelope ID")
    protocol: str = Field(..., description="Protocol name (e.g., 'AP2', 'x402')")
    protocol_version: str = Field(..., description="Protocol version")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Intent data
    intent_type: str = Field(
        ..., description="Type within protocol (e.g., 'CartMandate', 'PaymentPayload')"
    )
    intent_data: dict[str, Any] = Field(
        ..., description="Protocol-specific payload"
    )

    # Lifecycle
    current_state: IntentLifecycleState = Field(default=IntentLifecycleState.DRAFT)
    state_history: list[StateTransition] = Field(default_factory=list)

    # Signatures
    signatures: list[SignatureRecord] = Field(default_factory=list)

    # Execution context
    execution_context: dict[str, Any] = Field(default_factory=dict)

    # Scenario/run reference
    scenario_id: str | None = None
    run_id: str | None = None


class ExecutionStep(BaseModel):
    """Single step in intent execution.

    Captures request/response pairs, timing, and state transitions.
    """

    id: str = Field(..., description="Unique step ID")
    envelope_id: str = Field(..., description="Reference to IntentEnvelope")
    run_id: str = Field(..., description="Execution run ID")

    step_number: int = Field(..., description="Order in execution sequence")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # State transition
    from_state: IntentLifecycleState
    to_state: IntentLifecycleState

    # Actor
    actor_type: str = Field(
        ..., description="Type: 'user', 'agent', 'merchant', 'psp', 'network'"
    )
    actor_id: str = Field(..., description="Specific actor identifier")

    # Action
    action: str = Field(..., description="Action name (e.g., 'sign_cart_mandate')")
    request_payload: dict[str, Any] = Field(default_factory=dict)
    response_payload: dict[str, Any] = Field(default_factory=dict)

    # Nonces and idempotency
    nonce: str | None = None
    idempotency_key: str | None = None

    # Duration and result
    duration_ms: int = Field(default=0, description="Execution time in milliseconds")
    success: bool = Field(default=True)
    error_code: str | None = None
    error_message: str | None = None


class ControlCheck(BaseModel):
    """Security control assessment result.

    Documents whether a security control is present, partial, or absent,
    with evidence linking to code or specifications.
    """

    id: str = Field(..., description="Unique check ID")
    run_id: str = Field(..., description="Execution run ID")
    envelope_id: str = Field(..., description="Reference to IntentEnvelope")

    # Control metadata
    control_name: str = Field(
        ..., description="Control name (e.g., 'signature_verification')"
    )
    control_category: str = Field(
        ..., description="Category (e.g., 'authentication', 'authorization')"
    )
    description: str = Field(..., description="Human-readable description")

    # Assessment
    status: ControlStatus = Field(..., description="Present/Partial/Absent")
    evidence: list[str] = Field(
        default_factory=list, description="File paths or code references"
    )

    # Impact
    attacks_prevented: list[str] = Field(
        default_factory=list, description="Which attacks this control prevents"
    )
    risk_if_absent: str = Field(
        default="", description="Description of risk if control is absent"
    )


class CaseEvent(BaseModel):
    """Event in a case lifecycle."""

    timestamp: datetime = Field(default_factory=datetime.utcnow)
    event_type: str = Field(..., description="Event type")
    actor: str = Field(..., description="Who triggered the event")
    details: dict[str, Any] = Field(default_factory=dict)


class Case(BaseModel):
    """Operations case for recovery workflows.

    Maps to ISO 20022 concepts like camt.056 (recall), camt.029 (response),
    and pacs.004 (return payment).
    """

    id: str = Field(..., description="Unique case ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Reference
    envelope_id: str = Field(..., description="Reference to original intent")
    run_id: str = Field(..., description="Reference to execution run")

    # Case details
    case_type: CaseType
    status: CaseStatus = Field(default=CaseStatus.OPEN)

    # ISO 20022 mapping
    iso_message_type: str = Field(
        ..., description="ISO 20022 message type (e.g., 'camt.056')"
    )

    # Timing
    recall_window_ends: datetime | None = None
    sla_deadline: datetime | None = None

    # Parties
    initiator: str = Field(..., description="Who initiated the case")
    respondent: str = Field(..., description="Who must respond")

    # Resolution
    resolution: str | None = None
    compensation_amount: int | None = None
    compensation_currency: str | None = None

    # Audit trail
    events: list[CaseEvent] = Field(default_factory=list)


class AuditEvent(BaseModel):
    """Immutable audit log entry.

    Forms a hash chain for integrity verification.
    """

    id: str = Field(..., description="Unique event ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Context
    run_id: str
    envelope_id: str | None = None
    step_id: str | None = None
    case_id: str | None = None

    # Event
    event_type: str = Field(..., description="Type of event")
    actor: str = Field(..., description="Who performed the action")
    action: str = Field(..., description="What action was taken")

    # Data
    before_state: dict[str, Any] | None = None
    after_state: dict[str, Any] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    # Integrity
    hash: str = Field(..., description="SHA-256 of event content")
    previous_hash: str | None = Field(
        None, description="Hash of previous event for chain integrity"
    )


# =============================================================================
# Scenario and Run Models
# =============================================================================


class AttackToggle(BaseModel):
    """Configuration for an attack simulation."""

    attack_id: str = Field(..., description="Attack identifier")
    enabled: bool = Field(default=False)
    parameters: dict[str, Any] = Field(default_factory=dict)


class Scenario(BaseModel):
    """A predefined scenario for testing."""

    id: str
    name: str
    description: str
    protocol: str
    steps: list[dict[str, Any]] = Field(default_factory=list)
    expected_outcome: str = Field(default="success")


class ExecutionRun(BaseModel):
    """A single execution of a scenario or ad-hoc flow."""

    id: str
    scenario_id: str | None = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None

    # Current state
    envelopes: list[str] = Field(
        default_factory=list, description="IntentEnvelope IDs"
    )
    steps: list[str] = Field(default_factory=list, description="ExecutionStep IDs")

    # Attack configuration
    attacks: list[AttackToggle] = Field(default_factory=list)

    # Results
    success: bool | None = None
    summary: str | None = None
