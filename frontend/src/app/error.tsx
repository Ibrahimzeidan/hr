"use client";

import { AlertTriangle } from "lucide-react";

import { Button } from "@/components/ui/button";

export default function ErrorPage({ reset }: { reset: () => void }) {
  return (
    <div className="grid min-h-screen place-items-center p-6 text-center">
      <div className="space-y-4">
        <AlertTriangle className="mx-auto h-10 w-10 text-amber-600" />
        <h1 className="text-2xl font-semibold">Something went wrong</h1>
        <Button onClick={reset}>Try again</Button>
      </div>
    </div>
  );
}

