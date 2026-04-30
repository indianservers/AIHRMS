import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import {
  useReactTable,
  getCoreRowModel,
  flexRender,
  createColumnHelper,
} from "@tanstack/react-table";
import {
  Plus, Search, Filter, Download, RefreshCw,
  Eye, Edit, UserX, Camera
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { employeeApi } from "@/services/api";
import { assetUrl, formatDate, statusColor, getInitials } from "@/lib/utils";
import { toast } from "@/hooks/use-toast";

interface Employee {
  id: number;
  employee_id: string;
  first_name: string;
  last_name: string;
  personal_email: string | null;
  phone_number: string | null;
  designation_id: number | null;
  department_id: number | null;
  employment_type: string;
  status: string;
  date_of_joining: string;
  profile_photo_url: string | null;
}

const columnHelper = createColumnHelper<Employee>();

export default function EmployeesPage() {
  const qc = useQueryClient();
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState("");

  const { data, isLoading, refetch } = useQuery({
    queryKey: ["employees", search, page, statusFilter],
    queryFn: () =>
      employeeApi
        .list({ search: search || undefined, page, per_page: 20, status: statusFilter || undefined })
        .then((r) => r.data),
  });

  const photoMutation = useMutation({
    mutationFn: ({ employeeId, file }: { employeeId: number; file: File }) => {
      const form = new FormData();
      form.append("file", file);
      return employeeApi.uploadPhoto(employeeId, form);
    },
    onSuccess: () => {
      toast({ title: "Photo updated" });
      qc.invalidateQueries({ queryKey: ["employees"] });
    },
    onError: () => toast({ title: "Could not upload photo", variant: "destructive" }),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => employeeApi.delete(id),
    onSuccess: () => {
      toast({ title: "Employee terminated" });
      qc.invalidateQueries({ queryKey: ["employees"] });
    },
    onError: () => toast({ title: "Could not update employee", variant: "destructive" }),
  });

  const columns = [
    columnHelper.display({
      id: "avatar",
      cell: (info) => {
        const emp = info.row.original;
        const initials = getInitials(`${emp.first_name} ${emp.last_name}`);
        return (
          <div className="flex items-center gap-3">
            {emp.profile_photo_url ? (
              <img
                src={assetUrl(emp.profile_photo_url)}
                alt={initials}
                className="h-9 w-9 rounded-full object-cover"
              />
            ) : (
              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary/10 text-primary text-sm font-semibold">
                {initials}
              </div>
            )}
            <div>
              <p className="font-medium text-sm">
                {emp.first_name} {emp.last_name}
              </p>
              <p className="text-xs text-muted-foreground">{emp.employee_id}</p>
            </div>
          </div>
        );
      },
    }),
    columnHelper.accessor("personal_email", {
      header: "Email",
      cell: (info) => (
        <span className="text-sm text-muted-foreground">{info.getValue() || "—"}</span>
      ),
    }),
    columnHelper.accessor("phone_number", {
      header: "Phone",
      cell: (info) => (
        <span className="text-sm">{info.getValue() || "—"}</span>
      ),
    }),
    columnHelper.accessor("employment_type", {
      header: "Type",
      cell: (info) => (
        <Badge variant="outline" className="text-xs">
          {info.getValue()}
        </Badge>
      ),
    }),
    columnHelper.accessor("date_of_joining", {
      header: "Joined",
      cell: (info) => (
        <span className="text-sm">{formatDate(info.getValue())}</span>
      ),
    }),
    columnHelper.accessor("status", {
      header: "Status",
      cell: (info) => (
        <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${statusColor(info.getValue())}`}>
          {info.getValue()}
        </span>
      ),
    }),
    columnHelper.display({
      id: "actions",
      cell: (info) => (
        <div className="flex items-center gap-1">
          <Link to={`/employees/${info.row.original.id}`}>
            <Button variant="ghost" size="icon" className="h-8 w-8">
              <Eye className="h-3.5 w-3.5" />
            </Button>
          </Link>
          <Link to={`/employees/${info.row.original.id}?edit=true`}>
            <Button variant="ghost" size="icon" className="h-8 w-8">
              <Edit className="h-3.5 w-3.5" />
            </Button>
          </Link>
          <label className="inline-flex h-8 w-8 cursor-pointer items-center justify-center rounded-md hover:bg-muted">
            <Camera className="h-3.5 w-3.5" />
            <input
              type="file"
              accept="image/png,image/jpeg"
              className="hidden"
              onChange={(event) => {
                const file = event.target.files?.[0];
                if (file) photoMutation.mutate({ employeeId: info.row.original.id, file });
                event.currentTarget.value = "";
              }}
            />
          </label>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 text-destructive"
            onClick={() => deleteMutation.mutate(info.row.original.id)}
          >
            <UserX className="h-3.5 w-3.5" />
          </Button>
        </div>
      ),
    }),
  ];

  const table = useReactTable({
    data: data?.items || [],
    columns,
    getCoreRowModel: getCoreRowModel(),
    manualPagination: true,
    pageCount: data?.pages ?? 0,
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="page-title">Employees</h1>
          <p className="page-description">
            {data?.total ?? 0} total employees
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={() => refetch()}>
            <RefreshCw className="h-4 w-4" />
          </Button>
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
          <Link to="/employees/new">
            <Button size="sm">
              <Plus className="h-4 w-4 mr-2" />
              Add Employee
            </Button>
          </Link>
        </div>
      </div>

      {/* Filters */}
      <Card className="p-4">
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search by name, ID, email..."
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(1); }}
              className="pl-9"
            />
          </div>
          <select
            value={statusFilter}
            onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
            className="flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background"
          >
            <option value="">All Status</option>
            <option value="Active">Active</option>
            <option value="Probation">Probation</option>
            <option value="On Leave">On Leave</option>
            <option value="Resigned">Resigned</option>
            <option value="Terminated">Terminated</option>
          </select>
          <Button variant="outline" size="sm">
            <Filter className="h-4 w-4 mr-2" />
            More Filters
          </Button>
        </div>
      </Card>

      {/* Table */}
      <Card className="overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="border-b bg-muted/50">
              {table.getHeaderGroups().map((headerGroup) => (
                <tr key={headerGroup.id}>
                  {headerGroup.headers.map((header) => (
                    <th
                      key={header.id}
                      className="px-4 py-3 text-left font-medium text-muted-foreground text-xs uppercase tracking-wide"
                    >
                      {flexRender(header.column.columnDef.header, header.getContext())}
                    </th>
                  ))}
                </tr>
              ))}
            </thead>
            <tbody>
              {isLoading ? (
                Array.from({ length: 10 }).map((_, i) => (
                  <tr key={i} className="border-b">
                    <td className="px-4 py-3" colSpan={7}>
                      <div className="flex items-center gap-3">
                        <div className="h-9 w-9 skeleton rounded-full" />
                        <div className="space-y-1">
                          <div className="h-4 w-32 skeleton rounded" />
                          <div className="h-3 w-20 skeleton rounded" />
                        </div>
                      </div>
                    </td>
                  </tr>
                ))
              ) : table.getRowModel().rows.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-4 py-12 text-center text-muted-foreground">
                    <Users className="h-10 w-10 mx-auto mb-2 opacity-30" />
                    <p>No employees found</p>
                    <Link to="/employees/new">
                      <Button variant="link" size="sm">Add your first employee</Button>
                    </Link>
                  </td>
                </tr>
              ) : (
                table.getRowModel().rows.map((row) => (
                  <tr key={row.id} className="border-b hover:bg-muted/30 transition-colors">
                    {row.getVisibleCells().map((cell) => (
                      <td key={cell.id} className="px-4 py-3">
                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                      </td>
                    ))}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {data && data.pages > 1 && (
          <div className="flex items-center justify-between px-4 py-3 border-t">
            <p className="text-xs text-muted-foreground">
              Showing {(page - 1) * 20 + 1}–{Math.min(page * 20, data.total)} of {data.total}
            </p>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
              >
                Previous
              </Button>
              <span className="text-sm">
                Page {page} of {data.pages}
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage((p) => Math.min(data.pages, p + 1))}
                disabled={page === data.pages}
              >
                Next
              </Button>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}

// Missing import
function Users(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg {...props} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
      <circle cx="9" cy="7" r="4" />
      <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
      <path d="M16 3.13a4 4 0 0 1 0 7.75" />
    </svg>
  );
}
