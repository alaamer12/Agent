# blockiya-core — Polyglot Utility Contracts & Implementations

The utilities exist because the pattern demands them. They have **no domain knowledge** and **no visual output**. The test for membership: if you removed every domain word and the helper still made complete sense, it belongs here.

This document defines the **universal contract** each utility must satisfy, then provides idiomatic implementations for React and Vue Composition API. Other frameworks (Svelte, Solid, Angular, Qwik, etc.) implement the same contracts with their native reactivity primitives.

Import only from the package root of the target framework's `blockiya-core`.

---

## Universal Contracts

### Structural helpers

| Utility | Contract |
| --- | --- |
| **If** | Renders children only when condition is truthy. Optional fallback. Optional render-function / scoped slot that receives the truthy value. |
| **Maybe** | Renders only when value is non-null/undefined. Passes the narrowed value to children / slot. |
| **For** | Renders a list with an explicit key extractor. Optional empty/fallback state. |
| **Repeat** | Renders children N times (skeletons). |
| **Compose** | Flattens nested providers / wrappers without pyramid-of-doom. |

### Intent helpers

| Utility | Contract |
| --- | --- |
| **useIntent / useIntent()** | Wraps an async handler. Exposes `fire` (or equivalent), `isLoading`, `error`, `reset`. Stabilises the handler so identity does not thrash. Owns the loading/error lifecycle so the Blockiya never manages those pairs manually. |
| **createIntent** | Factory that stamps a payload with a string type for typed routing at the caller. |
| **composeIntents** | Fans one fire call out to multiple optional handlers. |

### Derivation helpers

| Utility | Contract |
| --- | --- |
| **useDerive / useDerive()** | Memoised / computed pure derivation. Deriver must be a stable pure function (module scope). Source change triggers re-derivation. |
| **useDerivedState / useDerivedState()** | Editable local copy that automatically resets when the source reference changes. Canonical for edit drafts. |

### Interaction helpers

| Utility | Contract |
| --- | --- |
| **useToggle** | Boolean flip: value + toggle + setTrue + setFalse. |
| **useDebounce** | Delays a value by N ms. |
| **usePrevious** | Returns the value from the previous evaluation / render. |
| **useStableCallback** | Stable function reference that always invokes the latest logic. |

---

## React Implementation (hooks + components)

### Structural

```tsx
// If.tsx
import React, { useMemo } from 'react';
type Falsy = false | null | undefined | 0 | '';
export function If<TValue = unknown>({
  condition, children, fallback,
}: {
  condition: TValue | Falsy;
  children: React.ReactNode | ((value: TValue) => React.ReactNode);
  fallback?: React.ReactNode;
}) {
  return useMemo(() => {
    if (condition) {
      return <>{typeof children === 'function' ? children(condition as TValue) : children}</>;
    }
    return fallback ? <>{fallback}</> : null;
  }, [condition, children, fallback]);
}
```

```tsx
// Maybe.tsx
export function Maybe<TValue>({
  value, children, fallback,
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
// For.tsx
export function For<TItem>({
  each, keyExtractor, children, fallback,
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
// Repeat.tsx
export function Repeat({ times, children }: {
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
// Compose.tsx
type Wrapper = React.ComponentType<{ children: React.ReactNode }>;
export function Compose({ pipes, children }: {
  pipes: Wrapper[];
  children: React.ReactNode;
}) {
  return pipes.reduceRight((acc, Wrapper) => <Wrapper>{acc}</Wrapper>, <>{children}</>);
}
```

### Intent

```tsx
// useIntent.ts
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
  }, []);

  const reset = useCallback(() => {
    setIsLoading(false);
    setError(null);
  }, []);

  return { fire, isLoading, error, reset };
}
```

```tsx
// createIntent.ts
export type Intent<TPayload = void> = { readonly type: string; readonly payload: TPayload };
export function createIntent<TPayload = void>(type: string) {
  return (payload: TPayload) => Object.freeze({ type, payload });
}
```

```tsx
// composeIntents.ts
export function composeIntents<TArgs extends unknown[]>(
  ...handlers: Array<((...args: TArgs) => void) | undefined>
) {
  return (...args: TArgs) => { handlers.forEach((h) => h?.(...args)); };
}
```

