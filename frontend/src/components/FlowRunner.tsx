import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import {
    Play,
    CheckCircle,
    XCircle,
    Clock,
    ArrowRight,
    AlertTriangle,
} from "lucide-react";

interface Scenario {
    id: string;
    name: string;
    protocol: string;
    description: string;
    flow_type: string;
    steps: { action: string; actor: string }[];
}

interface StepResult {
    step_index: number;
    action: string;
    actor: string;
    status: "pending" | "running" | "success" | "failed";
    message?: string;
    timestamp?: string;
}

interface FlowRun {
    scenario_id: string;
    steps: StepResult[];
    current_step: number;
    status: "idle" | "running" | "completed" | "failed";
}

const fetchScenario = async (id: string): Promise<Scenario> => {
    const res = await fetch(`/api/scenarios/${id}`);
    return res.json();
};

const StatusIcon = ({ status }: { status: string }) => {
    switch (status) {
        case "success":
            return <CheckCircle className="w-5 h-5 text-green-500" />;
        case "failed":
            return <XCircle className="w-5 h-5 text-red-500" />;
        case "running":
            return <Clock className="w-5 h-5 text-blue-500 animate-pulse" />;
        default:
            return <div className="w-5 h-5 rounded-full border-2 border-slate-600" />;
    }
};

interface FlowRunnerProps {
    scenarioId: string;
    onClose: () => void;
}

