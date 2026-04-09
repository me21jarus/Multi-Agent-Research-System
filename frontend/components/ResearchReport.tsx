"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface Source {
  title: string;
  url: string;
}

interface ResearchReportProps {
  query: string;
  report: string;
  sources: Source[];
}

export default function ResearchReport({ query, report, sources }: ResearchReportProps) {
  return (
    <div className="w-full bg-[#1a2234] border border-[#1e293b] rounded-2xl overflow-hidden">

      {/* Header */}
      <div className="px-6 py-4 border-b border-[#1e293b] bg-[#151f2e]">
        <div className="flex items-center gap-2 mb-1">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-xs font-semibold text-emerald-400 uppercase tracking-widest">
            Research Complete
          </span>
        </div>
        <p className="text-slate-300 text-sm font-medium">{query}</p>
      </div>

      {/* Report body */}
      <div className="px-6 py-5">
        <div className="markdown">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {report}
          </ReactMarkdown>
        </div>
      </div>

      {/* Sources */}
      {sources.length > 0 && (
        <div className="px-6 py-4 border-t border-[#1e293b] bg-[#151f2e]">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-3">
            Sources
          </p>
          <div className="flex flex-col gap-2">
            {sources.map((source, i) => (
              <a
                key={i}
                href={source.url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-start gap-2 group"
              >
                <span className="text-slate-600 text-xs mt-0.5 shrink-0">{i + 1}.</span>
                <span className="text-indigo-400 group-hover:text-indigo-300 text-xs
                                 underline underline-offset-2 transition-colors line-clamp-1">
                  {source.title}
                </span>
              </a>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
