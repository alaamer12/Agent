#!/usr/bin/env python3
"""Scaffold the complete v2.1.0 blockiya-core utility package into a target directory.

Usage:
    python scripts/scaffold_blockiya_core.py <target_directory> [--force]

Example:
    python scripts/scaffold_blockiya_core.py src/shared/blockiya-core
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

FILES: dict[str, str] = {
    "index.ts": """// blockiya-core/index.ts

export { If } from './structural/If';
export { Maybe } from './structural/Maybe';
export { For } from './structural/For';
export { Repeat } from './structural/Repeat';
export { Compose } from './structural/Compose';

export { useIntent } from './intents/useIntent';
export type { UseIntentResult } from './intents/useIntent';
export { createIntent } from './intents/createIntent';
export type { Intent, IntentCreator } from './intents/createIntent';
export { composeIntents } from './intents/composeIntents';

export { useDerive } from './derivation/useDerive';
export { useDerivedState } from './derivation/useDerivedState';

export { useToggle } from './hooks/useToggle';
export { useDebounce } from './hooks/useDebounce';
export { usePrevious } from './hooks/usePrevious';
export { useStableCallback } from './hooks/useStableCallback';
""",
    "structural/If.tsx": """// structural/If.tsx
import React, { useMemo } from 'react';

type Falsy = false | null | undefined | 0 | '';

export function If<TValue = unknown>({
  condition,
  children,
  fallback,
}: {
  condition: TValue | Falsy;
  children: React.ReactNode | ((value: TValue) => React.ReactNode);
  fallback?: React.ReactNode;
}) {
  return useMemo(() => {
    if (condition) {
      return (
        <>
          {typeof children === 'function'
            ? children(condition as TValue)
            : children}
        </>
      );
    }
    return fallback ? <>{fallback}</> : null;
  }, [condition, children, fallback]);
}
""",
    "structural/Maybe.tsx": """// structural/Maybe.tsx
import React from 'react';

export function Maybe<TValue>({
  value,
  children,
  fallback,
}: {
  value: TValue | null | undefined;
  children: (value: TValue) => React.ReactNode;
  fallback?: React.ReactNode;
}) {
  if (value == null) return fallback ? <>{fallback}</> : null;
  return <>{children(value)}</>;
}
""",
    "structural/For.tsx": """// structural/For.tsx
import React from 'react';

export function For<TItem>({
  each,
  keyExtractor,
  children,
  fallback,
}: {
  each: TItem[];
  keyExtractor: (item: TItem, index: number) => string;
  children: (item: TItem, index: number) => React.ReactNode;
  fallback?: React.ReactNode;
}) {
  if (each.length === 0) return fallback ? <>{fallback}</> : null;
  return (
    <>
      {each.map((item, index) => (
        <React.Fragment key={keyExtractor(item, index)}>
          {children(item, index)}
        </React.Fragment>
      ))}
    </>
  );
}
""",
    "structural/Repeat.tsx": """// structural/Repeat.tsx
import React from 'react';

export function Repeat({
  times,
  children,
}: {
  times: number;
  children: (index: number) => React.ReactNode;
}) {
  return (
    <>
      {Array.from({ length: times }, (_, i) => (
        <React.Fragment key={i}>{children(i)}</React.Fragment>
      ))}
    </>
  );
}
""",
    "structural/Compose.tsx": """// structural/Compose.tsx
import React from 'react';

type Wrapper = React.ComponentType<{ children: React.ReactNode }>;

export function Compose({
  pipes,
  children,
}: {
  pipes: Wrapper[];
  children: React.ReactNode;
}) {
  return pipes.reduceRight(
    (acc, Wrapper) => <Wrapper>{acc}</Wrapper>,
    <>{children}</>
  );
}
""",
    "intents/useIntent.ts": """// intents/useIntent.ts
import { useCallback, useEffect, useRef, useState } from 'react';

export type UseIntentResult<TArgs extends unknown[]> = {
  fire: (...args: TArgs) => Promise<void>;
  isLoading: boolean;
  error: Error | null;
  reset: () => void;
};

export function useIntent<TArgs extends unknown[]>(
  handler: (...args: TArgs) => Promise<void>
): UseIntentResult<TArgs> {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  // Stabilise handler so fire() never changes identity.
  // The caller does not need to wrap handler in useCallback.
  const handlerRef = useRef(handler);
  useEffect(() => { handlerRef.current = handler; });

  const fire = useCallback(async (...args: TArgs) => {
    setIsLoading(true);
    setError(null);
    try {
      await handlerRef.current(...args);
    } catch (err) {
      setError(err instanceof Error ? err : new Error(String(err)));
    } finally {
      setIsLoading(false);
    }
  }, []); // stable — handlerRef absorbs updates

  const reset = useCallback(() => {
    setIsLoading(false);
    setError(null);
  }, []);

  return { fire, isLoading, error, reset };
}
""",
    "intents/createIntent.ts": """// intents/createIntent.ts
