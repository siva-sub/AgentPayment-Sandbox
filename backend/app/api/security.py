"""Security API - Endpoints for security analysis.

Phase 6: Signature verification and security scoring endpoints.
"""

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.security import (
    SecurityAnalysis,
    analyze_x402_payment,
    analyze_ap2_mandate,
    SECURITY_CHECKS,
)

router = APIRouter()


# ============================================================================
# Request Models
# ============================================================================


class X402AnalysisRequest(BaseModel):
    """Request to analyze x402 payment."""

    payload: dict[str, Any]
    requirements: dict[str, Any]


class AP2AnalysisRequest(BaseModel):
    """Request to analyze AP2 mandate."""

    mandate: dict[str, Any]
    user_authorization: str


# ============================================================================
# Endpoints
# ============================================================================


@router.post("/analyze/x402", response_model=SecurityAnalysis)
async def analyze_x402(request: X402AnalysisRequest) -> SecurityAnalysis:
    """Analyze x402 payment payload for security issues.

    Returns security score, grade, and detailed check results.
    """
    try:
        return analyze_x402_payment(
            payload=request.payload,
            requirements=request.requirements,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Analysis failed: {e}")


@router.post("/analyze/ap2", response_model=SecurityAnalysis)
async def analyze_ap2(request: AP2AnalysisRequest) -> SecurityAnalysis:
    """Analyze AP2 mandate for security issues.

    Returns security score, grade, and detailed check results.
    """
    try:
        return analyze_ap2_mandate(
            mandate=request.mandate,
            authorization=request.user_authorization,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Analysis failed: {e}")


@router.get("/checks")
async def list_security_checks() -> dict[str, Any]:
    """List all available security checks and their weights."""
    return {
        "checks": [
            {
                "id": check_id,
                "name": check["name"],
                "description": check["description"],
                "weight": check["weight"],
                "severity": check["severity"],
            }
            for check_id, check in SECURITY_CHECKS.items()
        ],
        "total_weight": sum(c["weight"] for c in SECURITY_CHECKS.values()),
    }


@router.get("/grades")
async def list_grades() -> dict[str, Any]:
    """List security grade thresholds."""
    return {
        "grades": [
            {"grade": "A", "min_score": 90, "description": "Excellent - All critical checks pass"},
            {"grade": "B", "min_score": 80, "description": "Good - Minor issues only"},
            {"grade": "C", "min_score": 70, "description": "Fair - Some security concerns"},
            {"grade": "D", "min_score": 60, "description": "Poor - Significant issues"},
            {"grade": "F", "min_score": 0, "description": "Failing - Critical security failures"},
        ]
    }
