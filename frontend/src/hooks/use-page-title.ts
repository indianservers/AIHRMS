import { useEffect } from "react";

export function usePageTitle(title: string) {
  useEffect(() => {
    document.title = `${title} · AI HRMS`;
    return () => {
      document.title = "AI HRMS";
    };
  }, [title]);
}