export type Intent<TPayload = void> = {
  readonly type: string;
  readonly payload: TPayload;
};

export type IntentCreator<TPayload = void> =
  (payload: TPayload) => Intent<TPayload>;

export function createIntent<TPayload = void>(
  type: string
): IntentCreator<TPayload> {
  return (payload: TPayload) => Object.freeze({ type, payload });
}
""",
    "intents/composeIntents.ts": """// intents/composeIntents.ts
export function composeIntents<TArgs extends unknown[]>(
  ...handlers: Array<((...args: TArgs) => void) | undefined>
): (...args: TArgs) => void {
  return (...args: TArgs) => {
    handlers.forEach((h) => h?.(...args));
  };
}
""",
    "derivation/useDerive.ts": """// derivation/useDerive.ts
import { useMemo } from 'react';

export function useDerive<TSource, TDerived>(
  source: TSource,
  deriver: (source: TSource) => TDerived
): TDerived {
  // eslint-disable-next-line react-hooks/exhaustive-deps
  return useMemo(() => deriver(source), [source]);
  // deriver is intentionally excluded from deps —
  // it must be a stable function defined at module scope, not inline.
}
""",
    "derivation/useDerivedState.ts": """// derivation/useDerivedState.ts
import { useEffect, useRef, useState } from 'react';

export function useDerivedState<TSource, TState>(
  source: TSource,
  transform: (source: TSource) => TState
): [TState, React.Dispatch<React.SetStateAction<TState>>] {
  const [state, setState] = useState<TState>(() => transform(source));
  const prevRef = useRef<TSource>(source);

  useEffect(() => {
    if (!Object.is(prevRef.current, source)) {
      prevRef.current = source;
      setState(transform(source));
    }
  }, [source, transform]);

  return [state, setState];
}
""",
    "hooks/useToggle.ts": """// hooks/useToggle.ts
import { useCallback, useState } from 'react';

export function useToggle(
  initial = false
): [boolean, () => void, () => void, () => void] {
  const [value, setValue] = useState(initial);
  const toggle   = useCallback(() => setValue((v) => !v), []);
  const setTrue  = useCallback(() => setValue(true), []);
  const setFalse = useCallback(() => setValue(false), []);
  return [value, toggle, setTrue, setFalse];
}
""",
    "hooks/useDebounce.ts": """// hooks/useDebounce.ts
import { useEffect, useState } from 'react';

export function useDebounce<TValue>(value: TValue, delay: number): TValue {
  const [debounced, setDebounced] = useState<TValue>(value);

  useEffect(() => {
    const id = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(id);
  }, [value, delay]);

  return debounced;
}
""",
    "hooks/usePrevious.ts": """// hooks/usePrevious.ts
import { useEffect, useRef } from 'react';

export function usePrevious<TValue>(value: TValue): TValue | undefined {
  const ref = useRef<TValue | undefined>(undefined);

  useEffect(() => {
    ref.current = value;
  }, [value]); // updates after render — ref.current is always one render behind

  return ref.current;
}
""",
    "hooks/useStableCallback.ts": """// hooks/useStableCallback.ts
import { useCallback, useEffect, useRef } from 'react';

export function useStableCallback<TArgs extends unknown[], TReturn>(
  callback: (...args: TArgs) => TReturn
): (...args: TArgs) => TReturn {
  const callbackRef = useRef(callback);

  useEffect(() => {
    callbackRef.current = callback;
  }); // no deps — always syncs to latest

  return useCallback((...args: TArgs) => callbackRef.current(...args), []);
}
""",
}


def scaffold(target: Path, force: bool = False) -> int:
    created = 0
    skipped = 0
    for rel_path, content in FILES.items():
        dest = target / rel_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists() and not force:
            print(f"[SKIP] {dest} already exists (use --force to overwrite)")
            skipped += 1
            continue
        dest.write_text(content, encoding="utf-8", newline="\n")
        print(f"[OK]   {dest}")
        created += 1
    print(f"Done: {created} file(s) written, {skipped} skipped in {target}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Scaffold the v2.1.0 blockiya-core TypeScript utility package."
    )
    parser.add_argument(
        "target",
        type=Path,
        help="Destination directory (e.g., src/shared/blockiya-core)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files",
    )
    args = parser.parse_args()
    return scaffold(args.target, force=args.force)


if __name__ == "__main__":
    sys.exit(main())
