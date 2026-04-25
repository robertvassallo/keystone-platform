# JavaScript

For TS-specific rules see `typescript.md`. This file covers what applies to all JS — including `.mjs` config files, build scripts, and any plain-JS we end up with.

## Why semantic naming

A function or variable name is a one-line comment that never lies. Good names remove the need for explanation; bad names misdirect.

## Rules

### Naming

- **Variables / functions**: `camelCase`. Verbs for functions (`getUser`, `formatDate`), nouns for values (`user`, `formattedDate`).
- **Classes / components**: `PascalCase`.
- **Constants** (module-level, truly constant): `UPPER_SNAKE_CASE`. Inline literals stay camelCase.
- **Booleans**: prefix with `is` / `has` / `can` / `should` (`isLoaded`, `hasAccess`).
- **Predicates**: return `boolean`, name describes the truth condition (`isAdmin(user)`).
- **No abbreviations** that aren't widely understood: `usr`, `cnt`, `msg` — write `user`, `count`, `message`.

### Modern syntax

- `const` by default; `let` only when reassignment is needed; **never** `var`.
- `===` / `!==` only.
- Arrow functions for callbacks; `function` declarations for top-level named functions.
- Spread / rest over `Object.assign` / `arguments`.
- Template literals over `+` concatenation.
- Optional chaining (`?.`) and nullish coalescing (`??`) over `&&` / `||` chains.
- Async / await over raw promise chains.

### Modules

- ES modules only (`import` / `export`). No CommonJS `require` outside of legacy build configs.
- **Named exports** preferred. Default exports allowed only for the primary thing a module is about (e.g. a React component file, a Next.js page).
- One concept per module. If a file exports 6 unrelated functions, split it.

### No magic numbers / strings

```js
// Bad
if (status === 3) { ... }
setTimeout(retry, 5000);

// Good
const STATUS_FAILED = 3;
const RETRY_DELAY_MS = 5_000;
if (status === STATUS_FAILED) { ... }
setTimeout(retry, RETRY_DELAY_MS);
```

Exceptions: `0`, `1`, `-1`, `2` for indices / counts.

### Errors

- Throw `Error` subclasses, never strings.
- Don't swallow errors silently — at minimum, log and re-throw.
- `try` / `catch` only at the level where you can do something useful.

### Side effects

- Pure functions where possible — same input, same output, no I/O.
- Document side effects in the function name (`writeAuditLog`, `sendInvitation`).

### Comparison & equality

- Don't compare floating-point numbers with `===` — use a tolerance.
- Don't trust object identity across realm boundaries (web workers, iframes).

### Mutation

- Don't mutate function arguments.
- Prefer immutable updates (`{...obj, foo: 'bar'}`); deep mutation is a bug magnet.
- For large structures, use Immer.

## Anti-patterns

| Don't | Do |
|---|---|
| `var x = 1` | `const x = 1` |
| `if (x == null)` | `if (x === null \|\| x === undefined)` (or `x == null` once, with a comment) |
| `function() { ... }.bind(this)` | Arrow function |
| `new Promise((res, rej) => fetch(...).then(res, rej))` | Just return the promise |
| `for (let i = 0; i < arr.length; i++)` | `for (const item of arr)` |
| Single-letter names outside of tight loops | Descriptive names |
| Catching errors to silence them | Catch only when you can recover or annotate |

## Review checklist

- [ ] No `var`
- [ ] No `==` / `!=` (one exception: `== null`, with comment)
- [ ] No magic numbers / strings outside of `0/1/-1/2`
- [ ] Named exports unless the file is "about" one default thing
- [ ] No silently swallowed errors
- [ ] Functions are small (~25 lines target, hard cap ~60)
- [ ] Names accurately describe what the thing is / does