export function FlowRunner({ scenarioId, onClose }: FlowRunnerProps) {
    const [flowRun, setFlowRun] = useState<FlowRun | null>(null);
    const [isRunning, setIsRunning] = useState(false);

    const { data: scenario, isLoading } = useQuery({
        queryKey: ["scenario", scenarioId],
        queryFn: () => fetchScenario(scenarioId),
    });

    const simulateStep = async (stepIndex: number): Promise<StepResult> => {
        // Simulate network delay
        await new Promise((resolve) => setTimeout(resolve, 800 + Math.random() * 400));

        // 90% success rate for demo
        const success = Math.random() > 0.1;

        return {
            step_index: stepIndex,
            action: scenario?.steps[stepIndex].action || "",
            actor: scenario?.steps[stepIndex].actor || "",
            status: success ? "success" : "failed",
            message: success
                ? `Step completed successfully`
                : `Error: ${["Timeout", "Invalid signature", "Network error"][Math.floor(Math.random() * 3)]}`,
            timestamp: new Date().toISOString(),
        };
    };

    const runFlow = async () => {
        if (!scenario) return;

        setIsRunning(true);
        const steps: StepResult[] = scenario.steps.map((s, i) => ({
            step_index: i,
            action: s.action,
            actor: s.actor,
            status: "pending" as const,
        }));

        setFlowRun({
            scenario_id: scenarioId,
            steps,
            current_step: 0,
            status: "running",
        });

        for (let i = 0; i < scenario.steps.length; i++) {
            // Mark current step as running
            setFlowRun((prev) =>
                prev
                    ? {
                        ...prev,
                        current_step: i,
                        steps: prev.steps.map((s, idx) =>
                            idx === i ? { ...s, status: "running" as const } : s
                        ),
                    }
                    : null
            );

            const result = await simulateStep(i);

            // Update with result
            setFlowRun((prev) =>
                prev
                    ? {
                        ...prev,
                        steps: prev.steps.map((s, idx) => (idx === i ? result : s)),
                    }
                    : null
            );

            if (result.status === "failed") {
                setFlowRun((prev) =>
                    prev ? { ...prev, status: "failed" } : null
                );
                setIsRunning(false);
                return;
            }
        }

        setFlowRun((prev) =>
            prev ? { ...prev, status: "completed" } : null
        );
        setIsRunning(false);
    };

    if (isLoading) {
        return (
            <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                <div className="bg-slate-800 rounded-xl p-8 text-white">Loading...</div>
            </div>
        );
    }

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-slate-800 rounded-2xl w-full max-w-3xl max-h-[90vh] overflow-hidden flex flex-col">
                {/* Header */}
                <div className="p-6 border-b border-slate-700 flex items-center justify-between">
                    <div>
                        <h2 className="text-xl font-bold text-white">{scenario?.name}</h2>
                        <p className="text-sm text-slate-400">{scenario?.description}</p>
                    </div>
                    <div className="flex items-center gap-3">
                        <span className="px-3 py-1 bg-slate-700 text-slate-300 rounded-lg text-sm">
                            {scenario?.protocol}
                        </span>
                        <button
                            onClick={onClose}
                            className="text-slate-400 hover:text-white"
                        >
                            ✕
                        </button>
                    </div>
                </div>

                {/* Timeline */}
                <div className="flex-1 overflow-y-auto p-6">
                    <div className="space-y-4">
                        {scenario?.steps.map((step, idx) => {
                            const stepResult = flowRun?.steps[idx];
                            const isCurrent = flowRun?.current_step === idx && flowRun?.status === "running";

                            return (
                                <div
                                    key={idx}
                                    className={`relative flex items-start gap-4 p-4 rounded-xl transition-colors ${isCurrent
                                        ? "bg-blue-500/10 border border-blue-500/30"
                                        : stepResult?.status === "success"
                                            ? "bg-green-500/5 border border-green-500/20"
                                            : stepResult?.status === "failed"
                                                ? "bg-red-500/10 border border-red-500/30"
                                                : "bg-slate-700/30 border border-slate-700/50"
                                        }`}
                                >
                                    {/* Step number and status */}
                                    <div className="flex flex-col items-center">
                                        <div className="flex items-center justify-center w-8 h-8 rounded-full bg-slate-700 text-sm font-medium text-white">
                                            {idx + 1}
                                        </div>
                                        {idx < scenario.steps.length - 1 && (
                                            <div className="w-0.5 h-8 bg-slate-600 mt-2" />
                                        )}
                                    </div>

                                    {/* Step content */}
                                    <div className="flex-1">
                                        <div className="flex items-center gap-3 mb-1">
                                            <span className="font-medium text-white">{step.action}</span>
                                            <ArrowRight className="w-4 h-4 text-slate-500" />
                                            <span className="px-2 py-0.5 bg-purple-500/20 text-purple-400 rounded text-xs">
                                                {step.actor}
                                            </span>
                                        </div>
                                        {stepResult?.message && (
                                            <p className={`text-sm ${stepResult.status === "failed" ? "text-red-400" : "text-slate-400"
                                                }`}>
                                                {stepResult.message}
                                            </p>
                                        )}
                                        {stepResult?.timestamp && (
                                            <p className="text-xs text-slate-500 mt-1">
                                                {new Date(stepResult.timestamp).toLocaleTimeString()}
                                            </p>
                                        )}
                                    </div>

                                    {/* Status icon */}
                                    <StatusIcon status={stepResult?.status || "pending"} />
                                </div>
                            );
                        })}
                    </div>

                    {/* Error analysis for failed flows */}
                    {flowRun?.status === "failed" && (
                        <div className="mt-6 p-4 bg-red-500/10 border border-red-500/30 rounded-xl">
                            <div className="flex items-center gap-2 text-red-400 mb-2">
                                <AlertTriangle className="w-5 h-5" />
                                <span className="font-medium">Flow Failed</span>
                            </div>
                            <p className="text-sm text-slate-300">
                                The flow failed at step {(flowRun?.current_step || 0) + 1}.
                                Check your implementation's error handling for this state transition.
                            </p>
                        </div>
                    )}

                    {flowRun?.status === "completed" && (
                        <div className="mt-6 p-4 bg-green-500/10 border border-green-500/30 rounded-xl">
                            <div className="flex items-center gap-2 text-green-400 mb-2">
                                <CheckCircle className="w-5 h-5" />
                                <span className="font-medium">Flow Completed Successfully</span>
                            </div>
                            <p className="text-sm text-slate-300">
                                All {scenario?.steps.length} steps completed. Your implementation correctly handles this flow.
                            </p>
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="p-6 border-t border-slate-700 flex justify-end gap-3">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg text-sm font-medium transition-colors"
                    >
                        Close
                    </button>
                    <button
                        onClick={runFlow}
                        disabled={isRunning}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${isRunning
                            ? "bg-slate-600 text-slate-400 cursor-not-allowed"
                            : "bg-green-600 hover:bg-green-500 text-white"
                            }`}
                    >
                        <Play className="w-4 h-4" />
                        {isRunning ? "Running..." : flowRun ? "Run Again" : "Run Flow"}
                    </button>
                </div>
            </div>
        </div>
    );
}
