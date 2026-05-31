"use client";

import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Candidate } from "@/types/candidate";

export function ScoreDistribution({ candidates }: { candidates: Candidate[] }) {
  const buckets = [
    { label: "0-49", count: candidates.filter((item) => item.score < 50).length },
    { label: "50-69", count: candidates.filter((item) => item.score >= 50 && item.score < 70).length },
    { label: "70-84", count: candidates.filter((item) => item.score >= 70 && item.score < 85).length },
    { label: "85+", count: candidates.filter((item) => item.score >= 85).length }
  ];
  return (
    <Card>
      <CardHeader><CardTitle>Score Distribution</CardTitle></CardHeader>
      <CardContent className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={buckets}>
            <XAxis dataKey="label" tickLine={false} axisLine={false} />
            <YAxis allowDecimals={false} tickLine={false} axisLine={false} />
            <Tooltip cursor={{ fill: "hsl(var(--muted))" }} />
            <Bar dataKey="count" fill="hsl(var(--primary))" radius={[6, 6, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}

