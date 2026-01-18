import { useState, useEffect } from "react";
import { AlertCircle, CheckCircle, Copy, Check } from "lucide-react";

interface ValidationResult {
    valid: boolean;
    errors: ValidationError[];
    warnings: ValidationWarning[];
    securityScore: number;
}

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

interface PayloadEditorProps {
    payload: object;
    onChange: (payload: object) => void;
    validation?: ValidationResult;
    readOnly?: boolean;
}

export function PayloadEditor({
    payload,
    onChange,
    validation,
    readOnly = false,
}: PayloadEditorProps) {
    const [jsonString, setJsonString] = useState(JSON.stringify(payload, null, 2));
    const [parseError, setParseError] = useState<string | null>(null);
    const [copied, setCopied] = useState(false);

    useEffect(() => {
        setJsonString(JSON.stringify(payload, null, 2));
    }, [payload]);

    const handleChange = (value: string) => {
        setJsonString(value);
        try {
            const parsed = JSON.parse(value);
            setParseError(null);
            onChange(parsed);
        } catch (e) {
            setParseError((e as Error).message);
        }
    };

    const handleCopy = async () => {
        await navigator.clipboard.writeText(jsonString);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className="flex flex-col h-full">
            {/* Header */}
            <div className="flex items-center justify-between p-3 bg-slate-800 border-b border-slate-700">
                <span className="text-sm font-medium text-slate-300">Request Payload</span>
                <button
                    onClick={handleCopy}
                    className="flex items-center gap-1 px-2 py-1 text-xs text-slate-400 hover:text-white transition-colors"
                >
                    {copied ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                    {copied ? "Copied" : "Copy"}
                </button>
            </div>

            {/* Editor */}
            <div className="flex-1 relative">
                <textarea
                    value={jsonString}
                    onChange={(e) => handleChange(e.target.value)}
                    readOnly={readOnly}
                    spellCheck={false}
                    className={`
            w-full h-full p-4 bg-slate-900 text-slate-100 font-mono text-sm
            resize-none focus:outline-none focus:ring-2 focus:ring-blue-500/50
            ${parseError ? "border-2 border-red-500" : "border-transparent"}
            ${readOnly ? "opacity-75" : ""}
          `}
                    style={{ minHeight: "300px" }}
                />

                {/* Parse Error */}
                {parseError && (
                    <div className="absolute bottom-0 left-0 right-0 p-2 bg-red-500/20 border-t border-red-500">
                        <div className="flex items-center gap-2 text-sm text-red-400">
                            <AlertCircle className="w-4 h-4" />
                            <span>JSON Parse Error: {parseError}</span>
                        </div>
                    </div>
                )}
            </div>

            {/* Validation Summary */}
            {validation && (
                <div className="p-3 bg-slate-800 border-t border-slate-700">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            {validation.valid ? (
                                <CheckCircle className="w-5 h-5 text-green-500" />
                            ) : (
                                <AlertCircle className="w-5 h-5 text-red-500" />
                            )}
                            <span
                                className={`text-sm font-medium ${validation.valid ? "text-green-400" : "text-red-400"
                                    }`}
                            >
                                {validation.valid
                                    ? "Schema Valid"
                                    : `${validation.errors.length} Error${validation.errors.length > 1 ? "s" : ""}`}
                            </span>
                        </div>
                        <div className="flex items-center gap-2">
                            <span className="text-xs text-slate-500">Security Score</span>
                            <span
                                className={`text-sm font-bold ${validation.securityScore >= 80
                                        ? "text-green-400"
                                        : validation.securityScore >= 50
                                            ? "text-yellow-400"
                                            : "text-red-400"
                                    }`}
                            >
                                {validation.securityScore}/100
                            </span>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
