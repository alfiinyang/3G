# Pedagogy Engineering for Game-Based Learning

## Skill Definition

This skill transforms a teacher/trainer's learning request into a structured,
game-designer-ready learning plan.

The skill is topic-agnostic and may be applied to academic, vocational,
professional, technical, or general learning domains.

The skill does NOT design the game.

The skill defines the learning problem, learning requirements, pedagogical
structure, and game-facing learning requirements that a subsequent game
designer can use to design the game.

The final output is a static-schema structured learning plan.

---

## Core Principle

The skill must answer:

> Given this audience, goal, and context, what should actually be taught
> and what should the learner be able to do afterward?

The skill must then determine:

> What must a game enable the learner to do in order for that learning to occur?

The skill must derive game-form requirements from pedagogy rather than
selecting a game form merely from the topic.

---

# 1. USER INTAKE

The agent must obtain information for the following five inputs.

The five inputs form the initial pedagogical specification.

## 1.1 Audience — REQUIRED

The agent must obtain the intended learner population.

At minimum, identify:

* approximate age or educational level;
* relevant prior knowledge or experience, if known;
* learner setting, if relevant;
* significant learner characteristics that affect instruction.

If the user does not provide sufficient audience information, the agent
must ask for clarification before proceeding.

The agent must not independently invent the audience.

---

## 1.2 Topic / Domain — OPTIONAL USER INPUT

The agent should ask the user for the topic or subject domain.

Examples include:

* programming;
* mathematics;
* biology;
* history;
* electrical installation;
* financial literacy;
* professional communication.

If the user explicitly asks the agent to determine the topic, the agent may
derive it from the request.

If the topic is already unambiguously contained in the user's request,
additional questioning is unnecessary.

---

## 1.3 Intended Learning Goal — OPTIONAL USER INPUT

The agent should ask what the teacher/trainer wants learners to achieve.

The user's statement may be informal, incomplete, broad, or pedagogically
imprecise.

If the user explicitly asks the agent to determine the goal, the agent may
formulate it from the available context.

The agent must distinguish the user's original intent from the refined
pedagogical learning goal.

---

## 1.4 Learning Context — OPTIONAL USER INPUT

The agent should ask where, why, and under what circumstances the learning
will occur.

Relevant information may include:

* classroom;
* training programme;
* self-directed learning;
* workplace training;
* curriculum requirement;
* practical training;
* simulation;
* assessment preparation;
* real-world application.

If the user explicitly asks the agent to determine the context, the agent
may infer a reasonable context from available information.

Inferences must be identified as assumptions internally during reasoning and
must not be presented as user-provided facts.

---

## 1.5 Constraints / Requirements — OPTIONAL USER INPUT

The agent should ask for known constraints.

Relevant constraints include:

* available learning time;
* curriculum or standards;
* age appropriateness;
* required content;
* excluded content;
* delivery environment;
* technology limitations;
* expected learner output;
* assessment requirements;
* institutional requirements;
* accessibility requirements;
* desired scope.

If the user explicitly asks the agent to determine these, the agent may
establish reasonable constraints from context.

---

# 2. INTAKE RULES

The agent must not unnecessarily interrogate the user.

If information is already available in the request, it must be reused.

The agent must ask for missing information only when that information is
necessary to produce a valid pedagogical specification.

Audience is the only mandatory user-supplied input.

For inputs 2–5, the agent may decide or infer the information only when:

1. the user explicitly asks the agent to decide; or
2. the information is sufficiently determined by the request.

The agent must not silently convert uncertain assumptions into facts.

Where an assumption materially affects the learning design, it must be
identified in the final plan under "Assumptions and Design Decisions."

---

# 3. PEDAGOGICAL ENGINEERING PROCESS

After intake, the agent performs the remaining process autonomously.

The process is sequential in logic but iterative in execution.

Later analysis may reveal that an earlier decision needs revision.

The agent must therefore be able to return to earlier stages when necessary.

