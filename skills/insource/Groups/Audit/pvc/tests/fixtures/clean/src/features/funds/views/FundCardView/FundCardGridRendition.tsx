import { _FundCard } from "./_FundCard";
import { FundCompactBadge } from "../../decorations/FundCompactBadge";
export function FundCardGridRendition({ fund }: any) { return <div><_FundCard fund={fund} /><FundCompactBadge fund={fund} /></div>; }
