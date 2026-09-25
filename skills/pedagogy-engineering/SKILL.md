---
name: pedagogy-engineering
description: >-
  Transforms a teacher/trainer's learning request into a structured, game-designer-ready
  learning plan. Defines the learning problem, pedagogical structure, learning progression,
  evidence models, and game-facing learning requirements without designing the game itself.
  Use when developing, structuring, or analyzing pedagogical specifications, learning goals,
  and educational requirements for game-based learning.
---

# Pedagogy Engineering Instructions

Transform the user's educational request into a structured, game-designer-ready learning plan. Follow these instructions step by step.

> [!IMPORTANT]
> **Boundary of Responsibility**:
> **Do NOT design the game.** Do not write narrative stories, invent game lore, script characters, select art styles, mock up UI layouts, design levels, or write game engine code.
> 
> Confine your work strictly to engineering the **pedagogical architecture**: diagnose the learning problem, formulate measurable objectives, sequence progression, design scaffolding and feedback, establish observable evidence, and specify the functional learning capabilities the game must afford.

---

## Core Directives

Answer these two governing questions in strict sequential order:
1. **Pedagogical Requirement**: *Given this audience, goal, and context, what should actually be taught and what should the learner be able to do afterward?*
2. **Game-Facing Requirement**: *What must a game enable the learner to do in order for that learning to occur?*

Enforce this derivation chain at all times:
$$\mathbf{Goal} \longrightarrow \mathbf{Objectives} \longrightarrow \mathbf{Target\ Performance} \longrightarrow \mathbf{Activities} \longrightarrow \mathbf{Interactions} \longrightarrow \mathbf{Game\ Form}$$

**Never** select a game genre or mechanic purely from the subject topic or personal preference.

---

## Step-by-Step Execution Workflow

Execute the following 20 steps (Intake + Stages 1–19). You are permitted to backtrack to revise earlier decisions whenever later analysis reveals design inconsistencies.

### Step 0: User Intake & Assumption Management
1. Extract information across the 5 intake dimensions:
   - **Audience (MANDATORY)**: Age/educational level, prior knowledge/misconceptions, setting, significant learner traits. If missing or ambiguous, **stop and ask the user for clarification**. Never invent the audience.
   - **Topic / Domain**: Academic, vocational, or technical subject boundaries.
   - **Intended Learning Goal**: User's initial unrefined intent.
   - **Learning Context**: Classroom, self-directed, workplace, simulator, or real-world application.
   - **Constraints / Requirements**: Time limits, curriculum standards, tech limitations, exclusions.
2. Minimize user interrogation: ask only when missing info prevents valid pedagogical reasoning.
3. For optional inputs (2–5), infer reasonable defaults only if the user delegates them or the context determines them.
4. **Never present assumptions as facts**: Log every material inference under Section U.

### Step 1: Specify Intent and Context
1. Interpret the request without introducing game designs.
2. Strictly partition intake information into three distinct categories:
   - *Explicit User Facts*: Verbatim requirements from the user.
   - *Implied Requirements*: Necessitated by the domain, audience, or delivery context.
   - *Pedagogical Determinations*: Instructional elements engineered by the agent.
3. Document the learner motivation (intrinsic/extrinsic drivers) and the target capability transformation.

### Step 2: Diagnose the Learning Problem
1. Analyze: (a) Current learner state, (b) Target learner state, and (c) The cognitive or practical deficit.
2. **Never reduce the problem to a topic name** (e.g. ban "teach fractions" or "explain circuits"). Frame the problem around an inability to recognize, explain, compare, calculate, apply, diagnose, construct, evaluate, or transfer.
3. Write the mandatory Learning Problem Statement:
   > **Given** [learner state and prior background], **the learner needs to develop** [target capability or cognitive mechanism] **so that they can** [target performance] **in** [relevant context or operating environment].

### Step 3: Formulate the Learning Goal
1. Formulate **one primary, learner-centered capability goal** describing what the learner will be able to do.
   - *Weak*: "Teach conditional statements."
   - *Strong*: "Develop learners' ability to use conditional logic to make decisions in simple programs."
2. Restrict secondary goals only to essential sub-capabilities.

### Step 4: Decompose into Measurable Learning Objectives
1. Decompose the primary goal into discrete, uniquely identified objectives (`LO-01`, `LO-02`, ...).
2. Enforce the objective syntax formula:
   $$\mathbf{Learner} + \mathbf{Measurable\ Action\ Verb} + \mathbf{Target\ Knowledge/Skill} + \mathbf{Relevant\ Condition}$$
3. **Ban vague verbs**: Do not use *understand, know, learn, appreciate, grasp, become familiar with*. Use approved verbs (*identify, classify, explain, calculate, construct, apply, diagnose, compare, solve, evaluate*).
4. Verify every objective against the **10 Objective Quality Requirements**:
   (1) Describes learner performance, (2) Observable action, (3) Identifies target knowledge/skill, (4) Audience-calibrated, (5) Achievable in scope, (6) Identifiable evidence, (7) Directly supports primary goal, (8) Depth is specified, (9) Free of extraneous content, (10) Actionable for activity design.

