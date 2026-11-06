import { useNetworkCondition } from "../../../../shared/conditions/useNetworkCondition";
import { useSearchState } from "../../behaviour/useSearchState";
import { SearchErrorRendition } from "./SearchErrorRendition";
export function SearchView() {
  const { isOnline } = useNetworkCondition();
  const { state } = useSearchState("q");
  if (!isOnline) return <div>offline</div>;
  if (state === "error") return <SearchErrorRendition />;
  return <ResultsList />;
}
