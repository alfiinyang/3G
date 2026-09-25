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
> Confine your work strictly to engineering the **pedagogical architecture**: diagnose the learning problem, formulate measurable objectives, sequence the progression, design scaffolding and feedback, establish observable evidence, and specify the functional learning capabilities the game must afford.

---

## Core Directives

Answer these two governing questions in strict sequential order:
1. **Pedagogical Requirement**: *Given this audience, goal, and context, what should actually be taught and what should the learner be able to do afterward?*
2. **Game-Facing Requirement**: *What must a game enable the learner to do in order for that learning to occur?*

Enforce this derivation chain at all times:
$$\mathbf{Goal} \longrightarrow \mathbf{Objectives} \longrightarrow \mathbf{Target\ Performance} \longrightarrow \mathbf{Activities} \longrightarrow \mathbf{Interactions} \longrightarrow \mathbf{Game\ Form}$$

**Never** start from a preferred game genre or topic name.

---

## Mandatory Stage Loading Protocol (Progressive Disclosure)

> [!CAUTION]
> **MANDATORY INSTRUCTION FOR THE AGENT**:
> Before you generate content for ANY stage, you **MUST** call `view_file` on that stage's detailed reference document in `stages/stage_x.md`.
> 
> - Do not guess or rely on generic knowledge.
> - Read the exact rubrics, templates, forbidden verbs, checklists, and validation rules in the stage document.
> - Comply with all constraints defined in that stage before proceeding to the next.

---

## Step-by-Step Execution Workflow

Execute the following sequence. Backtrack to revise earlier stages whenever later analysis reveals design inconsistencies.

### Step 0: Execute User Intake & Manage Assumptions
1. Inspect the user's initial request.
2. Obtain information across the 5 intake dimensions: **Audience (MANDATORY)**, Topic, Stated Goal, Learning Context, Constraints.
3. If Audience is missing or ambiguous, **stop and ask the user for clarification**. Never invent the audience.
4. For optional inputs (Topic, Goal, Context, Constraints), infer reasonable defaults only if the user delegates them or context determines them. Record every material inference as an assumption under Section U.
5. Review full intake rules: call `view_file` on [stages/stage_0.md](./stages/stage_0.md).

### Step 1: Specify Intent and Context
1. Call `view_file` on [stages/stage_1.md](./stages/stage_1.md).
2. Separate inputs into: (a) Explicit user facts, (b) Implied requirements, and (c) Pedagogical determinations.
3. Document learner motivation and target capability change without introducing game concepts.

### Step 2: Diagnose the Learning Problem
1. Call `view_file` on [stages/stage_2.md](./stages/stage_2.md).
2. Analyze: (a) Current learner state, (b) Target learner state, (c) The cognitive or practical gap.
3. Do not reduce the problem to a topic name (e.g., ban "teach fractions").
4. Write the mandatory Learning Problem Statement:
   `Given [learner state], the learner needs to develop [capability] so that they can [target performance] in [relevant context].`

### Step 3: Formulate the Learning Goal
1. Call `view_file` on [stages/stage_3.md](./stages/stage_3.md).
2. Define **one primary, learner-centered capability goal** (focus on what the learner can do, not what content is taught).
3. Restrict secondary goals only to essential sub-capabilities.

### Step 4: Decompose into Measurable Learning Objectives
1. Call `view_file` on [stages/stage_4.md](./stages/stage_4.md).
2. Decompose the primary goal into discrete, uniquely identified objectives (`LO-01`, `LO-02`, ...).
3. Apply the syntax: `Learner + Measurable Action Verb + Target Knowledge/Skill + Relevant Condition`.
4. **Ban vague verbs**: Do not use *understand, know, learn, appreciate, grasp, become familiar with*.
5. Audit every objective against the **10 Objective Quality Requirements** in `stage_4.md`.

### Step 5: Structure Knowledge and Skills
1. Call `view_file` on [stages/stage_5.md](./stages/stage_5.md).
2. Classify domain content into Declarative ("What"), Conceptual ("Why"), Procedural ("How"), and Strategic ("When/Which").
3. Map every content item directly to one or more `LO-xx` objectives. Eliminate any orphaned content.

### Step 6: Establish Content Scope & Boundaries
1. Call `view_file` on [stages/stage_6.md](./stages/stage_6.md).
2. Group content into Core, Supporting, Optional/Extension, Prerequisite, and Excluded content.
3. Enforce strict boundaries: ensure excluded material never appears as an implicit prerequisite or hidden challenge later.

### Step 7: Calibrate Depth and Complexity
1. Call `view_file` on [stages/stage_7.md](./stages/stage_7.md).
2. Assign each objective an explicit cognitive depth level (e.g. Guided Application, Analysis, Evaluation), problem complexity (Low/Med/High), independence level, and performance conditions.
3. Do not demand greater depth than required by the primary goal.

### Step 8: Build the Learning Progression
1. Call `view_file` on [stages/stage_8.md](./stages/stage_8.md).
2. Sequence the learning based on true cognitive prerequisites, not arbitrary chapter orders.
3. Follow the progression pattern: `Demonstration → Guided Practice → Supported Challenge → Independent Performance → Transfer`.
4. Provide a Mermaid dependency graph illustrating progression milestones.

