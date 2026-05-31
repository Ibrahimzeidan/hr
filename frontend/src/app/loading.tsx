import { Skeleton } from "@/components/ui/skeleton";

export default function Loading() {
  return (
    <div className="space-y-4 p-8">
      <Skeleton className="h-10 w-72" />
      <Skeleton className="h-72 w-full" />
    </div>
  );
}

