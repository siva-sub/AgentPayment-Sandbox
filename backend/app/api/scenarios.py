"""Scenarios API router."""

from typing import Any

from fastapi import APIRouter, HTTPException

router = APIRouter()

# Built-in scenarios
SCENARIOS = [
    {
        "id": "ap2-happy-path",
        "name": "AP2 Happy Path",
        "protocol": "AP2",
        "description": "Complete cart → mandate → payment → settlement flow",
        "flow_type": "human-present",
        "steps": [
            {"action": "create_cart", "actor": "merchant"},
            {"action": "sign_cart_mandate", "actor": "merchant"},
            {"action": "display_cart", "actor": "agent"},
            {"action": "approve_cart", "actor": "user"},
            {"action": "create_payment_mandate", "actor": "agent"},
            {"action": "sign_payment_mandate", "actor": "user"},
            {"action": "initiate_payment", "actor": "merchant"},
            {"action": "process_payment", "actor": "psp"},
            {"action": "confirm_settlement", "actor": "psp"},
        ],
    },
    {
        "id": "x402-micropayment",
        "name": "x402 Micropayment",
        "protocol": "x402",
        "description": "HTTP 402 → Payment → Resource access flow",
        "flow_type": "exact-evm",
        "steps": [
            {"action": "request_resource", "actor": "client"},
            {"action": "return_402", "actor": "server"},
            {"action": "sign_payment", "actor": "payer"},
            {"action": "submit_payment", "actor": "client"},
            {"action": "verify_payment", "actor": "facilitator"},
            {"action": "settle_payment", "actor": "facilitator"},
            {"action": "return_resource", "actor": "server"},
        ],
    },
    {
        "id": "acp-checkout",
        "name": "ACP Checkout Session",
        "protocol": "ACP",
        "description": "Create → Update → Complete checkout session",
        "flow_type": "complete",
        "steps": [
            {"action": "create_session", "actor": "agent"},
            {"action": "add_items", "actor": "agent"},
            {"action": "set_fulfillment", "actor": "agent"},
            {"action": "complete_payment", "actor": "agent"},
            {"action": "confirm_order", "actor": "merchant"},
        ],
    },
    {
        "id": "bank-rail-settlement",
        "name": "Bank Rail Settlement",
        "protocol": "custom",
        "description": "Bank rail adapter with recall window demo",
        "flow_type": "rtgs-mock",
        "steps": [
            {"action": "initiate_transfer", "actor": "payer"},
            {"action": "submit_to_rail", "actor": "adapter"},
            {"action": "receive_ack", "actor": "adapter"},
            {"action": "await_settlement", "actor": "adapter"},
            {"action": "confirm_finality", "actor": "rail"},
        ],
    },
    {
        "id": "recovery-case-flow",
        "name": "Recovery Case Flow",
        "protocol": "custom",
        "description": "Post-settlement recall request (camt.056/029)",
        "flow_type": "iso20022",
        "steps": [
            {"action": "detect_issue", "actor": "ops"},
            {"action": "create_case", "actor": "ops"},
            {"action": "send_recall", "actor": "adapter"},
            {"action": "check_window", "actor": "adapter"},
            {"action": "process_response", "actor": "adapter"},
            {"action": "resolve_case", "actor": "ops"},
        ],
    },
]


@router.get("")
async def list_scenarios() -> list[dict[str, Any]]:
    """List all available scenarios."""
    return [
        {
            "id": s["id"],
            "name": s["name"],
            "protocol": s["protocol"],
            "description": s["description"],
            "flow_type": s["flow_type"],
            "step_count": len(s["steps"]),
        }
        for s in SCENARIOS
    ]


@router.get("/{scenario_id}")
async def get_scenario(scenario_id: str) -> dict[str, Any]:
    """Get scenario details with full step definitions."""
    scenario = next((s for s in SCENARIOS if s["id"] == scenario_id), None)
    if not scenario:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found")
    return scenario