The stages are:

1. Intent and Context Specification
2. Learning Problem Diagnosis
3. Learning Goal Formulation
4. Learning Objective Decomposition
5. Knowledge and Skill Structure
6. Content Scope
7. Depth and Complexity
8. Learning Progression
9. Learning Scenario
10. Learning Activities
11. Scaffolding
12. Feedback Requirements
13. Evidence of Learning
14. Transfer Requirements
15. Pedagogical Approach
16. Game-Design Requirements
17. Game-Form Requirements
18. Learning Plan Assembly
19. Quality Validation

---

# 4. STAGE 1 — INTENT AND CONTEXT SPECIFICATION

Interpret the user's request without prematurely designing the game.

Identify:

* audience;
* topic/domain;
* intended goal;
* context;
* constraints;
* motivation for learning;
* expected learner change;
* relevant assumptions.

Separate:

* what the user explicitly requested;
* what the request implies;
* what must be determined pedagogically.

Output:

**Intent and Context Specification**

The specification must establish a sufficiently clear starting point for
pedagogical reasoning.

---

# 5. STAGE 2 — LEARNING PROBLEM DIAGNOSIS

Determine the actual learning problem.

Ask:

> What does the learner currently know or do?

> What should the learner know or do afterward?

> What gap exists between those states?

The learning problem must not be reduced to the name of a topic.

For example, "teach fractions" is not a learning problem.

Possible learning problems include inability to:

* recognize;
* explain;
* compare;
* calculate;
* apply;
* diagnose;
* construct;
* evaluate;
* transfer.

Output:

**Learning Problem Statement**

Use the structure:

> Given [learner state], the learner needs to develop [capability]
> so that they can [target performance] in [relevant context].

---

# 6. STAGE 3 — LEARNING GOAL FORMULATION

Convert the broad intent into a meaningful learner-centred goal.

The learning goal must describe the overall capability to be developed.

Avoid goals that merely name content.

Weak:

> Teach conditional statements.

Stronger:

> Develop learners' ability to use conditional logic to make decisions
> in simple programs.

The goal must be:

* relevant;
* achievable within scope;
* learner-centred;
* sufficiently specific;
* consistent with the learning problem.

Output:

**One primary learning goal.**

Secondary goals may be included only when genuinely necessary.

---

# 7. STAGE 4 — LEARNING OBJECTIVE DECOMPOSITION

Decompose the learning goal into observable objectives.

Every objective must specify an observable learner capability.

Prefer:

> Learner + measurable action + target knowledge/skill + relevant condition.

Avoid vague verbs such as:

* understand;
* know;
* learn;
* appreciate;
* become familiar with.

Unless they are operationalized by observable evidence.

Useful action verbs include:

* identify;
* classify;
* explain;
* distinguish;
* interpret;
* calculate;
* construct;
* apply;
* diagnose;
* compare;
* sequence;
* analyze;
* select;
* solve;
* create;
* evaluate;
* justify;
* demonstrate.

Each objective must be independently meaningful.

Objectives must collectively support the learning goal.

---

# 8. OBJECTIVE QUALITY REQUIREMENTS

Every objective must satisfy all applicable criteria:

1. It describes learner performance.
2. It uses an observable action.
3. It identifies the target knowledge or skill.
4. It is appropriate for the audience.
5. It is achievable within the stated scope.
6. It has identifiable evidence of achievement.
7. It contributes directly to the learning goal.
8. Its required depth is specified.
9. It does not introduce unnecessary content.
10. It can eventually be translated into a learner activity.

If an objective fails these criteria, revise it.

---

# 9. STAGE 5 — KNOWLEDGE AND SKILL STRUCTURE

Determine what learners need to learn in order to achieve the objectives.

Classify relevant elements as:

### Declarative knowledge

Facts, terminology, definitions, properties, rules, and information.

### Conceptual knowledge

Concepts, relationships, principles, models, and underlying ideas.

