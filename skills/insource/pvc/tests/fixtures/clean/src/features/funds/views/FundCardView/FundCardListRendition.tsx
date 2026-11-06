import { _FundCard } from "./_FundCard";
import { _FundCardActions } from "./_FundCardActions";
export function FundCardListRendition({ fund }: any) { return <section><_FundCard fund={fund} /><_FundCardActions fund={fund} /></section>; }
