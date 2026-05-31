"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { ThemeToggle } from "@/components/shared/theme-toggle";
import { navigation } from "@/constants/navigation";
import { cn } from "@/lib/utils";

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  return (
    <div className="min-h-screen bg-background">
      <aside className="fixed inset-y-0 left-0 hidden w-64 border-r bg-card/80 p-4 backdrop-blur lg:block">
        <Link href="/" className="flex h-12 items-center rounded-md px-3 text-lg font-semibold">
          Resume Ranker
        </Link>
        <nav className="mt-6 space-y-1">
          {navigation.map((item) => {
            const active = pathname === item.href;
            return (
              <Link key={item.href} href={item.href} className={cn("flex items-center gap-3 rounded-md px-3 py-2 text-sm hover:bg-muted", active && "bg-muted font-medium")}>
                <item.icon className="h-4 w-4" />
                {item.label}
              </Link>
            );
          })}
        </nav>
      </aside>
      <header className="sticky top-0 z-40 border-b bg-background/85 backdrop-blur lg:ml-64">
        <div className="flex h-16 items-center justify-between px-4 md:px-8">
          <span className="font-semibold lg:hidden">Resume Ranker</span>
          <div className="ml-auto"><ThemeToggle /></div>
        </div>
      </header>
      <main className="px-4 pb-24 pt-8 md:px-8 lg:ml-64 lg:pb-8">{children}</main>
      <nav className="fixed inset-x-0 bottom-0 z-40 grid grid-cols-4 border-t bg-card lg:hidden">
        {navigation.slice(0, 4).map((item) => {
          const active = pathname === item.href;
          return (
            <Link key={item.href} href={item.href} className={cn("grid place-items-center gap-1 px-2 py-2 text-xs", active && "text-primary")}>
              <item.icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>
    </div>
  );
}