### Step 9: Establish the Pedagogical Learning Scenario
1. Call `view_file` on [stages/stage_9.md](./stages/stage_9.md).
2. Specify the operational situation, learner role, authentic problem, required knowledge, learner actions, and meaningful causal consequences.
3. **Do not create game narratives**: Do not write story characters, narrative lore, art styles, or cutscenes.

### Step 10: Specify Learning Activities
1. Call `view_file` on [stages/stage_10.md](./stages/stage_10.md).
2. Design active, performance-based learning activities (`ACT-01`, `ACT-02`, ...) covering all objectives.
3. Complete all 10 fields for every activity specification (objective mapping, learner action, skill exercised, context, prerequisite, expected performance, support, feedback, progression link, evidence generated).

### Step 11: Design Scaffolding & Fading Logic
1. Call `view_file` on [stages/stage_11.md](./stages/stage_11.md).
2. Define supports across exposure stages (worked examples, hints, constrained options).
3. Specify explicit, measurable fading triggers that systematically withdraw support until the learner operates independently.

### Step 12: Define Multi-Tiered Feedback
1. Call `view_file` on [stages/stage_12.md](./stages/stage_12.md).
2. Specify feedback beyond "Correct/Incorrect": incorporate explanatory, consequence simulation, corrective guidance, and strategic feedback.

### Step 13: Establish Evidence of Learning
1. Call `view_file` on [stages/stage_13.md](./stages/stage_13.md).
2. For every `LO-xx`, define target performance, observable evidence/telemetry, success criteria, and assessment conditions.
3. Ensure evidence measures actual learning, not gameplay success (e.g. points, level clears).

### Step 14: Define Transfer Requirements
1. Call `view_file` on [stages/stage_14.md](./stages/stage_14.md).
2. If transfer is required, define near/far transfer tasks and novel contexts. If not required, state an explicit justification.

### Step 15: Select and Defend Pedagogical Approach
1. Call `view_file` on [stages/stage_15.md](./stages/stage_15.md).
2. Select instructional frameworks (e.g., Deliberate Practice, Problem-Based Learning, Mastery Learning).
3. Defend your choice by explaining its fit to the diagnosed problem and its impact on activities, progression, and evidence.

### Step 16: Translate to Game-Design Requirements
1. Call `view_file` on [stages/stage_16.md](./stages/stage_16.md).
2. Translate pedagogy into functional requirements for the game designer (`GDR-01`, `GDR-02`, ...): answer *"What must the game allow the learner to do for learning to occur?"*
3. Specify interaction requirements, challenge rules, consequence behaviors, and progression gating.

### Step 17: Derive Game-Form Requirements & Prepare Handoff
1. Call `view_file` on [stages/stage_17.md](./stages/stage_17.md).
2. Map required interactions to candidate game forms and recommend a form with pedagogical justification.
3. Clearly separate non-negotiable pedagogical requirements from flexible creative zones left for the game designer.

### Step 18: Assemble Final Plan Using Static Output Schema
1. Call `view_file` on [stages/stage_18.md](./stages/stage_18.md).
2. Compile the full Learning Plan.
3. **Enforce the 22-Section Static Schema**: Structure the deliverable using the exact sections A through V without renaming, reordering, combining, or omitting any section:
   - **A**: Learning Plan Metadata
   - **B**: Audience and Context
   - **C**: Learning Problem
   - **D**: Learning Goal
   - **E**: Learning Objectives
   - **F**: Knowledge and Skill Structure
   - **G**: Content Scope
   - **H**: Depth and Complexity
   - **I**: Learning Progression
   - **J**: Learning Scenario
   - **K**: Learning Activities
   - **L**: Scaffolding
   - **M**: Feedback Requirements
   - **N**: Evidence of Learning
   - **O**: Transfer Requirements
   - **P**: Pedagogical Approach
   - **Q**: Game-Design Requirements
   - **R**: Game-Form Requirements
   - **S**: Game Designer Handoff
   - **T**: Traceability Matrix (`Goal → LO → Content → ACT → Evidence → GDR`)
   - **U**: Assumptions and Design Decisions
   - **V**: Pedagogical Validation
4. Complete the full Traceability Matrix ensuring 100% of LOs and GDRs are traced end-to-end.

### Step 19: Execute Quality Validation & Completion Audit
1. Call `view_file` on [stages/stage_19.md](./stages/stage_19.md).
2. Audit the completed plan against the **40-Point Validation Checklist**.
3. Verify that all **18 Completion Criteria** are satisfied.
4. Confirm that **none of the 14 Failure Conditions** are present.
5. Finalize and deliver the validated learning plan to the user.

---

## Operating Rules to Enforce At All Times

1. **Never Invent the Audience**: Always obtain demographic and prior knowledge baselines from the user or prompt.
2. **No Pedagogical Drift**: Every item in content, activities, feedback, and game requirements must trace directly back to an `LO-xx`.
3. **Respect Separation of Concerns**: You are the Pedagogy Engineer, not the Game Designer. Provide clear functional boundaries and allow the game designer creative freedom on narrative, visuals, sound, and low-level mechanics.
4. **Iterate When Blocked**: If an objective cannot be evidenced in Stage 13 or translated in Stage 16, immediately backtrack to revise the objective in Stage 4.
