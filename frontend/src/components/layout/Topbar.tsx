import * as DropdownMenu from "@radix-ui/react-dropdown-menu";
import * as Dialog from "@radix-ui/react-dialog";
import { useMutation, useQuery } from "@tanstack/react-query";
import { FormEvent, useState } from "react";
import { Bell, LogOut, Menu, Moon, Sun, UserCircle, KeyRound } from "lucide-react";
import { useLocation, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import GlobalSearch from "@/components/app/GlobalSearch";
import KeyboardShortcuts from "@/components/app/KeyboardShortcuts";
import { useThemeStore } from "@/store/themeStore";
import { useAuthStore } from "@/store/authStore";
import { getRoleLabel } from "@/lib/roles";
import { getProductForContext } from "@/lib/products";
import { authApi, notificationsApi } from "@/services/api";
import { toast } from "@/hooks/use-toast";

interface TopbarProps {
  onMenuClick: () => void;
}

export const NOTIF_UNREAD_KEY = ["notifications-unread-count"];

export default function Topbar({ onMenuClick }: TopbarProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const { theme, setTheme } = useThemeStore();
  const { user, logout } = useAuthStore();
  const product = getProductForContext(location.pathname, user?.role, user?.is_superuser);
  const [passwordDialogOpen, setPasswordDialogOpen] = useState(false);
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const roleLabel = getRoleLabel(user?.role, user?.is_superuser);
  const initials = user?.email?.slice(0, 2).toUpperCase() || "?";
  const unreadCount = useQuery({
    queryKey: NOTIF_UNREAD_KEY,
    queryFn: () => notificationsApi.unreadCount().then((response) => response.data.unread as number),
    refetchInterval: 60_000,
    staleTime: 30_000,
    retry: false,
  });

  const toggleTheme = () => setTheme(theme === "dark" ? "light" : "dark");
  const handleLogout = () => {
    logout();
    navigate(product.loginPath, { replace: true });
  };
  const isHrms = location.pathname.startsWith("/hrms");
  const profilePath = isHrms ? "/hrms/profile" : location.pathname.startsWith("/crm") ? "/crm" : "/pms";
  const selfServicePath = isHrms ? "/hrms/ess" : profilePath;
  const changePassword = useMutation({
    mutationFn: () => authApi.changePassword(currentPassword, newPassword),
    onSuccess: () => {
      toast({ title: "Password changed" });
      setPasswordDialogOpen(false);
      setCurrentPassword("");
      setNewPassword("");
    },
    onError: () => toast({ title: "Unable to change password", variant: "destructive" }),
  });
  const submitPasswordChange = (event: FormEvent) => {
    event.preventDefault();
    changePassword.mutate();
  };

  return (
    <header className="flex h-16 shrink-0 items-center gap-4 border-b bg-background/95 backdrop-blur px-4 md:px-6 lg:px-8">
      {/* Mobile menu button */}
      <Button
        variant="ghost"
        size="icon"
        className="lg:hidden"
        onClick={onMenuClick}
      >
        <Menu className="h-5 w-5" />
      </Button>

      <GlobalSearch />

      <div className="ml-auto flex items-center gap-2">
        {/* Notifications */}
        <Button variant="ghost" size="icon" className="relative" onClick={() => navigate(isHrms ? "/hrms/notifications" : profilePath)}>
          <Bell className="h-5 w-5" />
          {!!unreadCount.data && unreadCount.data > 0 && (
            <span className="absolute right-0.5 top-0.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-red-500 px-1 text-[9px] font-bold leading-none text-white">
              {unreadCount.data > 9 ? "9+" : unreadCount.data}
            </span>
          )}
        </Button>
        <KeyboardShortcuts />

        {/* Theme toggle */}
        <Button variant="ghost" size="icon" onClick={toggleTheme}>
          {theme === "dark" ? (
            <Sun className="h-5 w-5" />
          ) : (
            <Moon className="h-5 w-5" />
          )}
        </Button>

        <Dialog.Root open={passwordDialogOpen} onOpenChange={setPasswordDialogOpen}>
        <DropdownMenu.Root>
          <DropdownMenu.Trigger asChild>
            <button className="flex items-center gap-2 rounded-full border px-3 py-1.5 text-sm hover:bg-muted focus:outline-none focus:ring-2 focus:ring-ring">
              <div className="flex h-6 w-6 items-center justify-center rounded-full bg-primary text-[10px] font-bold text-primary-foreground">
                {initials}
              </div>
              <span className="hidden max-w-32 truncate text-sm font-medium md:block">
                {user?.email?.split("@")[0]}
              </span>
              <span className="hidden rounded-full bg-muted px-2 py-0.5 text-[10px] font-medium text-muted-foreground xl:block">
                {roleLabel}
              </span>
            </button>
          </DropdownMenu.Trigger>
          <DropdownMenu.Portal>
            <DropdownMenu.Content align="end" sideOffset={8} className="z-50 min-w-56 rounded-md border bg-popover p-1 text-popover-foreground shadow-md">
              <div className="px-3 py-2">
                <p className="truncate text-sm font-medium">{user?.email}</p>
                <p className="text-xs text-muted-foreground">{roleLabel}</p>
              </div>
              <DropdownMenu.Separator className="my-1 h-px bg-border" />
              <DropdownMenu.Item className="flex cursor-pointer items-center gap-2 rounded-sm px-3 py-2 text-sm outline-none hover:bg-accent" onSelect={() => navigate(profilePath)}>
                <UserCircle className="h-4 w-4" />
                My Profile
              </DropdownMenu.Item>
              <DropdownMenu.Item className="flex cursor-pointer items-center gap-2 rounded-sm px-3 py-2 text-sm outline-none hover:bg-accent" onSelect={() => navigate(selfServicePath)}>
                <UserCircle className="h-4 w-4" />
                {isHrms ? "ESS Portal" : "Workspace"}
              </DropdownMenu.Item>
              <DropdownMenu.Item className="flex cursor-pointer items-center gap-2 rounded-sm px-3 py-2 text-sm outline-none hover:bg-accent" onSelect={() => setPasswordDialogOpen(true)}>
                <KeyRound className="h-4 w-4" />
                Change Password
              </DropdownMenu.Item>
              <DropdownMenu.Separator className="my-1 h-px bg-border" />
              <DropdownMenu.Item className="flex cursor-pointer items-center gap-2 rounded-sm px-3 py-2 text-sm text-red-600 outline-none hover:bg-red-50" onSelect={handleLogout}>
                <LogOut className="h-4 w-4" />
                Logout
              </DropdownMenu.Item>
            </DropdownMenu.Content>
          </DropdownMenu.Portal>
        </DropdownMenu.Root>
        <Dialog.Portal>
          <Dialog.Overlay className="fixed inset-0 z-50 bg-black/40" />
          <Dialog.Content className="fixed left-1/2 top-1/2 z-50 w-[calc(100%-2rem)] max-w-md -translate-x-1/2 -translate-y-1/2 rounded-lg border bg-background p-6 shadow-xl">
            <Dialog.Title className="text-lg font-semibold">Change Password</Dialog.Title>
            <Dialog.Description className="mt-1 text-sm text-muted-foreground">
              Enter your current password and choose a new one.
            </Dialog.Description>
            <form className="mt-5 space-y-4" onSubmit={submitPasswordChange}>
              <div className="space-y-1.5">
                <Label htmlFor="current-password">Current Password</Label>
                <Input id="current-password" type="password" value={currentPassword} onChange={(event) => setCurrentPassword(event.target.value)} required />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="new-password">New Password</Label>
                <Input id="new-password" type="password" value={newPassword} onChange={(event) => setNewPassword(event.target.value)} required />
              </div>
              <div className="flex justify-end gap-2">
                <Dialog.Close asChild>
                  <Button type="button" variant="outline">Cancel</Button>
                </Dialog.Close>
                <Button type="submit" disabled={!currentPassword || !newPassword || changePassword.isPending}>
                  Save Password
                </Button>
              </div>
            </form>
          </Dialog.Content>
        </Dialog.Portal>
        </Dialog.Root>
      </div>
    </header>
  );
}
