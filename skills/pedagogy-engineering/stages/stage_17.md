# Stage 17: Learning Environment Requirements

Determine what environmental characteristics, manipulable elements, and contextual fidelity are required for the learning process.

---

## 1. Mandatory Directives

> [!IMPORTANT]
> **Define Functional Affordances, NOT Game Worlds**:
> Specify what the environment must **enable and simulate**, NOT its decorative or cosmetic layout.
> - *Pedagogical Requirement (Correct)*: "The environment must provide an interactive representation where variables X, Y, and Z can be manipulated dynamically and their causal impact on system throughput is immediately observable."
> - *Game World Design (Forbidden)*: "Place three wooden switches on the left console of a futuristic steam locomotive."

Answer this core question:
> **"What must the learning environment afford, simulate, or provide so that the learner can execute the required activities and achieve the objectives?"**

### The Contextual Fidelity Rule
* Do **NOT** assume that high graphical or narrative realism is always pedagogically superior. High fidelity can increase cognitive load and distract from core principles.
* Specify **contextual fidelity only where educationally necessary** (e.g. realistic multimeter displays for electrical apprentices vs. abstract schematic nodes for conceptual physics).
* Rigorously justify any demand for environmental authenticity against transfer requirements (Stage 14).

---

## 2. Environmental Types & Capabilities to Specify

Determine the environmental paradigm:
* **Abstract / Minimalist**: Uncluttered representation isolating target variables.
* **Contextualized / Authentic**: Realistic simulation mirroring actual workplace or domain conditions.
* **Dynamic Simulation**: Continuous causal model responding to learner input in real time.
* **Controlled Sandbox**: Safe parameter ranges preventing unrecoverable deadlocks.
* **Variable / Adaptive**: Changing environmental noise, failure rates, or constraint combinations.

---

## 3. Required Output Format

For every major environment requirement, specify all eight fields:

```markdown
### 17. Learning Environment Requirements

#### ENV-01: [Environment Requirement Name, e.g., Dynamic Circuit Simulation Canvas]
- **Environmental Characteristic**: [Abstract / Contextualized / High-Fidelity Simulation]
- **Pedagogical Purpose**: [Why this environment is essential for the learning process]
- **Objectives Supported**: [Exact LO-xx mappings]
- **Learner Actions Enabled**: [Specific actions enabled, e.g. wire components, inject current, measure voltage]
- **Required Contextual Fidelity**: [Minimal / Moderate / High, with explicit pedagogical justification]
- **Manipulable Elements**: [Exact variables, parameters, or objects the learner can alter]
- **Observable States & Consequences**: [Causal reactions, readouts, meter movements, or failure states]
- **Implications for Transfer**: [How this environment prepares the learner for real-world application]
```
