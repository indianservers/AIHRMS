import { Bell, Menu, Moon, Sun } from "lucide-react";
import { Button } from "@/components/ui/button";
import GlobalSearch from "@/components/app/GlobalSearch";
import KeyboardShortcuts from "@/components/app/KeyboardShortcuts";
import { useThemeStore } from "@/store/themeStore";
import { useAuthStore } from "@/store/authStore";
import { getRoleLabel } from "@/lib/roles";

interface TopbarProps {
  onMenuClick: () => void;
}

export default function Topbar({ onMenuClick }: TopbarProps) {
  const { theme, setTheme } = useThemeStore();
  const { user } = useAuthStore();
  const roleLabel = getRoleLabel(user?.role, user?.is_superuser);

  const toggleTheme = () => setTheme(theme === "dark" ? "light" : "dark");

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
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="h-5 w-5" />
          <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-red-500" />
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

        {/* User avatar */}
        <div className="flex items-center gap-2 rounded-full border px-3 py-1.5 text-sm">
          <div className="flex h-6 w-6 items-center justify-center rounded-full bg-primary text-[10px] font-bold text-primary-foreground">
            {user?.email?.slice(0, 2).toUpperCase() || "?"}
          </div>
          <span className="hidden md:block text-sm font-medium max-w-32 truncate">
            {user?.email?.split("@")[0]}
          </span>
          <span className="hidden xl:block rounded-full bg-muted px-2 py-0.5 text-[10px] font-medium text-muted-foreground">
            {roleLabel}
          </span>
        </div>
      </div>
    </header>
  );
}
