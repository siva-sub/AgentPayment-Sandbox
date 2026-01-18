"""UCP (Universal Commerce Protocol) profile implementation.

Based on: https://github.com/Universal-Commerce-Protocol/ucp

Key concepts:
- Composable capabilities (Checkout, Identity, Order, Payment Token)
- Dynamic discovery via OpenAPI
- Transport agnostic
- Builds on existing standards
"""

from typing import Any

from app.models.core import ControlCheck, ControlStatus, IntentLifecycleState
from protocols.base.profile import ProtocolProfile


class UCPProfile(ProtocolProfile):
    """Protocol profile for Universal Commerce Protocol."""

    @property
    def name(self) -> str:
        return "UCP"

    @property
    def version(self) -> str:
        return "0.1.0"

    @property
    def description(self) -> str:
        return (
            "Universal Commerce Protocol - An open standard for interoperability "
            "in commerce, particularly for AI agents. Composable capabilities with "
            "dynamic discovery. Explicitly excludes disputes and chargebacks."
        )

    @property
    def intent_types(self) -> list[str]:
        return [
            "CatalogRequest",
            "OfferRequest",
            "CheckoutIntent",
            "PaymentTokenExchange",
            "OrderStatus",
        ]

    def get_intent_schema(self, intent_type: str) -> dict[str, Any]:
        """Get JSON Schema for UCP intent types."""
        schemas = {
            "CatalogRequest": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "filters": {"type": "object"},
                    "pagination": {
                        "type": "object",
                        "properties": {
                            "page": {"type": "integer"},
                            "limit": {"type": "integer"},
                        },
                    },
                },
            },
            "OfferRequest": {
                "type": "object",
                "required": ["product_id", "quantity"],
                "properties": {
                    "product_id": {"type": "string"},
                    "quantity": {"type": "integer"},
                    "context": {"type": "object"},
                },
            },
            "CheckoutIntent": {
                "type": "object",
                "required": ["offer_id", "payment_method"],
                "properties": {
                    "offer_id": {"type": "string"},
                    "payment_method": {"type": "string"},
                    "shipping_address": {"type": "object"},
                    "billing_address": {"type": "object"},
                },
            },
            "PaymentTokenExchange": {
                "type": "object",
                "required": ["token_type", "token_value"],
                "properties": {
                    "token_type": {"type": "string"},
                    "token_value": {"type": "string"},
                    "provider": {"type": "string"},
                },
            },
            "OrderStatus": {
                "type": "object",
                "required": ["order_id"],
                "properties": {
                    "order_id": {"type": "string"},
                    "status": {
                        "type": "string",
                        "enum": ["pending", "processing", "shipped", "delivered", "cancelled"],
                    },
                    "tracking": {"type": "object"},
                },
            },
        }
        return schemas.get(intent_type, {})

    @property
    def lifecycle_states(self) -> list[IntentLifecycleState]:
        return [
            IntentLifecycleState.DRAFT,  # Discovery
            IntentLifecycleState.PENDING_APPROVAL,  # Offer received
            IntentLifecycleState.APPROVED,  # Checkout initiated
            IntentLifecycleState.EXECUTING,  # Payment processing
            IntentLifecycleState.AWAITING_SETTLEMENT,  # Order placement
            IntentLifecycleState.SETTLED,  # Order confirmed
            IntentLifecycleState.FAILED,
            IntentLifecycleState.CANCELLED,
        ]

    @property
    def point_of_no_return(self) -> IntentLifecycleState:
        return IntentLifecycleState.EXECUTING

    @property
    def signature_coverage(self) -> dict[str, list[str]]:
        return {
            "agent": ["checkout_request"],
            "merchant": ["offer_response", "order_confirmation"],
            "psp": ["payment_token"],
        }

    def validate_intent(
        self, intent_type: str, intent_data: dict[str, Any]
    ) -> tuple[bool, list[str]]:
        """Validate UCP intent against schema."""
        errors: list[str] = []

        if intent_type == "OfferRequest":
            if "product_id" not in intent_data:
                errors.append("Missing required field: product_id")
            if "quantity" not in intent_data:
                errors.append("Missing required field: quantity")

        elif intent_type == "CheckoutIntent":
            if "offer_id" not in intent_data:
                errors.append("Missing required field: offer_id")
            if "payment_method" not in intent_data:
                errors.append("Missing required field: payment_method")

        elif intent_type == "PaymentTokenExchange":
            if "token_type" not in intent_data:
                errors.append("Missing required field: token_type")
            if "token_value" not in intent_data:
                errors.append("Missing required field: token_value")

        elif intent_type == "OrderStatus":
            if "order_id" not in intent_data:
                errors.append("Missing required field: order_id")

        return (len(errors) == 0, errors)

    async def execute_step(
        self,
        current_state: IntentLifecycleState,
        intent_type: str,
        intent_data: dict[str, Any],
        context: dict[str, Any],
    ) -> tuple[IntentLifecycleState, dict[str, Any], dict[str, Any]]:
        """Execute UCP lifecycle step."""
        step_result: dict[str, Any] = {"action": "unknown", "success": False}

        if current_state == IntentLifecycleState.DRAFT:
            if context.get("offer_received"):
                new_state = IntentLifecycleState.PENDING_APPROVAL
                step_result = {
                    "action": "receive_offer",
                    "success": True,
                    "message": "Offer received from merchant",
                }
                return (new_state, intent_data, step_result)

        elif current_state == IntentLifecycleState.PENDING_APPROVAL:
            if context.get("checkout_initiated"):
                new_state = IntentLifecycleState.APPROVED
                step_result = {
                    "action": "initiate_checkout",
                    "success": True,
                    "message": "Checkout initiated",
                }
                return (new_state, intent_data, step_result)

        elif current_state == IntentLifecycleState.APPROVED:
            if context.get("payment_started"):
                new_state = IntentLifecycleState.EXECUTING
                step_result = {
                    "action": "process_payment",
                    "success": True,
                    "message": "Payment processing started",
                }
                return (new_state, intent_data, step_result)

        elif current_state == IntentLifecycleState.EXECUTING:
            if context.get("payment_completed"):
                new_state = IntentLifecycleState.AWAITING_SETTLEMENT
                step_result = {
                    "action": "payment_complete",
                    "success": True,
                    "message": "Payment completed, awaiting order confirmation",
                }
                return (new_state, intent_data, step_result)

        elif current_state == IntentLifecycleState.AWAITING_SETTLEMENT:
            if context.get("order_confirmed"):
                new_state = IntentLifecycleState.SETTLED
                step_result = {
                    "action": "order_confirmed",
                    "success": True,
                    "message": "Order confirmed by merchant",
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
                    "id": "browse_catalog",
                    "name": "Browse Catalog",
                    "actor": "agent",
                    "description": "Search merchant catalog",
                },
                {
                    "id": "request_offer",
                    "name": "Request Offer",
                    "actor": "agent",
                    "description": "Request pricing offer for products",
                },
            ])

        elif current_state == IntentLifecycleState.PENDING_APPROVAL:
            actions.extend([
                {
                    "id": "accept_offer",
                    "name": "Accept Offer",
                    "actor": "agent",
                    "description": "Accept the merchant's offer and proceed to checkout",
                },
                {
                    "id": "reject_offer",
                    "name": "Reject Offer",
                    "actor": "agent",
                    "description": "Reject offer and optionally request new one",
                },
            ])

        return actions

    def get_error_patterns(self) -> list[dict[str, Any]]:
        """Return UCP error patterns."""
        return [
            {
                "code": "OFFER_EXPIRED",
                "description": "The offer has expired",
                "recovery": ["Request new offer"],
            },
            {
                "code": "PRODUCT_UNAVAILABLE",
                "description": "Product is no longer available",
                "recovery": ["Search for alternatives"],
            },
            {
                "code": "PAYMENT_TOKEN_INVALID",
                "description": "Payment token rejected by processor",
                "recovery": ["Obtain new token", "Try different payment method"],
            },
            {
                "code": "SHIPPING_UNAVAILABLE",
                "description": "Shipping not available to address",
                "recovery": ["Try different address", "Select different fulfillment"],
            },
        ]

    def get_security_controls(self) -> list[ControlCheck]:
        """Return UCP security controls assessment."""
        return [
            ControlCheck(
                id="ucp-discovery",
                run_id="",
                envelope_id="",
                control_name="dynamic_discovery",
                control_category="integrity",
                description="Merchant capabilities discovered via OpenAPI",
                status=ControlStatus.PRESENT,
                evidence=["references/ucp/README.md"],
                attacks_prevented=["capability_mismatch"],
                risk_if_absent="Agent may assume capabilities that don't exist",
            ),
            ControlCheck(
                id="ucp-token-exchange",
                run_id="",
                envelope_id="",
                control_name="payment_token_exchange",
                control_category="authentication",
                description="Payment credentials exchanged via tokens",
                status=ControlStatus.PRESENT,
                evidence=["references/ucp/spec/schemas"],
                attacks_prevented=["credential_exposure"],
                risk_if_absent="Raw payment credentials exposed to agents",
            ),
            ControlCheck(
                id="ucp-disputes",
                run_id="",
                envelope_id="",
                control_name="dispute_handling",
                control_category="operations",
                description="Protocol-level dispute resolution",
                status=ControlStatus.ABSENT,
                evidence=["references/ucp/README.md"],
                attacks_prevented=[],
                risk_if_absent="Disputes handled outside protocol - bank-grade ops needed",
            ),
            ControlCheck(
                id="ucp-chargebacks",
                run_id="",
                envelope_id="",
                control_name="chargeback_handling",
                control_category="operations",
                description="Protocol-level chargeback process",
                status=ControlStatus.ABSENT,
                evidence=["references/ucp/README.md"],
                attacks_prevented=[],
                risk_if_absent="Chargebacks handled by PSP - UCP explicitly excludes this",
            ),
            ControlCheck(
                id="ucp-offer-binding",
                run_id="",
                envelope_id="",
                control_name="offer_binding",
                control_category="integrity",
                description="Merchant bound to offered price",
                status=ControlStatus.PARTIAL,
                evidence=["references/ucp/spec/schemas"],
                attacks_prevented=["price_manipulation"],
                risk_if_absent="Price could change between offer and checkout",
            ),
        ]
