export default function Loading({ label = "불러오는 중..." }: { label?: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 text-gray-500">
      <span className="h-8 w-8 animate-spin rounded-full border-4 border-primary-200 border-t-primary-600" />
      <p className="text-sm">{label}</p>
    </div>
  );
}
