import { useEffect, useState } from "react";
import { Keyboard } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function KeyboardShortcuts() {
  const [open, setOpen] = useState(false);
  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "?" && !event.ctrlKey && !event.metaKey) setOpen(true);
      if (event.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);
  return (
    <>
      <Button variant="ghost" size="icon" title="Keyboard shortcuts" aria-label="Keyboard shortcuts" onClick={() => setOpen(true)}>
        <Keyboard className="h-5 w-5" />
      </Button>
      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" onClick={() => setOpen(false)}>
          <div className="w-full max-w-md rounded-lg border bg-background p-5 shadow-xl" onClick={(e) => e.stopPropagation()}>
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-lg font-semibold">Keyboard Shortcuts</h2>
              <Button variant="ghost" size="sm" onClick={() => setOpen(false)}>Close</Button>
            </div>
            <div className="space-y-3 text-sm">
              {[
                ["Cmd/Ctrl + K", "Global search"],
                ["?", "Open this help"],
                ["Esc", "Close dialogs"],
                ["Alt + H", "Go dashboard"],
                ["Alt + P", "Go payroll"],
              ].map(([key, desc]) => (
                <div key={key} className="flex items-center justify-between rounded-md border p-3">
                  <span>{desc}</span>
                  <kbd className="rounded bg-muted px-2 py-1 text-xs font-semibold">{key}</kbd>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
