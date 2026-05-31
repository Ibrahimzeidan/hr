import Link from "next/link";
import { ArrowRight, CheckCircle2 } from "lucide-react";

import { ThemeToggle } from "@/components/shared/theme-toggle";
import { Button } from "@/components/ui/button";

const signals = ["Semantic scoring", "Skill gap detection", "Ranked shortlist"];

export function LandingPage() {
  return (
    <main>
      <section
        className="relative flex min-h-[86vh] flex-col bg-cover bg-center text-white"
        style={{ backgroundImage: "linear-gradient(90deg, rgba(6,31,35,.82), rgba(6,31,35,.36)), url('https://images.unsplash.com/photo-1551836022-d5d88e9218df?auto=format&fit=crop&w=1800&q=80')" }}
      >
        <nav className="flex items-center justify-between px-5 py-5 md:px-10">
          <Link href="/" className="text-lg font-semibold">Resume Ranker</Link>
          <div className="rounded-md bg-white/10 text-white backdrop-blur"><ThemeToggle /></div>
        </nav>
        <div className="flex flex-1 items-center px-5 pb-16 md:px-10">
          <div className="max-w-3xl">
            <h1 className="text-5xl font-semibold tracking-tight md:text-7xl">Resume Ranker</h1>
            <p className="mt-5 max-w-2xl text-lg leading-8 text-white/85">
              AI-assisted resume screening that compares candidates against a job description and ranks the strongest matches first.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Button asChild size="default"><Link href="/analysis">Start analysis <ArrowRight className="h-4 w-4" /></Link></Button>
              <Button asChild variant="outline"><Link href="/dashboard">Open dashboard</Link></Button>
            </div>
          </div>
        </div>
      </section>
      <section className="grid gap-4 px-5 py-8 md:grid-cols-3 md:px-10">
        {signals.map((signal) => (
          <div key={signal} className="flex items-center gap-3 rounded-lg border bg-card p-4">
            <CheckCircle2 className="h-5 w-5 text-primary" />
            <span className="font-medium">{signal}</span>
          </div>
        ))}
      </section>
    </main>
  );
}

