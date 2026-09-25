# Stage 16: Game-Design Requirements

Translate instructional requirements into functional specifications that an eventual game designer can implement.

---

## 1. The Governing Question

> [!IMPORTANT]
> The central translation question is:
> **"What must the game enable the learner to do in order for the intended learning to occur?"**

These are **functional educational requirements**, NOT mechanical game designs:
- *Requirement (Pedagogical)*: "The game must provide an environment where the learner can inspect variable states and inject test values to diagnose logic errors."
- *Game Design (Designer's Job)*: "The player uses an inspector magnifying glass tool on a steampunk machine console to view steam pressure gauges."

---

## 2. Core Functional Requirements Categories

Define game-facing requirements across seven critical dimensions:

1. **Required Learner Interactions**: Verbs the game mechanics must support (e.g. manipulate, assemble, isolate, test, query, compare).
2. **Challenge Characteristics**: How challenges must be framed (e.g. variable difficulty, competing resource constraints, time limits, realistic noise).
3. **Feedback Behaviors**: How the game world must react to player actions (e.g. immediate causal simulation, post-action debriefing, explanatory logs).
4. **Progression Behaviors**: How the game tracks mastery (e.g. mastery gating, adaptive difficulty, unlockable complexity).
5. **Practice Opportunities**: Frequency, variety, and spaced repetition required for fluency.
6. **Required Consequences**: Authentic domain failure states vs artificial game-over screens.
7. **Transfer Opportunities**: Structural shifts in scenarios to test generalized competence.

---

## 3. Required Output Format

```markdown
### 16. Game-Design Requirements

#### 1. Interaction Requirements
- [GDR-01]: The game system must allow the learner to [action, e.g. modify resistor values dynamically in an active schematic].

#### 2. Challenge & System Requirements
- [GDR-02]: The game must generate circuits with varying component topologies without changing the governing physical laws.

#### 3. Feedback & Consequence Requirements
- [GDR-03]: The simulation must model component overheating or blown fuses when current exceeds safe operating thresholds.

#### 4. Progression & Mastery Requirements
- [GDR-04]: Progression to multi-loop circuits must be gated on achieving unassisted diagnosis in single-loop configurations.
```
