import { _FundCard } from "./_FundCard";
export function FundCardListRendition({ fund }: any) {
  return <ListLayout><_FundCard fund={fund} /></ListLayout>;
}
