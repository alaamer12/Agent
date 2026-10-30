import { Button } from "../../../../ui/adaptive/Button";
export function RemoveFund({ fund }: any) { return <Button onClick={() => drop(fund.id)}>Remove</Button>; }
