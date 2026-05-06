import { useEffect } from "react";

export function usePageTitle(title: string) {
  useEffect(() => {
    document.title = `${title} - Business Suite`;
    return () => {
      document.title = "Business Suite";
    };
  }, [title]);
}

