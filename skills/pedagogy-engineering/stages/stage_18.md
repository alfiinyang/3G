# Stage 18: Game-Design Requirements

Translate instructional, experiential, and environmental requirements into functional specifications that an eventual game designer can act upon.

---

## 1. Mandatory Directives

> [!IMPORTANT]
> **Translate Pedagogy to Functional Capabilities, NOT Mechanical Solutions**:
> Answer: **"What must the game enable the learner to do in order for the intended learning to occur?"**
> - *Pedagogical Requirement*: "The game system must allow the learner to isolate faulty components and query operational telemetry without resetting overall puzzle state."
> - *Game Design (Designer's Territory)*: "The player uses an electromagnetic sensor tool while dodging patrol drones."

Synthesize and translate inputs directly from:
- Learning Activities (Stage 10)
- Scaffolding & Fading Logic (Stage 11)
- Multi-Tiered Feedback (Stage 12)
- Evidence of Learning (Stage 13)
- Transfer Requirements (Stage 14)
- **Learning Experience Requirements (Stage 16)**
- **Learning Environment Requirements (Stage 17)**

---

## 2. Core Functional Requirements Categories

Formulate explicit requirements across seven critical dimensions:

1. **Required Learner Interactions**: Verbs the game mechanics must afford (e.g. manipulate, assemble, isolate, test, query, compare).
2. **Challenge Characteristics**: How challenges must be framed (variable difficulty, competing constraints, realistic noise, time bounds).
3. **Feedback Behaviors**: How the game world must react to player decisions (dynamic causal simulations, explanatory logs, post-action debriefs).
4. **Progression Behaviors**: How the game tracks mastery (mastery gating, adaptive difficulty, unlockable complexity).
5. **Practice Opportunities**: Frequency, variety, and spaced repetition required for fluency.
6. **Required Experience Implementation**: How the game design must support the agency, uncertainty, and controlled discovery mandated in Stage 16.
7. **Required Environmental Implementation**: How the game engine/environment must provide the manipulable elements and contextual fidelity mandated in Stage 17.

---

## 3. Required Output Format

Assign every game-design requirement a unique identifier (`GDR-01`, `GDR-02`, ...) and map its pedagogical origin:

```markdown
### 18. Game-Design Requirements

#### 1. Interaction Requirements
- **GDR-01**: The game system must allow the learner to [action, e.g. alter resistor parameters dynamically within an active schematic]. *(Traces to: ACT-01, ENV-01)*

#### 2. Challenge & Environmental System Requirements
- **GDR-02**: The game must support [characteristic, e.g. varying circuit topologies while maintaining invariant physical laws]. *(Traces to: LO-02, ENV-01)*

#### 3. Experience & Feedback Implementation
- **GDR-03**: The simulation must [behavior, e.g. model physical component burnout when current exceeds threshold]. *(Traces to: LER-01, Stage 12)*

#### 4. Progression & Mastery Gating
- **GDR-04**: Progression to multi-branch networks must be gated on [benchmark, e.g. achieving 2 consecutive unassisted diagnoses in single-branch circuits]. *(Traces to: Stage 8, Stage 11)*
```
