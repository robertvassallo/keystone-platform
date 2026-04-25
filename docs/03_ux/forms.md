# Forms

## Anatomy

```
<form aria-labelledby="form-title">
  <h2 id="form-title">Create project</h2>

  <FormSection title="Basics" description="Name and visibility.">
    <Field>
      <Field.Label htmlFor="name">Project name</Field.Label>
      <Field.Input id="name" name="name" required />
      <Field.HelpText>Visible to your team.</Field.HelpText>
      <Field.Error /> {/* rendered when error exists */}
    </Field>
  </FormSection>

  <FormActions>
    <Button type="button" intent="secondary">Cancel</Button>
    <Button type="submit" intent="primary">Create</Button>
  </FormActions>
</form>
```

## Layout

- **Single column** for forms shorter than ~10 fields. Eye scan stays vertical, complete-rate is higher.
- **Two columns** only for related pairs (city / postal code, start / end date) or settings pages with many independent toggles.
- Section headings (`<h2>` / `<h3>`) group related fields. Each section has 1–3 sentences of context if it isn't self-explanatory.
- Logical tab order: top-to-bottom, left-to-right within a row.

## Labels

- **Always visible**, top-aligned over the input. No floating labels.
- Placeholder text is **not** a label — it disappears on focus and on filled state, taking the field name with it.
- Labels are short noun phrases, sentence case, no trailing colon: `Project name`, not `Project Name:`.

## Required / optional

- Pick **one** convention per project:
  - Mark **required** with `*` and `aria-required="true"`, optional fields plain. Use when most fields are optional.
  - Mark **optional** with `(optional)`, required fields plain. Use when most fields are required.
- Communicate the choice in the form's leading paragraph or section description.

## Help text

- Short, in present tense, sits below the input.
- Explains the *what* / *why* of the field, not the validation rule.
  - Good: "Used for billing receipts."
  - Bad: "Must be a valid email format."
- Validation rules are surfaced through real-time validation, not help text.

## Validation

### When to validate

| Trigger | Use for |
|---|---|
| `onBlur` | Format checks (email, URL) — don't nag while typing |
| `onChange` (debounced) | Async availability checks (username, slug) |
| `onSubmit` | Required-field checks, server-side cross-field validation |

Never **only** on submit — let users fix as they go.

### Error messages

- Specific. Say what's wrong **and** how to fix it.
- "Email must include @" beats "Invalid email".
- "Use 12+ characters with at least one number" beats "Password too weak".
- Don't say "please" / "sorry". Direct, neutral tone.

### Errors a11y

- Error text inside the field, programmatically associated via `aria-describedby` linking to the error's `id`.
- Field gets `aria-invalid="true"` when in error.
- On submit failure, **focus moves to the first error** and announces it via a polite live region.
- Error icon never the only signal — pair with text and the field's red border.

## Inputs

- Use the right `type` — `email`, `tel`, `number`, `url`, `date`, `time`, `search`. Mobile keyboards differ.
- `inputmode` for finer hints (`numeric`, `decimal`).
- `autocomplete` attribute on personal-info fields — `name`, `email`, `tel`, `street-address`, `country`, `postal-code`, `cc-number`, `one-time-code`.
- `enterkeyhint` on the last field of a multi-step form.

## Patterns

- **Disabled buttons** until form is valid? **No.** Disabled buttons hide *why* the action can't proceed. Show errors on submit; only disable while a request is in flight.
- **Saving state** for individual fields (autosave): "Saved" / "Saving…" near the field — stable, polite live region.
- **Destructive actions** require an explicit confirmation step. The confirm button's label restates the action ("Delete project").
- **Long forms**: break into steps with a stepper. Each step submits independently or persists draft state.
- **Confirm by typing** (e.g. "type the project name to confirm deletion") for irreversible destructive actions.

## Submission

- Submit triggers a single in-flight request; the button shows a spinner and is disabled (re-clicks ignored).
- Success: navigate / toast / inline confirmation. Don't leave the user wondering.
- Server error: surface the message inline near the relevant field if it's field-specific; banner at the top of the form for general errors.
- Save state — don't lose user input on transient errors (network blip).

## Patterns to avoid

| Don't | Do |
|---|---|
| Floating / inside-input labels | Top-aligned labels |
| Placeholder as label | Real `<label>` |
| Disabled submit until form is valid | Validate on blur; surface errors on submit |
| Generic "Invalid input" | Specific, actionable error |
| Validate every keystroke | Validate on blur; debounce async |
| Reset the form on submit error | Preserve all input |
| Modal that closes on background click for important forms | Require explicit close |

## Review checklist

- [ ] Labels visible, top-aligned, sentence case
- [ ] Required/optional convention applied consistently
- [ ] Error messages are specific and tell users how to fix
- [ ] Errors associated via `aria-describedby`; focus moves to first error on submit
- [ ] Correct `type` / `inputmode` / `autocomplete` on every input
- [ ] No disabled submit; submit shows in-flight state
- [ ] Destructive actions require explicit confirmation
- [ ] Form preserves input on transient failure
