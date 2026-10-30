# blockiya-core — Complete Utility Reference & Implementation

Source: The Blockiya Pattern Implementation Reference (v2.1)

`blockiya-core` is the utilities layer (`<<Utility>>` stereotype). It fills a gap that existed from the beginning: pattern-native structural helpers that every Blockiya needs but that had no designated home in the existing layers.

These are not business utilities. They are not generic React helpers that any codebase would want. They exist specifically because the Blockiya pattern demands them. The pattern says "derive before you pass" — `useDerive` makes that rule mechanical. The pattern says "fire intents upward" — `useIntent` owns the async lifecycle so the Blockiya never has to manage `isLoading` and `error` manually for every operation.

## Directory structure

```
shared/
  blockiya-core/
    structural/
      If.tsx
      Maybe.tsx
      For.tsx
      Repeat.tsx
      Compose.tsx
    intents/
      useIntent.ts
      createIntent.ts
      composeIntents.ts
    derivation/
      useDerive.ts
      useDerivedState.ts
    hooks/
      useToggle.ts
      useDebounce.ts
      usePrevious.ts
      useStableCallback.ts
    index.ts
```

## index.ts — the single export surface

All utilities are re-exported from a single `index.ts`. Consumers import from `blockiya-core` only — never from individual files.

```tsx
// blockiya-core/index.ts

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

// Import rule — always from the package, never from individual files:
// import { useIntent, useDerive, If, For } from '@/shared/blockiya-core';
```

## Complete utility reference table

| Export | Category | File | Purpose |
| --- | --- | --- | --- |
| `If` | Structural | `structural/If.tsx` | Truthy condition gate with optional fallback and render-function child |
| `Maybe` | Structural | `structural/Maybe.tsx` | Renders only when value is non-null/undefined; passes the value down typed |
| `For` | Structural | `structural/For.tsx` | Typed list rendering with explicit key extractor and built-in empty state |
| `Repeat` | Structural | `structural/Repeat.tsx` | Renders children N times; useful for skeleton placeholders |
| `Compose` | Structural | `structural/Compose.tsx` | Wraps children in multiple providers/wrappers without nesting hell |
| `useIntent` | Intents | `intents/useIntent.ts` | Wraps async handler with `isLoading` + `error` lifecycle. Stabilises handler ref internally |
| `createIntent` | Intents | `intents/createIntent.ts` | Typed intent factory. Stamps payload with a string type for caller-side routing |
| `composeIntents` | Intents | `intents/composeIntents.ts` | Fans one fire call out to multiple optional handlers |
| `useDerive` | Derivation | `derivation/useDerive.ts` | Memoised derivation. Enforces derive-before-pass mechanically |
| `useDerivedState` | Derivation | `derivation/useDerivedState.ts` | Editable local state that resets automatically when source reference changes |
| `useToggle` | Hooks | `hooks/useToggle.ts` | Boolean flip mechanic. Returns `[value, toggle, setTrue, setFalse]` |
| `useDebounce` | Hooks | `hooks/useDebounce.ts` | Delays a value update by N ms. Used for search inputs and auto-save drafts |
| `usePrevious` | Hooks | `hooks/usePrevious.ts` | Returns the value from the previous render. Undefined on first render |
| `useStableCallback` | Hooks | `hooks/useStableCallback.ts` | Stable function reference that always calls the latest callback. Identity never changes |

## Structural primitives

Structural primitives control rendering shape. They have no visual output and no domain knowledge. The Blockiya reaches for them the same way it reaches for `Box` or `Flex` — they are primitives, just structural rather than visual.

### If — truthy condition gate

`If` replaces inline ternaries and `&&` short-circuits in Blockiya render output. It supports a render-function child: when `condition` is truthy, the child function receives the condition value directly, eliminating a separate non-null assertion at the call site.

```tsx
// structural/If.tsx
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
```

```tsx
// Usage — simple boolean
<If condition={isEditing} fallback={<DisplayView />}>
  <EditView />
</If>

// Usage — render function (condition value is passed in typed)
<If condition={selectedUser}>
  {(user) => <UserDetail user={user} />}
</If>
```

### For — typed list rendering

`For` replaces `.map()` and the empty-state ternary that always accompanies it. `keyExtractor` is explicit — no accidental index keys.

```tsx
// structural/For.tsx
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
```