### Procedural knowledge

Methods, procedures, techniques, and sequences of action.

### Strategic knowledge

Choosing methods, recognizing when methods apply, planning, monitoring,
or adapting strategies.

Include only categories relevant to the learning problem.

Map every major content element to one or more learning objectives.

---

# 10. STAGE 6 — CONTENT SCOPE

Define explicit boundaries.

For each objective identify:

* core content;
* supporting content;
* optional content;
* prerequisite content;
* excluded content.

The agent must prevent scope expansion that does not contribute to the
learning goal.

Out-of-scope material must not appear as a hidden requirement elsewhere
in the plan.

The scope must be appropriate for the audience and available learning
conditions.

---

# 11. STAGE 7 — DEPTH AND COMPLEXITY

Determine how deeply each objective must be learned.

Possible levels include:

* recognition;
* recall;
* explanation;
* interpretation;
* guided application;
* independent application;
* analysis;
* creation;
* evaluation;
* fluent performance.

The exact taxonomy may vary by domain.

The important requirement is that the expected learner performance is
explicit.

For each objective specify:

* expected cognitive/performance level;
* complexity;
* independence;
* acceptable performance conditions.

Do not demand greater depth than the learning goal requires.

---

# 12. STAGE 8 — LEARNING PROGRESSION

Determine how learning develops from initial exposure to target performance.

Identify:

* prerequisites;
* foundational concepts;
* intermediate capabilities;
* integrated capabilities;
* advanced or transfer performance.

Define dependencies between objectives.

A progression may use patterns such as:

> Demonstration → Guided Practice → Supported Challenge →
> Independent Performance → Transfer

The chosen progression must follow the actual dependency structure of the
learning rather than an arbitrary topic order.

---

# 13. STAGE 9 — LEARNING SCENARIO

Define the situation in which learners can meaningfully use the target
knowledge or skill.

The learning scenario is pedagogical, not game narrative.

It should describe:

* situation;
* learner role;
* relevant problem;
* required knowledge/skill;
* desired learner action;
* meaningful consequence.

Do not prescribe:

* story characters;
* visual style;
* game world;
* narrative plot;
* specific game mechanics.

Those belong to later design stages.

---

# 14. STAGE 10 — LEARNING ACTIVITIES

Determine what learners must actually do to learn.

For every objective identify one or more appropriate activities.

Possible activities include:

* observe;
* identify;
* classify;
* recall;
* explain;
* predict;
* manipulate;
* construct;
* solve;
* diagnose;
* compare;
* sequence;
* simulate;
* experiment;
* practise;
* create;
* collaborate;
* reflect;
* decide;
* troubleshoot.

The activity must support the intended learning.

Avoid activities that merely expose learners to content without requiring
the target cognitive or practical performance.

---

# 15. ACTIVITY SPECIFICATION

For every major learning activity specify:

* objective addressed;
* learner action;
* knowledge/skill exercised;
* context;
* prerequisite;
* expected performance;
* support required;
* feedback required;
* progression relationship;
* evidence generated.

Activities must collectively provide sufficient opportunities to achieve the
learning objectives.

---

# 16. STAGE 11 — SCAFFOLDING

Determine how learner support changes over time.

Specify where learners receive:

* explanation;
* demonstration;
* worked examples;
* prompts;
* hints;
* constrained choices;
* partial solutions;
* corrective support.

Specify when support should be reduced.

The default principle should be:

> Increase learner independence as competence develops.

Scaffolding must not permanently replace the target learner performance.

---

# 17. STAGE 12 — FEEDBACK REQUIREMENTS

Define what learners need to learn from their actions.

For relevant activities specify:

* correctness feedback;
* explanatory feedback;
* consequence feedback;
* corrective guidance;
* strategic feedback;
* progress feedback.

Do not specify feedback merely as:

> Correct / Incorrect.

Where learning requires understanding, feedback should expose the relevant
principle, reasoning, consequence, or correction.

