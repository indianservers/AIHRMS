import { create } from "zustand";

export type RealtimeEvent = {
  id: string;
  actor: string;
  action: string;
  target: string;
  createdAt: string;
};

type RealtimeState = {
  events: RealtimeEvent[];
  onlineUsers: string[];
  publish: (event: Omit<RealtimeEvent, "id" | "createdAt">) => void;
  receive: (event: RealtimeEvent) => void;
};

const CHANNEL = "karyaflow-realtime";

const channel = typeof window !== "undefined" && "BroadcastChannel" in window ? new BroadcastChannel(CHANNEL) : null;

export const useRealtimeStore = create<RealtimeState>((set, get) => ({
  events: [
    { id: "evt-1", actor: "Maya Nair", action: "moved", target: "KAR-103 to In Review", createdAt: new Date().toISOString() },
    { id: "evt-2", actor: "Dev Patel", action: "assigned", target: "Calendar bug to Nora Khan", createdAt: new Date().toISOString() },
  ],
  onlineUsers: ["Maya Nair", "Dev Patel", "Isha Rao", "Nora Khan"],
  publish: (event) => {
    const fullEvent = {
      ...event,
      id: crypto.randomUUID(),
      createdAt: new Date().toISOString(),
    };
    set({ events: [fullEvent, ...get().events].slice(0, 30) });
    channel?.postMessage(fullEvent);
  },
  receive: (event) => set({ events: [event, ...get().events.filter((item) => item.id !== event.id)].slice(0, 30) }),
}));

channel?.addEventListener("message", (message) => {
  useRealtimeStore.getState().receive(message.data as RealtimeEvent);
});