```tsx
// Usage
<For
  each={todos}
  keyExtractor={(todo) => todo.id}
  fallback={<EmptyState message="No tasks yet." />}
>
  {(todo) => <TodoItem todo={todo} />}
</For>
```

### Maybe — non-null/undefined gate

`Maybe` is a narrower version of `If`. Where `If` accepts any truthy condition, `Maybe` accepts only a value that may be `null` or `undefined`. When the value is present, the render-function child receives it already narrowed — no non-null assertion needed at the call site.

```tsx
// structural/Maybe.tsx
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
```

```tsx
// Usage — value is typed as User inside the render function, no assertion needed
<Maybe value={selectedUser} fallback={<EmptySelection />}>
  {(user) => <UserDetail user={user} />}
</Maybe>
```

**`If` vs `Maybe` at a glance:**

|  | `If` | `Maybe` |
| --- | --- | --- |
| Condition type | Any truthy value | Non-null/undefined only |
| Render function child | Receives condition value | Receives value narrowed to `TValue` |
| Use case | Boolean flags, derived conditions | Optional domain objects |

### Repeat — render N times

`Repeat` renders its children a fixed number of times. The primary use case is skeleton placeholders — render `<SkeletonRow />` five times while data loads without building an array manually.

```tsx
// structural/Repeat.tsx
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
```

```tsx
// Usage — skeleton loading state
<If condition={!isLoading} fallback={<Repeat times={5}>{() => <SkeletonRow />}</Repeat>}>
  <For each={items} keyExtractor={(item) => item.id}>
    {(item) => <ItemRow item={item} />}
  </For>
</If>
```

### Compose — flatten provider nesting

`Compose` accepts an array of wrapper components (providers, context boundaries, theme layers) and nests them around `children` without the pyramid of doom. Each entry in `pipes` is a component that accepts `children`.

```tsx
// structural/Compose.tsx
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
```

```tsx
// Usage — three providers, zero nesting
<Compose pipes={[ThemeProvider, QueryProvider, AuthProvider]}>
  <App />
</Compose>
```

## Intent utilities

Intent utilities serve the pattern's core mechanic: Blockiyas fire intents upward and stop. These utilities make that mechanic typed, composable, and equipped with async lifecycle management.

### useIntent — async intent lifecycle

Every Blockiya operation that can fail or takes time gets a `useIntent`. It replaces the `isLoading`/`error` `useState` pair and the `try/catch` block that every async handler would otherwise repeat. The handler is stabilised internally via a ref — the caller does not need `useCallback`.

```tsx
// intents/useIntent.ts
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
```

```tsx
// Usage inside a Blockiya
const save = useIntent(async (user: User) => {
  const saved = await saveUser(user);
  onSaveIntent(saved); // fires upward — useIntent's job ends here
});

<Button onClick={() => save.fire(draft)} disabled={save.isLoading}>
  {save.isLoading ? 'Saving…' : 'Save'}
</Button>
{save.error && <Text variant="danger">{save.error.message}</Text>}
```

### createIntent — typed intent factory

Stamps a payload with a string type so the caller can route by type rather than by callback position. Worth adopting when the codebase grows large enough that routing multiple intents at the page level becomes noisy without typed labels.

```tsx
// intents/createIntent.ts
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
```

```tsx
// Usage
const deleteUser = createIntent<{ userId: number }>('user/delete');
const saveUser   = createIntent<{ userId: number; name: string }>('user/save');

// Inside a Blockiya:
onIntent(deleteUser({ userId: 42 }));
// Page receives: { type: 'user/delete', payload: { userId: 42 } }
```

### composeIntents — multi-handler fan-out

Merges multiple intent handlers into one call. The Blockiya fires once — `composeIntents` fans it out to every listener. Optional handlers are skipped safely.

```tsx
// intents/composeIntents.ts
export function composeIntents<TArgs extends unknown[]>(
  ...handlers: Array<((...args: TArgs) => void) | undefined>
): (...args: TArgs) => void {
  return (...args: TArgs) => {
    handlers.forEach((h) => h?.(...args));
  };
}
```

```tsx
// Usage — three listeners, one fire call
const handleSave = composeIntents(
  onSaveIntent,
  onAnalyticsIntent, // optional
  onAuditIntent,     // optional
);
handleSave(data);
```

## Derivation hooks

