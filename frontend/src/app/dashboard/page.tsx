import { AppShell } from "@/components/layout/app-shell";
import { DashboardHome } from "@/features/ranking/dashboard-home";

export default function DashboardPage() {
  return (
    <AppShell>
      <DashboardHome />
    </AppShell>
  );
}

