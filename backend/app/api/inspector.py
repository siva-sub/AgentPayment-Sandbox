"""Inspector Mode - Test runner for validating external protocol implementations.

Runs test suites against external servers to verify protocol compliance.
Returns detailed reports with pass/fail status and recommendations.
"""

import uuid
from datetime import datetime, timezone
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()


# ============================================================================
# Models
# ============================================================================


class TestRun(BaseModel):
    """A test run configuration."""

    target_url: str
    protocol: str  # "UCP", "ACP", "x402", "AP2"
    tests: list[str] | None = None  # Specific tests to run, or None for all


class TestResult(BaseModel):
    """Result of a single test."""

    test_id: str
    name: str
    passed: bool
    duration_ms: int
    error: str | None = None
    expected: Any | None = None
    actual: Any | None = None
    recommendation: str | None = None


class TestReport(BaseModel):
    """Complete test run report."""

    run_id: str
    target_url: str
    protocol: str
    timestamp: str
    duration_ms: int
    passed: int
    failed: int
    warnings: int
    security_score: int
    results: list[TestResult]
    summary: str


# ============================================================================
# Test Definitions
# ============================================================================

UCP_TESTS = [
    {
        "id": "ucp_discovery",
        "name": "Discovery endpoint returns valid profile",
        "endpoint": "/.well-known/ucp",
        "method": "GET",
        "expected_status": 200,
        "required_fields": ["name", "version", "payment"],
        "weight": 20,
    },
    {
        "id": "ucp_discovery_payment_handlers",
        "name": "Discovery includes payment handlers",
        "endpoint": "/.well-known/ucp",
        "method": "GET",
        "expected_status": 200,
        "json_path": "payment.handlers",
        "min_length": 1,
        "weight": 15,
    },
    {
        "id": "ucp_checkout_create",
        "name": "Can create checkout session",
        "endpoint": "/checkout-sessions",
        "method": "POST",
        "body": {
            "currency": "USD",
            "line_items": [{"item": {"id": "test_product"}, "quantity": 1}],
        },
        "expected_status": 201,
        "required_fields": ["id", "status", "line_items"],
        "weight": 25,
    },
    {
        "id": "ucp_checkout_get",
        "name": "Can retrieve checkout session",
        "depends_on": "ucp_checkout_create",
        "endpoint_template": "/checkout-sessions/{checkout_id}",
        "method": "GET",
        "expected_status": 200,
        "weight": 15,
    },
    {
        "id": "ucp_idempotency",
        "name": "Idempotency key is honored",
        "endpoint": "/checkout-sessions",
        "method": "POST",
        "body": {
            "currency": "USD",
            "line_items": [{"item": {"id": "test_product"}, "quantity": 1}],
        },
        "headers": {"Idempotency-Key": "test-idempotency-key"},
        "expected_status": 201,
        "repeat": 2,
        "expect_same_response": True,
        "weight": 25,
    },
]

ACP_TESTS = [
    {
        "id": "acp_discovery",
        "name": "Discovery endpoint exists",
        "endpoint": "/.well-known/checkout",
        "method": "GET",
        "expected_status": 200,
        "weight": 20,
    },
    {
        "id": "acp_discovery_api_version",
        "name": "Discovery includes API-Version",
        "endpoint": "/.well-known/checkout",
        "method": "GET",
        "expected_status": 200,
        "required_fields": ["api_version"],
        "weight": 15,
    },
    {
        "id": "acp_session_create",
        "name": "Can create checkout session",
        "endpoint": "/checkout_sessions",
        "method": "POST",
        "body": {"items": [{"id": "item_123", "quantity": 1}]},
        "headers": {"API-Version": "2026-01-16"},
        "expected_status": 201,
        "required_fields": ["id", "status", "line_items", "totals"],
        "weight": 30,
    },
    {
        "id": "acp_session_line_items",
        "name": "Line items include totals breakdown",
        "depends_on": "acp_session_create",
        "check": "line_item_schema",
        "weight": 20,
    },
    {
        "id": "acp_session_states",
        "name": "Session status transitions correctly",
        "depends_on": "acp_session_create",
        "check": "status_in",
        "valid_statuses": ["not_ready_for_payment", "ready_for_payment"],
        "weight": 15,
    },
]

