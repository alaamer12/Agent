export function useNetworkCondition() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  useEffect(() => { const on = () => setIsOnline(true); return on; }, []);
  return { isOnline };
}
