import { useDebounce } from "../../../../shared/behaviour/useDebounce";
import { _SearchInput } from "./_SearchInput";
export function DebouncedSearchInput({ onSearch }: any) { const [raw, setRaw] = useState(""); const q = useDebounce(raw, 300); useEffect(() => onSearch(q), [q]); return <_SearchInput value={raw} onChange={setRaw} />; }