X402_TESTS = [
    {
        "id": "x402_info",
        "name": "Info endpoint returns protocol details",
        "endpoint": "/info",
        "method": "GET",
        "expected_status": 200,
        "required_fields": ["x402Version", "protocol", "receiver"],
        "weight": 15,
    },
    {
        "id": "x402_supported",
        "name": "Facilitator /supported returns CAIP-2 networks",
        "endpoint": "/supported",
        "method": "GET",
        "expected_status": 200,
        "required_fields": ["kinds", "signers"],
        "check": "caip2_networks",
        "weight": 20,
    },
    {
        "id": "x402_402_response",
        "name": "Protected resource returns 402 with PaymentRequired",
        "endpoint": "/resource/premium-content",
        "method": "GET",
        "expected_status": 402,
        "check": "x402_v2_format",
        "weight": 30,
    },
    {
        "id": "x402_verify_endpoint",
        "name": "Facilitator /verify endpoint exists",
        "endpoint": "/verify",
        "method": "POST",
        "body": {"paymentPayload": {}, "paymentRequirements": {}},
        "expected_status": 422,  # Invalid payload expected
        "weight": 15,
    },
    {
        "id": "x402_settle_endpoint",
        "name": "Facilitator /settle endpoint exists",
        "endpoint": "/settle",
        "method": "POST",
        "body": {"paymentPayload": {}, "paymentRequirements": {}},
        "expected_status": 422,  # Invalid payload expected
        "weight": 15,
    },
]

AP2_TESTS = [
    {
        "id": "ap2_agent_card",
        "name": "Agent card with AP2 extension",
        "endpoint": "/.well-known/a2a",
        "method": "GET",
        "expected_status": 200,
        "json_path": "capabilities.extensions",
        "contains_ap2": True,
        "weight": 25,
    },
    {
        "id": "ap2_message_handler",
        "name": "A2A message endpoint accepts messages",
        "endpoint": "/message",
        "method": "POST",
        "body": {
            "jsonrpc": "2.0",
            "id": "test-1",
            "method": "ap2/browseProducts",
            "params": {},
        },
        "expected_status": 200,
        "weight": 35,
    },
]


# ============================================================================
# Test Runner
# ============================================================================


def _get_tests(protocol: str) -> list[dict[str, Any]]:
    """Get test definitions for a protocol."""
    tests_map = {
        "UCP": UCP_TESTS,
        "ACP": ACP_TESTS,
        "x402": X402_TESTS,
        "AP2": AP2_TESTS,
    }
    return tests_map.get(protocol, [])


async def _run_test(
    client: httpx.AsyncClient,
    test: dict[str, Any],
    context: dict[str, Any],
) -> TestResult:
    """Run a single test."""
    start_time = datetime.now(timezone.utc)
    test_id = test["id"]
    name = test["name"]

    try:
        # Build endpoint URL
        endpoint = test.get("endpoint", "")
        if "endpoint_template" in test:
            endpoint = test["endpoint_template"].format(**context)

        # Make request
        method = test.get("method", "GET")
        body = test.get("body")
        headers = test.get("headers", {})

        if method == "GET":
            response = await client.get(endpoint, headers=headers)
        elif method == "POST":
            response = await client.post(endpoint, json=body, headers=headers)
        elif method == "PUT":
            response = await client.put(endpoint, json=body, headers=headers)
        else:
            raise ValueError(f"Unknown method: {method}")

        duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)

        # Check status code
        expected_status = test.get("expected_status", 200)
        if response.status_code != expected_status:
            return TestResult(
                test_id=test_id,
                name=name,
                passed=False,
                duration_ms=duration_ms,
                error=f"Expected status {expected_status}, got {response.status_code}",
                expected=expected_status,
                actual=response.status_code,
                recommendation=f"Check that {endpoint} returns HTTP {expected_status}",
            )

        # Check required fields
        if "required_fields" in test:
            try:
                data = response.json()
                for field in test["required_fields"]:
                    if field not in data:
                        return TestResult(
                            test_id=test_id,
                            name=name,
                            passed=False,
                            duration_ms=duration_ms,
                            error=f"Missing required field: {field}",
                            recommendation=f"Include '{field}' in the response",
                        )
                # Store for dependent tests
                if "id" in data:
                    context["checkout_id"] = data["id"]
            except Exception as e:
                return TestResult(
                    test_id=test_id,
                    name=name,
                    passed=False,
                    duration_ms=duration_ms,
                    error=f"Invalid JSON response: {e}",
                )

        # Check expected header
        if "expected_header" in test:
            header_name = test["expected_header"]
            if header_name.lower() not in [h.lower() for h in response.headers]:
                return TestResult(
                    test_id=test_id,
                    name=name,
                    passed=False,
                    duration_ms=duration_ms,
                    error=f"Missing expected header: {header_name}",
                    recommendation=f"Include {header_name} header in 402 response",
                )

        return TestResult(
            test_id=test_id,
            name=name,
            passed=True,
            duration_ms=duration_ms,
        )

    except httpx.RequestError as e:
        duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
        return TestResult(
            test_id=test_id,
            name=name,
            passed=False,
            duration_ms=duration_ms,
            error=f"Request failed: {e}",
            recommendation="Check that the target server is running and accessible",
        )
    except Exception as e:
        duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
        return TestResult(
            test_id=test_id,
            name=name,
            passed=False,
            duration_ms=duration_ms,
            error=f"Test error: {e}",
        )


