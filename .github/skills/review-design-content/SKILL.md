---
name: review-design-content
description: Check a distributed-systems article or proposed explanation for correctness, explicit assumptions, realistic tradeoffs, and defensible performance claims. Use for technical content review, not a grammar-only pass.
---

# Review a system-design explanation

Read `AGENTS.md` and the complete affected argument, not just changed sentences.
Identify what the reader should be able to decide or demonstrate afterward.
Use the checks relevant to that argument; do not add every topic to every article.

## Test the argument

- **Contract:** What is promised, to whom, at what scope, and under which failures?
  Separate an assumption from an enforced invariant. Specify ordering, visibility,
  and loss guarantees rather than relying on words such as "consistent" or "safe."
- **Concurrency and recovery:** Walk a concrete interleaving. Consider concurrent
  writers, retries after a lost response, duplicate delivery, partial commits,
  stale reads, and failover where applicable. Name the atomic operation and its
  scope; a SQL snippet alone does not establish an isolation guarantee.
- **Capacity:** Recalculate units and arithmetic. Distinguish requests from
  internal operations, average from peak, and logical data from replicas,
  indexes, retention, and protocol overhead. State decimal or binary units.
- **Performance:** Identify the limiting resource, hot keys, skew, fan-out,
  queueing, and overload behavior. Explain which cost an optimization moves and
  when the alternative wins. Separate measured results from estimates; give the
  workload, environment, and method for any benchmark claim.
- **Tradeoffs:** Compare a plausible alternative under the same requirements.
  Include the cost of correctness, operation, and recovery, not only happy-path
  latency. Avoid universal prescriptions such as "NoSQL is faster."
- **Evidence:** Prefer primary documentation or papers for subtle guarantees.
  Qualify version- or configuration-dependent behavior. If evidence is missing,
  narrow the claim or mark the assumption rather than inventing authority.
- **Learning value:** Use a worked example, failure trace, or small exercise when
  it exposes the decision. An executable model proves only what it models, not
  production throughput, availability, or durability.

## Deliver a bounded result

Report concrete errors first, with their location, counterexample or source, and
a proposed correction. Keep improvements separate from required fixes.
Do not inflate the article with generic terminology or production machinery.

When edits are requested, update the affected Markdown and notebook explanation
together. Validate executable changes with the
[notebook workflow](../validate-notebooks/SKILL.md); an output snapshot is not a
substitute for a behavior assertion.