---

# 18. STAGE 13 — EVIDENCE OF LEARNING

For every learning objective determine how achievement can be observed.

Specify:

### Target performance

What the learner must do.

### Evidence

What observable behaviour demonstrates achievement.

### Criteria

What constitutes acceptable performance.

### Conditions

Under what circumstances the performance must occur.

Evidence must be directly related to the objective.

Do not use unrelated game success as evidence of learning.

---

# 19. STAGE 14 — TRANSFER REQUIREMENTS

Determine whether learners must apply learning beyond the immediate activity.

Identify required transfer such as:

* new problem;
* new context;
* unfamiliar example;
* altered conditions;
* real-world situation;
* explanation;
* adaptation of an existing solution.

If transfer is not required, state that explicitly.

If transfer is required, include it in the learning progression and evidence
model.

---

# 20. STAGE 15 — PEDAGOGICAL APPROACH

Select or combine pedagogical approaches based on the learning requirements.

Possible approaches include:

* direct instruction;
* inquiry-based learning;
* problem-based learning;
* experiential learning;
* mastery learning;
* discovery learning;
* deliberate practice;
* collaborative learning;
* simulation-based learning;
* scenario-based learning.

Do not select a framework merely because it is fashionable or familiar.

For each selected approach explain:

* why it fits the learning problem;
* which objectives it supports;
* how it affects learning activities;
* how it affects progression;
* how it affects evidence of learning.

---

# 21. STAGE 16 — GAME-DESIGN REQUIREMENTS

Translate pedagogical requirements into requirements that a game designer
can act upon.

Ask:

> What must the game allow the learner to do for the intended learning to
> occur?

Examples:

If learners must diagnose:

* the game must provide observable evidence;
* learners must gather/interrogate information;
* learners must make a diagnosis;
* consequences must respond to the diagnosis.

If learners must construct:

* the game must allow meaningful construction;
* the construction must reflect the target knowledge;
* incorrect construction must produce informative consequences.

If learners must practise:

* the game must provide repeated opportunities;
* challenges must vary sufficiently;
* feedback must support improvement.

These are requirements, not game designs.

---

# 22. STAGE 17 — GAME-FORM REQUIREMENTS

Determine the interaction model required by the pedagogy.

First identify required interactions:

* manipulation;
* decision-making;
* exploration;
* construction;
* diagnosis;
* simulation;
* sequencing;
* resource management;
* experimentation;
* collaboration;
* problem solving;
* creation.

Then identify game forms capable of supporting those interactions.

Possible forms include:

* puzzle;
* simulation;
* adventure;
* investigation;
* strategy;
* drag-and-drop;
* scenario-based game;
* mixed/hybrid form.

The agent may recommend a game form.

The agent must explain the pedagogical basis for the recommendation.

The agent must not design the complete game.

---

# 23. GAME-FORM DECISION RULE

The game form must be derived through the following chain:

> Learning Goal
> → Objectives
> → Required Learner Performance
> → Learning Activities
> → Required Interactions
> → Game-Form Requirements

Do not use this chain:

> Topic
> → Favourite Genre
> → Learning Activities

Genre must never be the starting point.

A game form is appropriate only when its interaction model can support the
required learner activities and evidence of learning.

---

# 24. GAME DESIGNER HANDOFF

The final learning plan must tell a game designer:

* what must be learned;
* why it must be learned;
* who is learning;
* what learners must be able to do;
* what content is in scope;
* how deeply it must be learned;
* how learning should progress;
* what learners should do;
* what support they require;
* what feedback they require;
* what evidence demonstrates learning;
* what transfer is expected;
* what pedagogical approach is recommended;
* what interactions the game must support;
* what game-form characteristics are required.

It must not prescribe the complete:

* game concept;
* game loop;
* level design;
* story;
* characters;
* mechanics implementation;
* interface;
* visual design;
* audio;
* technical architecture.

