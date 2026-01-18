"""AP2 (Agent Payments Protocol) profile implementation.

Based on: https://github.com/google-agentic-commerce/AP2

Key concepts:
- Verifiable Digital Credentials (VDCs)
- CartMandate, IntentMandate, PaymentMandate
- Human-present vs Human-not-present flows
"""

from typing import Any

from app.models.core import ControlCheck, ControlStatus, IntentLifecycleState
from protocols.base.profile import ProtocolProfile


class AP2Profile(ProtocolProfile):
    """Protocol profile for Google's Agent Payments Protocol (AP2)."""

    @property
    def name(self) -> str:
        return "AP2"

    @property
    def version(self) -> str:
        return "0.1.0"

    @property
    def description(self) -> str:
        return (
            "Agent Payments Protocol - A secure framework for AI agent-mediated "
            "transactions using Verifiable Digital Credentials (VDCs) for "
            "non-repudiation and accountability."
        )

    @property
    def intent_types(self) -> list[str]:
        return ["CartMandate", "IntentMandate", "PaymentMandate", "PaymentReceipt"]

    def get_intent_schema(self, intent_type: str) -> dict[str, Any]:
        """Get JSON Schema for AP2 intent types."""
        schemas = {
            "CartMandate": {
                "type": "object",
                "required": ["contents", "merchant_authorization"],
                "properties": {
                    "contents": {
                        "type": "object",
                        "required": ["id", "merchant_name", "payment_request"],
                        "properties": {
                            "id": {"type": "string"},
                            "merchant_name": {"type": "string"},
                            "payment_request": {"$ref": "#/$defs/PaymentRequest"},
                        },
                    },
                    "merchant_authorization": {
                        "type": "string",
                        "description": "JWT signed by merchant's private key",
                    },
                },
            },
            "PaymentMandate": {
                "type": "object",
                "required": ["payment_mandate_contents"],
                "properties": {
                    "payment_mandate_contents": {
                        "type": "object",
                        "required": [
                            "payment_mandate_id",
                            "timestamp",
                            "payment_details_id",
                            "payment_details_total",
                            "payment_response",
                            "merchant_agent",
                        ],
                        "properties": {
                            "payment_mandate_id": {"type": "string"},
                            "timestamp": {"type": "string", "format": "date-time"},
                            "payment_details_id": {"type": "string"},
                            "payment_details_total": {"$ref": "#/$defs/PaymentTotal"},
                            "payment_response": {"$ref": "#/$defs/PaymentResponse"},
                            "merchant_agent": {"type": "string"},
                        },
                    },
                    "user_authorization": {
                        "type": "string",
                        "description": "User's cryptographic signature",
                    },
                },
            },
            "IntentMandate": {
                "type": "object",
                "required": ["contents", "user_authorization"],
                "properties": {
                    "contents": {
                        "type": "object",
                        "required": ["intent_id", "intent_description", "limits"],
                        "properties": {
                            "intent_id": {"type": "string"},
                            "intent_description": {"type": "string"},
                            "limits": {"$ref": "#/$defs/IntentLimits"},
                            "allowed_merchants": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                        },
                    },
                    "user_authorization": {"type": "string"},
                },
            },
            "PaymentReceipt": {
                "type": "object",
                "required": ["receipt_id", "status", "timestamp"],
                "properties": {
                    "receipt_id": {"type": "string"},
                    "status": {
                        "type": "string",
                        "enum": ["SUCCESS", "FAILED", "PENDING"],
                    },
                    "timestamp": {"type": "string", "format": "date-time"},
                    "transaction_id": {"type": "string"},
                    "amount": {"$ref": "#/$defs/PaymentTotal"},
                },
            },
        }
        return schemas.get(intent_type, {})

    @property
    def lifecycle_states(self) -> list[IntentLifecycleState]:
        return [
            IntentLifecycleState.DRAFT,
            IntentLifecycleState.PENDING_APPROVAL,
            IntentLifecycleState.APPROVED,
            IntentLifecycleState.EXECUTING,
            IntentLifecycleState.AWAITING_SETTLEMENT,
            IntentLifecycleState.SETTLED,
            IntentLifecycleState.FAILED,
            IntentLifecycleState.CANCELLED,
            IntentLifecycleState.DISPUTED,
        ]

    @property
    def point_of_no_return(self) -> IntentLifecycleState:
        return IntentLifecycleState.AWAITING_SETTLEMENT

    @property
    def signature_coverage(self) -> dict[str, list[str]]:
        return {
            "user": [
                "payment_mandate",
                "cart_mandate_hash",
                "payment_mandate_hash",
                "intent_mandate",
            ],
            "merchant": ["cart_mandate"],
            "payment_processor": ["payment_receipt"],
            "credentials_provider": ["payment_credential"],
        }

    def validate_intent(
        self, intent_type: str, intent_data: dict[str, Any]
    ) -> tuple[bool, list[str]]:
        """Validate AP2 intent against schema."""
        errors: list[str] = []

        if intent_type == "CartMandate":
            if "contents" not in intent_data:
                errors.append("Missing required field: contents")
            else:
                contents = intent_data["contents"]
                if "id" not in contents:
                    errors.append("Missing required field: contents.id")
                if "merchant_name" not in contents:
                    errors.append("Missing required field: contents.merchant_name")
                if "payment_request" not in contents:
                    errors.append("Missing required field: contents.payment_request")

        elif intent_type == "PaymentMandate":
            if "payment_mandate_contents" not in intent_data:
                errors.append("Missing required field: payment_mandate_contents")

        elif intent_type == "IntentMandate":
            if "contents" not in intent_data:
                errors.append("Missing required field: contents")
            if "user_authorization" not in intent_data:
                errors.append("Missing required field: user_authorization")

        return (len(errors) == 0, errors)

    async def execute_step(
        self,
        current_state: IntentLifecycleState,
        intent_type: str,
        intent_data: dict[str, Any],
        context: dict[str, Any],
    ) -> tuple[IntentLifecycleState, dict[str, Any], dict[str, Any]]:
        """Execute AP2 lifecycle step."""
        step_result: dict[str, Any] = {"action": "unknown", "success": False}

        # State machine transitions
        if current_state == IntentLifecycleState.DRAFT:
            if intent_type == "CartMandate":
                # Merchant creates and signs cart
                if "merchant_authorization" in intent_data:
                    new_state = IntentLifecycleState.PENDING_APPROVAL
                    step_result = {
                        "action": "merchant_sign_cart",
                        "success": True,
                        "message": "Cart mandate signed by merchant",
                    }
                    return (new_state, intent_data, step_result)

        elif current_state == IntentLifecycleState.PENDING_APPROVAL:
            # User reviews and approves
            if context.get("user_approved"):
                new_state = IntentLifecycleState.APPROVED
                step_result = {
                    "action": "user_approve",
                    "success": True,
                    "message": "User approved the mandate",
                }
                return (new_state, intent_data, step_result)

        elif current_state == IntentLifecycleState.APPROVED:
            if intent_type == "PaymentMandate":
                # User signs payment mandate
                if "user_authorization" in intent_data:
                    new_state = IntentLifecycleState.EXECUTING
                    step_result = {
                        "action": "user_sign_payment",
                        "success": True,
                        "message": "Payment mandate signed by user",
                    }
                    return (new_state, intent_data, step_result)

        elif current_state == IntentLifecycleState.EXECUTING:
            # Payment processor executes
            if context.get("payment_initiated"):
                new_state = IntentLifecycleState.AWAITING_SETTLEMENT
                step_result = {
                    "action": "initiate_payment",
                    "success": True,
                    "message": "Payment initiated with processor",
                }
                return (new_state, intent_data, step_result)

        elif current_state == IntentLifecycleState.AWAITING_SETTLEMENT:
            if context.get("settlement_confirmed"):
                new_state = IntentLifecycleState.SETTLED
                step_result = {
                    "action": "confirm_settlement",
                    "success": True,
                    "message": "Settlement confirmed",
                }
                return (new_state, intent_data, step_result)
            elif context.get("settlement_failed"):
                new_state = IntentLifecycleState.FAILED
                step_result = {
                    "action": "settlement_failed",
                    "success": False,
                    "message": context.get("failure_reason", "Settlement failed"),
                }
                return (new_state, intent_data, step_result)

        # No transition
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
            if intent_type == "CartMandate":
                actions.append(
                    {
                        "id": "merchant_sign_cart",
                        "name": "Sign Cart Mandate",
                        "actor": "merchant",
                        "description": "Merchant signs the cart with their private key",
                    }
                )

        elif current_state == IntentLifecycleState.PENDING_APPROVAL:
            actions.extend(
                [
                    {
                        "id": "user_approve",
                        "name": "Approve",
                        "actor": "user",
                        "description": "User reviews and approves the mandate",
                    },
                    {
                        "id": "user_reject",
                        "name": "Reject",
                        "actor": "user",
                        "description": "User rejects the mandate",
                    },
                ]
            )

        elif current_state == IntentLifecycleState.APPROVED:
            if intent_type in ["CartMandate", "PaymentMandate"]:
                actions.append(
                    {
                        "id": "user_sign_payment",
                        "name": "Sign Payment Mandate",
                        "actor": "user",
                        "description": "User signs the payment authorization",
                    }
                )

        elif current_state == IntentLifecycleState.EXECUTING:
            actions.append(
                {
                    "id": "await_completion",
                    "name": "Await Completion",
                    "actor": "system",
                    "description": "Wait for payment processor response",
                }
            )

        return actions

    def get_error_patterns(self) -> list[dict[str, Any]]:
        """Return AP2 error patterns."""
        return [
            {
                "code": "INVALID_MANDATE",
                "description": "Mandate validation failed",
                "recovery": ["Correct mandate fields", "Regenerate mandate"],
            },
            {
                "code": "SIGNATURE_MISMATCH",
                "description": "Cryptographic signature verification failed",
                "recovery": ["Re-sign with correct key", "Verify key ownership"],
            },
            {
                "code": "CART_EXPIRED",
                "description": "Cart mandate has expired",
                "recovery": ["Request fresh cart from merchant"],
            },
            {
                "code": "PAYMENT_DECLINED",
                "description": "Payment processor declined the transaction",
                "recovery": ["Try different payment method", "Contact issuer"],
            },
            {
                "code": "MERCHANT_NOT_TRUSTED",
                "description": "Merchant not in user's allowlist",
                "recovery": ["Add merchant to allowlist", "Use different merchant"],
            },
            {
                "code": "LIMIT_EXCEEDED",
                "description": "Transaction exceeds configured limits",
                "recovery": ["Split transaction", "Request limit increase"],
            },
        ]

    def get_security_controls(self) -> list[ControlCheck]:
        """Return AP2 security controls assessment."""
        return [
            ControlCheck(
                id="ap2-sig-user",
                run_id="",
                envelope_id="",
                control_name="user_signature",
                control_category="authentication",
                description="User signs payment mandate with private key",
                status=ControlStatus.PRESENT,
                evidence=[
                    "references/AP2/samples/python/src/roles/shopping_agent/tools.py:222-254"
                ],
                attacks_prevented=["forgery", "repudiation"],
                risk_if_absent="Unauthorized transactions possible",
            ),
            ControlCheck(
                id="ap2-sig-merchant",
                run_id="",
                envelope_id="",
                control_name="merchant_signature",
                control_category="authentication",
                description="Merchant signs cart mandate with JWT",
                status=ControlStatus.PRESENT,
                evidence=[
                    "references/AP2/samples/python/src/roles/merchant_agent/tools.py:128-130"
                ],
                attacks_prevented=["cart_tampering", "merchant_substitution"],
                risk_if_absent="Cart contents can be modified after creation",
            ),
            ControlCheck(
                id="ap2-hash-binding",
                run_id="",
                envelope_id="",
                control_name="hash_binding",
                control_category="integrity",
                description="User authorization includes hashes of cart and payment mandates",
                status=ControlStatus.PARTIAL,
                evidence=[
                    "references/AP2/samples/python/src/roles/shopping_agent/tools.py:285-325"
                ],
                attacks_prevented=["replay", "tampering"],
                risk_if_absent="Signed authorization can be reused with different payload",
            ),
            ControlCheck(
                id="ap2-confirmation-ux",
                run_id="",
                envelope_id="",
                control_name="confirmation_ux",
                control_category="authorization",
                description="Human-present flow requires explicit user confirmation",
                status=ControlStatus.PRESENT,
                evidence=["references/AP2/docs/specification.md:200-300"],
                attacks_prevented=["confused_deputy", "prompt_injection"],
                risk_if_absent="Agent can execute payments without user awareness",
            ),
            ControlCheck(
                id="ap2-intent-limits",
                run_id="",
                envelope_id="",
                control_name="intent_limits",
                control_category="authorization",
                description="IntentMandate specifies spending limits and allowed merchants",
                status=ControlStatus.PRESENT,
                evidence=["references/AP2/docs/specification.md:400-450"],
                attacks_prevented=["budget_exhaustion", "merchant_substitution"],
                risk_if_absent="Unbounded spending possible",
            ),
            ControlCheck(
                id="ap2-idempotency",
                run_id="",
                envelope_id="",
                control_name="idempotency",
                control_category="integrity",
                description="Payment mandate ID prevents duplicate processing",
                status=ControlStatus.PARTIAL,
                evidence=[
                    "references/AP2/samples/python/src/roles/shopping_agent/tools.py:207-209"
                ],
                attacks_prevented=["replay", "double_spend"],
                risk_if_absent="Same payment can be processed multiple times",
            ),
        ]
