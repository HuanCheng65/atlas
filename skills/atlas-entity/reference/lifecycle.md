# Entity Lifecycles

Each type has its own state machine. `validate.py` checks final-state invariants (e.g. `status=superseded` requires non-empty `superseded-by`); it does not track transitions over time.

## Decision

```
planned ──┬──> active ────> superseded
          └──> rejected
```

- **planned**: documented but not yet adopted. Code does not reflect it yet.
- **active**: in effect. Code reflects this decision.
- **superseded**: replaced by another decision. `superseded-by` must be non-empty.
- **rejected**: explicitly decided against. Kept for record.

Transitions in practice:
- `planned → active`: when implementation begins
- `planned → rejected`: decided against without implementation
- `active → superseded`: create the new decision first, then run `supersede.py`
- No transitions out of `superseded` or `rejected`

To "reopen" a superseded decision, do **not** flip status back. Instead create a new D-NNN that reverses the previous superseding decision, and `supersede.py` again. This preserves the audit chain.

## Experiment

```
planned ──> running ──┬──> completed
                      └──> abandoned
```

- **planned**: hypothesis and setup written, not yet run
- **running**: in progress; Run log being updated
- **completed**: result and conclusion filled
- **abandoned**: stopped early; conclusion explains why

## Question

```
open ──┬──> answered
       ├──> wontfix
       └──> merged-into-D
```

- **open**: unresolved
- **answered**: one-off resolution; `answered-by` points to journal entry
- **wontfix**: decided not to pursue
- **merged-into-D**: the answer became a decision; `answered-by` is a D-id

No transitions out of terminal states.
