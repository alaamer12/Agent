export function SearchDisabledCondition() {
  const { isOnline } = useNetworkCondition();
  return isOnline ? null : <SearchDisabledMessage />;
}
