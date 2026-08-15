/** Carte d'indicateur réutilisable (tableau de bord, rapports) */
export function StatCard({
  icon,
  label,
  value,
  sub,
  color,
}: {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  sub?: string;
  color: string;
}) {
  return (
    <div className="card bg-base-100 shadow-sm">
      <div className="card-body p-4">
        <div className={`w-9 h-9 ${color} rounded-lg flex items-center justify-center text-white`}>
          {icon}
        </div>
        <div className="mt-2">
          <p className="text-2xl font-bold">{value}</p>
          <p className="text-xs text-base-content/60">{label}</p>
          {sub && <p className="text-[10px] text-base-content/40 mt-0.5">{sub}</p>}
        </div>
      </div>
    </div>
  );
}
