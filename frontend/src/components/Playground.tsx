import { useState } from "react";
import { StepIndicator, AP2_STEPS, X402_STEPS, UCP_STEPS } from "./StepIndicator";
import { PayloadEditor } from "./PayloadEditor";
import { ErrorCard, WarningCard, SuccessCard } from "./ErrorCard";
import { ChevronLeft, ChevronRight, RotateCcw, Zap, Play, Loader2, Info } from "lucide-react";
import { executeProtocolStep, type ApiResponse, type Protocol as ApiProtocol, IS_DEMO_MODE } from "../services/api";

type Protocol = "AP2" | "x402" | "UCP";

// Demo mode banner component
const DemoModeBanner = () => (
    <div className="bg-gradient-to-r from-amber-500/20 to-orange-500/20 border border-amber-500/50 rounded-xl p-4 mb-6">
        <div className="flex items-start gap-3">
            <Info className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
            <div>
                <h3 className="text-amber-300 font-medium mb-1">Demo Mode</h3>
                <p className="text-amber-200/80 text-sm">
                    Running with mock data. For live API calls, run the backend locally:
                    <code className="ml-2 px-2 py-0.5 bg-slate-900/50 rounded text-xs">uvicorn app.main:app --port 8080</code>
                </p>
            </div>
        </div>
    </div>
);

// Sample payloads for each step
const AP2_PAYLOADS: Record<number, object> = {
    0: {
        role: "shopper",
        capabilities: ["purchase", "browse"],
        vdc_supported: true,
    },
    1: {
        name: "Shopping Assistant",
        description: "AI agent that helps users purchase products",
        capabilities: {
            extensions: [
                {
                    uri: "https://github.com/google-agentic-commerce/ap2/tree/v0.1",
                    description: "This agent can pay for items on behalf of users",
                    params: {
                        roles: ["shopper"],
                    },
                },
            ],
        },
        skills: [
            {
                id: "purchase_items",
                name: "Purchase Items",
                description: "Purchase products from merchants",
            },
        ],
    },
    2: {
        messageId: "msg-intent-001",
        contextId: "shopping-context-001",
        taskId: "purchase-task-001",
        role: "user",
        parts: [
            {
                kind: "data",
                data: {
                    "ap2.mandates.IntentMandate": {
                        user_cart_confirmation_required: true,
                        natural_language_description: "I want to buy red shoes under $100",
                        required_refundability: true,
                        intent_expiry: "2026-01-20T15:00:00Z",
                    },
                },
            },
        ],
    },
    3: {
        name: "Shopping Cart",
        artifactId: "cart-001",
        parts: [
            {
                kind: "data",
                data: {
                    "ap2.mandates.CartMandate": {
                        contents: {
                            id: "cart_shoes_123",
                            user_signature_required: true,
                            payment_request: {
                                method_data: [{ supported_methods: "CARD" }],
                                details: {
                                    id: "order_shoes_123",
                                    displayItems: [
                                        {
                                            label: "Red Running Shoes",
                                            amount: { currency: "USD", value: 89.99 },
                                        },
                                    ],
                                    total: {
                                        label: "Total",
                                        amount: { currency: "USD", value: 89.99 },
                                    },
                                },
                            },
                        },
                        merchant_signature: "sig_merchant_abc123",
                        timestamp: "2026-01-18T12:00:00Z",
                    },
                },
            },
        ],
    },
    4: {
        user_confirmation: true,
        confirmed_cart_id: "cart_shoes_123",
        confirmed_total: { currency: "USD", value: 89.99 },
    },
    5: {
        messageId: "msg-payment-001",
        contextId: "shopping-context-001",
        taskId: "purchase-task-001",
        role: "user",
        parts: [
            {
                kind: "data",
                data: {
                    "ap2.mandates.PaymentMandate": {
                        payment_mandate_contents: {
                            payment_mandate_id: "pm_12345",
                            payment_details_id: "order_shoes_123",
                            payment_details_total: {
                                label: "Total",
                                amount: { currency: "USD", value: 89.99 },
                                refund_period: 30,
                            },
                            payment_response: {
                                request_id: "order_shoes_123",
                                method_name: "CARD",
                                details: { token: "tok_visa_4242" },
                            },
                            merchant_agent: "MerchantAgent",
                            timestamp: "2026-01-18T12:05:00Z",
                        },
                        user_authorization: "eyJhbGciOiJFUzI1NksiLCJ...",
                    },
                },
            },
        ],
    },
    6: {
        settlement_id: "settle_001",
        payment_mandate_id: "pm_12345",
        amount: { currency: "USD", value: 89.99 },
        status: "PROCESSING",
        processor_reference: "stripe_pi_abc123",
    },
    7: {
        receipt_id: "receipt_001",
        order_id: "order_shoes_123",
        payment_mandate_id: "pm_12345",
        status: "COMPLETED",
        amount: { currency: "USD", value: 89.99 },
        timestamp: "2026-01-18T12:06:00Z",
        merchant: "ShoeStore",
        items: [{ name: "Red Running Shoes", quantity: 1, price: 89.99 }],
    },
};

