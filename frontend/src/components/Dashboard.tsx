import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import {
    FlaskConical,
    Route,
    Shield,
    Play,
    AlertTriangle,
    CheckCircle,
    XCircle,
    Clock,
    Info,
} from "lucide-react";
import { FlowRunner } from "./FlowRunner";
import { IS_DEMO_MODE, dashboardApi } from "../services/api";

interface Protocol {
    id: string;
    name: string;
    status: string;
    version?: string;
    description?: string;
    intent_types?: string[];
    lifecycle_states?: string[];
    point_of_no_return?: string;
}

interface Scenario {
    id: string;
    name: string;
    protocol: string;
    description?: string;
    flow_type?: string;
    step_count?: number;
}

interface Control {
    id: string;
    control_name: string;
    control_category: string;
    description: string;
    status: "present" | "partial" | "absent";
    attacks_prevented: string[];
    risk_if_absent: string;
}

const StatusBadge = ({ status }: { status: string }) => {
    const config = {
        present: { bg: "bg-green-100", text: "text-green-800", icon: CheckCircle },
        partial: { bg: "bg-yellow-100", text: "text-yellow-800", icon: AlertTriangle },
        absent: { bg: "bg-red-100", text: "text-red-800", icon: XCircle },
        active: { bg: "bg-green-100", text: "text-green-800", icon: CheckCircle },
    }[status] || { bg: "bg-gray-100", text: "text-gray-800", icon: Clock };

    const Icon = config.icon;

    return (
        <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${config.bg} ${config.text}`}>
            <Icon className="w-3 h-3" />
            {status}
        </span>
    );
};

// Demo mode banner component
const DemoModeBanner = () => (
    <div className="bg-gradient-to-r from-amber-500/20 to-orange-500/20 border border-amber-500/50 rounded-xl p-4 mb-6">
        <div className="flex items-start gap-3">
            <Info className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
            <div>
                <h3 className="text-amber-300 font-medium mb-1">Demo Mode</h3>
                <p className="text-amber-200/80 text-sm">
                    You're viewing the static demo on GitHub Pages. For full functionality with live API calls,
                    run the backend locally:
                </p>
                <pre className="mt-2 p-2 bg-slate-900/50 rounded text-xs text-slate-300 overflow-x-auto">
                    cd backend && uvicorn app.main:app --port 8080
                </pre>
            </div>
        </div>
    </div>
);

// Demo protocols data
const DEMO_PROTOCOLS: Protocol[] = [
    {
        id: "ucp",
        name: "UCP (Stripe)",
        status: "active",
        version: "2026-01-11",
        description: "Universal Commerce Protocol for seamless checkout experiences",
        intent_types: ["purchase", "refund", "subscription"],
        point_of_no_return: "payment_captured"
    },
    {
        id: "acp",
        name: "ACP (Shopify)",
        status: "active",
        version: "2026-01-16",
        description: "Agentic Commerce Protocol with OpenAPI checkout sessions",
        intent_types: ["checkout", "fulfillment"],
        point_of_no_return: "session_completed"
    },
    {
        id: "x402",
        name: "x402 (Coinbase)",
        status: "active",
        version: "2",
        description: "HTTP 402 Payment Required for micropayments and premium content",
        intent_types: ["resource_access", "streaming"],
        point_of_no_return: "settled"
    },
    {
        id: "ap2",
        name: "AP2 (Google)",
        status: "active",
        version: "0.1",
        description: "Agent Payments Protocol with mandates and multi-agent flows",
        intent_types: ["intent_mandate", "cart_mandate", "payment_mandate"],
        point_of_no_return: "payment_authorized"
    }
];

// Demo scenarios data
const DEMO_SCENARIOS: Scenario[] = [
    { id: "ucp_checkout", name: "UCP Checkout Flow", protocol: "UCP", description: "Complete purchase with product selection and payment", flow_type: "happy_path", step_count: 4 },
    { id: "acp_session", name: "ACP Session Create", protocol: "ACP", description: "Create and manage checkout session with fulfillment", flow_type: "happy_path", step_count: 4 },
    { id: "x402_payment", name: "x402 Micropayment", protocol: "x402", description: "Access premium content with crypto micropayment", flow_type: "happy_path", step_count: 4 },
    { id: "ap2_purchase", name: "AP2 Agent Purchase", protocol: "AP2", description: "Multi-agent purchase with OTP verification", flow_type: "happy_path", step_count: 8 },
];

// Demo controls data
const DEMO_CONTROLS: Record<string, Control[]> = {
    AP2: [
        { id: "ap2_sig", control_name: "User Signature", control_category: "Authentication", description: "User signs mandates cryptographically", status: "present", attacks_prevented: ["Unauthorized transactions"], risk_if_absent: "Agent could spend without user consent" },
        { id: "ap2_mandate", control_name: "Spending Limits", control_category: "Authorization", description: "Mandates enforce spending caps", status: "present", attacks_prevented: ["Overspending"], risk_if_absent: "No limit on transaction amounts" },
    ],
    x402: [
        { id: "x402_sig", control_name: "EIP-712 Signature", control_category: "Authentication", description: "Typed data signatures for payments", status: "present", attacks_prevented: ["Signature forgery"], risk_if_absent: "Payments could be forged" },
        { id: "x402_nonce", control_name: "Nonce Tracking", control_category: "Replay Protection", description: "Unique nonces prevent replay attacks", status: "present", attacks_prevented: ["Replay attacks"], risk_if_absent: "Same payment could be replayed" },
    ],
    ACP: [
        { id: "acp_version", control_name: "API Version Header", control_category: "Compatibility", description: "Version negotiation for breaking changes", status: "present", attacks_prevented: ["Version mismatch errors"], risk_if_absent: "Breaking changes affect clients" },
    ],
    UCP: [
        { id: "ucp_webhook", control_name: "Webhook Signatures", control_category: "Authentication", description: "Signed webhooks for event verification", status: "present", attacks_prevented: ["Webhook spoofing"], risk_if_absent: "Fake webhook events accepted" },
    ]
};

export function Dashboard() {
    const [activeTab, setActiveTab] = useState<"protocols" | "scenarios" | "scoreboard">("protocols");
    const [selectedProtocol, setSelectedProtocol] = useState<string>("AP2");
    const [runningScenario, setRunningScenario] = useState<string | null>(null);

    const { data: protocolsData, isLoading: protocolsLoading } = useQuery<Protocol[]>({
        queryKey: ["protocols"],
        queryFn: async (): Promise<Protocol[]> => {
            if (IS_DEMO_MODE) return DEMO_PROTOCOLS;
            const res = await dashboardApi.getProtocols();
            return (res.data || []) as Protocol[];
        },
    });

    const { data: scenariosData, isLoading: scenariosLoading } = useQuery<Scenario[]>({
        queryKey: ["scenarios"],
        queryFn: async (): Promise<Scenario[]> => {
            if (IS_DEMO_MODE) return DEMO_SCENARIOS;
            const res = await dashboardApi.getScenarios();
            return (res.data || []) as Scenario[];
        },
    });

    const { data: controlsData, isLoading: controlsLoading } = useQuery({
        queryKey: ["controls", selectedProtocol],
        queryFn: async () => {
            if (IS_DEMO_MODE) return DEMO_CONTROLS[selectedProtocol] || [];
            const res = await fetch(`/api/protocols/${selectedProtocol}/controls`);
            return res.json();
        },
        enabled: activeTab === "scoreboard",
    });

    const protocols = protocolsData || [];
    const scenarios = scenariosData || [];
    const controls = controlsData || [];

    const tabs = [
        { id: "protocols", label: "Protocols", icon: Route },
        { id: "scenarios", label: "Scenarios", icon: Play },
        { id: "scoreboard", label: "Controls Scoreboard", icon: Shield },
    ] as const;

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
            {/* Header */}
            <header className="border-b border-slate-700/50 bg-slate-900/80 backdrop-blur-sm">
                <div className="container mx-auto px-6 py-4">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl">
                            <FlaskConical className="w-6 h-6 text-white" />
                        </div>
                        <div>
                            <h1 className="text-xl font-bold text-white">AgentPayment Sandbox</h1>
                            <p className="text-xs text-slate-400">
                                Postman + Chaos Monkey + Case Manager
                                {IS_DEMO_MODE && <span className="ml-2 text-amber-400">(Demo Mode)</span>}
                            </p>
                        </div>
                    </div>
                </div>
            </header>

            {/* Navigation */}
            <nav className="border-b border-slate-700/50 bg-slate-800/50">
                <div className="container mx-auto px-6">
                    <div className="flex gap-1">
                        {tabs.map((tab) => {
                            const Icon = tab.icon;
                            return (
                                <button
                                    key={tab.id}
                                    onClick={() => setActiveTab(tab.id)}
                                    className={`flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors ${activeTab === tab.id
                                        ? "text-white border-b-2 border-blue-500"
                                        : "text-slate-400 hover:text-white"
                                        }`}
                                >
                                    <Icon className="w-4 h-4" />
                                    {tab.label}
                                </button>
                            );
                        })}
                    </div>
                </div>
            </nav>

            {/* Content */}
            <main className="container mx-auto px-6 py-8">
                {IS_DEMO_MODE && <DemoModeBanner />}

                {activeTab === "protocols" && (
                    <div className="grid gap-6 md:grid-cols-2">
                        {protocolsLoading ? (
                            <div className="text-slate-400">Loading protocols...</div>
                        ) : (
                            protocols.map((protocol) => (
                                <div
                                    key={protocol.id || protocol.name}
                                    className="p-6 bg-slate-800/50 rounded-2xl border border-slate-700/50 hover:border-blue-500/50 transition-colors"
                                >
                                    <div className="flex items-start justify-between mb-4">
                                        <div>
                                            <h3 className="text-lg font-semibold text-white">{protocol.name}</h3>
                                            <span className="text-xs text-slate-500">v{protocol.version || '1.0'}</span>
                                        </div>
                                        <StatusBadge status={protocol.status} />
                                    </div>
                                    <p className="text-sm text-slate-400 mb-4 line-clamp-2">{protocol.description || 'Protocol description'}</p>
                                    <div className="flex flex-wrap gap-2">
                                        {(protocol.intent_types || []).map((type) => (
                                            <span
                                                key={type}
                                                className="px-2 py-1 bg-slate-700/50 text-slate-300 rounded-lg text-xs"
                                            >
                                                {type}
                                            </span>
                                        ))}
                                    </div>
                                    {protocol.point_of_no_return && (
                                        <div className="mt-4 pt-4 border-t border-slate-700/50">
                                            <div className="flex items-center gap-2 text-xs text-slate-500">
                                                <AlertTriangle className="w-3 h-3 text-amber-500" />
                                                <span>Point of no return: <strong className="text-amber-400">{protocol.point_of_no_return}</strong></span>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            ))
                        )}
                    </div>
                )}

                {activeTab === "scenarios" && (
                    <div className="space-y-4">
                        {scenariosLoading ? (
                            <div className="text-slate-400">Loading scenarios...</div>
                        ) : (
                            scenarios.map((scenario) => (
                                <div
                                    key={scenario.id}
                                    className="p-5 bg-slate-800/50 rounded-xl border border-slate-700/50 hover:border-green-500/50 transition-colors flex items-center justify-between"
                                >
                                    <div className="flex-1">
                                        <div className="flex items-center gap-3 mb-2">
                                            <h3 className="font-medium text-white">{scenario.name}</h3>
                                            <span className="px-2 py-0.5 bg-slate-700 text-slate-300 rounded text-xs">
                                                {scenario.protocol}
                                            </span>
                                            {scenario.flow_type && (
                                                <span className="px-2 py-0.5 bg-purple-500/10 text-purple-400 rounded text-xs">
                                                    {scenario.flow_type}
                                                </span>
                                            )}
                                        </div>
                                        <p className="text-sm text-slate-400">{scenario.description || 'Scenario description'}</p>
                                    </div>
                                    <div className="flex items-center gap-4">
                                        {scenario.step_count && (
                                            <span className="text-xs text-slate-500">{scenario.step_count} steps</span>
                                        )}
                                        <button
                                            onClick={() => setRunningScenario(scenario.id)}
                                            className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-500 text-white rounded-lg text-sm font-medium transition-colors"
                                        >
                                            <Play className="w-4 h-4" />
                                            Run
                                        </button>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                )}

                {activeTab === "scoreboard" && (
                    <div>
                        <div className="flex gap-2 mb-6 flex-wrap">
                            {["AP2", "x402", "ACP", "UCP"].map((p) => (
                                <button
                                    key={p}
                                    onClick={() => setSelectedProtocol(p)}
                                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${selectedProtocol === p
                                        ? "bg-blue-600 text-white"
                                        : "bg-slate-700 text-slate-300 hover:bg-slate-600"
                                        }`}
                                >
                                    {p}
                                </button>
                            ))}
                        </div>

                        <div className="bg-slate-800/50 rounded-xl border border-slate-700/50 overflow-hidden">
                            <table className="w-full">
                                <thead>
                                    <tr className="border-b border-slate-700/50">
                                        <th className="text-left px-4 py-3 text-xs font-medium text-slate-400 uppercase">Control</th>
                                        <th className="text-left px-4 py-3 text-xs font-medium text-slate-400 uppercase">Category</th>
                                        <th className="text-left px-4 py-3 text-xs font-medium text-slate-400 uppercase">Status</th>
                                        <th className="text-left px-4 py-3 text-xs font-medium text-slate-400 uppercase">Attacks Prevented</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {controlsLoading ? (
                                        <tr>
                                            <td colSpan={4} className="px-4 py-8 text-center text-slate-400">
                                                Loading controls...
                                            </td>
                                        </tr>
                                    ) : controls.length === 0 ? (
                                        <tr>
                                            <td colSpan={4} className="px-4 py-8 text-center text-slate-400">
                                                No controls defined for {selectedProtocol}
                                            </td>
                                        </tr>
                                    ) : (
                                        controls.map((control: Control) => (
                                            <tr key={control.id} className="border-b border-slate-700/30 hover:bg-slate-700/20">
                                                <td className="px-4 py-3">
                                                    <div>
                                                        <div className="font-medium text-white">{control.control_name}</div>
                                                        <div className="text-xs text-slate-500">{control.description}</div>
                                                    </div>
                                                </td>
                                                <td className="px-4 py-3">
                                                    <span className="px-2 py-1 bg-slate-700 text-slate-300 rounded text-xs">
                                                        {control.control_category}
                                                    </span>
                                                </td>
                                                <td className="px-4 py-3">
                                                    <StatusBadge status={control.status} />
                                                </td>
                                                <td className="px-4 py-3">
                                                    <div className="flex flex-wrap gap-1">
                                                        {control.attacks_prevented.map((attack) => (
                                                            <span
                                                                key={attack}
                                                                className="px-2 py-0.5 bg-red-500/10 text-red-400 rounded text-xs"
                                                            >
                                                                {attack}
                                                            </span>
                                                        ))}
                                                    </div>
                                                </td>
                                            </tr>
                                        ))
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}
            </main>

            {/* FlowRunner Modal */}
            {runningScenario && (
                <FlowRunner
                    scenarioId={runningScenario}
                    onClose={() => setRunningScenario(null)}
                />
            )}
        </div>
    );
}