### Derivation

```tsx
// useDerive.ts
import { useMemo } from 'react';
export function useDerive<TSource, TDerived>(
  source: TSource,
  deriver: (source: TSource) => TDerived
): TDerived {
  // eslint-disable-next-line react-hooks/exhaustive-deps
  return useMemo(() => deriver(source), [source]);
}
```

```tsx
// useDerivedState.ts
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

### Interaction

```tsx
// useToggle.ts
import { useCallback, useState } from 'react';
export function useToggle(initial = false): [boolean, () => void, () => void, () => void] {
  const [value, setValue] = useState(initial);
  const toggle = useCallback(() => setValue((v) => !v), []);
  const setTrue = useCallback(() => setValue(true), []);
  const setFalse = useCallback(() => setValue(false), []);
  return [value, toggle, setTrue, setFalse];
}
```

```tsx
// useDebounce.ts
import { useEffect, useState } from 'react';
export function useDebounce<TValue>(value: TValue, delay: number): TValue {
  const [debounced, setDebounced] = useState<TValue>(value);
  useEffect(() => {
    const id = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(id);
  }, [value, delay]);
  return debounced;
}
```

```tsx
// usePrevious.ts
import { useEffect, useRef } from 'react';
export function usePrevious<TValue>(value: TValue): TValue | undefined {
  const ref = useRef<TValue | undefined>(undefined);
  useEffect(() => { ref.current = value; }, [value]);
  return ref.current;
}
```

```tsx
// useStableCallback.ts
import { useCallback, useEffect, useRef } from 'react';
export function useStableCallback<TArgs extends unknown[], TReturn>(
  callback: (...args: TArgs) => TReturn
): (...args: TArgs) => TReturn {
  const callbackRef = useRef(callback);
  useEffect(() => { callbackRef.current = callback; });
  return useCallback((...args: TArgs) => callbackRef.current(...args), []);
}
```

---

## Vue Composition API Implementation

Vue equivalents use `ref` / `computed` / `watch` and provide the same contracts. Structural helpers can be implemented as functional components or as simple render helpers; the examples below use the Composition API style preferred by modern Vue.

### Intent (composable)

```ts
// useIntent.ts (Vue)
import { ref, type Ref } from 'vue';

export interface UseIntentResult<TArgs extends any[]> {
  fire: (...args: TArgs) => Promise<void>;
  isLoading: Ref<boolean>;
  error: Ref<Error | null>;
  reset: () => void;
}

export function useIntent<TArgs extends any[]>(
  handler: (...args: TArgs) => Promise<void>
): UseIntentResult<TArgs> {
  const isLoading = ref(false);
  const error = ref<Error | null>(null);

  // Keep latest handler without identity thrashing
  let currentHandler = handler;
  // In setup, reassignment is fine; for reactivity of the handler itself use a ref if needed

  async function fire(...args: TArgs) {
    isLoading.value = true;
    error.value = null;
    try {
      await currentHandler(...args);
    } catch (err) {
      error.value = err instanceof Error ? err : new Error(String(err));
    } finally {
      isLoading.value = false;
    }
  }

  function reset() {
    isLoading.value = false;
    error.value = null;
  }

  // Allow caller to update the underlying handler if desired
  function setHandler(h: (...args: TArgs) => Promise<void>) {
    currentHandler = h;
  }

  return { fire, isLoading, error, reset };
}
```

Usage inside a Vue Blockiya (script setup):

```vue
<script setup lang="ts">
const save = useIntent(async (user: User) => {
  const saved = await saveUser(user);
  emit('save-intent', saved); // fire upward and stop
});
</script>

<template>
  <Button :disabled="save.isLoading.value" @click="save.fire(draft)">
    {{ save.isLoading.value ? 'Saving…' : 'Save' }}
  </Button>
  <Text v-if="save.error.value" variant="danger">{{ save.error.value.message }}</Text>
</template>
```

### Derivation

```ts
// useDerive.ts (Vue)
import { computed, type ComputedRef, type Ref } from 'vue';

