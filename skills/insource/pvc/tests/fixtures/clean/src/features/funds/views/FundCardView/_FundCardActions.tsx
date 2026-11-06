import { AddToWatchlist } from "../../components/AddToWatchlist";
import { CompareFund } from "../../components/CompareFund";
import { RemoveFund } from "../../components/RemoveFund";
export function _FundCardActions({ fund }: any) { return <div className="actions"><AddToWatchlist fund={fund} /><CompareFund fund={fund} /><RemoveFund fund={fund} /></div>; }
