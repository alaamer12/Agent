import { _ReceiptLine } from "../_ReceiptLine";
export function OrderSummary({ items }: any) {
  return <section>{items.map((i: any) => <_ReceiptLine key={i.id} label={i.name} />)}</section>;
}
