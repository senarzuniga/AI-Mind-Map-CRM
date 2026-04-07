interface Props {
  className?: string;
  children: React.ReactNode;
}

export default function Card({ className = '', children }: Props) {
  return (
    <div className={`bg-white rounded-xl shadow-sm border border-gray-200 ${className}`}>
      {children}
    </div>
  );
}