Those belong to subsequent design stages.

---

# 25. STATIC OUTPUT SCHEMA

The final document MUST use the following top-level structure.

The structure is static and must not be reordered, renamed, or omitted.

## A. Learning Plan Metadata

Include:

* title;
* version;
* domain;
* intended audience;
* authoring context;
* status;
* assumptions;
* constraints.

## B. Audience and Context

Include:

* audience profile;
* prior knowledge;
* learning environment;
* learning context;
* relevant constraints.

## C. Learning Problem

Include:

* current learner state;
* desired learner state;
* identified gap;
* problem statement.

## D. Learning Goal

Include:

* primary goal;
* supporting goals, if necessary;
* goal rationale.

## E. Learning Objectives

For every objective include:

* objective ID;
* objective statement;
* knowledge/skill type;
* expected level;
* prerequisites;
* evidence of achievement.

## F. Knowledge and Skill Structure

Include:

* declarative knowledge;
* conceptual knowledge;
* procedural knowledge;
* strategic knowledge;
* objective mappings.

## G. Content Scope

Include:

* core content;
* supporting content;
* optional content;
* prerequisite content;
* excluded content.

## H. Depth and Complexity

For every major objective include:

* required depth;
* complexity;
* independence;
* performance conditions.

## I. Learning Progression

Include:

* sequence;
* dependencies;
* stages;
* increasing complexity;
* mastery/transition conditions.

## J. Learning Scenario

Include:

* situation;
* learner role;
* problem;
* relevant knowledge;
* expected action;
* consequence.

## K. Learning Activities

For every activity include:

* activity ID;
* objective mapping;
* learner action;
* knowledge/skill exercised;
* context;
* support;
* expected performance.

## L. Scaffolding

Include:

* initial support;
* guided support;
* reduced support;
* independent performance;
* support-removal logic.

## M. Feedback Requirements

Include:

* feedback type;
* trigger;
* information conveyed;
* corrective function;
* progression implications.

## N. Evidence of Learning

For every objective include:

* target performance;
* observable evidence;
* success criteria;
* conditions;
* assessment/evidence method.

## O. Transfer Requirements

Include:

* transfer expectation;
* transfer contexts;
* transfer activities;
* transfer evidence.

## P. Pedagogical Approach

Include:

* selected approach(es);
* rationale;
* objective alignment;
* activity implications;
* progression implications;
* evidence implications.

## Q. Game-Design Requirements

Include:

* required learner interactions;
* required challenge characteristics;
* required feedback behaviour;
* required progression behaviour;
* required practice opportunities;
* required consequences;
* required transfer opportunities.

## R. Game-Form Requirements

Include:

* required interaction model;
* candidate game forms;
* selected/recommended form;
* pedagogical rationale;
* required characteristics;
* constraints;
* unresolved decisions for the game designer.

## S. Game Designer Handoff

Include:

* learning requirements summary;
* non-negotiable pedagogical requirements;
* flexible design areas;
* design constraints;
* open design questions;
* explicit statement of what the pedagogy does not prescribe.

## T. Traceability Matrix

Map:

> Goal → Objective → Content → Activity → Evidence → Game Requirement

Every objective must appear in the traceability matrix.

## U. Assumptions and Design Decisions

List:

* user-provided information;
* agent-derived decisions;
* assumptions;
* unresolved uncertainties;
* implications of each material assumption.

## V. Pedagogical Validation

Record whether each quality criterion has been satisfied.

---

# 26. TRACEABILITY REQUIREMENTS

The final document must maintain traceability throughout the plan.

Every objective must map to:

* relevant knowledge/skill;
* relevant content;
* at least one learning activity;
* evidence of learning;
* relevant game-design requirement.

Every major game-design requirement must trace back to at least one:

* learning objective;
* learning activity;
* evidence requirement;
* pedagogical requirement.

Requirements without pedagogical justification must be removed or marked as
outside the scope of this skill.

---

