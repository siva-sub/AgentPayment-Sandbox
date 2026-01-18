"""Security Analysis Module - Signature Verification and Security Scoring.

Phase 6: Provides cryptographic signature verification and security analysis
for payment protocols.
"""

import re
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


# ============================================================================
# Security Score Configuration
# ============================================================================

SECURITY_CHECKS = {
    "signature_present": {
        "name": "Signature Present",
        "description": "Payment includes a cryptographic signature",
        "weight": 20,
        "severity": "critical",
    },
    "signature_format": {
        "name": "Valid Signature Format",
        "description": "Signature follows expected format (hex, length)",
        "weight": 15,
        "severity": "high",
    },
    "nonce_unique": {
        "name": "Unique Nonce",
        "description": "Nonce has not been used before (replay protection)",
        "weight": 25,
        "severity": "critical",
    },
    "time_window": {
        "name": "Valid Time Window",
        "description": "Authorization is within valid time bounds",
        "weight": 15,
        "severity": "high",
    },
    "amount_match": {
        "name": "Amount Matches",
        "description": "Payment amount meets or exceeds required amount",
        "weight": 10,
        "severity": "medium",
    },
    "recipient_match": {
        "name": "Recipient Matches",
        "description": "Payment recipient matches expected address",
        "weight": 15,
        "severity": "critical",
    },
}


# ============================================================================
# Models
# ============================================================================


class SecurityCheck(BaseModel):
    """Result of a single security check."""

    check_id: str
    name: str
    passed: bool
    severity: str  # critical, high, medium, low
    message: str
    recommendation: str | None = None


class SecurityAnalysis(BaseModel):
    """Complete security analysis result."""

    score: int = Field(ge=0, le=100)
    grade: str  # A, B, C, D, F
    checks: list[SecurityCheck]
    summary: str
    timestamp: str


# ============================================================================
# Signature Verification
# ============================================================================


def verify_evm_signature(signature: str) -> tuple[bool, str]:
    """Verify EVM signature format.

    Returns (is_valid, message)
    """
    # Check hex format
    if not signature.startswith("0x"):
        return False, "Signature must start with 0x"

    # Check length (65 bytes = 130 hex chars + 0x = 132)
    if len(signature) != 132:
        return False, f"Invalid signature length: expected 132, got {len(signature)}"

    # Check valid hex
    try:
        int(signature, 16)
    except ValueError:
        return False, "Signature contains invalid hex characters"

    return True, "Valid EVM signature format"


def verify_eip712_signature(
    signature: str,
    authorization: dict[str, Any],
) -> tuple[bool, str]:
    """Verify EIP-712 signature (mock verification for sandbox).

    In production, this would:
    1. Reconstruct the EIP-712 typed data hash
    2. Use ecrecover to get the signer address
    3. Compare with the claimed 'from' address

    For sandbox, we do format validation only.
    """
    # Format check
    valid, msg = verify_evm_signature(signature)
    if not valid:
        return False, msg

    # Check authorization has required fields
    required = ["from", "to", "value", "validAfter", "validBefore", "nonce"]
    for field in required:
        if field not in authorization:
            return False, f"Missing authorization field: {field}"

    # Validate addresses
    for addr_field in ["from", "to"]:
        addr = authorization.get(addr_field, "")
        if not addr.startswith("0x") or len(addr) != 42:
            return False, f"Invalid address format for {addr_field}"

    return True, "EIP-712 signature format valid"


def verify_nonce(nonce: str, used_nonces: set[str]) -> tuple[bool, str]:
    """Check if nonce has been used (replay protection)."""
    if nonce in used_nonces:
        return False, "Nonce already used - potential replay attack"

    # Check nonce format (32 bytes = 64 hex + 0x = 66)
    if not nonce.startswith("0x") or len(nonce) != 66:
        return False, f"Invalid nonce format: expected 66 chars, got {len(nonce)}"

    return True, "Nonce is unique and valid"


def verify_time_window(valid_after: str, valid_before: str) -> tuple[bool, str]:
    """Verify authorization is within valid time window."""
    try:
        now = int(datetime.now(timezone.utc).timestamp())
        after = int(valid_after)
        before = int(valid_before)

        if now < after:
            return False, f"Authorization not yet valid (starts in {after - now}s)"

        if now > before:
            return False, f"Authorization expired ({now - before}s ago)"

        return True, f"Within valid time window ({before - now}s remaining)"

    except ValueError as e:
        return False, f"Invalid timestamp format: {e}"


# ============================================================================
# Security Scoring
# ============================================================================


def calculate_security_score(checks: list[SecurityCheck]) -> int:
    """Calculate overall security score from checks."""
    total_weight = sum(SECURITY_CHECKS[c.check_id]["weight"] for c in checks if c.check_id in SECURITY_CHECKS)
    earned_weight = sum(
        SECURITY_CHECKS[c.check_id]["weight"]
        for c in checks
        if c.check_id in SECURITY_CHECKS and c.passed
    )

    if total_weight == 0:
        return 100

    return int((earned_weight / total_weight) * 100)


def get_grade(score: int) -> str:
    """Convert score to letter grade."""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


def generate_summary(checks: list[SecurityCheck], score: int) -> str:
    """Generate human-readable summary."""
    critical_failures = [c for c in checks if not c.passed and c.severity == "critical"]
    high_failures = [c for c in checks if not c.passed and c.severity == "high"]

    if score >= 90:
        return "Excellent! All critical security checks passed."
    elif score >= 70:
        if critical_failures:
            return f"Warning: {len(critical_failures)} critical check(s) failed."
        return f"Good, but {len(high_failures)} high-severity check(s) need attention."
    else:
        return f"Security concerns: {len(critical_failures)} critical and {len(high_failures)} high-severity failures."


