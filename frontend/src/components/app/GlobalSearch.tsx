import { FormEvent, KeyboardEvent as ReactKeyboardEvent, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import { reportsApi } from "@/services/api";

type Result = { type: string; title: string; subtitle?: string; url: string };

export default function GlobalSearch() {
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [focusedIndex, setFocusedIndex] = useState(-1);
  const enabled = open && query.trim().length >= 2;
  const { data } = useQuery({
    queryKey: ["global-search", query],
    queryFn: () => reportsApi.globalSearch(query).then((r) => r.data),
    enabled,
  });
  const staticResults = useMemo<Result[]>(() => [
    { type: "Page", title: "Dashboard", url: "/dashboard" },
    { type: "Page", title: "Payroll", subtitle: "Run, pre-checks, payslips", url: "/payroll" },
    { type: "Page", title: "ESS Profile", subtitle: "Photo, completeness, change requests", url: "/profile" },
    { type: "Page", title: "Talent", subtitle: "OKR, 360, competencies", url: "/performance" },
    { type: "Page", title: "Org Chart", subtitle: "Company hierarchy", url: "/company" },
  ], []);
  const results: Result[] = enabled ? (data?.results || []) : staticResults;

  useEffect(() => {
    setFocusedIndex(-1);
  }, [query]);

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setOpen(true);
      }
      if (event.altKey && event.key.toLowerCase() === "h") navigate("/dashboard");
      if (event.altKey && event.key.toLowerCase() === "p") navigate("/payroll");
      if (event.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [navigate]);

  function submit(event: FormEvent) {
    event.preventDefault();
    const selected = (focusedIndex >= 0 ? results[focusedIndex] : undefined) || results[0];
    if (selected) {
      navigate(selected.url);
      setOpen(false);
    }
  }

  function handleSearchKeyDown(event: ReactKeyboardEvent<HTMLInputElement>) {
    if (event.key === "ArrowDown") {
      event.preventDefault();
      setFocusedIndex((current) => (results.length ? (current + 1) % results.length : -1));
    }
    if (event.key === "ArrowUp") {
      event.preventDefault();
      setFocusedIndex((current) => (results.length ? (current <= 0 ? results.length - 1 : current - 1) : -1));
    }
  }

  return (
    <>
      <button
        type="button"
        className="relative hidden max-w-md flex-1 sm:flex"
        onClick={() => setOpen(true)}
      >
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input readOnly value="" placeholder="Search employees, payroll, policies...  Cmd+K" className="cursor-pointer border-0 bg-secondary/50 pl-9 focus-visible:ring-1" />
      </button>
      {open && (
        <div className="fixed inset-0 z-50 bg-black/40 p-4 pt-[12vh]" onClick={() => setOpen(false)}>
          <div className="mx-auto max-w-2xl rounded-lg border bg-background shadow-2xl" onClick={(e) => e.stopPropagation()}>
            <form onSubmit={submit} className="border-b p-3">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input autoFocus value={query} onChange={(e) => setQuery(e.target.value)} onKeyDown={handleSearchKeyDown} placeholder="Search anything..." className="border-0 pl-9 text-base focus-visible:ring-0" />
              </div>
            </form>
            <div className="max-h-[420px] overflow-y-auto p-2">
              {results.length ? results.map((item, index) => (
                <button
                  key={`${item.type}-${item.title}-${index}`}
                  className={`flex w-full items-center justify-between rounded-md p-3 text-left hover:bg-muted ${focusedIndex === index ? "bg-accent" : ""}`}
                  onClick={() => {
                    navigate(item.url);
                    setOpen(false);
                  }}
                >
                  <div>
                    <p className="text-sm font-medium">{item.title}</p>
                    <p className="text-xs text-muted-foreground">{item.subtitle || item.type}</p>
                  </div>
                  <span className="rounded bg-muted px-2 py-1 text-[10px] font-semibold uppercase text-muted-foreground">{item.type}</span>
                </button>
              )) : (
                <div className="p-8 text-center text-sm text-muted-foreground">No results found</div>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
