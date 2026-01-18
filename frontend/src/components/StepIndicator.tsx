import { Check } from "lucide-react";

interface Step {
    id: number;
    name: string;
    description: string;
}

interface StepIndicatorProps {
    steps: Step[];
    currentStep: number;
    onStepClick?: (step: number) => void;
}

export function StepIndicator({ steps, currentStep, onStepClick }: StepIndicatorProps) {
    return (
        <div className="w-full py-4">
            <div className="flex items-center justify-between">
                {steps.map((step, index) => {
                    const isCompleted = index < currentStep;
                    const isCurrent = index === currentStep;
                    const isClickable = index <= currentStep && onStepClick;

                    return (
                        <div key={step.id} className="flex items-center flex-1 last:flex-none">
                            {/* Step Circle */}
                            <button
                                onClick={() => isClickable && onStepClick(index)}
                                disabled={!isClickable}
                                className={`
                  relative flex items-center justify-center w-10 h-10 rounded-full
                  text-sm font-semibold transition-all duration-300
                  ${isCompleted
                                        ? "bg-green-500 text-white"
                                        : isCurrent
                                            ? "bg-blue-600 text-white ring-4 ring-blue-600/30"
                                            : "bg-slate-700 text-slate-400"
                                    }
                  ${isClickable ? "cursor-pointer hover:scale-110" : "cursor-default"}
                `}
                            >
                                {isCompleted ? (
                                    <Check className="w-5 h-5" />
                                ) : (
                                    <span>{step.id}</span>
                                )}
                            </button>

                            {/* Step Label (below circle) */}
                            <div className="absolute mt-14 -ml-4 w-20 text-center hidden md:block">
                                <span
                                    className={`text-xs font-medium ${isCurrent ? "text-blue-400" : isCompleted ? "text-green-400" : "text-slate-500"
                                        }`}
                                >
                                    {step.name}
                                </span>
                            </div>

                            {/* Connector Line */}
                            {index < steps.length - 1 && (
                                <div className="flex-1 h-1 mx-2">
                                    <div
                                        className={`h-full rounded-full transition-all duration-500 ${isCompleted ? "bg-green-500" : "bg-slate-700"
                                            }`}
                                    />
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>

            {/* Current Step Description */}
            <div className="mt-8 text-center">
                <h3 className="text-lg font-semibold text-white">
                    Step {steps[currentStep]?.id}: {steps[currentStep]?.name}
                </h3>
                <p className="text-sm text-slate-400 mt-1">
                    {steps[currentStep]?.description}
                </p>
            </div>
        </div>
    );
}

// Default AP2 steps
export const AP2_STEPS: Step[] = [
    { id: 1, name: "Profile", description: "Select your agent role (shopper or merchant)" },
    { id: 2, name: "Discovery", description: "Generate or validate your AgentCard with AP2 extension" },
    { id: 3, name: "IntentMandate", description: "Express purchase intent with natural language" },
    { id: 4, name: "CartMandate", description: "Merchant returns cart with signature" },
    { id: 5, name: "Approval", description: "User confirms cart details" },
    { id: 6, name: "PaymentMandate", description: "User authorizes payment with VDC" },
    { id: 7, name: "Settlement", description: "Payment is processed" },
    { id: 8, name: "Receipt", description: "Transaction complete, receipt generated" },
];

// x402 steps
export const X402_STEPS: Step[] = [
    { id: 1, name: "Profile", description: "Configure agent identity and capabilities" },
    { id: 2, name: "Request", description: "Make HTTP request to protected resource" },
    { id: 3, name: "402 Response", description: "Server returns 402 with payment requirements" },
    { id: 4, name: "Mint Token", description: "Create payment token with EIP-712 signature" },
    { id: 5, name: "Pay Header", description: "Add X-PAYMENT header to request" },
    { id: 6, name: "Verification", description: "Server verifies signature and processes payment" },
    { id: 7, name: "Resource", description: "Server returns protected resource" },
];

// UCP steps
export const UCP_STEPS: Step[] = [
    { id: 1, name: "Profile", description: "Select platform capability profile" },
    { id: 2, name: "Discovery", description: "Fetch /.well-known/ucp from business" },
    { id: 3, name: "Negotiation", description: "Intersect platform and business capabilities" },
    { id: 4, name: "Create Checkout", description: "Initialize checkout session" },
    { id: 5, name: "Update Checkout", description: "Add items, discounts, fulfillment" },
    { id: 6, name: "Mint Instrument", description: "Acquire payment credential" },
    { id: 7, name: "Complete Checkout", description: "Submit payment and create order" },
    { id: 8, name: "Webhook", description: "Simulate backend event notifications" },
];
