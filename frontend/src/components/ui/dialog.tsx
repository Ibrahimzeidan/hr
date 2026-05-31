"use client";

import * as DialogPrimitive from "@radix-ui/react-dialog";
import { X } from "lucide-react";
import * as React from "react";

import { cn } from "@/lib/utils";

export const Dialog = DialogPrimitive.Root;
export const DialogTrigger = DialogPrimitive.Trigger;

type ContentProps = React.ComponentPropsWithoutRef<typeof DialogPrimitive.Content>;
type TitleProps = React.ComponentPropsWithoutRef<typeof DialogPrimitive.Title>;
type DescriptionProps = React.ComponentPropsWithoutRef<typeof DialogPrimitive.Description>;

export function DialogContent({ className, children, ...props }: ContentProps) {
  return (
    <DialogPrimitive.Portal>
      <DialogPrimitive.Overlay className="fixed inset-0 z-50 bg-black/50" />
      <DialogPrimitive.Content
        className={cn("fixed left-1/2 top-1/2 z-50 max-h-[88vh] w-[92vw] max-w-2xl -translate-x-1/2 -translate-y-1/2 overflow-auto rounded-lg border bg-card p-6 shadow-soft", className)}
        {...props}
      >
        {children}
        <DialogPrimitive.Close className="absolute right-4 top-4 rounded-md p-1 hover:bg-muted">
          <X className="h-4 w-4" />
        </DialogPrimitive.Close>
      </DialogPrimitive.Content>
    </DialogPrimitive.Portal>
  );
}

export function DialogHeader(props: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("mb-4 space-y-1", props.className)} {...props} />;
}

export function DialogTitle(props: TitleProps) {
  return <DialogPrimitive.Title className={cn("text-lg font-semibold", props.className)} {...props} />;
}

export function DialogDescription(props: DescriptionProps) {
  return <DialogPrimitive.Description className={cn("text-sm text-muted-foreground", props.className)} {...props} />;
}
