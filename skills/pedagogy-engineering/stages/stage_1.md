# Stage 1: Intent and Context Specification

In this stage, the agent formally analyzes and interprets the intake information to establish a rigorous pedagogical baseline.

> [!CAUTION]
> **Warning**: Do NOT begin designing game mechanics, stories, or game systems at this stage. Focus solely on interpreting pedagogical intent and educational context.

---

## 1. Specification Analysis

Carefully analyze the request and articulate the following core dimensions:

1. **Audience**: Baseline demographic, developmental stage, language/reading level, and prerequisite knowledge.
2. **Topic / Domain**: Academic, vocational, technical, or practical subject boundaries.
3. **Intended Goal**: User's initial statement of intent (unrefined).
4. **Learning Context**: Setting, delivery model, schedule, facilitator role, and learning environment.
5. **Constraints**: Time, platform, accessibility, curriculum standards, regulatory bounds.
6. **Motivation for Learning**: Why the learner needs or wants to learn this (intrinsic/extrinsic drivers, vocational requirement, problem resolution).
7. **Expected Learner Change**: The fundamental transformation in thinking, capability, understanding, or behavior that should occur.
8. **Relevant Assumptions**: Any working hypotheses or defaults introduced to resolve ambiguities.

---

## 2. Tri-Partite Separation of Inputs

To prevent assumption creep and ensure transparency, the agent **must strictly separate**:

* **Explicit User Requests**: Facts, goals, and constraints directly stated by the user.
* **Implied Needs**: Requirements strongly implied by the audience, setting, or domain standards.
* **Pedagogical Determinations**: Gaps or decisions that must be engineered pedagogically by the agent.

---

## 3. Required Output Format

```markdown
### 1. Intent and Context Specification
- **Audience Baseline**: [Target population, educational level, prior experience]
- **Domain & Topic**: [Subject area]
- **Raw User Intent**: [Teacher/trainer's stated objective]
- **Delivery Context**: [Physical or digital setting, instructional format]
- **Operational Constraints**: [Time, devices, standards, exclusions]
- **Learning Motivation**: [Underlying purpose driving the need to learn]
- **Target Transformation**: [High-level shift in learner capability]
- **Input Classification**:
  - *Explicit Facts*: [...]
  - *Inferences / Implied*: [...]
  - *Pedagogical Decisions to Formulate*: [...]
```
