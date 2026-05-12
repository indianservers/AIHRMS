import { useNavigate } from "react-router-dom";
import { Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { toast } from "@/hooks/use-toast";
import { aiAgentsApi, type AiModule } from "@/services/aiAgentsApi";

export default function AskAiButton({
  module,
  relatedEntityType,
  relatedEntityId,
  defaultAgentCode,
  defaultPrompt,
  buttonLabel = "Ask AI",
  size = "sm",
  variant = "outline",
}: {
  module: AiModule;
  relatedEntityType?: string;
  relatedEntityId?: string | number;
  defaultAgentCode?: string;
  defaultPrompt?: string;
  buttonLabel?: string;
  size?: "sm" | "default";
  variant?: "outline" | "default" | "ghost";
}) {
  const navigate = useNavigate();

  const openAi = async () => {
    try {
      const response = await aiAgentsApi.getAgents({ module });
      const agents = response.data;
      const agent = agents.find((item) => item.code === defaultAgentCode) || agents.find((item) => item.is_active) || agents[0];
      if (!agent) {
        toast({ title: "No AI agent is available", description: "AI Agents are not configured for this module yet.", variant: "destructive" });
        return;
      }
      const params = new URLSearchParams();
      params.set("module", module);
      if (relatedEntityType) params.set("related_entity_type", relatedEntityType);
      if (relatedEntityId !== undefined && relatedEntityId !== null) params.set("related_entity_id", String(relatedEntityId));
      if (defaultPrompt) params.set("prompt", defaultPrompt);
      navigate(`/ai-agents/chat/${agent.id}?${params.toString()}`);
    } catch (error: any) {
      toast({ title: "Could not open AI Agent", description: error?.response?.data?.detail || "Please try again.", variant: "destructive" });
    }
  };

  return (
    <Button type="button" size={size} variant={variant} onClick={openAi}>
      <Sparkles className="h-4 w-4" />
      {buttonLabel}
    </Button>
  );
}

