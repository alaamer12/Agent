# Blockiya Core (`blockiya-core`) Implementation Reference

> **Naming:** `blockiya-core` is the author's recommended name for the utilities package. Any name is valid — the requirements are the `<<Utility>>` compatibility contract and the single-barrel import rule, not the label.

This document covers the `blockiya-core` utility package introduced in v2.1 (Strict Blockiya). For the methodology, mental model, stereotypes, and pattern rules, see the [methodology document](methodology-and-rules.md). For the tool-agnostic procedure to assemble this package into a project, see the [scaffolding guide](scaffold-blockiya-core.md).

---

## Table of Contents

- [`blockiya-core` — overview](#blockiya-core--overview)
- [Directory structure](#directory-structure)
- [`index.ts` — the single export surface](#indexts--the-single-export-surface)
- [Complete utility reference](#complete-utility-reference)
- [Structural primitives](#structural-primitives)
  - [`If` — truthy condition gate](#if--truthy-condition-gate)
  - [`For` — typed list rendering](#for--typed-list-rendering)
  - [`Maybe` — non-null/undefined gate](#maybe--non-nullundefined-gate)
  - [`Repeat` — render N times](#repeat--render-n-times)
  - [`Compose` — flatten provider nesting](#compose--flatten-provider-nesting)
- [Intent utilities](#intent-utilities)
  - [`useIntent` — async intent lifecycle](#useintent--async-intent-lifecycle)
  - [`createIntent` — typed intent factory](#createintent--typed-intent-factory)
  - [`composeIntents` — multi-handler fan-out](#composeintents--multi-handler-fan-out)
- [Derivation hooks](#derivation-hooks)
  - [`useDerive` — memoised derivation](#usederive--memoised-derivation)
  - [`useDerivedState` — editable derived state](#usederivedstate--editable-derived-state)
- [Interaction hooks](#interaction-hooks)
  - [`useToggle`](#usetoggle)
  - [`useDebounce`](#usedebounce)
  - [`usePrevious`](#useprevious)
  - [`useStableCallback`](#usestablecallback)
- [Original Structural Primitives Draft Note](#original-structural-primitives-draft-note)
- [Version history](#version-history)

---

## `blockiya-core` — overview

`blockiya-core` is the utilities layer (`<<Utility>>` stereotype) — the canonical **compatibility standard** for helpers that work alongside Blockiya machinery. Membership is defined by interoperability, not by origin: a helper qualifies when it contributes without contradiction and without taking over control — no domain knowledge, no visual output, never steering state placement or intent flow. Any package can hold that slot; this one holds it first, with the helpers every Blockiya reaches for.

The intent utilities, derivation hooks, and structural renderers are not general-purpose code — they exist because the Blockiya pattern demands them. The pattern says "derive before you pass" — `useDerive` makes that rule mechanical. The pattern says "fire intents upward" — `useIntent` owns the async lifecycle so the Blockiya never has to manage `isLoading` and `error` manually for every operation. The interaction hooks are a different kind of member: generic mechanics admitted by contract, not by demand — they qualify because they satisfy the interoperability clauses above, which is exactly the opening that lets any compatible package take this slot.

This package is the canonical React/TypeScript implementation of those rules. The rules it enforces — intent lifecycle ownership, derive-before-pass, explicit rendering shape — are the pattern's substance; the hook and JSX syntax is this stack's expression of them. In Vue, Svelte, Solid, or MAUI/Blazor C#, re-express the concepts natively (composables, runes/signals, commands with async state) rather than porting these files verbatim — see "Blockiya beyond React" in [methodology-and-rules.md](methodology-and-rules.md).

---

## Directory structure

```
shared/
  blockiya-core/
    structural/
      If.tsx              ← truthy condition gate
      Maybe.tsx           ← non-null/undefined gate, passes value down
      For.tsx             ← typed list rendering with enforced key
      Repeat.tsx          ← renders children N times (skeletons)
      Compose.tsx         ← wraps children in multiple providers without nesting hell
    intents/
      useIntent.ts        ← async intent lifecycle hook
      createIntent.ts     ← typed intent factory
      composeIntents.ts   ← multi-handler fan-out
    derivation/
      useDerive.ts        ← memoised derivation hook
      useDerivedState.ts  ← editable derived state hook
    hooks/
      useToggle.ts        ← boolean flip mechanic
      useDebounce.ts      ← value delay mechanic
      usePrevious.ts      ← cross-render memory
      useStableCallback.ts ← stable function reference
    index.ts              ← single public export surface
```

---

## `index.ts` — the single export surface

All utilities are re-exported from a single `index.ts`. Consumers import from `blockiya-core` only — never from individual files. This keeps the internal file structure free to change without breaking import paths across the codebase.

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

---

## Complete utility reference

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

---

## Structural primitives

Structural primitives control rendering shape. They have no visual output and no domain knowledge. The Blockiya reaches for them the same way it reaches for `Box` or `Flex` — they are primitives, just structural rather than visual.

Here's a fuller list, grouped by what problem they solve:

**Conditional Rendering**

- `<If />` — truthy condition gate
- `<Maybe />` — renders only when value is non-null/undefined, passes the value down

**List & Iteration**

- `<For each={} keyBy={} empty={<EmptyState />} />` — typed list rendering with enforced key
- `<Repeat times={} />` — renders children N times, useful for skeletons

**Composition & Slotting**

- `<Compose pipes={[]} />` — wraps children in multiple providers/wrappers without nesting hell

---

### `If` — truthy condition gate

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

### `For` — typed list rendering

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

---

### `Maybe` — non-null/undefined gate

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

// vs the If equivalent — condition is truthy but not narrowed to non-null
<If condition={selectedUser}>
  {(user) => <UserDetail user={user} />}
</If>
```

**`If` vs `Maybe` at a glance:**

|  | `If` | `Maybe` |
| --- | --- | --- |
| Condition type | Any truthy value | Non-null/undefined only |
| Render function child | Receives condition value | Receives value narrowed to `TValue` |
| Use case | Boolean flags, derived conditions | Optional domain objects |

---

### `Repeat` — render N times

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

---

### `Compose` — flatten provider nesting

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

// vs the manual equivalent
<ThemeProvider>
  <QueryProvider>
    <AuthProvider>
      <App />
    </AuthProvider>
  </QueryProvider>
</ThemeProvider>
```

---

## Intent utilities

Intent utilities serve the pattern's core mechanic: Blockiyas fire intents upward and stop. These utilities make that mechanic typed, composable, and equipped with async lifecycle management.

### `useIntent` — async intent lifecycle

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

// Before useIntent — repeated in every Blockiya handler:
// const [isLoading, setIsLoading] = useState(false)
// const [error, setError] = useState<Error | null>(null)
// const handleSave = useCallback(async () => {
//   setIsLoading(true)
//   try { ... } catch (err) { setError(err) } finally { setIsLoading(false) }
// }, [...])
```

### `createIntent` — typed intent factory

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
// and routes accordingly — the Blockiya has no opinion on what happens next
```

### `composeIntents` — multi-handler fan-out

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
// all three fire; Blockiya fires once and stops
```

---

## Derivation hooks

Derivation hooks make the pattern rule "derive before you pass" mechanical. Without them, every Blockiya writes `useMemo` calls by hand and the pattern rule is aspirational. With them, the rule has a named, enforced home.

### `useDerive` — memoised derivation

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

// Before useDerive:
// const displayUser = useMemo(() => deriveDisplayUser(user), [user])
// After: the pattern's intent is named, not implied
```

### `useDerivedState` — editable derived state

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

<input
  value={draft.name}
  onChange={(e) => setDraft((prev) => ({ ...prev, name: e.target.value }))}
/>

// Before useDerivedState — repeated in every edit Blockiya:
// const [draft, setDraft] = useState(() => transform(user))
// useEffect(() => { if (user !== prev) setDraft(transform(user)) }, [user])
```

**`useDerive` vs `useDerivedState` at a glance:**

|  | `useDerive` | `useDerivedState` |
| --- | --- | --- |
| User can edit? | No | Yes |
| Resets on source change? | Always (read-only) | Yes, automatically |
| Returns | derived value | `[state, setState]` |
| Use case | Display props passed to child | Edit draft that starts from server data |

---

## Interaction hooks

Interaction hooks are mechanics the host framework does not provide out of the box. They carry no domain knowledge and take no control away from a Blockiya — which is precisely the engagement the `<<Utility>>` slot requires. They live in `blockiya-core` as the canonical compatible versions: written once, correctly, snapping in without contradiction.

### `useToggle`

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

### `useDebounce`

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

### `usePrevious`

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

### `useStableCallback`

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

---

## Original Structural Primitives Draft Note

> Preserved verbatim from the original `Draft` document alongside the implemented v2.1 API above. Note that the early draft sketched `<For each={} keyBy={} empty={<EmptyState /> />` whereas the final v2.1 TypeScript implementation in `structural/For.tsx` uses `<For each={} keyExtractor={} fallback={} />`.

# Draft

Here's a fuller list, grouped by what problem they solve:

---

**Conditional Rendering**

- `<If />` — truthy condition gate
- `<Maybe />` — renders only when value is non-null/undefined, passes the value down

---

**List & Iteration**

- `<For each={} keyBy={} empty={<EmptyState /> />` — typed list rendering with enforced key
- `<Repeat times={} />` — renders children N times, useful for skeletons

---

**Composition & Slotting**

- `<Compose pipes={[]} />` — wraps children in multiple providers/wrappers without nesting hell

## Version history

**v2.2.0** (2026-11-24) — documentation alignment with pattern v2.2.0; **no implementation changes**, the `blockiya-core` package itself remains at v2.1.0

- Changed: overview reframed — the `<<Utility>>` layer is a **compatibility standard**: membership is earned by interoperability (no domain knowledge, no visual output, never steering state placement or intent flow), not by origin; any package may occupy the slot
- Changed: interaction-hooks rationale now rests on the engagement contract rather than "projects re-invent them"
- Changed: `blockiya-core` stated as the author's recommended package name — the slot is name-agnostic (`--core-name` in the audit)

**v2.1.0** (2026-03-25)

- Added: `<<Utility>>` stereotype — pattern-native structural helpers with no domain knowledge and no visual output
- Added: `blockiya-core/` directory structure — `structural/`, `intents/`, `derivation/`, `hooks/`, and `index.ts`
- Added: Structural primitives — `If` (conditional rendering), `Maybe` (non-null gate), `For` (typed list rendering), `Repeat` (N-times rendering), `Compose` (provider flattening)
- Added: Intent utilities — `useIntent`, `createIntent`, `composeIntents`
- Added: Derivation hooks — `useDerive`, `useDerivedState`
- Added: Interaction hooks — `useToggle`, `useDebounce`, `usePrevious`, `useStableCallback`
- Added: `useDerive` vs `useDerivedState` comparison table
- Added: `useStableCallback` vs `useCallback` comparison table