// Validation results for each step
const AP2_VALIDATIONS: Record<number, { valid: boolean; errors: any[]; warnings: any[]; securityScore: number }> = {
    0: { valid: true, errors: [], warnings: [], securityScore: 100 },
    1: {
        valid: true,
        errors: [],
        warnings: [
            {
                path: "capabilities.extensions[0].params.roles",
                message: "Only 'shopper' role declared",
                recommendation: "Consider adding 'credentials-provider' if agent will manage VDCs",
            },
        ],
        securityScore: 90,
    },
    2: { valid: true, errors: [], warnings: [], securityScore: 95 },
    3: {
        valid: true,
        errors: [],
        warnings: [
            {
                path: "parts[0].data['ap2.mandates.CartMandate'].contents.user_signature_required",
                message: "user_signature_required is true",
                recommendation: "Ensure VDC verification is implemented before payment",
            },
        ],
        securityScore: 85,
    },
    4: { valid: true, errors: [], warnings: [], securityScore: 100 },
    5: {
        valid: false,
        errors: [
            {
                path: "parts[0].data['ap2.mandates.PaymentMandate'].user_authorization",
                message: "user_authorization appears truncated",
                expected: "Complete JWT with signature",
                got: "eyJhbGciOiJFUzI1NksiLCJ...",
                fix: `// Complete the JWT signature
const user_authorization = sign(
  payment_mandate_contents,
  user_private_key
);`,
                specRef: "https://google-agentic-commerce.github.io/ap2/mandates/#paymentmandate",
            },
        ],
        warnings: [],
        securityScore: 60,
    },
    6: { valid: true, errors: [], warnings: [], securityScore: 95 },
    7: { valid: true, errors: [], warnings: [], securityScore: 100 },
};