# 27. QUALITY VALIDATION

Before finalizing the document, perform a complete validation.

The skill is considered successfully applied only when all required criteria
are satisfied.

## Intake validation

1. Audience is explicitly defined.
2. Topic/domain is defined.
3. Learning goal is defined.
4. Context is defined.
5. Relevant constraints are defined.
6. User-provided information is distinguishable from agent-derived decisions.

## Learning validation

7. A coherent learning problem is stated.
8. The learning goal addresses that problem.
9. Every objective contributes to the goal.
10. Every objective is observable/measurable.
11. Every objective has an expected depth.
12. Content supports the objectives.
13. Scope explicitly identifies exclusions.
14. Prerequisites are identified where necessary.
15. Objective dependencies are represented.
16. Progression increases capability appropriately.

## Activity validation

17. Every objective has at least one learning activity.
18. Activities require meaningful learner action.
19. Activities support the intended objective.
20. Scaffolding is specified where required.
21. Feedback is specified where required.
22. Learner independence increases appropriately.
23. Transfer is addressed where required.

## Evidence validation

24. Every objective has observable evidence.
25. Success criteria are identifiable.
26. Conditions are specified where relevant.
27. Evidence measures learning rather than merely game success.

## Pedagogy validation

28. The pedagogical approach follows from the learning requirements.
29. The approach is justified.
30. The approach is consistent with the audience.
31. The approach is consistent with the learning context.
32. The approach is consistent with the progression.

## Game-handoff validation

33. Required learner interactions are explicitly identified.
34. Game requirements trace to pedagogical requirements.
35. Game form is derived from interaction requirements.
36. Game-form recommendation is pedagogically justified.
37. The document does not prescribe the complete game design.
38. Game designer responsibilities remain clearly separated.
39. Open design decisions are identified.
40. The final handoff is sufficiently specific to guide game design.

---

# 28. COMPLETION CRITERIA

The agent must consider the skill fully applied only if:

* all mandatory intake information is available;
* the learning problem is explicit;
* the learning goal is explicit;
* objectives are measurable;
* content scope is bounded;
* depth is specified;
* progression is coherent;
* learning activities are specified;
* scaffolding is addressed;
* feedback requirements are addressed;
* evidence of learning is defined;
* transfer requirements are addressed;
* pedagogical approach is justified;
* game-facing learning requirements are explicit;
* game-form requirements are derived from pedagogy;
* every objective is traceable through the plan;
* all major game requirements have pedagogical justification;
* the final document follows the static output schema;
* the document is usable by a game designer without requiring the agent to
  perform the actual game design.

---

# 29. FAILURE CONDITIONS

The skill must not be considered complete if:

* the audience is unknown;
* the learning goal is merely a topic label;
* objectives are vague;
* content is listed without learner performance;
* activities are disconnected from objectives;
* progression is arbitrary;
* evidence of learning is absent;
* game mechanics are proposed without pedagogical justification;
* genre is selected solely from the subject matter;
* the output becomes a game design document;
* the output omits the required static schema;
* important assumptions are presented as user-provided facts;
* objectives cannot be traced to evidence;
* game requirements cannot be traced to learning requirements.

---

# 30. OPERATING PRINCIPLES

The agent must:

* prioritize learning requirements over game conventions;
* remain topic-agnostic;
* distinguish content from capability;
* distinguish learning scenario from game narrative;
* distinguish pedagogy from game design;
* preserve traceability;
* minimize unnecessary user questioning;
* ask when missing information materially affects correctness;
* make permitted decisions when the user delegates them;
* explicitly manage assumptions;
* iterate when later reasoning invalidates earlier decisions;
* optimize for a useful designer handoff rather than a theoretically complete
  pedagogical essay.

The final question governing the entire skill is:

> **What does the learner need to become capable of doing, what learning
> process will develop that capability, and what must the eventual game
> enable in order for that process to occur?**

The final artifact is the structured answer to that question.