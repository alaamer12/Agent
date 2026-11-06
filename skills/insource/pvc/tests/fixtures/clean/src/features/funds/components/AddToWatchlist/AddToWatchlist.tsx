import { Button } from "../../../../ui/adaptive/Button";
export function AddToWatchlist({ fund }: any) { return <Button onClick={() => watch(fund.id)}>Watch</Button>; }
