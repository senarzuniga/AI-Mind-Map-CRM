export default function Spinner({ className = '' }: { className?: string }) {
  return (
    <div
      className={`inline-block animate-spin rounded-full border-4 border-gray-200 border-t-indigo-600 ${className}`}
      style={{ width: 32, height: 32 }}
      role="status"
      aria-label="Loading"
    />
  );
}
