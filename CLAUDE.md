# Plan mode

When in plan mode, your job is to help me **talk through the approach** — not to
produce an implementation plan and not to write code. I write all the code myself.

Do:
- Discuss the overall structure and how the pieces fit together.
- Propose DB schema, data models, and relationships.
- Compare approaches and call out trade-offs, edge cases, and risks.
- Point to the existing files/patterns a change would touch, so I know where to look.

Don't:
- Write a step-by-step implementation checklist or task breakdown.
- Write the actual code, diffs, or file-by-file edit instructions.
- Treat the goal as "hand off a plan to execute." The goal is a shared understanding
  of the approach that I then implement by hand.

When you call `ExitPlanMode`, the "plan" you present should be a concise summary of
the **agreed approach** (structure, schema, key decisions) — never a list of code
changes to make.
