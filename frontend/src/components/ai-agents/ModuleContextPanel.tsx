import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { AiAgent } from "@/services/aiAgentsApi";
import { moduleBadgeClass } from "./AgentCard";

export default function ModuleContextPanel({
  agent,
  module,
  relatedEntityType,
  relatedEntityId,
}: {
  agent?: AiAgent | null;
  module?: string | null;
  relatedEntityType?: string | null;
  relatedEntityId?: string | null;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Context</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3 text-sm">
        <div className="flex items-center justify-between gap-3">
          <span className="text-muted-foreground">Agent</span>
          <span className="text-right font-medium">{agent?.name || "Loading..."}</span>
        </div>
        <div className="flex items-center justify-between gap-3">
          <span className="text-muted-foreground">Module</span>
          <Badge className={moduleBadgeClass(module || agent?.module)}>{module || agent?.module || "CROSS"}</Badge>
        </div>
        <div className="rounded-md border bg-muted/30 p-3">
          <p className="text-xs font-semibold uppercase text-muted-foreground">Related record</p>
          <p className="mt-1">{relatedEntityType ? `${relatedEntityType} #${relatedEntityId || "-"}` : "No record context selected"}</p>
        </div>
        <p className="text-xs text-muted-foreground">
          The frontend only sends record context to the backend. The agent must fetch details through safe backend tools.
        </p>
      </CardContent>
    </Card>
  );
}

