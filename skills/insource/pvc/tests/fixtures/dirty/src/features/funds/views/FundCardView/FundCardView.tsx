import { useLayoutToggleCondition } from "../../behaviour/useLayoutToggleCondition";
import { FundCardListRendition } from "./FundCardListRendition";
export function FundCardView({ fund }: any) {
  const { layout } = useLayoutToggleCondition();
  if (layout === "grid") return <FundCardGridRendition fund={fund} />;
  return <FundCardListRendition fund={fund} />;
}
