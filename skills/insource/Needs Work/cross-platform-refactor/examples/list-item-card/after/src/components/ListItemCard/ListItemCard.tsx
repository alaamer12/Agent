// src/components/ListItemCard/ListItemCard.tsx  ✅ host shell — no real layout content
import { useMediaQuery } from '@/hooks/useMediaQuery';
import { ListItemCardDesktopLayout } from './ListItemCardDesktopLayout';
import { ListItemCardMobileLayout } from './ListItemCardMobileLayout';
import type { Entity } from '@/types';

export function ListItemCard({ item }: { item: Entity }) {
  const isMobile = useMediaQuery('(max-width: 600px)');
  const Layout = isMobile ? ListItemCardMobileLayout : ListItemCardDesktopLayout;
  return <Layout item={item} />;
}
