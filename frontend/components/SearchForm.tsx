"use client";

interface SearchFormProps {
  onSubmit: (query: string) => void;
  isLoading: boolean;
}

export default function SearchForm({ onSubmit, isLoading }: SearchFormProps) {
  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = e.currentTarget;
    const query = (form.elements.namedItem("query") as HTMLInputElement).value.trim();
    if (query) onSubmit(query);
  };

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="flex gap-3">
        <input
          name="query"
          type="text"
          placeholder="e.g. What are the latest breakthroughs in quantum computing?"
          disabled={isLoading}
          className="flex-1 bg-[#1e293b] border border-[#334155] rounded-xl px-5 py-4
                     text-slate-200 placeholder-slate-500 text-sm
                     focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500
                     disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        />
        <button
          type="submit"
          disabled={isLoading}
          className="px-6 py-4 bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700
                     text-white font-semibold rounded-xl text-sm
                     disabled:opacity-50 disabled:cursor-not-allowed
                     transition-colors whitespace-nowrap"
        >
          {isLoading ? "Researching..." : "Research"}
        </button>
      </div>
    </form>
  );
}
