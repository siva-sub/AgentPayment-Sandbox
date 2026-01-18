import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";
import { Dashboard } from "./components/Dashboard";
import { Playground } from "./components/Playground";
import "./index.css";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30000,
      refetchOnWindowFocus: false,
    },
  },
});

type Page = "dashboard" | "playground";

function App() {
  const [page, setPage] = useState<Page>("playground");

  return (
    <QueryClientProvider client={queryClient}>
      {/* Navigation */}
      <nav className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 bg-slate-900/90 backdrop-blur-sm border border-slate-700 rounded-full px-2 py-1">
        <div className="flex items-center gap-1">
          <button
            onClick={() => setPage("playground")}
            className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${page === "playground"
                ? "bg-blue-600 text-white"
                : "text-slate-400 hover:text-white"
              }`}
          >
            Playground
          </button>
          <button
            onClick={() => setPage("dashboard")}
            className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${page === "dashboard"
                ? "bg-blue-600 text-white"
                : "text-slate-400 hover:text-white"
              }`}
          >
            Dashboard
          </button>
        </div>
      </nav>

      {/* Content */}
      {page === "playground" ? <Playground /> : <Dashboard />}
    </QueryClientProvider>
  );
}

export default App;

