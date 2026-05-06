import type React from "react";

export type FrontendAppKey = "hrms" | "crm" | "project_management";

export type FrontendRoute = {
  path: string;
  element: React.ReactNode;
};

export type FrontendAppModule = {
  key: FrontendAppKey;
  label: string;
  basePath: string;
  routes: FrontendRoute[];
};

const rawInstalledApps = import.meta.env.VITE_INSTALLED_APPS || "hrms";
const validAppKeys: FrontendAppKey[] = ["hrms", "crm", "project_management"];

export function normalizeAppKey(value: string) {
  return value.trim().toLowerCase().replace(/-/g, "_");
}

export function getInstalledAppKeys(): FrontendAppKey[] {
  return rawInstalledApps
    .split(",")
    .map(normalizeAppKey)
    .filter((key: string): key is FrontendAppKey => validAppKeys.includes(key as FrontendAppKey));
}

export function getSuiteName() {
  return "Business Suite";
}
