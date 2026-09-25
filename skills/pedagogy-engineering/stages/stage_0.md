# Stage 0: User Intake and Intake Rules

This stage governs how the agent collects, interprets, and infers initial information before beginning autonomous pedagogical reasoning.

---

## 1. The Five Intake Inputs

The agent must obtain information for the following five inputs, which form the initial pedagogical specification:

### 1.1 Audience — REQUIRED
The agent must obtain the intended learner population. At minimum, identify:
* Approximate age or educational level;
* Relevant prior knowledge or experience, if known;
* Learner setting, if relevant;
* Significant learner characteristics that affect instruction.

> [!CAUTION]
> **Strict Rule**: If the user does not provide sufficient audience information, the agent **must ask for clarification** before proceeding. The agent must **not** independently invent the audience.

### 1.2 Topic / Domain — OPTIONAL USER INPUT
The subject domain (e.g., programming, mathematics, biology, history, electrical installation, financial literacy, professional communication).
* If the user explicitly asks the agent to determine the topic, the agent may derive it from the request.
* If the topic is already unambiguously contained in the user's request, additional questioning is unnecessary.

### 1.3 Intended Learning Goal — OPTIONAL USER INPUT
What the teacher/trainer wants learners to achieve.
* The user's statement may be informal, incomplete, broad, or pedagogically imprecise.
* If the user explicitly asks the agent to determine the goal, the agent may formulate it from the available context.
* The agent must distinguish the user's original intent from the refined pedagogical learning goal developed in Stage 3.

### 1.4 Learning Context — OPTIONAL USER INPUT
Where, why, and under what circumstances the learning will occur (e.g., classroom, training programme, self-directed learning, workplace training, curriculum requirement, practical training, simulation, assessment prep, real-world application).
* If the user asks the agent to decide, the agent may infer a reasonable context from available information.
* Inferences must be identified internally as assumptions and must not be presented as user-provided facts.

### 1.5 Constraints / Requirements — OPTIONAL USER INPUT
Known constraints or boundary parameters:
* Available learning time;
* Curriculum or standards;
* Age appropriateness;
* Required or excluded content;
* Delivery environment & technology limitations;
* Expected learner output & assessment requirements;
* Institutional, accessibility, or scope limits.
* If the user asks the agent to decide, the agent may establish reasonable constraints from context.

---

## 2. Intake Rules & Protocol

1. **Minimize Interrogation**:
   * Do not unnecessarily interrogate the user.
   * If information is already available in the request, reuse it directly.
   * Ask for missing information *only* when that information is strictly necessary to produce a valid pedagogical specification.
2. **Audience is the Only Mandatory Input**:
   * For inputs 2–5, the agent may decide or infer the information only when:
     1. The user explicitly asks the agent to decide; or
     2. The information is sufficiently determined by the request.
3. **Explicit Assumption Management**:
   * The agent must **not** silently convert uncertain assumptions into facts.
   * Where an assumption materially affects the learning design, it must be explicitly recorded in the final plan under **Section U: Assumptions and Design Decisions**.

---

## Deliverable from Stage 0

A validated initial pedagogical specification containing:
- Explicit Audience Profile
- Topic / Domain
- Stated User Goal
- Learning Context
- Operating Constraints
- Log of Initial Assumptions (if any)
