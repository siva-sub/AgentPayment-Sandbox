"""Runs API router."""

import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models.core import AttackToggle, ExecutionRun

router = APIRouter()

# In-memory store for runs (would be SQLite in production)
RUNS: dict[str, ExecutionRun] = {}


class CreateRunRequest(BaseModel):
    """Request to create a new execution run."""

    scenario_id: str | None = None
    attacks: list[AttackToggle] = []


class RunStepRequest(BaseModel):
    """Request to execute a step in a run."""

    action: str
    context: dict[str, Any] = {}


@router.get("")
async def list_runs() -> list[dict[str, Any]]:
    """List all execution runs."""
    return [
        {
            "id": run.id,
            "scenario_id": run.scenario_id,
            "started_at": run.started_at.isoformat(),
            "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            "success": run.success,
            "step_count": len(run.steps),
            "attack_count": len([a for a in run.attacks if a.enabled]),
        }
        for run in RUNS.values()
    ]


@router.post("")
async def create_run(request: CreateRunRequest) -> dict[str, Any]:
    """Create a new execution run."""
    run_id = str(uuid.uuid4())
    run = ExecutionRun(
        id=run_id,
        scenario_id=request.scenario_id,
        attacks=request.attacks,
    )
    RUNS[run_id] = run
    return {
        "id": run.id,
        "scenario_id": run.scenario_id,
        "started_at": run.started_at.isoformat(),
        "attacks": [a.model_dump() for a in run.attacks],
    }


@router.get("/{run_id}")
async def get_run(run_id: str) -> dict[str, Any]:
    """Get execution run details."""
    run = RUNS.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")
    return run.model_dump()


@router.post("/{run_id}/step")
async def execute_step(run_id: str, request: RunStepRequest) -> dict[str, Any]:
    """Execute a step in the run."""
    run = RUNS.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")

    if run.completed_at:
        raise HTTPException(status_code=400, detail="Run is already completed")

    # Placeholder step execution
    step_id = str(uuid.uuid4())
    run.steps.append(step_id)

    return {
        "step_id": step_id,
        "action": request.action,
        "success": True,
        "message": f"Executed action: {request.action}",
    }


@router.post("/{run_id}/complete")
async def complete_run(run_id: str) -> dict[str, Any]:
    """Mark a run as completed."""
    run = RUNS.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")

    run.completed_at = datetime.utcnow()
    run.success = True  # Simplified for now
    run.summary = f"Completed with {len(run.steps)} steps"

    return {
        "id": run.id,
        "completed_at": run.completed_at.isoformat(),
        "success": run.success,
        "summary": run.summary,
    }


@router.delete("/{run_id}")
async def delete_run(run_id: str) -> dict[str, str]:
    """Delete an execution run."""
    if run_id not in RUNS:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")

    del RUNS[run_id]
    return {"status": "deleted", "id": run_id}
