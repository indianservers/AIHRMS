import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Building2, Globe, Mail, MapPin, Phone, Plus, Save } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { companyApi } from "@/services/api";
import { toast } from "@/hooks/use-toast";

export default function CompanyPage() {
  const qc = useQueryClient();
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [form, setForm] = useState<Record<string, any>>({ country: "India" });

  const companies = useQuery({
    queryKey: ["companies"],
    queryFn: () => companyApi.listCompanies().then((r) => r.data),
  });

  const selected = (companies.data || []).find((c: any) => c.id === selectedId) || companies.data?.[0];

  useEffect(() => {
    if (selected) {
      setSelectedId(selected.id);
      setForm(selected);
    }
  }, [selected?.id]);

  const saveMutation = useMutation({
    mutationFn: () => {
      const payload = { ...form };
      Object.keys(payload).forEach((key) => {
        if (payload[key] === "") payload[key] = null;
      });
      return form.id ? companyApi.updateCompany(form.id, payload) : companyApi.createCompany(payload);
    },
    onSuccess: () => {
      toast({ title: "Company details saved" });
      qc.invalidateQueries({ queryKey: ["companies"] });
    },
    onError: (err: any) => toast({ title: "Could not save company", description: err?.response?.data?.detail || "Please check fields", variant: "destructive" }),
  });

  const update = (key: string, value: string) => setForm((current) => ({ ...current, [key]: value }));

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="page-title">Company</h1>
          <p className="page-description">Manage legal, statutory, contact, and address details for each company.</p>
        </div>
        <Button variant="outline" onClick={() => { setSelectedId(null); setForm({ country: "India" }); }}>
          <Plus className="mr-2 h-4 w-4" />
          New Company
        </Button>
      </div>

      <div className="grid gap-5 lg:grid-cols-[280px_1fr]">
        <div className="space-y-2">
          {(companies.data || []).map((company: any) => (
            <button
              key={company.id}
              onClick={() => { setSelectedId(company.id); setForm(company); }}
              className={`w-full rounded-lg border p-4 text-left transition-colors ${company.id === form.id ? "border-primary bg-primary/5" : "bg-card hover:bg-muted/40"}`}
            >
              <div className="flex items-center justify-between gap-2">
                <p className="font-semibold">{company.name}</p>
                <Badge variant={company.is_active ? "success" : "outline"}>{company.is_active ? "Active" : "Inactive"}</Badge>
              </div>
              <p className="mt-1 text-xs text-muted-foreground">{company.city || company.email || company.phone || "Company profile"}</p>
            </button>
          ))}
        </div>

        <Card>
          <CardHeader>
            <div className="flex items-start gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-primary/10 text-primary">
                <Building2 className="h-5 w-5" />
              </div>
              <div>
                <CardTitle>{form.id ? "Update Company Details" : "Create Company"}</CardTitle>
                <CardDescription>These details appear in letters, payslips, statutory forms, and reports.</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <form
              className="grid gap-4 sm:grid-cols-2"
              onSubmit={(event) => {
                event.preventDefault();
                saveMutation.mutate();
              }}
            >
              <Field label="Company Name *"><Input value={form.name || ""} onChange={(e) => update("name", e.target.value)} /></Field>
              <Field label="Legal Name"><Input value={form.legal_name || ""} onChange={(e) => update("legal_name", e.target.value)} /></Field>
              <Field label="Registration Number"><Input value={form.registration_number || ""} onChange={(e) => update("registration_number", e.target.value)} /></Field>
              <Field label="PAN"><Input value={form.pan_number || ""} onChange={(e) => update("pan_number", e.target.value)} /></Field>
              <Field label="TAN"><Input value={form.tan_number || ""} onChange={(e) => update("tan_number", e.target.value)} /></Field>
              <Field label="GSTIN"><Input value={form.gstin || ""} onChange={(e) => update("gstin", e.target.value)} /></Field>
              <Field label="Email"><Input value={form.email || ""} onChange={(e) => update("email", e.target.value)} /></Field>
              <Field label="Phone"><Input value={form.phone || ""} onChange={(e) => update("phone", e.target.value)} /></Field>
              <Field label="Website"><Input value={form.website || ""} onChange={(e) => update("website", e.target.value)} /></Field>
              <Field label="City"><Input value={form.city || ""} onChange={(e) => update("city", e.target.value)} /></Field>
              <Field label="State"><Input value={form.state || ""} onChange={(e) => update("state", e.target.value)} /></Field>
              <Field label="Pincode"><Input value={form.pincode || ""} onChange={(e) => update("pincode", e.target.value)} /></Field>
              <div className="space-y-2 sm:col-span-2">
                <Label>Address</Label>
                <textarea value={form.address || ""} onChange={(e) => update("address", e.target.value)} rows={3} className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm" />
              </div>
              <div className="grid gap-3 rounded-lg bg-muted/30 p-4 text-sm sm:col-span-2 sm:grid-cols-3">
                <span className="flex items-center gap-2"><Mail className="h-4 w-4 text-muted-foreground" />{form.email || "No email"}</span>
                <span className="flex items-center gap-2"><Phone className="h-4 w-4 text-muted-foreground" />{form.phone || "No phone"}</span>
                <span className="flex items-center gap-2"><Globe className="h-4 w-4 text-muted-foreground" />{form.website || "No website"}</span>
                <span className="flex items-center gap-2 sm:col-span-3"><MapPin className="h-4 w-4 text-muted-foreground" />{[form.address, form.city, form.state, form.pincode].filter(Boolean).join(", ") || "No address"}</span>
              </div>
              <div className="flex justify-end sm:col-span-2">
                <Button type="submit" disabled={saveMutation.isPending}>
                  <Save className="mr-2 h-4 w-4" />
                  {saveMutation.isPending ? "Saving..." : "Save Company"}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return <div className="space-y-2"><Label>{label}</Label>{children}</div>;
}
