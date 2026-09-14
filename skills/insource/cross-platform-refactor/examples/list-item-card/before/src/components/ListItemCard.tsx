// src/components/ListItemCard.tsx  ❌ one layout tree pretending to serve both form factors
export function ListItemCard({ item }: { item: Entity }) {
  const isMobile = useMediaQuery('(max-width: 600px)');
  return (
    <div className={isMobile ? 'card card--compact' : 'card card--grid'}>
      <img src={item.thumbnail} />
      <h3>{item.title}</h3>
      {!isMobile && <span className="col">{item.owner}</span>}
      {!isMobile && <span className="col">{item.updatedAt}</span>}
      {!isMobile && <span className="col">{item.category}</span>}
      {!isMobile && <span className="col">{item.status}</span>}
      {!isMobile && <HoverActionsMenu item={item} />}
      {isMobile && <SwipeActions item={item} />}
    </div>
  );
}
