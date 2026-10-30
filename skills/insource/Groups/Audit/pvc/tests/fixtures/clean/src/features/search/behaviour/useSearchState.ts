import { useAsyncState } from "../../../shared/behaviour/useAsyncState";
export function useSearchState(q: string) { return useAsyncState(() => fetchResults(q)); }