export function Playground() {
    const [protocol, setProtocol] = useState<Protocol>("AP2");
    const [currentStep, setCurrentStep] = useState(0);
    const [payload, setPayload] = useState<object>(AP2_PAYLOADS[0] || {});
    const [isExecuting, setIsExecuting] = useState(false);
    const [serverResponse, setServerResponse] = useState<ApiResponse | null>(null);

    const steps = protocol === "AP2" ? AP2_STEPS : protocol === "x402" ? X402_STEPS : UCP_STEPS;
    const validation = protocol === "AP2" ? AP2_VALIDATIONS[currentStep] : null;

    const handleStepChange = (step: number) => {
        setCurrentStep(step);
        if (protocol === "AP2" && AP2_PAYLOADS[step]) {
            setPayload(AP2_PAYLOADS[step]);
        }
    };

    const handleNext = () => {
        if (currentStep < steps.length - 1) {
            handleStepChange(currentStep + 1);
        }
    };

    const handlePrev = () => {
        if (currentStep > 0) {
            handleStepChange(currentStep - 1);
        }
    };

    const handleReset = () => {
        setCurrentStep(0);
        setPayload(AP2_PAYLOADS[0] || {});
        setServerResponse(null);
    };

    const handleExecute = async () => {
        setIsExecuting(true);
        setServerResponse(null);
        try {
            const result = await executeProtocolStep(
                protocol as ApiProtocol,
                currentStep,
                payload as Record<string, unknown>
            );
            setServerResponse(result);
        } catch (err) {
            setServerResponse({
                success: false,
                error: err instanceof Error ? err.message : 'Unknown error',
            });
        } finally {
            setIsExecuting(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
            {/* Header */}
            <header className="border-b border-slate-700/50 bg-slate-900/50 backdrop-blur-sm sticky top-0 z-10">
                <div className="max-w-7xl mx-auto px-6 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <Zap className="w-8 h-8 text-blue-500" />
                            <div>
                                <h1 className="text-xl font-bold text-white">APS Playground</h1>
                                <p className="text-xs text-slate-400">Interactive Protocol Testing</p>
                            </div>
                        </div>

                        {/* Protocol Selector */}
                        <div className="flex items-center gap-2">
                            {(["AP2", "x402", "UCP"] as Protocol[]).map((p) => (
                                <button
                                    key={p}
                                    onClick={() => {
                                        setProtocol(p);
                                        handleReset();
                                    }}
                                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${protocol === p
                                        ? "bg-blue-600 text-white"
                                        : "bg-slate-800 text-slate-400 hover:text-white"
                                        }`}
                                >
                                    {p}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>
            </header>

            {/* Step Indicator */}
            <div className="max-w-7xl mx-auto px-6 py-6">
                <StepIndicator
                    steps={steps}
                    currentStep={currentStep}
                    onStepClick={handleStepChange}
                />
            </div>

            {/* Main Content */}
            <div className="max-w-7xl mx-auto px-6 pb-12">
                {IS_DEMO_MODE && <DemoModeBanner />}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Left: Payload Editor */}
                    <div className="bg-slate-800/50 rounded-2xl border border-slate-700/50 overflow-hidden">
                        <PayloadEditor
                            payload={payload}
                            onChange={setPayload}
                            validation={validation || undefined}
                        />
                    </div>

                    {/* Right: Validation Results */}
                    <div className="space-y-4">
                        <div className="bg-slate-800/50 rounded-2xl border border-slate-700/50 p-6">
                            <h3 className="text-lg font-semibold text-white mb-4">Validation</h3>

                            {validation?.valid && validation.errors.length === 0 && (
                                <SuccessCard
                                    message="Schema Valid"
                                    details="Payload matches protocol specification"
                                />
                            )}

                            {validation?.errors.map((error, idx) => (
                                <ErrorCard key={idx} error={error} />
                            ))}

                            {validation?.warnings.map((warning, idx) => (
                                <WarningCard key={idx} warning={warning} />
                            ))}

                            {!validation && (
                                <p className="text-slate-400 text-sm">
                                    Select a protocol and step to see validation
                                </p>
                            )}
                        </div>

                        {/* Security Score */}
                        {validation && (
                            <div className="bg-slate-800/50 rounded-2xl border border-slate-700/50 p-6">
                                <h3 className="text-lg font-semibold text-white mb-4">Security Score</h3>
                                <div className="flex items-center gap-4">
                                    <div
                                        className={`text-4xl font-bold ${validation.securityScore >= 80
                                            ? "text-green-400"
                                            : validation.securityScore >= 50
                                                ? "text-yellow-400"
                                                : "text-red-400"
                                            }`}
                                    >
                                        {validation.securityScore}
                                    </div>
                                    <div className="flex-1 h-3 bg-slate-700 rounded-full overflow-hidden">
                                        <div
                                            className={`h-full transition-all duration-500 ${validation.securityScore >= 80
                                                ? "bg-green-500"
                                                : validation.securityScore >= 50
                                                    ? "bg-yellow-500"
                                                    : "bg-red-500"
                                                }`}
                                            style={{ width: `${validation.securityScore}%` }}
                                        />
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Server Response */}
                        {serverResponse && (
                            <div className={`rounded-2xl border p-6 ${serverResponse.success
                                ? 'bg-green-900/20 border-green-700/50'
                                : 'bg-red-900/20 border-red-700/50'
                                }`}
                            >
                                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                                    {serverResponse.success ? '✓' : '✗'} Server Response
                                    {serverResponse.status && (
                                        <span className="text-sm font-normal text-slate-400">
                                            HTTP {serverResponse.status}
                                        </span>
                                    )}
                                </h3>
                                {serverResponse.error && (
                                    <div className="text-red-400 text-sm mb-3">
                                        Error: {String(serverResponse.error)}
                                    </div>
                                )}
                                {serverResponse.data ? (
                                    <pre className="text-xs text-slate-300 bg-slate-900/50 rounded-lg p-4 overflow-auto max-h-64">
                                        {JSON.stringify(serverResponse.data, null, 2)}
                                    </pre>
                                ) : null}
                                {serverResponse.headers?.['X-Payment-Required'] && (
                                    <div className="mt-3 p-3 bg-yellow-900/30 rounded-lg border border-yellow-700/50">
                                        <div className="text-yellow-400 text-sm font-medium mb-1">Payment Required</div>
                                        <pre className="text-xs text-slate-300 overflow-auto">
                                            {serverResponse.headers['X-Payment-Required']}
                                        </pre>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                </div>

                {/* Navigation */}
                <div className="flex items-center justify-between mt-8">
                    <div className="flex items-center gap-2">
                        <button
                            onClick={handleReset}
                            className="flex items-center gap-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg text-sm font-medium transition-colors"
                        >
                            <RotateCcw className="w-4 h-4" />
                            Reset
                        </button>
                        <button
                            onClick={handleExecute}
                            disabled={isExecuting}
                            className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-500 disabled:bg-green-800 disabled:cursor-not-allowed text-white rounded-lg text-sm font-medium transition-colors"
                        >
                            {isExecuting ? (
                                <Loader2 className="w-4 h-4 animate-spin" />
                            ) : (
                                <Play className="w-4 h-4" />
                            )}
                            {isExecuting ? 'Executing...' : 'Execute'}
                        </button>
                    </div>

                    <div className="flex items-center gap-3">
                        <button
                            onClick={handlePrev}
                            disabled={currentStep === 0}
                            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${currentStep === 0
                                ? "bg-slate-700 text-slate-500 cursor-not-allowed"
                                : "bg-slate-700 hover:bg-slate-600 text-white"
                                }`}
                        >
                            <ChevronLeft className="w-4 h-4" />
                            Previous
                        </button>

                        <button
                            onClick={handleNext}
                            disabled={currentStep === steps.length - 1}
                            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${currentStep === steps.length - 1
                                ? "bg-slate-700 text-slate-500 cursor-not-allowed"
                                : "bg-blue-600 hover:bg-blue-500 text-white"
                                }`}
                        >
                            Next
                            <ChevronRight className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
