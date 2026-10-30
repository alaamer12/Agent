import { Button } from "../../../../ui/adaptive/Button";
import { Spinner } from "../../../../ui/adaptive/Spinner";
export function _SearchInput({ value, onChange }: any) { return <div><Spinner /><Button onClick={onChange}>{value}</Button></div>; }
