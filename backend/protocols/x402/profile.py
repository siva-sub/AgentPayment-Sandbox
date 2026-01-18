"""x402 Protocol profile implementation.

Based on: https://github.com/coinbase/x402

Key concepts:
- HTTP 402 Payment Required response
- PaymentPayload with EIP-712 signature
- EIP-3009 transferWithAuthorization
- Facilitator verification and settlement
"""

from typing import Any

from app.models.core import ControlCheck, ControlStatus, IntentLifecycleState
from protocols.base.profile import ProtocolProfile


class X402Profile(ProtocolProfile):
    """Protocol profile for Coinbase's x402 micropayments protocol."""

    @property
    def name(self) -> str:
        return "x402"

    @property
    def version(self) -> str:
        return "2.0.0"

    @property
    def description(self) -> str:
        return (
            "x402 - An open standard for internet-native payments using HTTP 402. "
            "Supports EVM and Solana chains with cryptographic payment authorization."
        )

    @property
    def intent_types(self) -> list[str]:
        return [
            "PaymentRequired",
            "PaymentPayload",
            "SettlementResponse",
            "VerifyResponse",
        ]

    def get_intent_schema(self, intent_type: str) -> dict[str, Any]:
        """Get JSON Schema for x402 intent types."""
        schemas = {
            "PaymentRequired": {
                "type": "object",
                "required": ["accepts", "x402Version"],
                "properties": {
                    "x402Version": {"type": "integer", "const": 1},
                    "accepts": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["scheme", "network", "maxAmountRequired"],
                            "properties": {
                                "scheme": {"type": "string"},
                                "network": {
                                    "type": "string",
                                    "description": "CAIP-2 network identifier",
                                },
                                "maxAmountRequired": {"type": "string"},
                                "resource": {"type": "string"},
                                "description": {"type": "string"},
                                "mimeType": {"type": "string"},
                                "payTo": {"type": "string"},
                                "maxTimeoutSeconds": {"type": "integer"},
                                "extra": {"type": "object"},
                            },
                        },
                    },
                    "error": {"type": "string"},
                },
            },
            "PaymentPayload": {
                "type": "object",
                "required": ["x402Version", "scheme", "network", "payload"],
                "properties": {
                    "x402Version": {"type": "integer", "const": 1},
                    "scheme": {"type": "string"},
                    "network": {"type": "string"},
                    "payload": {
                        "type": "object",
                        "description": "Scheme-specific payload (e.g., EIP-3009 signature)",
                    },
                },
            },
            "SettlementResponse": {
                "type": "object",
                "required": ["success"],
                "properties": {
                    "success": {"type": "boolean"},
                    "transaction": {"type": "string"},
                    "network": {"type": "string"},
                    "payer": {"type": "string"},
                    "error": {"type": "string"},
                    "errorCode": {"type": "string"},
                },
            },
            "VerifyResponse": {
                "type": "object",
                "required": ["isValid"],
                "properties": {
                    "isValid": {"type": "boolean"},
                    "invalidReason": {"type": "string"},
                    "payer": {"type": "string"},
                },
            },
        }
        return schemas.get(intent_type, {})

    @property
    def lifecycle_states(self) -> list[IntentLifecycleState]:
        return [
            IntentLifecycleState.DRAFT,  # Request prepared
            IntentLifecycleState.PENDING_APPROVAL,  # 402 received, awaiting payment
            IntentLifecycleState.APPROVED,  # Payment signed
            IntentLifecycleState.EXECUTING,  # Verification in progress
            IntentLifecycleState.AWAITING_SETTLEMENT,  # On-chain settlement
            IntentLifecycleState.SETTLED,  # Transaction confirmed
            IntentLifecycleState.FAILED,
        ]

    @property
    def point_of_no_return(self) -> IntentLifecycleState:
        return IntentLifecycleState.AWAITING_SETTLEMENT

    @property
    def signature_coverage(self) -> dict[str, list[str]]:
        return {
            "payer": [
                "transferWithAuthorization",  # EIP-3009 signature
                "payment_payload",
            ],
            "facilitator": ["settlement_response", "verify_response"],
        }

    def validate_intent(
        self, intent_type: str, intent_data: dict[str, Any]
    ) -> tuple[bool, list[str]]:
        """Validate x402 intent against schema."""
        errors: list[str] = []

        if intent_type == "PaymentRequired":
            if "accepts" not in intent_data:
                errors.append("Missing required field: accepts")
            elif not isinstance(intent_data["accepts"], list):
                errors.append("Field 'accepts' must be an array")
            elif len(intent_data["accepts"]) == 0:
                errors.append("Field 'accepts' must have at least one payment option")
            else:
                for i, option in enumerate(intent_data["accepts"]):
                    if "scheme" not in option:
                        errors.append(f"accepts[{i}]: Missing required field: scheme")
                    if "network" not in option:
                        errors.append(f"accepts[{i}]: Missing required field: network")

        elif intent_type == "PaymentPayload":
            required = ["x402Version", "scheme", "network", "payload"]
            for field in required:
                if field not in intent_data:
                    errors.append(f"Missing required field: {field}")

        elif intent_type == "SettlementResponse":
            if "success" not in intent_data:
                errors.append("Missing required field: success")

        return (len(errors) == 0, errors)

    async def execute_step(
        self,
        current_state: IntentLifecycleState,
        intent_type: str,
        intent_data: dict[str, Any],
        context: dict[str, Any],
    ) -> tuple[IntentLifecycleState, dict[str, Any], dict[str, Any]]:
        """Execute x402 lifecycle step."""
        step_result: dict[str, Any] = {"action": "unknown", "success": False}

        if current_state == IntentLifecycleState.DRAFT:
            # Client makes request, receives 402
            if context.get("request_sent"):
                new_state = IntentLifecycleState.PENDING_APPROVAL
                step_result = {
                    "action": "receive_402",
                    "success": True,
                    "message": "Received 402 Payment Required with payment options",
                }
                return (new_state, intent_data, step_result)

        elif current_state == IntentLifecycleState.PENDING_APPROVAL:
            # Client signs payment
            if "payload" in intent_data and context.get("signature_ready"):
                new_state = IntentLifecycleState.APPROVED
                step_result = {
                    "action": "sign_payment",
                    "success": True,
                    "message": "Payment payload signed with EIP-712",
                }
                return (new_state, intent_data, step_result)

        elif current_state == IntentLifecycleState.APPROVED:
            # Facilitator verifies
            if context.get("verification_complete"):
                if context.get("is_valid"):
                    new_state = IntentLifecycleState.EXECUTING
                    step_result = {
                        "action": "verify_payment",
                        "success": True,
                        "message": "Facilitator verified payment signature",
                    }
                else:
                    new_state = IntentLifecycleState.FAILED
                    step_result = {
                        "action": "verify_payment",
                        "success": False,
                        "message": context.get("invalid_reason", "Verification failed"),
                    }
                return (new_state, intent_data, step_result)

        elif current_state == IntentLifecycleState.EXECUTING:
            # Settlement initiated
            if context.get("settlement_started"):
                new_state = IntentLifecycleState.AWAITING_SETTLEMENT
                step_result = {
                    "action": "initiate_settlement",
                    "success": True,
                    "message": "On-chain settlement initiated",
                }
                return (new_state, intent_data, step_result)

        elif current_state == IntentLifecycleState.AWAITING_SETTLEMENT:
            if context.get("transaction_confirmed"):
                new_state = IntentLifecycleState.SETTLED
                intent_data["transaction_hash"] = context.get("transaction_hash")
                step_result = {
                    "action": "confirm_settlement",
                    "success": True,
                    "message": f"Transaction confirmed: {context.get('transaction_hash')}",
                }
                return (new_state, intent_data, step_result)
            elif context.get("transaction_failed"):
                new_state = IntentLifecycleState.FAILED
                step_result = {
                    "action": "settlement_failed",
                    "success": False,
                    "message": context.get("failure_reason", "Settlement failed"),
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
            actions.append(
                {
                    "id": "send_request",
                    "name": "Send Request",
                    "actor": "client",
                    "description": "Send HTTP request to protected resource",
                }
            )

        elif current_state == IntentLifecycleState.PENDING_APPROVAL:
            actions.extend(
                [
                    {
                        "id": "sign_payment",
                        "name": "Sign Payment",
                        "actor": "payer",
                        "description": "Sign EIP-712 payment authorization",
                    },
                    {
                        "id": "cancel",
                        "name": "Cancel",
                        "actor": "client",
                        "description": "Abandon payment request",
                    },
                ]
            )

        elif current_state == IntentLifecycleState.APPROVED:
            actions.append(
                {
                    "id": "submit_payment",
                    "name": "Submit Payment",
                    "actor": "client",
                    "description": "Submit signed payment to resource server",
                }
            )

        elif current_state == IntentLifecycleState.EXECUTING:
            actions.append(
                {
                    "id": "await_verification",
                    "name": "Await Verification",
                    "actor": "facilitator",
                    "description": "Facilitator verifies and settles payment",
                }
            )

        return actions

    def get_error_patterns(self) -> list[dict[str, Any]]:
        """Return x402 error patterns."""
        return [
            {
                "code": "INVALID_SIGNATURE",
                "description": "EIP-712 signature verification failed",
                "recovery": ["Re-sign with correct key", "Check nonce"],
            },
            {
                "code": "INSUFFICIENT_BALANCE",
                "description": "Payer has insufficient token balance",
                "recovery": ["Fund wallet", "Use different payment method"],
            },
            {
                "code": "NONCE_ALREADY_USED",
                "description": "Payment nonce has already been used",
                "recovery": ["Generate new nonce", "Check for duplicate submission"],
            },
            {
                "code": "AUTHORIZATION_EXPIRED",
                "description": "Payment authorization has expired",
                "recovery": ["Request new payment", "Increase validBefore"],
            },
            {
                "code": "UNSUPPORTED_NETWORK",
                "description": "Requested network not supported by facilitator",
                "recovery": ["Use different network", "Find compatible facilitator"],
            },
            {
                "code": "SETTLEMENT_FAILED",
                "description": "On-chain transaction reverted",
                "recovery": ["Check gas", "Retry with higher gas", "Check allowance"],
            },
        ]

    def get_security_controls(self) -> list[ControlCheck]:
        """Return x402 security controls assessment."""
        return [
            ControlCheck(
                id="x402-eip3009-nonce",
                run_id="",
                envelope_id="",
                control_name="eip3009_nonce",
                control_category="integrity",
                description="EIP-3009 nonce prevents replay attacks",
                status=ControlStatus.PRESENT,
                evidence=["references/x402/specs/x402-specification-v2.md:500-550"],
                attacks_prevented=["replay"],
                risk_if_absent="Same payment can be submitted multiple times",
            ),
            ControlCheck(
                id="x402-eip712-signature",
                run_id="",
                envelope_id="",
                control_name="eip712_signature",
                control_category="authentication",
                description="EIP-712 typed data signature for payment authorization",
                status=ControlStatus.PRESENT,
                evidence=["references/x402/specs/x402-specification-v2.md:300-400"],
                attacks_prevented=["forgery", "tampering"],
                risk_if_absent="Payments can be forged",
            ),
            ControlCheck(
                id="x402-time-bounds",
                run_id="",
                envelope_id="",
                control_name="time_bounds",
                control_category="authorization",
                description="validAfter and validBefore timestamp constraints",
                status=ControlStatus.PRESENT,
                evidence=["references/x402/specs/x402-specification-v2.md:400-450"],
                attacks_prevented=["delayed_replay"],
                risk_if_absent="Old authorizations remain valid indefinitely",
            ),
            ControlCheck(
                id="x402-simulation",
                run_id="",
                envelope_id="",
                control_name="transaction_simulation",
                control_category="verification",
                description="Facilitator simulates transaction before settlement",
                status=ControlStatus.PRESENT,
                evidence=["references/x402/specs/x402-specification-v2.md:550-600"],
                attacks_prevented=["failed_settlement"],
                risk_if_absent="Settlement may fail after authorization",
            ),
            ControlCheck(
                id="x402-facilitator-trust",
                run_id="",
                envelope_id="",
                control_name="facilitator_trust",
                control_category="trust",
                description="Resource server trusts facilitator for verification",
                status=ControlStatus.PARTIAL,
                evidence=["references/x402/specs/x402-specification-v2.md:100-150"],
                attacks_prevented=["unauthorized_settlement"],
                risk_if_absent="Malicious facilitator could falsely claim settlement",
            ),
            ControlCheck(
                id="x402-network-isolation",
                run_id="",
                envelope_id="",
                control_name="network_isolation",
                control_category="integrity",
                description="CAIP-2 network identifier prevents cross-chain replay",
                status=ControlStatus.PRESENT,
                evidence=["references/x402/specs/x402-specification-v2.md:200-250"],
                attacks_prevented=["cross_chain_replay"],
                risk_if_absent="Payment valid on one chain could be replayed on another",
            ),
        ]
