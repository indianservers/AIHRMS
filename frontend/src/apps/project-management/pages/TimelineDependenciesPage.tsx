import { useState } from "react";
import { Check, ChevronRight, Link2, Search, UserPlus } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { dependencyLinks, teamMembers, timelineItems } from "../workData";

export default function TimelineDependenciesPage() {
  const [selected, setSelected] = useState(timelineItems[1]);
  return (
    <div className="space-y-5">
      <div className="rounded-xl border bg-slate-950 text-slate-100">
        <div className="flex flex-col gap-4 border-b border-slate-800 p-5 xl:flex-row xl:items-center xl:justify-between">
          <div>
            <h1 className="text-2xl font-semibold">The Next Big Thing</h1>
            <div className="mt-3 flex gap-6 overflow-x-auto text-sm font-medium text-slate-400">
              {["Summary", "Board", "List", "Calendar", "Timeline", "Forms", "Pages", "Issues", "Reports", "Shortcuts"].map((tab) => (
                <span key={tab} className={tab === "Timeline" ? "border-b-2 border-blue-500 pb-2 text-blue-400" : "pb-2"}>{tab}</span>
              ))}
            </div>
          </div>
          <Button className="w-fit">Today</Button>
        </div>
        <div className="flex flex-col gap-3 border-b border-slate-800 p-5 md:flex-row md:items-center">
          <div className="flex w-full max-w-sm items-center gap-2 rounded-md border border-slate-700 bg-slate-900 px-3 py-2">
            <Search className="h-4 w-4 text-slate-500" />
            <Input placeholder="Search" className="border-0 bg-transparent p-0 text-slate-100 shadow-none focus-visible:ring-0" />
          </div>
          <AvatarStack />
          <Button variant="secondary" size="sm"><UserPlus className="h-4 w-4" /></Button>
        </div>
        <div className="overflow-x-auto">
          <div className="min-w-[980px]">
            <div className="grid grid-cols-[27rem_1fr] border-b border-slate-800 bg-slate-900/80 text-sm text-slate-400">
              <div className="px-5 py-4">Items</div>
              <div className="grid grid-cols-2">
                <div className="border-l border-slate-800 px-5 py-4 text-center font-semibold">JAN</div>
                <div className="border-l border-slate-800 px-5 py-4 text-center font-semibold">FEB</div>
              </div>
            </div>
            <div className="relative">
              <div className="pointer-events-none absolute bottom-0 left-[27rem] top-0 grid w-[calc(100%-27rem)] grid-cols-4">
                {Array.from({ length: 4 }).map((_, index) => <div key={index} className="border-l border-slate-800/80" />)}
              </div>
              <div className="pointer-events-none absolute left-[72%] top-0 h-full w-px bg-orange-400" />
              {dependencyLinks.map((link) => <DependencyLine key={`${link.from}-${link.to}`} offset={link.offset} />)}
              {timelineItems.map((item) => (
                <div key={item.key} className="grid grid-cols-[27rem_1fr] border-b border-slate-800/80 hover:bg-slate-900/70">
                  <button type="button" className="grid grid-cols-[2rem_2rem_5rem_1fr_2rem] items-center gap-2 px-5 py-4 text-left" onClick={() => setSelected(item)}>
                    <ChevronRight className="h-4 w-4 text-slate-500" />
                    <span className="flex h-5 w-5 items-center justify-center rounded bg-blue-500 text-white"><Check className="h-3 w-3" /></span>
                    <span className="font-semibold text-blue-400">{item.key}</span>
                    <span>{item.title}</span>
                    {item.done ? <span className="flex h-5 w-5 items-center justify-center rounded-full bg-emerald-500 text-slate-950"><Check className="h-3 w-3" /></span> : null}
                  </button>
                  <div className="relative py-3">
                    {item.span ? (
                      <button type="button" onClick={() => setSelected(item)} className={`absolute top-3 h-9 rounded-md ${item.color} shadow-lg`} style={{ left: `${item.start}%`, width: `${item.span}%` }}>
                        <span className="ml-4 flex h-7 w-7 items-center justify-center rounded-full bg-amber-400 text-xs font-bold text-slate-900">{item.owner.slice(0, 1)}</span>
                      </button>
                    ) : null}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
      <Card>
        <CardContent className="grid gap-4 p-5 md:grid-cols-[1fr_18rem]">
          <div>
            <p className="text-sm text-muted-foreground">Selected dependency</p>
            <h2 className="mt-1 text-xl font-semibold">{selected.key} {selected.title}</h2>
            <p className="mt-2 text-muted-foreground">This view supports timeline planning, dependency inspection, owner visibility, completion markers, and today tracking.</p>
          </div>
          <div className="rounded-lg border p-4">
            <Badge variant="outline"><Link2 className="h-3 w-3" /> blocks</Badge>
            <p className="mt-3 text-sm text-muted-foreground">NBT-1 Web campaign project specs blocks TBT - Build Web campaign.</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function DependencyLine({ offset }: { offset: number }) {
  return <div className="pointer-events-none absolute h-16 w-28 rounded-br-2xl border-b-4 border-r-4 border-orange-500" style={{ left: `calc(27rem + ${offset}%)`, top: "13.5rem" }} />;
}

function AvatarStack() {
  return <div className="flex -space-x-2">{teamMembers.slice(0, 4).map((member) => <span key={member.name} className="flex h-9 w-9 items-center justify-center rounded-full border-2 border-slate-950 bg-blue-600 text-xs font-semibold text-white">{member.name.slice(0, 1)}</span>)}<span className="flex h-9 w-9 items-center justify-center rounded-full border-2 border-slate-950 bg-slate-800 text-sm">+3</span></div>;
}

