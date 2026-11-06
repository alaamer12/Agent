import { useNetworkCondition } from "../../../../shared/conditions/useNetworkCondition";
import { useSearchState } from "../../behaviour/useSearchState";
import { DebouncedSearchInput } from "../../components/SearchInput/DebouncedSearchInput";
import { SearchDescription } from "../../decorations/SearchDescription";
import { SearchDisabledRendition } from "./SearchDisabledRendition";
import { SearchLoadingRendition } from "./SearchLoadingRendition";
export function SearchView() {
  const [query, setQuery] = useState("");
  const { isOnline } = useNetworkCondition();
  const { state } = useSearchState(query);
  if (!isOnline) return <SearchDisabledRendition />;
  if (state === "loading") return <SearchLoadingRendition />;
  return <section><SearchDescription /><DebouncedSearchInput onSearch={setQuery} /></section>;
}
