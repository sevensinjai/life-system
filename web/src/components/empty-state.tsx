export function EmptyState({ children }: { children: React.ReactNode }) {
  return (
    <p className="text-muted-foreground rounded-lg border border-dashed px-4 py-8 text-center text-sm">
      {children}
    </p>
  )
}
