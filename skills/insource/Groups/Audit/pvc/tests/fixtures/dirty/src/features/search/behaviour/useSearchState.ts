export function useSearchState(q: string) {
  const [state, setState] = useState("idle");
  return { state };
}
