# Stage 11: Scaffolding

Design instructional support systems that accelerate competence and systematically fade as learner independence grows.

---

## 1. The Core Principle of Scaffolding

> [!IMPORTANT]
> **Fading Rule**:
> Scaffolding must **never permanently replace** the target learner performance. Supports are temporary structures designed to be systematically removed until the learner executes independently.

$$\mathbf{High\ Support\ (Modeling)} \longrightarrow \mathbf{Medium\ Support\ (Coaching)} \longrightarrow \mathbf{Low\ Support\ (Hints)} \longrightarrow \mathbf{Zero\ Support\ (Independent)}$$

---

## 2. Forms of Instructional Support

Specify the exact forms of support deployed across learning stages:

* **Worked Examples**: Fully solved problems illustrating expert reasoning and step-by-step procedure.
* **Demonstration / Modeling**: Visual or narrated execution showing proper performance.
* **Constrained Choices**: Reducing search space or decision parameters initially (e.g. choose between 2 options rather than open syntax).
* **Partial Solutions / Completion Tasks**: Providing skeleton code, pre-wired circuits, or partially formatted templates where learner completes critical sections.
* **Contextual Prompts & Cues**: Highlighting salient features, warnings, or checklist reminders.
* **Multi-tiered Hints**: Escalating hints (General conceptual nudge $\to$ specific directional hint $\to$ direct correction).

---

## 3. Systematic Fading Logic

Define explicit trigger conditions for reducing support:
* **Fading Triggers**: e.g., 2 consecutive unassisted successes, achieving a specific accuracy threshold, time-based progression.
* **Failure Interventions**: Conditions under which support is temporarily restored if the learner stalls.

---

## 4. Required Output Format

```markdown
### 11. Scaffolding

#### Support Levels
- **Initial Exposure (Full Support)**: [Worked examples, explicit demonstrations, constrained inputs]
- **Guided Practice (Faded Support)**: [Partial solutions, contextual hints on error, step checklists]
- **Supported Challenge (Low Support)**: [Open-ended tasks with optional hints on demand]
- **Independent Mastery (Zero Support)**: [Full unassisted execution matching real-world conditions]

#### Support-Removal Logic
- **Fading Threshold**: [Explicit criteria to transition between levels, e.g., 80% accuracy without hint usage]
- **Fallback Rule**: [When and how assistance re-engages if severe misconception is detected]
```
