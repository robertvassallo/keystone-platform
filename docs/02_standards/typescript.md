# TypeScript

Builds on `javascript.md`. Strict mode is non-negotiable.

## Why

- Catches whole classes of bugs at edit time.
- Types are documentation that can't drift from the code.
- IDE intelligence depends on type accuracy.

## tsconfig — required flags

```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "noFallthroughCasesInSwitch": true,
    "useUnknownInCatchVariables": true,
    "exactOptionalPropertyTypes": true,
    "verbatimModuleSyntax": true,
    "isolatedModules": true,
    "moduleResolution": "bundler",
    "target": "ES2022",
    "lib": ["DOM", "DOM.Iterable", "ES2023"]
  }
}
```

## Rules

### No `any`

- Forbidden in source. Use `unknown` and narrow.
- For genuine "I don't know the shape" cases (e.g., third-party callbacks): `unknown` + type guard.
- `// @ts-ignore` requires a `// @ts-expect-error: <reason>` instead — fails build when the underlying error is fixed.

### Naming

- **Types / interfaces**: `PascalCase`. No `I` prefix (`User`, not `IUser`).
- **Enums**: avoid them. Prefer string-literal unions: `type Status = 'pending' | 'active' | 'closed'`.
- **Generics**: descriptive (`TUser`, `TResponse`) over single letters when meaning isn't obvious.

### `interface` vs `type`

- `interface` for object shapes meant to be extended / augmented.
- `type` for unions, tuples, mapped / conditional types.
- Don't redeclare an interface in two places — extend it.

### Discriminated unions over flags

```ts
// Bad
type Result = { ok: boolean; data?: User; error?: string };

// Good
type Result =
  | { ok: true; data: User }
  | { ok: false; error: string };
```

### Return types

- **Public** functions (exported, or class members crossing a module boundary): explicit return type.
- Local arrow functions / private helpers: inference is OK.

### Immutability

- `readonly` on properties that shouldn't change after construction.
- `as const` for literal arrays / objects used as constants.
- `Readonly<T>` / `ReadonlyArray<T>` at API boundaries.

### Imports

- `import type` for type-only imports — compiles to nothing, avoids accidental runtime imports.
- ESLint `consistent-type-imports` enforces this.

### Narrowing

- Type guards are real functions: `function isUser(x: unknown): x is User { ... }`.
- Use `satisfies` to validate without widening:
  ```ts
  const config = { theme: 'dark', density: 'compact' } satisfies AppConfig;
  ```

### `null` vs `undefined`

- Pick one per project for "missing"; default is `null` (Django returns `null`).
- Use `undefined` only for "not yet set" / "absent".
- `exactOptionalPropertyTypes` catches mixing.

### Branded types for IDs

```ts
type UserId = string & { readonly __brand: 'UserId' };
type ProjectId = string & { readonly __brand: 'ProjectId' };
```

Prevents accidental `passUser(projectId)` from compiling.

### React-specific

- Component props: `interface ButtonProps { ... }`.
- No `React.FC` — declare return type explicitly: `function Button(props: ButtonProps): JSX.Element`.
- Children: `children: React.ReactNode`.
- Event handlers: typed via the element-specific type (`React.MouseEvent<HTMLButtonElement>`).

## Anti-patterns

| Don't | Do |
|---|---|
| `any` anywhere | `unknown` + narrow |
| `// @ts-ignore` | `// @ts-expect-error: <reason>` |
| `IUser` interface | `User` |
| `enum Status` | `type Status = 'pending' \| 'active'` |
| `function Foo: React.FC<Props>` | `function Foo(props: Props): JSX.Element` |
| Asserting type with `as`: `data as User` | Type guard or `satisfies` |
| `Object`, `{}`, `Function` | Specific shapes |

## Review checklist

- [ ] `strict: true` plus the additional flags above
- [ ] No `any` in source
- [ ] No `as` type-cast that hides a real type mismatch
- [ ] `import type` for type-only imports
- [ ] Discriminated unions for variant data
- [ ] `readonly` / `Readonly<T>` at API boundaries
- [ ] Branded IDs where mixing types would cause harm