### Step 5: Structure Knowledge and Skills
1. Categorize all required learning elements into the 4 knowledge taxonomies:
   - **Declarative ("What")**: Facts, terminology, definitions, formulas, rules.
   - **Conceptual ("Why")**: Mental models, principles, causal relationships, theories.
   - **Procedural ("How")**: Step-by-step techniques, workflows, algorithms.
   - **Strategic ("When/Which")**: Decision heuristics, method selection, self-monitoring.
2. Map **every single content element** to at least one `LO-xx`. Eliminate any orphaned content.

### Step 6: Establish Content Scope & Boundaries
1. Partition domain content into five explicit tiers:
   - **Core Content**: Indispensable topics mastered by every learner.
   - **Supporting Content**: Contextual examples that aid core comprehension.
   - **Optional / Extension Content**: Advanced stretch material for fast learners.
   - **Prerequisite Content**: Assumed entry baseline (do not re-teach from scratch).
   - **Excluded Content**: Explicitly forbidden topics and edge cases.
2. Prevent scope creep: excluded content must never appear as hidden challenges in later activities.

### Step 7: Calibrate Depth and Complexity
1. Calibrate each `LO-xx` across four dimensions:
   - **Cognitive Depth**: Recognition, Recall, Explanation, Interpretation, Guided Application, Independent Application, Analysis, Creation, Evaluation, or Fluent Performance.
   - **Complexity**: Low (single-variable), Medium (multi-step), or High (ambiguous, competing constraints).
   - **Independence Level**: Full scaffolding, faded assistance, peer collaboration, or unassisted.
   - **Performance Conditions**: Allowed tools (calculators, IDE, cheat-sheets), time bounds, environments.
2. Do not demand greater depth than required by the overarching learning goal.

### Step 8: Build the Learning Progression
1. Sequence learning by cognitive prerequisite dependencies, never by arbitrary textbook chapter order.
2. Apply standard progression patterns:
   $$\mathbf{Demonstration} \longrightarrow \mathbf{Guided\ Practice} \longrightarrow \mathbf{Supported\ Challenge} \longrightarrow \mathbf{Independent\ Performance} \longrightarrow \mathbf{Transfer}$$
3. Render a clear Mermaid flowchart showing progression milestones and prerequisite links.

### Step 9: Establish the Pedagogical Learning Scenario
1. Specify an authentic operational context:
   - *Operational Situation*: Real-world environment where the challenge occurs.
   - *Learner Role*: Functional capacity (e.g. Systems Analyst, Electrical Inspector).
   - *Authentic Problem*: The operational failure, discrepancy, or task demanding action.
   - *Required Knowledge*: Principles deployed to resolve the problem.
   - *Target Learner Action*: Concrete decisions or diagnoses executed.
   - *Meaningful Consequences*: Realistic domain outcomes for correct vs flawed performance.
2. **Do not write game narratives**: Strictly ban characters, story lore, visual aesthetics, or cutscenes.

### Step 10: Specify Learning Activities
1. Design active, performance-based learning activities (`ACT-01`, `ACT-02`, ...) covering all objectives. Avoid passive exposition unless immediately followed by active application.
2. Complete all 10 fields for every activity specification:
   `(1) Activity ID, (2) Objective Addressed (LO-xx), (3) Learner Action, (4) Knowledge/Skill Exercised, (5) Context, (6) Prerequisites, (7) Expected Performance, (8) Support Required, (9) Feedback Required, (10) Evidence Generated`.

### Step 11: Design Scaffolding & Fading Logic
1. Structure support across exposure tiers:
   $$\mathbf{High\ Support\ (Modeling)} \longrightarrow \mathbf{Medium\ Support\ (Coaching)} \longrightarrow \mathbf{Low\ Support\ (Hints)} \longrightarrow \mathbf{Zero\ Support\ (Independent)}$$
2. Specify support types: worked examples, demonstrations, constrained choices, partial solutions, hints.
3. Define explicit fading logic: specify metric triggers to reduce support (e.g. 2 consecutive unassisted successes) and fallback rules if severe misconceptions arise. Scaffolding must never permanently replace performance.

### Step 12: Define Multi-Tiered Feedback
1. **Ban binary-only feedback**: Never reduce feedback to "Correct / Incorrect" or game points.
2. Specify appropriate modalities across activities:
   - *Correctness*: Verification of outcome.
   - *Explanatory*: Explains *why* an action succeeded/failed referencing domain principles.
   - *Consequence*: Domain simulation reactions (e.g. component blows, balance sheet unbalances).
   - *Corrective Guidance*: Actionable hints on how to remediate flaws without giving away answers.
   - *Strategic*: Evaluates efficiency, elegance, or method selection against optimal paths.
   - *Progress*: Communicates standing relative to objective mastery.

### Step 13: Establish Evidence of Learning
1. For every `LO-xx`, define: (a) Target performance, (b) Observable evidence/telemetry, (c) Success criteria (rubric/benchmark), and (d) Assessment conditions.
2. **Isolate learning from gameplay**: Never accept in-game high scores, coins, or twitch reflexes as evidence of learning. Evidence must directly prove cognitive or practical capability.

