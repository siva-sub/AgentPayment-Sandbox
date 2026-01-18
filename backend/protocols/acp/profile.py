"""ACP (Agentic Commerce Protocol) profile implementation.

Based on: https://github.com/agentic-commerce-protocol/agentic-commerce-protocol

Key concepts:
- CheckoutSession as central object
- Status-driven lifecycle
- 3DS authentication support
- Intent trace for cancellation analytics
"""

from typing import Any

from app.models.core import ControlCheck, ControlStatus, IntentLifecycleState
from protocols.base.profile import ProtocolProfile


class ACPProfile(ProtocolProfile):
    """Protocol profile for OpenAI/Stripe Agentic Commerce Protocol."""

    @property
    def name(self) -> str:
        return "ACP"

    @property
    def version(self) -> str:
        return "draft"

    @property
    def description(self) -> str:
        return (
            "Agentic Commerce Protocol - An open standard for connecting buyers, "
            "their AI agents, and businesses. Maintained by OpenAI and Stripe."
        )

    @property
    def intent_types(self) -> list[str]:
        return ["CheckoutSession", "CheckoutUpdate", "CheckoutComplete"]

    def get_intent_schema(self, intent_type: str) -> dict[str, Any]:
        """Get JSON Schema for ACP intent types."""
        schemas = {
            "CheckoutSession": {
                "type": "object",
                "required": ["id", "status", "items"],
                "properties": {
                    "id": {"type": "string"},
                    "status": {
                        "type": "string",
                        "enum": [
                            "not_ready_for_payment",
                            "ready_for_payment",
                            "authentication_required",
                            "completed",
                            "cancelled",
                        ],
                    },
                    "items": {
                        "type": "array",
                        "items": {"$ref": "#/$defs/LineItem"},
                    },
                    "buyer": {"$ref": "#/$defs/Buyer"},
                    "fulfillment_details": {"$ref": "#/$defs/FulfillmentDetails"},
                    "payment_data": {"$ref": "#/$defs/PaymentData"},
                    "affiliate_attribution": {"$ref": "#/$defs/AffiliateAttribution"},
                    "authentication_metadata": {
                        "type": "object",
                        "description": "3DS authentication details when status is authentication_required",
                    },
                },
            },
            "CheckoutUpdate": {
                "type": "object",
                "properties": {
                    "items": {"type": "array"},
                    "fulfillment_details": {"type": "object"},
                    "payment_data": {"type": "object"},
                },
            },
            "CheckoutComplete": {
                "type": "object",
                "required": ["session_id"],
                "properties": {
                    "session_id": {"type": "string"},
                    "payment_confirmation": {"type": "object"},
                },
            },
        }
        return schemas.get(intent_type, {})

    @property
    def lifecycle_states(self) -> list[IntentLifecycleState]:
        return [
            IntentLifecycleState.DRAFT,  # not_ready_for_payment
            IntentLifecycleState.PENDING_APPROVAL,  # ready_for_payment
            IntentLifecycleState.APPROVED,  # authentication handled
            IntentLifecycleState.EXECUTING,  # payment processing
            IntentLifecycleState.AWAITING_SETTLEMENT,  # confirmation pending
            IntentLifecycleState.SETTLED,  # completed
            IntentLifecycleState.CANCELLED,
            IntentLifecycleState.FAILED,
        ]

    @property
    def point_of_no_return(self) -> IntentLifecycleState:
        return IntentLifecycleState.EXECUTING

    @property
    def signature_coverage(self) -> dict[str, list[str]]:
        return {
            "agent": ["checkout_request"],
            "merchant": ["session_response", "fulfillment_confirmation"],
            "psp": ["payment_confirmation", "authentication_result"],
        }

    def validate_intent(
        self, intent_type: str, intent_data: dict[str, Any]
    ) -> tuple[bool, list[str]]:
        """Validate ACP intent against schema."""
        errors: list[str] = []

        if intent_type == "CheckoutSession":
            if "id" not in intent_data:
                errors.append("Missing required field: id")
            if "status" not in intent_data:
                errors.append("Missing required field: status")
            if "items" not in intent_data:
                errors.append("Missing required field: items")
            elif not isinstance(intent_data["items"], list):
                errors.append("Field 'items' must be an array")

        elif intent_type == "CheckoutComplete":
            if "session_id" not in intent_data:
                errors.append("Missing required field: session_id")

        return (len(errors) == 0, errors)

    async def execute_step(
        self,
        current_state: IntentLifecycleState,
        intent_type: str,
        intent_data: dict[str, Any],
        context: dict[str, Any],
    ) -> tuple[IntentLifecycleState, dict[str, Any], dict[str, Any]]:
        """Execute ACP lifecycle step."""
        step_result: dict[str, Any] = {"action": "unknown", "success": False}

        if current_state == IntentLifecycleState.DRAFT:
            if context.get("items_added") and context.get("payment_data_set"):
                intent_data["status"] = "ready_for_payment"
                new_state = IntentLifecycleState.PENDING_APPROVAL
                step_result = {
                    "action": "prepare_checkout",
                    "success": True,
                    "message": "Checkout ready for payment",
                }
                return (new_state, intent_data, step_result)

        elif current_state == IntentLifecycleState.PENDING_APPROVAL:
            if context.get("requires_authentication"):
                intent_data["status"] = "authentication_required"
                step_result = {
                    "action": "request_3ds",
                    "success": True,
                    "message": "3DS authentication required",
                }
                return (current_state, intent_data, step_result)
            elif context.get("payment_authorized"):
                new_state = IntentLifecycleState.APPROVED
                step_result = {
                    "action": "authorize_payment",
                    "success": True,
                    "message": "Payment authorized",
                }
                return (new_state, intent_data, step_result)

        elif current_state == IntentLifecycleState.APPROVED:
            if context.get("complete_checkout"):
                new_state = IntentLifecycleState.EXECUTING
                step_result = {
                    "action": "complete_checkout",
                    "success": True,
                    "message": "Processing checkout completion",
                }
                return (new_state, intent_data, step_result)

        elif current_state == IntentLifecycleState.EXECUTING:
            if context.get("payment_captured"):
                new_state = IntentLifecycleState.AWAITING_SETTLEMENT
                step_result = {
                    "action": "capture_payment",
                    "success": True,
                    "message": "Payment captured, awaiting settlement",
                }
                return (new_state, intent_data, step_result)

        elif current_state == IntentLifecycleState.AWAITING_SETTLEMENT:
            if context.get("order_confirmed"):
                intent_data["status"] = "completed"
                new_state = IntentLifecycleState.SETTLED
                step_result = {
                    "action": "confirm_order",
                    "success": True,
                    "message": "Order confirmed and settled",
                }
                return (new_state, intent_data, step_result)

        step_result = {
            "action": "no_transition",
            "success": True,
            "message": f"No transition from {current_state.value}",
        }
        return (current_state, intent_data, step_result)

    def get_available_actions(
        self,
        current_state: IntentLifecycleState,
        intent_type: str,
        context: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Get available actions from current state."""
        actions: list[dict[str, Any]] = []

        if current_state == IntentLifecycleState.DRAFT:
            actions.extend([
                {
                    "id": "add_items",
                    "name": "Add Items",
                    "actor": "agent",
                    "description": "Add line items to checkout",
                },
                {
                    "id": "set_fulfillment",
                    "name": "Set Fulfillment",
                    "actor": "agent",
                    "description": "Configure shipping/delivery details",
                },
                {
                    "id": "set_payment",
                    "name": "Set Payment Data",
                    "actor": "agent",
                    "description": "Configure payment method",
                },
            ])

        elif current_state == IntentLifecycleState.PENDING_APPROVAL:
            actions.extend([
                {
                    "id": "complete",
                    "name": "Complete Checkout",
                    "actor": "agent",
                    "description": "Finalize and submit checkout",
                },
                {
                    "id": "cancel",
                    "name": "Cancel",
                    "actor": "agent",
                    "description": "Cancel checkout with intent_trace",
                },
            ])

        return actions

    def get_error_patterns(self) -> list[dict[str, Any]]:
        """Return ACP error patterns."""
        return [
            {
                "code": "INVALID_ITEMS",
                "description": "Line items validation failed",
                "recovery": ["Check item availability", "Verify prices"],
            },
            {
                "code": "PAYMENT_FAILED",
                "description": "Payment processing failed",
                "recovery": ["Try different payment method", "Contact issuer"],
            },
            {
                "code": "AUTHENTICATION_FAILED",
                "description": "3DS authentication failed",
                "recovery": ["Retry authentication", "Use different card"],
            },
            {
                "code": "FULFILLMENT_UNAVAILABLE",
                "description": "Shipping/delivery not available",
                "recovery": ["Select different fulfillment option"],
            },
            {
                "code": "SESSION_EXPIRED",
                "description": "Checkout session has expired",
                "recovery": ["Create new session"],
            },
        ]

    def get_security_controls(self) -> list[ControlCheck]:
        """Return ACP security controls assessment."""
        return [
            ControlCheck(
                id="acp-session-auth",
                run_id="",
                envelope_id="",
                control_name="session_authentication",
                control_category="authentication",
                description="Checkout session tied to authenticated agent",
                status=ControlStatus.PRESENT,
                evidence=["references/agentic-commerce-protocol/spec/openapi/openapi.agentic_checkout.yaml"],
                attacks_prevented=["session_hijacking"],
                risk_if_absent="Session can be manipulated by unauthorized parties",
            ),
            ControlCheck(
                id="acp-3ds",
                run_id="",
                envelope_id="",
                control_name="3ds_authentication",
                control_category="authentication",
                description="SCA via 3DS for card payments",
                status=ControlStatus.PRESENT,
                evidence=["references/agentic-commerce-protocol/examples/examples.agentic_checkout.json"],
                attacks_prevented=["card_fraud", "unauthorized_payment"],
                risk_if_absent="Higher fraud risk on card transactions",
            ),
            ControlCheck(
                id="acp-intent-trace",
                run_id="",
                envelope_id="",
                control_name="intent_trace",
                control_category="audit",
                description="Cancellation includes reason_code and trace_summary",
                status=ControlStatus.PRESENT,
                evidence=["references/agentic-commerce-protocol/examples/examples.agentic_checkout.json"],
                attacks_prevented=["analytics_gap"],
                risk_if_absent="No visibility into why checkouts are abandoned",
            ),
            ControlCheck(
                id="acp-idempotency",
                run_id="",
                envelope_id="",
                control_name="idempotency",
                control_category="integrity",
                description="Idempotency-Key header for safe retries",
                status=ControlStatus.PRESENT,
                evidence=["references/agentic-commerce-protocol/spec/openapi/openapi.agentic_checkout.yaml"],
                attacks_prevented=["duplicate_submission"],
                risk_if_absent="Retry could create duplicate orders",
            ),
            ControlCheck(
                id="acp-error-jsonpath",
                run_id="",
                envelope_id="",
                control_name="structured_errors",
                control_category="integrity",
                description="Error responses include JSONPath to problematic fields",
                status=ControlStatus.PRESENT,
                evidence=["references/agentic-commerce-protocol/spec/openapi/openapi.agentic_checkout.yaml"],
                attacks_prevented=["debugging_gap"],
                risk_if_absent="Difficult to identify validation failures",
            ),
        ]
