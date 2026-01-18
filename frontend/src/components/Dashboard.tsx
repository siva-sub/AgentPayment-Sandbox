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
} from "lucide-react";
import { FlowRunner } from "./FlowRunner";

interface Protocol {
    name: string;
    version: string;
    description: string;
    intent_types: string[];
    lifecycle_states: string[];
    point_of_no_return: string;
}

interface Scenario {
    id: string;
    name: string;
    protocol: string;
    description: string;
    flow_type: string;
    step_count: number;
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

const fetchProtocols = async (): Promise<Protocol[]> => {
    const res = await fetch("/api/protocols");
    return res.json();
};

const fetchScenarios = async (): Promise<Scenario[]> => {
    const res = await fetch("/api/scenarios");
    return res.json();
};

const fetchControls = async (protocol: string): Promise<Control[]> => {
    const res = await fetch(`/api/protocols/${protocol}/controls`);
    return res.json();
};

const StatusBadge = ({ status }: { status: string }) => {
    const config = {
        present: { bg: "bg-green-100", text: "text-green-800", icon: CheckCircle },
        partial: { bg: "bg-yellow-100", text: "text-yellow-800", icon: AlertTriangle },
        absent: { bg: "bg-red-100", text: "text-red-800", icon: XCircle },
    }[status] || { bg: "bg-gray-100", text: "text-gray-800", icon: Clock };

    const Icon = config.icon;

    return (
        <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${config.bg} ${config.text}`}>
            <Icon className="w-3 h-3" />
            {status}
        </span>
    );
};

export function Dashboard() {
    const [activeTab, setActiveTab] = useState<"protocols" | "scenarios" | "scoreboard">("protocols");
    const [selectedProtocol, setSelectedProtocol] = useState<string>("AP2");
    const [runningScenario, setRunningScenario] = useState<string | null>(null);

    const { data: protocols, isLoading: protocolsLoading } = useQuery({
        queryKey: ["protocols"],
        queryFn: fetchProtocols,
    });

    const { data: scenarios, isLoading: scenariosLoading } = useQuery({
        queryKey: ["scenarios"],
        queryFn: fetchScenarios,
    });

    const { data: controls, isLoading: controlsLoading } = useQuery({
        queryKey: ["controls", selectedProtocol],
        queryFn: () => fetchControls(selectedProtocol),
        enabled: activeTab === "scoreboard",
    });

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
                            <p className="text-xs text-slate-400">Postman + Chaos Monkey + Case Manager</p>
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
                {activeTab === "protocols" && (
                    <div className="grid gap-6 md:grid-cols-2">
                        {protocolsLoading ? (
                            <div className="text-slate-400">Loading protocols...</div>
                        ) : (
                            protocols?.map((protocol) => (
                                <div
                                    key={protocol.name}
                                    className="p-6 bg-slate-800/50 rounded-2xl border border-slate-700/50 hover:border-blue-500/50 transition-colors"
                                >
                                    <div className="flex items-start justify-between mb-4">
                                        <div>
                                            <h3 className="text-lg font-semibold text-white">{protocol.name}</h3>
                                            <span className="text-xs text-slate-500">v{protocol.version}</span>
                                        </div>
                                        <span className="px-2 py-1 bg-blue-500/10 text-blue-400 rounded-lg text-xs">
                                            {protocol.intent_types.length} intent types
                                        </span>
                                    </div>
                                    <p className="text-sm text-slate-400 mb-4 line-clamp-2">{protocol.description}</p>
                                    <div className="flex flex-wrap gap-2">
                                        {protocol.intent_types.map((type) => (
                                            <span
                                                key={type}
                                                className="px-2 py-1 bg-slate-700/50 text-slate-300 rounded-lg text-xs"
                                            >
                                                {type}
                                            </span>
                                        ))}
                                    </div>
                                    <div className="mt-4 pt-4 border-t border-slate-700/50">
                                        <div className="flex items-center gap-2 text-xs text-slate-500">
                                            <AlertTriangle className="w-3 h-3 text-amber-500" />
                                            <span>Point of no return: <strong className="text-amber-400">{protocol.point_of_no_return}</strong></span>
                                        </div>
                                    </div>
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
                            scenarios?.map((scenario) => (
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
                                            <span className="px-2 py-0.5 bg-purple-500/10 text-purple-400 rounded text-xs">
                                                {scenario.flow_type}
                                            </span>
                                        </div>
                                        <p className="text-sm text-slate-400">{scenario.description}</p>
                                    </div>
                                    <div className="flex items-center gap-4">
                                        <span className="text-xs text-slate-500">{scenario.step_count} steps</span>
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
                                    ) : (
                                        controls?.map((control) => (
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