export function useDerive<TSource, TDerived>(
  source: Ref<TSource> | (() => TSource),
  deriver: (source: TSource) => TDerived
): ComputedRef<TDerived> {
  return computed(() => {
    const value = typeof source === 'function' ? source() : source.value;
    return deriver(value);
  });
}
```

```ts
// useDerivedState.ts (Vue)
import { ref, watch, type Ref } from 'vue';

export function useDerivedState<TSource, TState>(
  source: Ref<TSource>,
  transform: (source: TSource) => TState
): [Ref<TState>, (v: TState | ((prev: TState) => TState)) => void] {
  const state = ref(transform(source.value)) as Ref<TState>;

  watch(source, (newSource) => {
    state.value = transform(newSource);
  });

  function setState(v: TState | ((prev: TState) => TState)) {
    state.value = typeof v === 'function' ? (v as any)(state.value) : v;
  }

  return [state, setState];
}
```

### Structural (Vue)

In Vue the structural helpers are most naturally expressed with native directives (`v-if`, `v-for`) or thin functional components / render functions. When Strict mode is desired, provide thin components that mirror the React contracts so the rendering shape stays explicit:

```vue
<!-- If.vue -->
<script setup lang="ts" generic="T">
defineProps<{
  condition: T | false | null | undefined | 0 | '';
  fallback?: any;
}>();
</script>
<template>
  <template v-if="condition">
    <slot :value="condition" />
  </template>
  <template v-else>
    <slot name="fallback" />
  </template>
</template>
```

```vue
<!-- For.vue -->
<script setup lang="ts" generic="T">
defineProps<{
  each: T[];
  keyBy: (item: T, index: number) => string;
}>();
</script>
<template>
  <template v-if="each.length === 0">
    <slot name="fallback" />
  </template>
  <template v-else>
    <template v-for="(item, index) in each" :key="keyBy(item, index)">
      <slot :item="item" :index="index" />
    </template>
  </template>
</template>
```

`Maybe`, `Repeat`, and `Compose` follow the same pattern (scoped slots / functional components).

### Interaction (Vue)

```ts
// useToggle.ts (Vue)
import { ref } from 'vue';
export function useToggle(initial = false) {
  const value = ref(initial);
  const toggle = () => { value.value = !value.value; };
  const setTrue = () => { value.value = true; };
  const setFalse = () => { value.value = false; };
  return { value, toggle, setTrue, setFalse };
}
```

```ts
// useDebounce.ts (Vue)
import { ref, watch } from 'vue';
export function useDebounce<T>(source: Ref<T>, delay: number) {
  const debounced = ref(source.value) as Ref<T>;
  let timer: ReturnType<typeof setTimeout>;
  watch(source, (v) => {
    clearTimeout(timer);
    timer = setTimeout(() => { debounced.value = v; }, delay);
  });
  return debounced;
}
```

`usePrevious` and `useStableCallback` map directly onto `ref` + `watch` / a stable function reference.

### Intent factories (identical)

`createIntent` and `composeIntents` are pure functions and are shared unchanged across frameworks.

---

## Other Frameworks — Contract Mapping

| Contract | React | Vue | Svelte | Solid |
| --- | --- | --- | --- | --- |
| Intent lifecycle | `useIntent` hook | `useIntent` composable | `createIntent` rune / store | `createIntent` primitive |
| Pure derivation | `useDerive` | `useDerive` + `computed` | `$derived` / `derived` | `createMemo` |
| Editable derived | `useDerivedState` | `useDerivedState` + `watch` | writable derived | signal + effect |
| Conditional | `<If>` | `<If>` or `v-if` (Strict prefers component) | `{#if}` | `<Show>` |
| List | `<For>` | `<For>` or `v-for` | `{#each}` | `<For>` |
| Stable callback | `useStableCallback` | stable function ref | stable function | stable function |

When generating code for a framework not shown above, implement the **universal contracts** using that framework's native reactivity and component primitives. Do not invent new architectural rules.

---

## Strict mode reminder

In Strict Blockiya the utilities are required, not optional. The Blockiya body must not contain:

- manual `isLoading` / `error` pairs for async work
- inline derivation objects
- ad-hoc `map` / ternary rendering of domain lists

Use the utilities of the target framework instead.
