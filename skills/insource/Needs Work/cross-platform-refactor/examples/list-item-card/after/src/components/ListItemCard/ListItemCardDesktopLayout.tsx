// src/components/ListItemCard/ListItemCardDesktopLayout.tsx  ✅ new file — full detail, real desktop design
export function ListItemCardDesktopLayout({ item }: { item: Entity }) {
  return (
    <div className="card card--grid">
      <img src={item.thumbnail} />
      <h3>{item.title}</h3>
      <span className="col">{item.owner}</span>
      <span className="col">{item.updatedAt}</span>
      <span className="col">{item.category}</span>
      <span className="col">{item.status}</span>
      <HoverActionsMenu item={item} />
    </div>
  );
}
