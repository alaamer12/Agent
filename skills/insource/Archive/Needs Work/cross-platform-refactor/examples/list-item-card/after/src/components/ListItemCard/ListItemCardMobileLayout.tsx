// src/components/ListItemCard/ListItemCardMobileLayout.tsx  ✅ new file — designed FOR mobile, not shrunk from desktop
export function ListItemCardMobileLayout({ item }: { item: Entity }) {
  // Deliberately shows only what matters at a glance on a small screen —
  // owner/updatedAt/category/status live behind a tap-through detail view instead of
  // being crammed in.
  return (
    <SwipeActions item={item}>
      <div className="card card--compact">
        <img src={item.thumbnail} />
        <div>
          <h3>{item.title}</h3>
          <StatusBadge status={item.status} />
        </div>
      </div>
    </SwipeActions>
  );
}
