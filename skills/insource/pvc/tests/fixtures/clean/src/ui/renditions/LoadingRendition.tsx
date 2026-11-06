import { Spinner } from "../adaptive/Spinner";
export function LoadingRendition({ text }: { text: string }) { return <Spinner aria-label={text} />; }
