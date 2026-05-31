import { BarChart3, FileSearch, LayoutDashboard, Settings, Users } from "lucide-react";

export const navigation = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/analysis", label: "Analysis", icon: FileSearch },
  { href: "/candidates", label: "Candidates", icon: Users },
  { href: "/settings", label: "Settings", icon: Settings },
  { href: "/", label: "Overview", icon: BarChart3 }
] as const;