Derivation hooks make the pattern rule "derive before you pass" mechanical. Without them, every Blockiya writes `useMemo` calls by hand and the pattern rule is aspirational. With them, the rule has a named, enforced home.

### useDerive — memoised derivation

```tsx
// derivation/useDerive.ts
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
```

```tsx
// Deriver defined at module scope — stable reference
function deriveDisplayUser(user: User): DisplayUser {
  return {
    fullName: user.name,
    roleBadge: { admin: 'Admin', editor: 'Editor', viewer: 'Viewer' }[user.role],
    accessLevel: user.isPremium ? 'Premium' : 'Standard',
  };
}

// Inside Blockiya — child never sees the raw User shape
const displayUser = useDerive(user, deriveDisplayUser);
<UserCardView user={displayUser} />
```

### useDerivedState — editable derived state

Different from `useDerive`: the state is editable and resets automatically when the source reference changes. The canonical use case is an edit draft that starts from server data and resets when a new version arrives.

```tsx
// derivation/useDerivedState.ts
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
```

```tsx
// Usage — draft starts from server user, resets if parent sends a new user prop
const [draft, setDraft] = useDerivedState(user, (u) => ({
  name: u.name,
  email: u.email,
}));
```

**`useDerive` vs `useDerivedState` at a glance:**

|  | `useDerive` | `useDerivedState` |
| --- | --- | --- |
| User can edit? | No | Yes |
| Resets on source change? | Always (read-only) | Yes, automatically |
| Returns | derived value | `[state, setState]` |
| Use case | Display props passed to child | Edit draft that starts from server data |

## Interaction hooks

Interaction hooks are generic React mechanics that React does not provide out of the box. They have no domain knowledge. They live in `blockiya-core` because every project re-invents them — having them here means they are written once, correctly.

### useToggle

```tsx
// hooks/useToggle.ts
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

// Usage
const [isEditing, toggleEditing, startEditing, stopEditing] = useToggle();
```

### useDebounce

```tsx
// hooks/useDebounce.ts
import { useEffect, useState } from 'react';

export function useDebounce<TValue>(value: TValue, delay: number): TValue {
  const [debounced, setDebounced] = useState<TValue>(value);

  useEffect(() => {
    const id = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(id);
  }, [value, delay]);

  return debounced;
}

// Usage — only fires search 400ms after typing stops
const debouncedQuery = useDebounce(query, 400);
useEffect(() => {
  if (debouncedQuery) search(debouncedQuery);
}, [debouncedQuery]);
```

### usePrevious

```tsx
// hooks/usePrevious.ts
import { useEffect, useRef } from 'react';

export function usePrevious<TValue>(value: TValue): TValue | undefined {
  const ref = useRef<TValue | undefined>(undefined);

  useEffect(() => {
    ref.current = value;
  }, [value]); // updates after render — ref.current is always one render behind

  return ref.current;
}

// Usage
const prevCount = usePrevious(count);
const direction = count > (prevCount ?? count) ? 'up' : 'down';
```

### useStableCallback

Different from `useCallback`: identity never changes, it always calls the latest version of the callback. Safe to pass to `ResizeObserver`, event listeners, or children that should not re-render when the callback logic changes.

```tsx
// hooks/useStableCallback.ts
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

// Usage — onResize never changes identity; closes over breakpoint safely
const onResize = useStableCallback((width: number) => {
  if (width < breakpoint) setLayout('compact');
});
```

**`useStableCallback` vs `useCallback` at a glance:**

|  | `useCallback` | `useStableCallback` |
| --- | --- | --- |
| Identity changes when? | When deps change | Never |
| Always calls latest version? | Only if deps are correct | Yes, always |
| Safe to omit from deps arrays? | No | Yes |
| Use case | Optimise child re-renders with stable deps | Event listeners, observers, children that must not re-render |

## Strict Blockiya enforcement summary

| Pattern rule | Utility that makes it mechanical |
| --- | --- |
| Derive before you pass | `useDerive` / `useDerivedState` |
| Fire intents upward (async) | `useIntent` |
| Conditional / list rendering | `If` / `Maybe` / `For` / `Repeat` |
| Provider nesting | `Compose` |
| No manual loading/error pairs | `useIntent` owns them |

When generating Strict Blockiya code, always prefer these utilities over the manual React equivalents.
