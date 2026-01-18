import { AlertTriangle, CheckCircle, XCircle, ExternalLink, Code } from "lucide-react";

interface ValidationError {
    path: string;
    message: string;
    expected: string;
    got: string;
    fix: string;
    specRef?: string;
}

interface ValidationWarning {
    path: string;
    message: string;
    recommendation: string;
}

interface ErrorCardProps {
    error: ValidationError;
}

export function ErrorCard({ error }: ErrorCardProps) {
    return (
        <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-xl">
            <div className="flex items-start gap-3">
                <XCircle className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" />
                <div className="flex-1">
                    {/* Error Message */}
                    <div className="flex items-center gap-2 mb-2">
                        <span className="font-medium text-red-400">ERROR</span>
                        <code className="px-2 py-0.5 bg-slate-800 text-slate-300 rounded text-xs">
                            {error.path}
                        </code>
                    </div>
                    <p className="text-sm text-white mb-3">{error.message}</p>

                    {/* Expected vs Got */}
                    <div className="grid grid-cols-2 gap-3 mb-3">
                        <div className="p-2 bg-slate-800/50 rounded">
                            <span className="text-xs text-slate-500 block mb-1">EXPECTED</span>
                            <code className="text-xs text-green-400">{error.expected}</code>
                        </div>
                        <div className="p-2 bg-slate-800/50 rounded">
                            <span className="text-xs text-slate-500 block mb-1">GOT</span>
                            <code className="text-xs text-red-400">{error.got || "null"}</code>
                        </div>
                    </div>

                    {/* Fix Recommendation */}
                    <div className="p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg">
                        <div className="flex items-center gap-2 mb-2">
                            <Code className="w-4 h-4 text-blue-400" />
                            <span className="text-xs font-medium text-blue-400">FIX</span>
                        </div>
                        <pre className="text-xs text-slate-300 whitespace-pre-wrap font-mono">
                            {error.fix}
                        </pre>
                    </div>

                    {/* Spec Reference */}
                    {error.specRef && (
                        <a
                            href={error.specRef}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1 mt-3 text-xs text-blue-400 hover:text-blue-300"
                        >
                            <ExternalLink className="w-3 h-3" />
                            View Specification
                        </a>
                    )}
                </div>
            </div>
        </div>
    );
}

interface WarningCardProps {
    warning: ValidationWarning;
}

export function WarningCard({ warning }: WarningCardProps) {
    return (
        <div className="p-4 bg-yellow-500/10 border border-yellow-500/30 rounded-xl">
            <div className="flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-yellow-500 mt-0.5 flex-shrink-0" />
                <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                        <span className="font-medium text-yellow-400">WARNING</span>
                        <code className="px-2 py-0.5 bg-slate-800 text-slate-300 rounded text-xs">
                            {warning.path}
                        </code>
                    </div>
                    <p className="text-sm text-white mb-2">{warning.message}</p>
                    <p className="text-sm text-slate-400">{warning.recommendation}</p>
                </div>
            </div>
        </div>
    );
}

interface SuccessCardProps {
    message: string;
    details?: string;
}

export function SuccessCard({ message, details }: SuccessCardProps) {
    return (
        <div className="p-4 bg-green-500/10 border border-green-500/30 rounded-xl">
            <div className="flex items-start gap-3">
                <CheckCircle className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
                <div>
                    <span className="font-medium text-green-400">{message}</span>
                    {details && <p className="text-sm text-slate-400 mt-1">{details}</p>}
                </div>
            </div>
        </div>
    );
}
