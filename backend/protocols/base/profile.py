"""Protocol profile plugin interface.

All protocol profiles must implement this abstract base class.
"""

from abc import ABC, abstractmethod
from typing import Any

from app.models.core import ControlCheck, IntentLifecycleState


class ProtocolProfile(ABC):
    """Abstract base class for protocol profiles.

    Each protocol (AP2, UCP, x402, ACP, A2A, IntentKit) implements this
    interface to provide:
    - Schema definitions
    - Lifecycle state machine
    - Execution logic
    - Security control detection
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Protocol name (e.g., 'AP2', 'UCP', 'x402')."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Protocol version being implemented."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of the protocol."""
        pass

    @property
    @abstractmethod
    def intent_types(self) -> list[str]:
        """List of intent types supported by this protocol.

        Examples:
        - AP2: ['CartMandate', 'IntentMandate', 'PaymentMandate']
        - x402: ['PaymentPayload', 'PaymentRequired']
        - ACP: ['CheckoutSession']
        """
        pass

    @abstractmethod
    def get_intent_schema(self, intent_type: str) -> dict[str, Any]:
        """Get JSON Schema for a specific intent type.

        Args:
            intent_type: Type of intent (e.g., 'CartMandate')

        Returns:
            JSON Schema dictionary
        """
        pass

    @property
    @abstractmethod
    def lifecycle_states(self) -> list[IntentLifecycleState]:
        """Ordered list of lifecycle states for this protocol.

        States should be in typical progression order.
        """
        pass

    @property
    @abstractmethod
    def point_of_no_return(self) -> IntentLifecycleState:
        """The state after which execution is irreversible.

        For most protocols this is AWAITING_SETTLEMENT or SETTLED.
        """
        pass

    @property
    @abstractmethod
    def signature_coverage(self) -> dict[str, list[str]]:
        """Map of what is signed by whom.

        Returns:
            Dictionary mapping signer role to list of signed elements.

        Example:
            {
                "user": ["payment_mandate", "cart_mandate_hash"],
                "merchant": ["cart_mandate"],
                "facilitator": ["settlement_response"]
            }
        """
        pass

    @abstractmethod
    def validate_intent(
        self, intent_type: str, intent_data: dict[str, Any]
    ) -> tuple[bool, list[str]]:
        """Validate an intent against its schema.

        Args:
            intent_type: Type of intent being validated
            intent_data: The intent payload to validate

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        pass

    @abstractmethod
    async def execute_step(
        self,
        current_state: IntentLifecycleState,
        intent_type: str,
        intent_data: dict[str, Any],
        context: dict[str, Any],
    ) -> tuple[IntentLifecycleState, dict[str, Any], dict[str, Any]]:
        """Execute a single step in the lifecycle.

        Args:
            current_state: Current lifecycle state
            intent_type: Type of intent
            intent_data: The intent payload
            context: Execution context (actors, config, etc.)

        Returns:
            Tuple of (new_state, updated_intent_data, step_result)
        """
        pass

    @abstractmethod
    def get_available_actions(
        self,
        current_state: IntentLifecycleState,
        intent_type: str,
        context: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Get available actions from current state.

        Args:
            current_state: Current lifecycle state
            intent_type: Type of intent
            context: Execution context

        Returns:
            List of available actions with metadata
        """
        pass

    @abstractmethod
    def get_error_patterns(self) -> list[dict[str, Any]]:
        """Return recognized error/rejection patterns.

        Returns:
            List of error pattern definitions with:
            - code: Error code
            - description: Human-readable description
            - recovery: Possible recovery actions
        """
        pass

    @abstractmethod
    def get_security_controls(self) -> list[ControlCheck]:
        """Return list of security controls with assessment.

        Returns:
            List of ControlCheck objects documenting each control
        """
        pass

    def get_metadata(self) -> dict[str, Any]:
        """Get protocol metadata for display.

        Returns:
            Dictionary with protocol information for UI
        """
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "intent_types": self.intent_types,
            "lifecycle_states": [s.value for s in self.lifecycle_states],
            "point_of_no_return": self.point_of_no_return.value,
            "signature_coverage": self.signature_coverage,
        }
