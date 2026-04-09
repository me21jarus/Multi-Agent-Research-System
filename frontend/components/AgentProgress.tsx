"use client";

export type AgentStep = {
  node: string;
  message: string;
  status: "pending" | "running" | "done";
};

const AGENT_ORDER = ["search", "rag", "summarize", "fact_check", "write"];

const AGENT_LABELS: Record<string, { label: string; icon: string }> = {
  search:     { label: "Search Agent",       icon: "🔍" },
  rag:        { label: "RAG Agent",           icon: "🧠" },
  summarize:  { label: "Summarizer Agent",    icon: "📝" },
  fact_check: { label: "Fact-Checker Agent",  icon: "✅" },
  write:      { label: "Writer Agent",        icon: "✍️" },
};

interface AgentProgressProps {
  completedNodes: string[];
  currentNode: string | null;
  isLoading: boolean;
}

export default function AgentProgress({
  completedNodes,
  currentNode,
  isLoading,
}: AgentProgressProps) {
  if (!isLoading && completedNodes.length === 0) return null;

  return (
    <div className="w-full bg-[#1a2234] border border-[#1e293b] rounded-2xl p-5">
      <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-4">
        Agent Pipeline
      </h3>
      <div className="flex flex-col gap-2">
        {AGENT_ORDER.map((node, idx) => {
          const isDone    = completedNodes.includes(node);
          const isRunning = currentNode === node;
          const isPending = !isDone && !isRunning;
          const meta      = AGENT_LABELS[node];

          return (
            <div
              key={node}
              className={`flex items-center gap-3 p-3 rounded-xl transition-all duration-300
                ${isDone    ? "bg-[#0f2a1e] border border-[#1a4a30]" : ""}
                ${isRunning ? "bg-[#1e1b4b] border border-indigo-500/40 animate-pulse" : ""}
                ${isPending ? "opacity-40" : ""}
              `}
            >
              {/* Step number / check */}
              <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold shrink-0
                ${isDone    ? "bg-emerald-500/20 text-emerald-400" : ""}
                ${isRunning ? "bg-indigo-500/20 text-indigo-400" : ""}
                ${isPending ? "bg-slate-700 text-slate-500" : ""}
              `}>
                {isDone ? "✓" : idx + 1}
              </div>

              {/* Label */}
              <div className="flex-1 min-w-0">
                <p className={`text-sm font-medium
                  ${isDone    ? "text-emerald-400" : ""}
                  ${isRunning ? "text-indigo-300" : ""}
                  ${isPending ? "text-slate-500" : ""}
                `}>
                  {meta.icon} {meta.label}
                </p>
              </div>

              {/* Status */}
              {isRunning && (
                <div className="flex gap-1">
                  {[0, 1, 2].map((i) => (
                    <div
                      key={i}
                      className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce"
                      style={{ animationDelay: `${i * 0.15}s` }}
                    />
                  ))}
                </div>
              )}
              {isDone && (
                <span className="text-xs text-emerald-500">Done</span>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