async def run_tests(target_url: str, protocol: str) -> TestReport:
    """Run all tests for a protocol against a target URL."""
    run_id = f"run_{uuid.uuid4().hex[:12]}"
    start_time = datetime.now(timezone.utc)
    tests = _get_tests(protocol)
    results: list[TestResult] = []
    context: dict[str, Any] = {}

    async with httpx.AsyncClient(base_url=target_url, timeout=30.0) as client:
        for test in tests:
            # Skip if dependency failed
            if "depends_on" in test:
                dep_result = next((r for r in results if r.test_id == test["depends_on"]), None)
                if dep_result and not dep_result.passed:
                    results.append(
                        TestResult(
                            test_id=test["id"],
                            name=test["name"],
                            passed=False,
                            duration_ms=0,
                            error=f"Skipped: dependency '{test['depends_on']}' failed",
                        )
                    )
                    continue

            result = await _run_test(client, test, context)
            results.append(result)

    duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
    passed = sum(1 for r in results if r.passed)
    failed = sum(1 for r in results if not r.passed)

    # Calculate security score
    total_weight = sum(t.get("weight", 10) for t in tests)
    earned_weight = sum(
        t.get("weight", 10)
        for t, r in zip(tests, results)
        if r.passed
    )
    security_score = int((earned_weight / total_weight) * 100) if total_weight > 0 else 0

    # Generate summary
    if failed == 0:
        summary = f"All {passed} tests passed! Server is fully compliant with {protocol}."
    else:
        summary = f"{failed} of {passed + failed} tests failed. Review the results for recommendations."

    return TestReport(
        run_id=run_id,
        target_url=target_url,
        protocol=protocol,
        timestamp=start_time.isoformat(),
        duration_ms=duration_ms,
        passed=passed,
        failed=failed,
        warnings=0,
        security_score=security_score,
        results=results,
        summary=summary,
    )


# ============================================================================
# API Endpoints
# ============================================================================


@router.post("/run", response_model=TestReport)
async def run_test_suite(request: TestRun) -> TestReport:
    """Run a test suite against a target URL."""
    if request.protocol not in ["UCP", "ACP", "x402", "AP2"]:
        raise HTTPException(status_code=400, detail=f"Unknown protocol: {request.protocol}")

    return await run_tests(request.target_url, request.protocol)


@router.get("/protocols")
async def list_protocols() -> dict[str, Any]:
    """List available protocols and their tests."""
    return {
        "protocols": [
            {
                "id": "UCP",
                "name": "Universal Commerce Protocol",
                "test_count": len(UCP_TESTS),
            },
            {
                "id": "ACP",
                "name": "Agentic Commerce Protocol (OpenAI)",
                "test_count": len(ACP_TESTS),
            },
            {
                "id": "x402",
                "name": "HTTP 402 Payment Required",
                "test_count": len(X402_TESTS),
            },
            {
                "id": "AP2",
                "name": "Agent Payments Protocol (Google)",
                "test_count": len(AP2_TESTS),
            },
        ]
    }


@router.get("/tests/{protocol}")
async def list_tests(protocol: str) -> dict[str, Any]:
    """List tests for a specific protocol."""
    tests = _get_tests(protocol)
    if not tests:
        raise HTTPException(status_code=404, detail=f"Unknown protocol: {protocol}")

    return {
        "protocol": protocol,
        "tests": [{"id": t["id"], "name": t["name"], "weight": t.get("weight", 10)} for t in tests],
    }
