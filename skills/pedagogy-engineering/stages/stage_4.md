# Stage 4: Learning Objective Decomposition & Quality Requirements

Decompose the overarching learning goal into a discrete set of specific, observable, and measurable learning objectives.

---

## 1. Objective Syntax Formula

Every objective must describe an observable learner capability using the standard pedagogical construction:

$$\mathbf{Learner} + \mathbf{Measurable\ Action\ Verb} + \mathbf{Target\ Knowledge/Skill} + \mathbf{Relevant\ Condition}$$

*Example*: *"The learner will **calculate** [action] circuit voltage drops [knowledge] given schematic diagrams with varying resistor configurations [condition]."*

---

## 2. Forbidden vs. Approved Action Verbs

### ❌ Forbidden Vague Verbs
Avoid unobservable cognitive states unless directly operationalized by measurable performance:
* *Do NOT use*: understand, know, learn, appreciate, grasp, familiarize with, comprehend.

### ✅ Approved Observable Action Verbs
* **Cognitive / Conceptual**: identify, classify, distinguish, explain, interpret, compare, contrast, summarize.
* **Procedural / Analytical**: calculate, sequence, construct, execute, assemble, measure, diagnose, troubleshoot.
* **Evaluative / Strategic**: analyze, select, evaluate, justify, optimize, recommend, test, validate.

---

## 3. The 10 Objective Quality Requirements

Before an objective is finalized, verify that it passes all 10 criteria:

1. **Performance-oriented**: Describes what the learner will do, not what the teacher will teach.
2. **Observable action**: Uses an explicit, observable, and measurable action verb.
3. **Identified target**: Identifies specific knowledge, skill, or procedure.
4. **Audience-calibrated**: Matches the cognitive, linguistic, and developmental stage of the audience.
5. **Achievable**: Realistic within the stated constraints, scope, and time.
6. **Evidenced**: Has an immediately identifiable means of demonstrating achievement.
7. **Goal-aligned**: Directly supports the primary learning goal without topic drift.
8. **Depth-calibrated**: Its cognitive depth and complexity can be explicitly determined.
9. **Minimal & non-redundant**: Excludes extraneous or distracting content.
10. **Actionable for activities**: Can be directly translated into a learner activity and game interaction.

---

## 4. Required Output Format

Assign a unique identifier to every objective (`LO-01`, `LO-02`, etc.):

```markdown
### 4. Learning Objectives
- **LO-01**: The learner will [action verb] [target knowledge/skill] [condition].
  - *Target Type*: [Declarative / Conceptual / Procedural / Strategic]
  - *Prerequisites*: [None / LO-xx]
  - *Alignment*: [How it contributes to Primary Goal]
- **LO-02**: The learner will [action verb] [target knowledge/skill] [condition].
  - *Target Type*: [...]
  - *Prerequisites*: [LO-01]
  - *Alignment*: [...]
```
