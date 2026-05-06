import { useState } from "react";
import { BarChart3, Bot, CheckCircle2, ClipboardList, MoreHorizontal, Play, Plus, Search, Sparkles, Zap } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { automationAuditRows, automationTemplates } from "../workData";

const tabs = [
  { label: "Rules", icon: Zap },
  { label: "Audit log", icon: CheckCircle2 },
  { label: "Templates", icon: ClipboardList },
  { label: "Usage", icon: BarChart3 },
];

export default function AutomationAIPage() {
  const [activeTab, setActiveTab] = useState("Templates");
  const [prompt, setPrompt] = useState("When a design request with a 'webpage' label is submitted, create a task and assign it to Daniel.");
  const [generated, setGenerated] = useState<string[]>([]);

  const generateRule = () => {
    setGenerated([
      "Trigger: Work item created from request form",
      "Condition: labels contains webpage",
      "Action: Create child task named Webpage design task",
      "Assignment: Daniel based on design component ownership",
      "Notification: Comment on parent item with created task link",
    ]);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
        <div>
          <h1 className="page-title">Automation</h1>
          <p className="page-description">Create workflow rules from natural language, templates, triggers, and connected project events.</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">Global automation</Button>
          <Button><Plus className="h-4 w-4" />Create rule</Button>
          <Button variant="outline" size="icon"><MoreHorizontal className="h-4 w-4" /></Button>
        </div>
      </div>

      <div className="flex gap-6 border-b">
        {tabs.map((tab) => (
          <button key={tab.label} type="button" onClick={() => setActiveTab(tab.label)} className={`flex items-center gap-2 border-b-2 px-1 py-3 text-sm font-medium ${activeTab === tab.label ? "border-primary text-primary" : "border-transparent text-muted-foreground"}`}>
            <tab.icon className="h-4 w-4" />{tab.label}
          </button>
        ))}
      </div>

      <Card className="overflow-hidden border-blue-200">
        <CardContent className="p-0">
          <div className="bg-gradient-to-r from-blue-50 via-white to-amber-50 p-6">
            <h2 className="text-2xl font-semibold">Create rules quickly with the power of AI</h2>
            <div className="mt-5 rounded-xl border-2 border-blue-400 bg-white p-4 shadow-sm">
              <textarea value={prompt} onChange={(event) => setPrompt(event.target.value)} className="min-h-28 w-full resize-none border-0 text-lg outline-none" />
              <div className="mt-4 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                <div className="flex items-center gap-3 text-muted-foreground"><Sparkles className="h-6 w-6 text-blue-600" />Karya AI is ready to generate a rule.</div>
                <div className="flex gap-2"><Button variant="outline">Cancel <Badge variant="outline">Esc</Badge></Button><Button onClick={generateRule}><Bot className="h-4 w-4" />Generate rule</Button></div>
              </div>
            </div>
            <div className="mt-4 flex flex-wrap items-center gap-2">
              <span className="text-sm text-muted-foreground">Need inspiration?</span>
              {["Transition linked issues", "Create new issues", "Email ticket owners", "Set due date by priority"].map((item) => <Button key={item} variant="outline" size="sm" onClick={() => setPrompt(examplePrompt(item))}>{item}</Button>)}
            </div>
          </div>
          {generated.length ? (
            <div className="border-t bg-muted/20 p-6">
              <h3 className="font-semibold">Generated rule preview</h3>
              <div className="mt-3 grid gap-2 md:grid-cols-2">
                {generated.map((item) => <div key={item} className="rounded-lg border bg-background p-3 text-sm">{item}</div>)}
              </div>
              <div className="mt-4 flex justify-end gap-2"><Button variant="outline">Edit rule</Button><Button><Play className="h-4 w-4" />Enable rule</Button></div>
            </div>
          ) : null}
        </CardContent>
      </Card>

      <div className="grid gap-4 xl:grid-cols-[1fr_24rem]">
        <div className="space-y-4">
          <div className="flex max-w-md items-center gap-2 rounded-md border px-3 py-2">
            <Search className="h-4 w-4 text-muted-foreground" />
            <Input placeholder="Search for template" className="border-0 p-0 shadow-none focus-visible:ring-0" />
          </div>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {automationTemplates.map((template) => (
              <Card key={template.title} className="transition hover:border-primary/50 hover:shadow-md">
                <CardHeader><CardTitle className="flex items-center gap-2 text-base"><Zap className="h-5 w-5 text-primary" />{template.title}</CardTitle></CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">{template.description}</p>
                  <Badge className="mt-4" variant="outline">{template.category}</Badge>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
        <Card className="h-fit">
          <CardHeader><CardTitle>Audit and Usage</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            {automationAuditRows.map((row) => (
              <div key={`${row.rule}-${row.time}`} className="rounded-lg border bg-muted/30 p-3 text-sm">
                <p className="font-medium">{row.rule}</p>
                <p className="text-muted-foreground">{row.actor}: {row.result}</p>
                <p className="mt-1 text-xs text-muted-foreground">{row.time}</p>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function examplePrompt(label: string) {
  const prompts: Record<string, string> = {
    "Transition linked issues": "When a blocker issue is marked done, transition all linked issues that were blocked into Selected and notify their assignees.",
    "Create new issues": "When a feature request form is submitted, create design, API, QA, and documentation tasks and assign them by component owner.",
    "Email ticket owners": "When a support ticket is due in 24 hours and still open, email the ticket owner and project manager.",
    "Set due date by priority": "When a critical bug is created, set the due date to the next business day and assign it to the component lead.",
  };
  return prompts[label] || "";
}