# ============================================================================
# Analysis Functions
# ============================================================================


def analyze_x402_payment(
    payload: dict[str, Any],
    requirements: dict[str, Any],
    used_nonces: set[str] | None = None,
) -> SecurityAnalysis:
    """Analyze x402 v2 payment for security issues."""
    checks: list[SecurityCheck] = []
    used_nonces = used_nonces or set()

    # Extract signature and authorization
    signature = payload.get("payload", {}).get("signature", "")
    authorization = payload.get("payload", {}).get("authorization", {})

    # Check 1: Signature present
    if signature:
        checks.append(SecurityCheck(
            check_id="signature_present",
            name="Signature Present",
            passed=True,
            severity="critical",
            message="Payment includes cryptographic signature",
        ))
    else:
        checks.append(SecurityCheck(
            check_id="signature_present",
            name="Signature Present",
            passed=False,
            severity="critical",
            message="Missing signature in payment payload",
            recommendation="Include a valid EIP-712 signature",
        ))

    # Check 2: Signature format
    if signature:
        valid, msg = verify_eip712_signature(signature, authorization)
        checks.append(SecurityCheck(
            check_id="signature_format",
            name="Valid Signature Format",
            passed=valid,
            severity="high",
            message=msg,
            recommendation=None if valid else "Use proper EIP-712 signature format",
        ))

    # Check 3: Nonce unique
    nonce = authorization.get("nonce", "")
    if nonce:
        valid, msg = verify_nonce(nonce, used_nonces)
        checks.append(SecurityCheck(
            check_id="nonce_unique",
            name="Unique Nonce",
            passed=valid,
            severity="critical",
            message=msg,
            recommendation=None if valid else "Generate a unique 32-byte nonce for each payment",
        ))

    # Check 4: Time window
    valid_after = authorization.get("validAfter", "0")
    valid_before = authorization.get("validBefore", str(int(datetime.now(timezone.utc).timestamp()) + 300))
    valid, msg = verify_time_window(valid_after, valid_before)
    checks.append(SecurityCheck(
        check_id="time_window",
        name="Valid Time Window",
        passed=valid,
        severity="high",
        message=msg,
        recommendation=None if valid else "Set appropriate validAfter/validBefore timestamps",
    ))

    # Check 5: Amount matches
    auth_value = int(authorization.get("value", "0"))
    required_amount = int(requirements.get("amount", "0"))
    amount_ok = auth_value >= required_amount
    checks.append(SecurityCheck(
        check_id="amount_match",
        name="Amount Matches",
        passed=amount_ok,
        severity="medium",
        message=f"Amount {auth_value} {'≥' if amount_ok else '<'} required {required_amount}",
        recommendation=None if amount_ok else f"Increase payment amount to at least {required_amount}",
    ))

    # Check 6: Recipient matches
    auth_to = authorization.get("to", "")
    required_to = requirements.get("payTo", "")
    recipient_ok = auth_to.lower() == required_to.lower() if auth_to and required_to else False
    checks.append(SecurityCheck(
        check_id="recipient_match",
        name="Recipient Matches",
        passed=recipient_ok,
        severity="critical",
        message=f"Recipient {'matches' if recipient_ok else 'does NOT match'} required address",
        recommendation=None if recipient_ok else f"Set 'to' address to {required_to}",
    ))

    # Calculate score
    score = calculate_security_score(checks)
    grade = get_grade(score)
    summary = generate_summary(checks, score)

    return SecurityAnalysis(
        score=score,
        grade=grade,
        checks=checks,
        summary=summary,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


def analyze_ap2_mandate(
    mandate: dict[str, Any],
    authorization: str,
) -> SecurityAnalysis:
    """Analyze AP2 mandate for security issues."""
    checks: list[SecurityCheck] = []

    # Check 1: Authorization present
    if authorization:
        checks.append(SecurityCheck(
            check_id="signature_present",
            name="User Authorization Present",
            passed=True,
            severity="critical",
            message="Mandate includes user authorization",
        ))
    else:
        checks.append(SecurityCheck(
            check_id="signature_present",
            name="User Authorization Present",
            passed=False,
            severity="critical",
            message="Missing user authorization",
            recommendation="User must sign the mandate before payment",
        ))

    # Check 2: Mandate has content hash
    content_hash = mandate.get("content_hash", "")
    if content_hash:
        checks.append(SecurityCheck(
            check_id="signature_format",
            name="Content Hash Present",
            passed=True,
            severity="high",
            message="Mandate contents are hashed for integrity",
        ))
    else:
        checks.append(SecurityCheck(
            check_id="signature_format",
            name="Content Hash Present",
            passed=False,
            severity="high",
            message="Missing content hash",
            recommendation="Include SHA-256 hash of mandate contents",
        ))

    # Check 3: Merchant authorization
    merchant_auth = mandate.get("merchant_authorization", "")
    if merchant_auth:
        checks.append(SecurityCheck(
            check_id="recipient_match",
            name="Merchant Authorization",
            passed=True,
            severity="critical",
            message="Merchant has signed the cart mandate",
        ))
    else:
        checks.append(SecurityCheck(
            check_id="recipient_match",
            name="Merchant Authorization",
            passed=False,
            severity="critical",
            message="Missing merchant authorization",
            recommendation="Merchant must sign cart before user approval",
        ))

    # Calculate score
    score = calculate_security_score(checks)
    grade = get_grade(score)
    summary = generate_summary(checks, score)

    return SecurityAnalysis(
        score=score,
        grade=grade,
        checks=checks,
        summary=summary,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
