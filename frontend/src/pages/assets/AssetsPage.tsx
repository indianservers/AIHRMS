import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Laptop, Plus, RefreshCw, Search } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { assetApi, employeeApi } from "@/services/api";
import { toast } from "@/hooks/use-toast";
import { formatCurrency, formatDate } from "@/lib/utils";

type Asset = {
  id: number;
  asset_tag: string;
  name: string;
  category_id?: number | null;
  brand?: string | null;
  model?: string | null;
  serial_number?: string | null;
  purchase_cost?: string | number | null;
  warranty_expiry?: string | null;
  condition: string;
  status: string;
  location?: string | null;
};

export default function AssetsPage() {
  const qc = useQueryClient();
  const [search, setSearch] = useState("");
  const [assetTag, setAssetTag] = useState("");
  const [name, setName] = useState("");
  const [brand, setBrand] = useState("");
  const [serial, setSerial] = useState("");
  const [cost, setCost] = useState("");
  const [assignAssetId, setAssignAssetId] = useState("");
  const [assignEmployeeId, setAssignEmployeeId] = useState("");

  const assets = useQuery({
    queryKey: ["assets", search],
    queryFn: () => assetApi.list({ search: search || undefined }).then((r) => r.data as Asset[]),
  });
  const employees = useQuery({
    queryKey: ["asset-employees"],
    queryFn: () => employeeApi.list({ per_page: 100 }).then((r) => r.data.items),
  });

  const createAsset = useMutation({
    mutationFn: () => assetApi.create({
      asset_tag: assetTag,
      name,
      brand: brand || undefined,
      serial_number: serial || undefined,
      purchase_cost: cost || undefined,
    }),
    onSuccess: () => {
      toast({ title: "Asset created" });
      setAssetTag("");
      setName("");
      setBrand("");
      setSerial("");
      setCost("");
      qc.invalidateQueries({ queryKey: ["assets"] });
    },
    onError: () => toast({ title: "Could not create asset", variant: "destructive" }),
  });

  const assign = useMutation({
    mutationFn: () => assetApi.assign({
      asset_id: Number(assignAssetId),
      employee_id: Number(assignEmployeeId),
      assigned_date: new Date().toISOString().slice(0, 10),
      condition_at_assignment: "Good",
    }),
    onSuccess: () => {
      toast({ title: "Asset assigned" });
      setAssignAssetId("");
      setAssignEmployeeId("");
      qc.invalidateQueries({ queryKey: ["assets"] });
    },
    onError: () => toast({ title: "Could not assign asset", variant: "destructive" }),
  });

  function submitAsset(event: FormEvent) {
    event.preventDefault();
    createAsset.mutate();
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-col gap-3 rounded-lg border bg-card p-5 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Assets</p>
          <h1 className="mt-2 text-2xl font-semibold tracking-tight">Asset management</h1>
          <p className="mt-1 text-sm text-muted-foreground">Create inventory, track status, and assign assets to employees.</p>
        </div>
        <Button variant="outline" onClick={() => assets.refetch()}><RefreshCw className="h-4 w-4" />Refresh</Button>
      </div>

      <div className="grid gap-5 xl:grid-cols-[0.8fr_1.2fr]">
        <div className="space-y-5">
          <Card>
            <CardHeader><CardTitle className="text-base">New asset</CardTitle><CardDescription>Add laptop, phone, ID card, equipment, or other inventory.</CardDescription></CardHeader>
            <CardContent>
              <form onSubmit={submitAsset} className="space-y-3">
                <div className="grid gap-3 sm:grid-cols-2">
                  <div className="space-y-2"><Label>Asset tag</Label><Input value={assetTag} onChange={(e) => setAssetTag(e.target.value)} required /></div>
                  <div className="space-y-2"><Label>Name</Label><Input value={name} onChange={(e) => setName(e.target.value)} required /></div>
                  <div className="space-y-2"><Label>Brand</Label><Input value={brand} onChange={(e) => setBrand(e.target.value)} /></div>
                  <div className="space-y-2"><Label>Serial</Label><Input value={serial} onChange={(e) => setSerial(e.target.value)} /></div>
                  <div className="space-y-2"><Label>Cost</Label><Input type="number" value={cost} onChange={(e) => setCost(e.target.value)} /></div>
                </div>
                <Button type="submit" disabled={createAsset.isPending}><Plus className="h-4 w-4" />Create asset</Button>
              </form>
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle className="text-base">Assign asset</CardTitle></CardHeader>
            <CardContent className="space-y-3">
              <select value={assignAssetId} onChange={(e) => setAssignAssetId(e.target.value)} className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm">
                <option value="">Select available asset</option>
                {assets.data?.filter((a) => a.status !== "Assigned").map((a) => <option key={a.id} value={a.id}>{a.asset_tag} - {a.name}</option>)}
              </select>
              <select value={assignEmployeeId} onChange={(e) => setAssignEmployeeId(e.target.value)} className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm">
                <option value="">Select employee</option>
                {employees.data?.map((e: any) => <option key={e.id} value={e.id}>{e.first_name} {e.last_name}</option>)}
              </select>
              <Button onClick={() => assign.mutate()} disabled={!assignAssetId || !assignEmployeeId || assign.isPending}>Assign</Button>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Inventory</CardTitle>
            <CardDescription>{assets.data?.length ?? 0} assets</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input className="pl-9" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search assets..." />
            </div>
            {assets.data?.map((asset) => (
              <div key={asset.id} className="flex flex-col gap-3 rounded-lg border p-4 sm:flex-row sm:items-center sm:justify-between">
                <div className="flex gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary"><Laptop className="h-5 w-5" /></div>
                  <div>
                    <p className="font-medium">{asset.name} <span className="text-muted-foreground">({asset.asset_tag})</span></p>
                    <p className="text-sm text-muted-foreground">{asset.brand || "No brand"} • {asset.serial_number || "No serial"} • Warranty {formatDate(asset.warranty_expiry || null)}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {asset.purchase_cost && <span className="text-sm text-muted-foreground">{formatCurrency(Number(asset.purchase_cost))}</span>}
                  <Badge variant={asset.status === "Available" ? "success" : "secondary"}>{asset.status}</Badge>
                </div>
              </div>
            ))}
            {!assets.isLoading && !assets.data?.length && <p className="rounded-lg border p-4 text-sm text-muted-foreground">No assets yet.</p>}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
