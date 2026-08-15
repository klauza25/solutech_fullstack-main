/** Message affiché lorsqu'une liste filtrée ne retourne aucun résultat */
export function EmptyState({ message, icon }: { message: string; icon?: React.ReactNode }) {
  return (
    <div className="text-center py-8 text-base-content/50 text-sm">
      {icon && <div className="flex justify-center mb-2 opacity-50">{icon}</div>}
      {message}
    </div>
  );
}
