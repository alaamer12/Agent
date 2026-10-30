import { useSearchStore } from "../../behaviour/searchStore";
export function SearchErrorRendition() {
  const { error } = useSearchStore();
  return <SearchErrorMessage message={error} />;
}