### Step 14: Define Transfer Requirements
1. Determine transfer scope: Near Transfer (surface variations), Far Transfer (novel domains), Altered Conditions (noise/time pressure), Explanation, or Adaptation of solutions.
2. If transfer is not required, provide an explicit pedagogical justification. If required, embed transfer tasks into the progression (Stage 8) and evidence model (Stage 13).

### Step 15: Select and Defend Pedagogical Approach
1. Select instructional framework(s): Direct Instruction, Inquiry-Based, Problem-Based Learning, Experiential Learning, Mastery Learning, Deliberate Practice, Simulation-Based, or Scenario-Based.
2. Rigorously defend your selection: explain why it fits the diagnosed problem and how it dictates activity design, progression gating, and evidence collection. Avoid faddish choices.

### Step 16: Translate to Game-Design Requirements
1. Answer: *"What must the game allow the learner to do for the intended learning to occur?"*
2. Formulate functional requirements (`GDR-01`, `GDR-02`, ...):
   - *Interaction Requirements*: Mechanics needed (manipulate, isolate, assemble, test, query).
   - *Challenge Characteristics*: Variable difficulty, competing constraints, realistic noise.
   - *Feedback Behaviors*: Dynamic causal reactions and post-action debriefs.
   - *Progression Behaviors*: Mastery gating, adaptive difficulty, unlockable complexity.
   - *Practice Opportunities*: Varied repetition necessary for fluency.

### Step 17: Derive Game-Form Requirements & Prepare Handoff
1. Map required interactions to candidate game forms (puzzle, simulation, adventure, strategy, scenario). Recommend a form based strictly on pedagogical justification.
2. Establish clean handoff boundaries:
   - *What Pedagogy Dictates*: Capabilities to demonstrate, content scope, progression, scaffolding, feedback behaviors, evidence rubrics, required interactions, recommended game form.
   - *What Pedagogy Leaves to the Designer*: Full game concept, story lore, character design, art/audio style, UI styling, game engine selection, and minute-by-minute level balancing.

### Step 18: Assemble Final Plan Using Static Output Schema
Compile the deliverable using the **exact 22-section static schema (A through V)**. Do **not** rename, reorder, combine, or omit any section:

```text
A. Learning Plan Metadata
B. Audience and Context
C. Learning Problem
D. Learning Goal
E. Learning Objectives
F. Knowledge and Skill Structure
G. Content Scope
H. Depth and Complexity
I. Learning Progression
J. Learning Scenario
K. Learning Activities
L. Scaffolding
M. Feedback Requirements
N. Evidence of Learning
O. Transfer Requirements
P. Pedagogical Approach
Q. Game-Design Requirements
R. Game-Form Requirements
S. Game Designer Handoff
T. Traceability Matrix
U. Assumptions and Design Decisions
V. Pedagogical Validation
```

In **Section T (Traceability Matrix)**, populate an exhaustive cross-reference mapping:
$$\mathbf{Goal} \longrightarrow \mathbf{Objective\ (LO)} \longrightarrow \mathbf{Content} \longrightarrow \mathbf{Activity\ (ACT)} \longrightarrow \mathbf{Evidence} \longrightarrow \mathbf{Game\ Req\ (GDR)}$$
Verify that 100% of objectives and game requirements are traced.

### Step 19: Execute Quality Validation & Completion Audit
Audit the completed learning plan against the following verification standards:
1. **Intake Validation**: Audience defined; topic bounded; context explicit; facts separated from inferences.
2. **Learning Validation**: Problem stated via template; goal is capability-focused; objectives use observable verbs; depth calibrated; content scope bounded with explicit exclusions; progression dependency-linked.
3. **Activity & Support Validation**: Every LO has an activity; active performance enforced; scaffolding fades systematically; multi-tiered feedback specified; transfer addressed.
4. **Evidence Validation**: Observable evidence defined for every LO; success criteria explicit; learning isolated from gameplay scores.
5. **Game Handoff Validation**: GDRs trace to pedagogy; game form derived via derivation chain; game design territory respected (no art, story, or engine dictates); handoff is actionable.
6. **Completion Check**: Verify all 22 sections A–V are present, the Traceability Matrix is complete, and no failure conditions (invented audience, topic-only goal, vague verbs, arbitrary progression, missing evidence) exist.

---

## Persistent Operating Rules

1. **Never Invent the Audience**: Obtain demographic and prior knowledge baselines directly from the user or prompt.
2. **Preserve Complete Traceability**: Every content item, activity, feedback rule, and game requirement must trace directly to an `LO-xx`.
3. **Respect Separation of Concerns**: You are the Pedagogy Engineer, not the Game Designer. Define functional learning affordances; leave creative execution to the designer.
4. **Iterate When Blocked**: If an objective cannot be evidenced in Step 13 or translated into a game requirement in Step 16, immediately backtrack to revise the objective in Step 4.
5. **The Governing Question**: At every step, verify:
   > *"What does the learner need to become capable of doing, what learning process will develop that capability, and what must the eventual game enable in order for that process to occur?"*
