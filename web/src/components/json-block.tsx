export function JsonBlock({ value }: { value: unknown }) {
  return (
    <pre className="bg-muted/50 max-h-96 overflow-auto rounded-md border p-3 font-mono text-xs whitespace-pre-wrap">
      {JSON.stringify(value, null, 2)}
    </pre>
  )
}
