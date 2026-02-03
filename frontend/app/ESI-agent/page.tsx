"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import {
    Upload,
    FileText,
    Check,
    X,
    Loader2,
    AlertCircle,
    Clock,
    ChevronDown,
    RefreshCw,
    Eye
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

// Type definitions for async job tracking
interface JobInfo {
    job_id: string;
    filename: string;
    status: "PENDING" | "PROCESSING" | "COMPLETED" | "FAILED";
    ledger_name?: string;
    financial_year?: string;
    result?: any;
    error?: string;
    created_at?: string;
}

export default function ESIReceivableAgent() {
    const [activeTab, setActiveTab] = useState<"upload" | "history">("upload");
    const [files, setFiles] = useState<File[]>([]);
    const [ledgerName, setLedgerName] = useState<string>("");
    const [financialYears, setFinancialYears] = useState<string[]>([]);
    const [selectedFY, setSelectedFY] = useState<string>("");
    const [isLoading, setIsLoading] = useState(false);
    const [isUploading, setIsUploading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);

    // Async job tracking state
    const [activeJobs, setActiveJobs] = useState<JobInfo[]>([]);
    const [completedJobs, setCompletedJobs] = useState<JobInfo[]>([]);
    const [selectedJob, setSelectedJob] = useState<JobInfo | null>(null);

    const fileInputRef = useRef<HTMLInputElement>(null);

    // Fetch initial data (financial years)
    useEffect(() => {
        const fetchData = async () => {
            setIsLoading(true);
            try {
                const fyRes = await fetch(`${API_BASE_URL}/api/v1/documents/financial-years`);
                if (fyRes.ok) {
                    const fyData = await fyRes.json();
                    setFinancialYears(fyData);
                    if (fyData.length > 0) setSelectedFY(fyData[0]);
                }
            } catch (err) {
                console.error("Failed to fetch financial years:", err);
            } finally {
                setIsLoading(false);
            }
        };
        fetchData();
    }, []);

    // Poll for job status updates
    const pollJobStatus = useCallback(async (jobId: string): Promise<JobInfo | null> => {
        try {
            const res = await fetch(`${API_BASE_URL}/api/v1/documents/jobs/${jobId}`);
            if (res.ok) {
                return await res.json();
            }
        } catch (e) {
            console.error(`Error polling job ${jobId}:`, e);
        }
        return null;
    }, []);

    // Polling effect for active jobs
    useEffect(() => {
        if (activeJobs.length === 0) return;

        const pollInterval = setInterval(async () => {
            const updatedJobs: JobInfo[] = [];
            const newlyCompleted: JobInfo[] = [];

            for (const job of activeJobs) {
                const updated = await pollJobStatus(job.job_id);
                if (updated) {
                    if (updated.status === "COMPLETED" || updated.status === "FAILED") {
                        newlyCompleted.push(updated);
                    } else {
                        updatedJobs.push(updated);
                    }
                } else {
                    updatedJobs.push(job); // Keep as-is if poll failed
                }
            }

            if (newlyCompleted.length > 0) {
                setCompletedJobs(prev => [...newlyCompleted, ...prev]);
            }
            setActiveJobs(updatedJobs);
        }, 3000); // Poll every 3 seconds

        return () => clearInterval(pollInterval);
    }, [activeJobs, pollJobStatus]);

    // Load existing jobs on mount
    useEffect(() => {
        const loadJobs = async () => {
            try {
                const res = await fetch(`${API_BASE_URL}/api/v1/documents/jobs`);
                if (res.ok) {
                    const data = await res.json();
                    const jobs: JobInfo[] = data.jobs || [];

                    const active = jobs.filter(j => j.status === "PENDING" || j.status === "PROCESSING");
                    const completed = jobs.filter(j => j.status === "COMPLETED" || j.status === "FAILED");

                    setActiveJobs(active);
                    setCompletedJobs(completed);
                }
            } catch (e) {
                console.error("Failed to load jobs:", e);
            }
        };
        loadJobs();
    }, []);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files) {
            setFiles(Array.from(e.target.files));
        }
    };

    const removeFile = (index: number) => {
        setFiles(files.filter((_, i) => i !== index));
    };

    const handleUpload = async (e: React.FormEvent) => {
        e.preventDefault();
        if (files.length === 0) {
            setError("Please select at least one file to upload.");
            return;
        }
        // Ledger name and financial year are optional

        setIsUploading(true);
        setError(null);
        setSuccess(null);

        const formData = new FormData();
        files.forEach(file => formData.append("files", file));
        if (ledgerName.trim()) formData.append("ledger_names", ledgerName.trim());
        if (selectedFY) formData.append("financial_year", selectedFY);

        try {
            const response = await fetch(`${API_BASE_URL}/api/v1/documents/upload`, {
                method: "POST",
                body: formData,
            });

            if (response.ok) {
                const result = await response.json();
                const newJobs: JobInfo[] = result.jobs.map((j: any) => ({
                    job_id: j.job_id,
                    filename: j.filename,
                    status: j.status,
                    ledger_name: ledgerName,
                    financial_year: selectedFY
                }));

                setActiveJobs(prev => [...newJobs, ...prev]);
                setSuccess(`Successfully queued ${files.length} document(s) for AI analysis.`);
                setFiles([]);
                setLedgerName("");

                // Switch to history tab to show progress
                setActiveTab("history");
            } else {
                const errorData = await response.json();
                setError(errorData.detail || "Failed to upload documents.");
            }
        } catch (err) {
            setError("Network error: Could not upload documents.");
        } finally {
            setIsUploading(false);
        }
    };

    const getStatusBadge = (status: JobInfo["status"]) => {
        const styles = {
            PENDING: "bg-amber-100 text-amber-700",
            PROCESSING: "bg-blue-100 text-blue-700",
            COMPLETED: "bg-emerald-100 text-emerald-700",
            FAILED: "bg-red-100 text-red-700"
        };
        return (
            <span className={cn("rounded-full px-2.5 py-0.5 text-[10px] font-semibold uppercase", styles[status])}>
                {status}
            </span>
        );
    };

    const activeJobCount = activeJobs.length;

    return (
        <div className="mx-auto max-w-5xl space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-slate-900">ESI Agent</h1>
                    <p className="text-slate-500">Automate your ESI document management and reconciliation.</p>
                </div>
                <div className="flex gap-2 rounded-lg bg-slate-200/50 p-1">
                    <button
                        onClick={() => setActiveTab("upload")}
                        className={cn(
                            "rounded-md px-4 py-1.5 text-sm font-medium transition-all",
                            activeTab === "upload" ? "bg-white text-indigo-600 shadow-sm" : "text-slate-600 hover:text-slate-900"
                        )}
                    >
                        Upload
                    </button>
                    <button
                        onClick={() => setActiveTab("history")}
                        className={cn(
                            "rounded-md px-4 py-1.5 text-sm font-medium transition-all flex items-center gap-2",
                            activeTab === "history" ? "bg-white text-indigo-600 shadow-sm" : "text-slate-600 hover:text-slate-900"
                        )}
                    >
                        Processing History
                        {activeJobCount > 0 && (
                            <span className="flex h-5 w-5 items-center justify-center rounded-full bg-indigo-600 text-[10px] font-bold text-white">
                                {activeJobCount}
                            </span>
                        )}
                    </button>
                </div>
            </div>

            {/* Alerts */}
            {error && (
                <div className="flex items-center gap-3 rounded-lg border border-red-100 bg-red-50 p-4 text-red-700">
                    <AlertCircle className="h-5 w-5" />
                    <p className="text-sm font-medium">{error}</p>
                    <button onClick={() => setError(null)} className="ml-auto"><X className="h-4 w-4" /></button>
                </div>
            )}
            {success && (
                <div className="flex items-center gap-3 rounded-lg border border-emerald-100 bg-emerald-50 p-4 text-emerald-700">
                    <Check className="h-5 w-5" />
                    <p className="text-sm font-medium">{success}</p>
                    <button onClick={() => setSuccess(null)} className="ml-auto"><X className="h-4 w-4" /></button>
                </div>
            )}

            {activeTab === "upload" ? (
                /* Upload Tab */
                <div className="grid gap-8 lg:grid-cols-3">
                    <div className="lg:col-span-2 space-y-6">
                        <Card className="border-slate-200 shadow-sm">
                            <CardHeader>
                                <CardTitle className="text-lg">Document Upload</CardTitle>
                                <CardDescription>Upload your 26AS, AIS/TIS or Ledger statements for AI analysis.</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div
                                    className={cn(
                                        "relative flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-slate-200 bg-slate-50/50 p-12 transition-all hover:bg-slate-100/50",
                                        files.length > 0 && "border-indigo-100 bg-indigo-50/20"
                                    )}
                                    onClick={() => fileInputRef.current?.click()}
                                >
                                    <input
                                        type="file"
                                        ref={fileInputRef}
                                        onChange={handleFileChange}
                                        className="hidden"
                                        multiple
                                        accept=".pdf,.jpg,.jpeg,.png,.xlsx,.xls,.csv"
                                    />
                                    <div className="rounded-full bg-white p-4 shadow-sm ring-1 ring-slate-100">
                                        <Upload className="h-6 w-6 text-indigo-600" />
                                    </div>
                                    <div className="mt-4 text-center">
                                        <p className="font-semibold text-slate-900">Click to upload or drag and drop</p>
                                        <p className="text-xs text-slate-500 mt-1">PDF, Excel, or CSV (up to 20MB)</p>
                                    </div>
                                </div>

                                {files.length > 0 && (
                                    <div className="mt-6 space-y-3">
                                        <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                                            Selected Files ({files.length})
                                        </p>
                                        {files.map((file, idx) => (
                                            <div key={idx} className="flex items-center justify-between rounded-lg border bg-white p-3 shadow-sm">
                                                <div className="flex items-center gap-3">
                                                    <div className="rounded bg-indigo-50 p-2">
                                                        <FileText className="h-4 w-4 text-indigo-600" />
                                                    </div>
                                                    <div>
                                                        <p className="text-sm font-medium text-slate-900">{file.name}</p>
                                                        <p className="text-[10px] text-slate-500">{(file.size / 1024).toFixed(1)} KB</p>
                                                    </div>
                                                </div>
                                                <button
                                                    onClick={(e) => { e.stopPropagation(); removeFile(idx); }}
                                                    className="rounded-full p-1 text-slate-400 hover:bg-slate-100 hover:text-red-500"
                                                >
                                                    <X className="h-4 w-4" />
                                                </button>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </CardContent>
                        </Card>

                        <div className="flex justify-end gap-3">
                            <Button variant="outline" onClick={() => setFiles([])} disabled={files.length === 0 || isUploading}>
                                Clear All
                            </Button>
                            <Button
                                onClick={handleUpload}
                                disabled={files.length === 0 || isUploading}
                                className="bg-indigo-600 hover:bg-indigo-700"
                            >
                                {isUploading ? (
                                    <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Uploading...</>
                                ) : (
                                    "Start Async Analysis"
                                )}
                            </Button>
                        </div>
                    </div>

                    <div className="space-y-6">
                        <Card className="border-slate-200 shadow-sm">
                            <CardHeader>
                                <CardTitle className="text-lg">Metadata</CardTitle>
                                <CardDescription>Associate information with these documents.</CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-6">
                                <div className="space-y-2">
                                    <Label className="text-sm font-semibold">Financial Year</Label>
                                    <div className="relative">
                                        <select
                                            value={selectedFY}
                                            onChange={(e) => setSelectedFY(e.target.value)}
                                            className="w-full appearance-none rounded-md border border-slate-200 bg-white px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                                        >
                                            {financialYears.map(fy => (
                                                <option key={fy} value={fy}>{fy}</option>
                                            ))}
                                        </select>
                                        <ChevronDown className="absolute right-3 top-2.5 h-4 w-4 text-slate-400 pointer-events-none" />
                                    </div>
                                </div>
                                <div className="space-y-3">
                                    <Label className="text-sm font-semibold">Ledger Name</Label>
                                    <div className="relative">
                                        <FileText className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
                                        <Input
                                            placeholder="Enter ledger name..."
                                            className="pl-9 text-sm"
                                            value={ledgerName}
                                            onChange={(e) => setLedgerName(e.target.value)}
                                        />
                                    </div>
                                </div>
                            </CardContent>
                        </Card>

                        <div className="rounded-xl bg-gradient-to-br from-indigo-600 to-indigo-700 p-6 text-white shadow-lg">
                            <h4 className="font-semibold">Async Processing</h4>
                            <p className="mt-2 text-sm text-indigo-100">
                                Documents are processed in the background. Check the History tab to view real-time status updates.
                            </p>
                        </div>
                    </div>
                </div>
            ) : (
                /* History Tab */
                <div className="space-y-6">
                    {/* Active Jobs Section */}
                    {activeJobs.length > 0 && (
                        <Card className="border-indigo-100 bg-indigo-50/30 shadow-sm">
                            <CardHeader className="pb-3">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <CardTitle className="text-base font-bold text-indigo-900">Active Processing</CardTitle>
                                        <CardDescription className="text-xs text-indigo-600">AI is analyzing your documents...</CardDescription>
                                    </div>
                                    <RefreshCw className="h-4 w-4 animate-spin text-indigo-500" />
                                </div>
                            </CardHeader>
                            <CardContent className="space-y-3">
                                {activeJobs.map(job => (
                                    <div key={job.job_id} className="flex items-center justify-between rounded-lg border border-indigo-100 bg-white p-4 shadow-sm">
                                        <div className="flex items-center gap-4">
                                            <div className="rounded-lg bg-indigo-50 p-2.5">
                                                <Loader2 className="h-5 w-5 animate-spin text-indigo-600" />
                                            </div>
                                            <div>
                                                <p className="font-medium text-slate-900">{job.filename}</p>
                                                <p className="text-[10px] text-slate-500">
                                                    {job.ledger_name} • {job.financial_year} • ID: {job.job_id.slice(0, 8)}...
                                                </p>
                                            </div>
                                        </div>
                                        {getStatusBadge(job.status)}
                                    </div>
                                ))}
                            </CardContent>
                        </Card>
                    )}

                    {/* Completed Jobs Section */}
                    <Card className="border-slate-200 shadow-sm">
                        <CardHeader>
                            <CardTitle className="text-base font-bold">Processing Results</CardTitle>
                            <CardDescription className="text-xs">View extraction results and AI analysis.</CardDescription>
                        </CardHeader>
                        <CardContent>
                            {completedJobs.length > 0 ? (
                                <div className="space-y-3">
                                    {completedJobs.map(job => (
                                        <div
                                            key={job.job_id}
                                            className="group cursor-pointer rounded-lg border border-slate-100 bg-white p-4 shadow-sm transition-all hover:border-indigo-200 hover:shadow-md"
                                            onClick={() => setSelectedJob(selectedJob?.job_id === job.job_id ? null : job)}
                                        >
                                            <div className="flex items-center justify-between">
                                                <div className="flex items-center gap-4">
                                                    <div className={cn(
                                                        "rounded-lg p-2.5",
                                                        job.status === "COMPLETED" ? "bg-emerald-50" : "bg-red-50"
                                                    )}>
                                                        {job.status === "COMPLETED"
                                                            ? <Check className="h-5 w-5 text-emerald-600" />
                                                            : <X className="h-5 w-5 text-red-600" />
                                                        }
                                                    </div>
                                                    <div>
                                                        <p className="font-medium text-slate-900">{job.filename}</p>
                                                        <p className="text-[10px] text-slate-500">
                                                            {job.ledger_name} • {job.financial_year} • ID: {job.job_id.slice(0, 8)}...
                                                        </p>
                                                    </div>
                                                </div>
                                                <div className="flex items-center gap-3">
                                                    {getStatusBadge(job.status)}
                                                    <Eye className="h-4 w-4 text-slate-400 group-hover:text-indigo-500" />
                                                </div>
                                            </div>

                                            {/* Expanded Details */}
                                            {selectedJob?.job_id === job.job_id && (
                                                <div className="mt-4 rounded-lg bg-slate-50 p-4">
                                                    <p className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
                                                        {job.status === "COMPLETED" ? "Extraction Results" : "Error Details"}
                                                    </p>
                                                    <pre className="max-h-64 overflow-auto text-[11px] font-mono text-slate-700 whitespace-pre-wrap">
                                                        {job.status === "COMPLETED"
                                                            ? JSON.stringify(job.result, null, 2)
                                                            : job.error || "Unknown error occurred"
                                                        }
                                                    </pre>
                                                </div>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className="flex flex-col items-center justify-center py-12 text-center">
                                    <div className="rounded-full bg-slate-100 p-4">
                                        <Clock className="h-8 w-8 text-slate-400" />
                                    </div>
                                    <h3 className="mt-4 font-semibold text-slate-900">No completed jobs yet</h3>
                                    <p className="mt-1 text-sm text-slate-500">Upload documents to start async processing.</p>
                                    <Button variant="outline" className="mt-6" onClick={() => setActiveTab("upload")}>
                                        Upload your first document
                                    </Button>
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </div>
            )}
        </div>
    );
}
