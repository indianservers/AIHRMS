import AgentCard from "@/components/ai-agents/AgentCard";
import type { AiAgent, AiModule } from "@/services/aiAgentsApi";

export default function AgentList({
  agents,
  moduleFilter = "ALL",
  onToggleStatus,
}: {
  agents: AiAgent[];
  moduleFilter?: AiModule | "ALL";
  onToggleStatus?: (agent: AiAgent) => void;
}) {
  const visibleAgents = moduleFilter === "ALL" ? agents : agents.filter((agent) => agent.module === moduleFilter);

  if (!visibleAgents.length) {
    return (
      <div className="rounded-lg border bg-card p-8 text-center text-sm text-muted-foreground">
        No AI agents match this module filter.
      </div>
    );
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      {visibleAgents.map((agent) => (
        <AgentCard key={agent.id} agent={agent} onToggleStatus={onToggleStatus} />
      ))}
    </div>
  );
}

