"use client";

import { useState } from "react";
import SearchForm from "@/components/SearchForm";
import AgentProgress from "@/components/AgentProgress";
import ResearchReport from "@/components/ResearchReport";
import { streamResearch, ResearchEvent } from "@/lib/api";

type ReportData = {
  query: string;
  final_report: string;
  sources: { title: string; url: string }[];
};

export default function Home() {
  const [isLoading, setIsLoading]         = useState(false);
  const [completedNodes, setCompletedNodes] = useState<string[]>([]);
  const [currentNode, setCurrentNode]     = useState<string | null>(null);
  const [report, setReport]               = useState<ReportData | null>(null);
  const [error, setError]                 = useState<string | null>(null);

  const handleSearch = async (query: string) => {
    // Reset state
    setIsLoading(true);
    setCompletedNodes([]);
    setCurrentNode(null);
    setReport(null);
    setError(null);

    try {
      await streamResearch(
        query,
        (event: ResearchEvent) => {
          if (event.type === "progress") {
            // Mark the previous current node as done, set new current
            setCurrentNode((prev) => {
              if (prev && prev !== event.node) {
                setCompletedNodes((c) =>
                  c.includes(prev) ? c : [...c, prev]
                );
              }
              return event.node;
            });
          }

          if (event.type === "result") {
            setCurrentNode(null);
            setCompletedNodes(["search", "rag", "summarize", "fact_check", "write"]);
            setReport({
              query:        event.data.query,
              final_report: event.data.final_report,
              sources:      event.data.sources,
            });
          }

          if (event.type === "error") {
            setError(event.message);
          }
        },
        () => {
          setIsLoading(false);
          setCurrentNode(null);
        }
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0f1117]">

      {/* Header */}
      <header className="border-b border-[#1e293b] px-6 py-4">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-2xl">🔬</span>
            <div>
              <h1 className="text-white font-bold text-lg leading-none">
                ResearchAI
              </h1>
              <p className="text-slate-500 text-xs">Multi-Agent Research System</p>
            </div>
          </div>
          <div className="flex items-center gap-2 text-xs text-slate-500">
            <span className="w-2 h-2 rounded-full bg-emerald-400" />
            Powered by Groq · Gemini · LangGraph
          </div>
        </div>
      </header>

      {/* Main */}
      <main className="max-w-5xl mx-auto px-6 py-10">

        {/* Hero — only show when idle */}
        {!isLoading && !report && (
          <div className="text-center mb-10">
            <h2 className="text-4xl font-bold text-white mb-3 tracking-tight">
              Research anything,{" "}
              <span className="text-indigo-400">instantly</span>
            </h2>
            <p className="text-slate-400 text-base max-w-xl mx-auto">
              5 AI agents collaborate — searching the web, summarizing findings,
              fact-checking claims, and writing a structured report in real time.
            </p>
          </div>
        )}

        {/* Search bar */}
        <div className="mb-8">
          <SearchForm onSubmit={handleSearch} isLoading={isLoading} />
        </div>

        {/* Example queries — only when idle */}
        {!isLoading && !report && (
          <div className="flex flex-wrap gap-2 justify-center mb-10">
            {[
              "Latest developments in quantum computing 2025",
              "Impact of AI on healthcare",
              "How does CRISPR gene editing work?",
              "State of renewable energy in 2025",
            ].map((q) => (
              <button
                key={q}
                onClick={() => handleSearch(q)}
                className="px-4 py-2 bg-[#1e293b] hover:bg-[#263548] border border-[#334155]
                           text-slate-400 hover:text-slate-200 text-xs rounded-full transition-colors"
              >
                {q}
              </button>
            ))}
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-xl">
            <p className="text-red-400 text-sm">⚠ {error}</p>
          </div>
        )}

        {/* Two-column layout when loading or done */}
        {(isLoading || report) && (
          <div className="grid grid-cols-1 lg:grid-cols-[280px_1fr] gap-6 items-start">

            {/* Left: Agent progress */}
            <AgentProgress
              completedNodes={completedNodes}
              currentNode={currentNode}
              isLoading={isLoading}
            />

            {/* Right: Report or skeleton */}
            <div>
              {report ? (
                <ResearchReport
                  query={report.query}
                  report={report.final_report}
                  sources={report.sources}
                />
              ) : (
                <div className="bg-[#1a2234] border border-[#1e293b] rounded-2xl p-6 space-y-3">
                  <div className="h-4 bg-[#1e293b] rounded animate-pulse w-3/4" />
                  <div className="h-4 bg-[#1e293b] rounded animate-pulse w-full" />
                  <div className="h-4 bg-[#1e293b] rounded animate-pulse w-5/6" />
                  <div className="h-4 bg-[#1e293b] rounded animate-pulse w-2/3" />
                  <div className="mt-4 h-4 bg-[#1e293b] rounded animate-pulse w-full" />
                  <div className="h-4 bg-[#1e293b] rounded animate-pulse w-4/5" />
                  <p className="text-slate-600 text-xs text-center pt-4">
                    Agents are working...
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

      </main>
    </div>
  );
}
