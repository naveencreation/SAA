import * as React from "react";

import { cn } from "@/lib/utils";

export function FieldGroup({ className, ...props }: React.ComponentProps<"div">) {
  return <div className={cn("flex flex-col gap-6", className)} {...props} />;
}

export function Field({ className, ...props }: React.ComponentProps<"div">) {
  return <div className={cn("grid gap-2", className)} {...props} />;
}

export function FieldLabel({ className, ...props }: React.ComponentProps<"label">) {
  return (
    <label
      className={cn("text-sm font-medium leading-none text-foreground", className)}
      {...props}
    />
  );
}

export function FieldDescription({ className, ...props }: React.ComponentProps<"p">) {
  return <p className={cn("text-sm text-muted-foreground", className)} {...props} />;
}

export function FieldSeparator({ className, children, ...props }: React.ComponentProps<"div">) {
  return (
    <div className={cn("flex items-center gap-3 text-xs text-muted-foreground", className)} {...props}>
      <div className="h-px flex-1 bg-border" data-slot="field-separator-line" />
      <span className="px-2" data-slot="field-separator-content">
        {children}
      </span>
      <div className="h-px flex-1 bg-border" data-slot="field-separator-line" />
    </div>
  );
}
