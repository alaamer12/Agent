import { usePremiumCondition } from "../../../../shared/conditions/usePremiumCondition";
import { PremiumResultRendition } from "./PremiumResultRendition";
import { StandardResultRendition } from "./StandardResultRendition";
export function SearchResultRendition({ result }: { result: any }) {
  const { isPremium } = usePremiumCondition();
  if (isPremium) return <PremiumResultRendition result={result} />;
  return <StandardResultRendition result={result} />;
}
