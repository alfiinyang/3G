---
name: learner-experience-engineering
description: >-
  Transform an approved pedagogical plan into a coherent,
  traceable learner-facing game experience specification for the
  Requirements Translation (RT) layer.

---

# Learner-Experience Engineering Instructions

## ANIR Legend

Use the following labels as an operational instruction convention:

-   `ROLE`: identity and responsibility of the agent.
-   `GOAL`: required result.
-   `INPUT`: information consumed by the agent.
-   `PRECONDITIONS`: conditions that must be met before execution or a
    stage can proceed.
-   `STATE`: current working representation or meaningful experience
    condition.
-   `STAGE`: an ordered transformation step.
-   `ACTION`: an operation the agent must perform.
-   `DECISION`: a condition and the corresponding required branch.
-   `RULE`: a binding design constraint.
-   `OUTPUT`: artifact or information produced.
-   `VALIDATION`: a check with explicit pass/fail criteria.
-   `TRANSITION`: condition for moving to the next stage.
-   `ESCALATION`: issue that must be referred upstream or reported as
    blocking.
-   `COMPLETION`: conditions for finishing the skill execution.

Apply these labels consistently. Treat mandatory rules as binding. Treat
conditional instructions as mandatory whenever their stated condition is
met.

## 1. Input Contract

INPUT Receive the pedagogical plan as Markdown or an equivalent
structured artifact. Also consume any applicable safety guides, project
constraints, and upstream decisions supplied by the larger system.

Extract the following fields wherever supplied:

-   Target audience, age range, educational level, and relevant learner
    characteristics.
-   Subject, topic, and learning context.
-   Overall learning goal.
-   Learning objectives and learning requirements.
-   Included and excluded content, expected depth, and prerequisite
    knowledge.
-   Expected learning outcomes.
-   Recommended pedagogical approach or framework.
-   Approved game genre or interaction format, including hybrid genres.
-   Learning environment, setting, context, or circumstances in which
    learning occurs.
-   Explicit constraints, preferences, accessibility requirements, and
    earlier-stage decisions.
-   Applicable safety guides and relevant project scope limits.
-   Source plan identifier, version, or revision, if provided.

RULE Treat the pedagogical plan as authoritative for audience, learning
goals, objectives, content scope, expected outcomes, and approved game
genre. Preserve the intended depth of understanding and all stated
constraints.

RULE Treat the learning environment as both a constraint and a
contextual resource. Use it to shape the experience only when doing so
remains consistent with the approved plan.

RULE Maintain traceability from each learning objective and major
learning requirement to at least one scene or task and an observable
learner action or response.

DECISION - If a field is absent but the experience can be designed
without materially changing learning intent, make a conservative
experiential assumption, record it in **Assumptions and
Clarifications**, and proceed. - If information is ambiguous but a safe,
coherent interpretation is evident within the approved constraints, use
that interpretation and document it. - If a missing, ambiguous, or
conflicting requirement materially prevents a coherent design, request
clarification through the upstream conversational mechanism and pause
the affected design decision. - If a decision would materially change
learning objectives, content scope, expected outcomes, or approved
genre, escalate it to the Pedagogy stage. Do not silently revise the
pedagogical plan. - If applicable safety guidance is missing or
conflicting in a way that prevents a reliable safety decision, identify
the dependency and escalate rather than inventing policy.

## 4. Global Execution Rules

RULE Use the approved genre as an established constraint. Express the
experience through that genre; do not replace it with a different genre
on your own authority.

RULE Make learning requirements integral to learner tasks, choices, and
consequences. Educational terminology in the story alone does not count
as learning coverage.

RULE Design a coherent learner-facing experience that another LLM can
translate without reconstructing missing story, scene, task, dialogue,
feedback, or transition decisions.

RULE Use stable identifiers throughout: - Requirements: `LR-01`,
`LR-02`, ... - Learning objectives: `LO-01`, `LO-02`, ... - Characters:
`CHAR-01`, `CHAR-02`, ... - Scenes: `SC-01`, `SC-02`, ... - Tasks:
`TASK-01`, `TASK-02`, ... - Experience states: `STATE-01`, `STATE-02`,
... - Safety or alignment issues: `ISSUE-01`, `ISSUE-02`, ... Keep an
identifier stable once assigned. Do not reuse identifiers for different
entities.

RULE Use deterministic sequences when the approved learning design
requires a specific order. Use branching, randomized ordering, or
alternative paths only when the branch supports the learning objectives,
has a clear learner-facing purpose, and can be described unambiguously
for RT.

RULE Keep experience design feasible for the stated lightweight GBL
system and project scope. Do not introduce level progression, audio,
assessment layers, persistent performance tracking, adaptive difficulty,
or elaborate reward systems unless explicitly approved by the input plan
or project requirements.

RULE Use supplied safety guides as active constraints throughout design.
Safety guidance shapes generation; safety validation checks the
completed artifact. Do not replace supplied policies with an invented
policy.

RULE Keep the learner's experience and observable outcomes explicit.
Describe what the learner sees or hears, what they can attempt, what
happens after the attempt, and what permits the experience to continue.

## 5. Transformation Workflow

Execute stages in order. Maintain a working state containing normalized
requirements, design decisions, unresolved questions, scene and task
definitions, traceability mappings, and review findings. Revisit earlier
stages when validation exposes a defect.

### STAGE LX-01 --- Parse and Normalize the Pedagogical Plan

PRECONDITIONS A pedagogical plan has been supplied.

INPUT Pedagogical plan, project constraints, and applicable safety
guides.

ACTION 1. Extract the input fields listed in the Input Contract. 2.
Assign stable identifiers to learning objectives and major learning
requirements. 3. Normalize synonymous terms without changing their
meaning. 4. Record content included, excluded, and the required depth of
understanding. 5. Identify dependencies, prerequisites, ordering
constraints, and relationships among objectives. 6. Separate explicit
requirements from inferred assumptions. 7. Record the approved game
genre and learning environment as constraints.

OUTPUT A normalized learning context containing the extracted fields,
identifiers, dependencies, constraints, source reference, and a list of
missing or conflicting information.

VALIDATION Confirm that every stated objective, major requirement, scope
limit, outcome, genre constraint, and relevant environment detail is
represented. Confirm that no requirement has been silently broadened,
narrowed, or rewritten.

DECISION If a material blocker exists, request clarification or escalate
it under the Input Contract. Otherwise proceed with documented
conservative assumptions.

TRANSITION Proceed when the normalized context is complete enough to
guide experience design.

### STAGE LX-02 --- Establish the Experience Design Direction

PRECONDITIONS The normalized learning context has passed LX-01 or has
only non-blocking uncertainties.

INPUT Normalized learning context.

ACTION 1. Define the core premise: the situation that gives the learner
a meaningful reason to engage. 2. Define the learner's role, purpose,
and relationship to the central problem. 3. Explain how the setting and
learning environment relate to the subject matter. 4. State the
principal experiential approach, such as exploration, investigation,
repair, creation, problem-solving, or guided practice, only where
compatible with the approved genre. 5. Define how narrative, learner
tasks, and learning outcomes reinforce one another. 6. Explain why this
experience fits the audience, objectives, environment, and approved
genre. 7. Establish the intended emotional and motivational tone in
audience-appropriate terms without allowing entertainment to displace
learning.

OUTPUT An experience direction with premise, learner role, experiential
concept, genre expression, learning connection, and rationale.

VALIDATION Check that the concept is understandable, appropriate for the
audience, compatible with the approved genre, feasible within scope, and
capable of accommodating all learning requirements.

DECISION If the concept cannot accommodate a learning requirement
without changing the approved plan, revise the concept. If no compatible
concept can satisfy the requirement, escalate to Pedagogy.

TRANSITION Proceed when the experience direction provides a coherent
basis for the world, scenes, and tasks.

### STAGE LX-03 --- Construct the Narrative and Game World

PRECONDITIONS The experience direction is coherent and approved within
the LX layer's authority.

INPUT Normalized learning context and experience direction.

ACTION 1. Write a concise narrative overview and establish the setting.
2. Define only the world rules needed to understand the learner's role,
tasks, and consequences. 3. Define relevant characters, including the
player character, non-player characters, narrator, or other entities. 4.
For each character, specify identifier, role, motivation, relationship
to the learner, and narrative function. 5. Establish the principal
problem, conflict, objective, or sequence of events. 6. Connect
narrative elements to specific learning requirements. 7. Remove
decorative story elements that add complexity without supporting
learning, orientation, motivation, feedback, or continuity. 8. Keep the
world and cast feasible for the defined GBL system and its scope.

OUTPUT A coherent narrative and world specification with characters,
world rules, plot, principal events, and learning connections.

VALIDATION Confirm that the narrative is internally consistent,
understandable, age-appropriate, compatible with the approved genre, and
relevant to the learning context. Confirm that no narrative premise
contradicts supplied safety guidance.

TRANSITION Proceed when the learner's purpose and the world context are
clear enough to structure a journey.

### STAGE LX-04 --- Design the Learner Journey and Scene Structure

PRECONDITIONS The narrative and world establish a clear learner purpose.

INPUT Experience direction, narrative/world specification, normalized
learning context.

ACTION 1. Define the entry point and the context the learner needs
before acting. 2. Create an ordered list of scenes or activities using
stable `SC-##` identifiers. 3. For each scene, state its purpose,
narrative context, learning purpose, entry condition, learner activity,
key information, exit condition, and next transition. 4. Place scenes in
an order that respects prerequisite knowledge and any pedagogically
required sequence. 5. Identify the transitions that follow successful
actions, unsuccessful attempts, or required learner decisions. 6. Define
branches only when they have a clear purpose and explicit convergence or
ending conditions. 7. Keep scene transitions understandable from the
learner's perspective and explicit enough for RT to translate.

OUTPUT A journey overview and scene sequence with scene purposes,
dependencies, entry conditions, exits, and transitions.

VALIDATION Confirm that the journey has a clear start, coherent
progression, and defined ending; that every transition has a condition;
and that all required learning tasks have a plausible place.

TRANSITION Proceed when the scene sequence is coherent and supports the
normalized objectives and content scope.

### STAGE LX-05 --- Design Learner Tasks and Interaction Contexts

PRECONDITIONS The journey and scene structure are defined.

INPUT Normalized learning context, experience direction, narrative/world
specification, scene sequence.

ACTION For every major learner task, assign a stable `TASK-##`
identifier and specify:

1.  Title and purpose.
2.  Associated `LO-##` and `LR-##` identifiers.
3.  Narrative and scene context.
4.  What the learner must accomplish and why it matters in the
    experience.
5.  Information, characters, or objects presented to the learner.
6.  Available learner choices or actions, described from the learner's
    perspective.
7.  Intended decision, response, or successful action.
8.  Expected correct response or successful action, where applicable.
9.  Plausible incorrect or unsuccessful responses, where applicable.
10. Immediate contextual feedback for each materially different
    response.
11. The resulting narrative or experience state.
12. Completion condition and subsequent event or transition.

RULE Make the task require or elicit the intended learning. A task that
can be completed without engaging the target concept does not adequately
represent that learning requirement unless the approved pedagogical
approach explicitly calls for observation or exposure.

RULE Describe the learner-visible interaction and expected outcome.
Leave detailed component architecture, UI layout, event handlers,
internal data structures, scoring implementation, and code-level logic
to RT.

RULE For tasks with no objectively correct answer, define acceptable
response characteristics or the intended reflective/creative outcome
instead of inventing a single correct answer.

DECISION If the task requires content or an answer not supplied by the
pedagogical plan, use only a clearly supported inference within the
approved scope. If the missing content materially affects correctness or
depth, request clarification or escalate to Pedagogy.

OUTPUT A complete set of task and interaction specifications linked to
scenes and learning requirements.

VALIDATION Confirm that each task has a purpose, learner action,
expected response or outcome, feedback, state consequence, completion
condition, and transition when applicable.

TRANSITION Proceed when all major tasks are explicit enough for
learner-facing specification and downstream translation.

### STAGE LX-06 --- Define Learner-Facing Language and Communication

PRECONDITIONS The scene and task specifications identify what the
learner needs to understand and do.

INPUT Audience profile, learning context, narrative, scenes, tasks,
applicable safety guides.

ACTION 1. Set vocabulary level, sentence complexity, tone, narrative
voice, and terminology consistency for the target audience. 2. Write
clear learner-facing instructions that state the immediate goal and the
action expected. 3. Write character dialogue and narration where they
materially support orientation, context, motivation, or learning. 4.
Define contextual hints and explanations that help the learner
understand the relevant concept without obscuring the task. 5. Write
success and unsuccessful-attempt messages that state what happened and
provide a useful next step. 6. Tie each feedback message to the action
or state that triggers it. 7. Use concrete example text when it
clarifies a critical interaction. 8. Keep terminology stable across
scenes, tasks, hints, and feedback.

RULE Make feedback specific, respectful, and useful. Explain the
relevant concept or invite a retry when that fits the approved
pedagogical approach. Do not use humiliating, threatening,
discriminatory, or needlessly punitive language.

OUTPUT A learner-facing content set organized by scene, task, and
trigger, including dialogue, narration, instructions, hints,
explanations, and feedback messages.

VALIDATION Confirm that text is understandable for the audience,
consistent with the narrative, aligned with learning goals, and
compatible with safety guidance. Confirm that every essential learner
action has sufficient instruction.

TRANSITION Proceed when the communication gives the learner enough
information to understand the experience and act meaningfully.

### STAGE LX-07 --- Define Experience States and Outcomes

PRECONDITIONS Scenes, tasks, and learner-facing content are defined.

INPUT Scene sequence, task specifications, learner-facing content.

ACTION 1. Identify meaningful learner-visible experience states,
assigning stable `STATE-##` identifiers. 2. Include applicable states
such as initial/entry, scene active, awaiting learner action, response
received, success, unsuccessful attempt, feedback shown, task complete,
scene complete, transition, and end of experience. 3. For each state,
define what the learner experiences and what condition leads into or out
of it. 4. Specify the learner-visible consequence of every meaningful
action and response. 5. Define task and scene completion conditions and
the end-of-experience condition. 6. Define retry or continuation
behavior when an attempt is unsuccessful, consistent with the approved
pedagogy. 7. Include score-based progression, persistent performance
tracking, adaptive difficulty, or reward systems only when explicitly
authorized by the approved scope.

OUTPUT An experience-state model expressed in plain language or a table,
including states, triggers/conditions, learner-visible results, and next
states.

VALIDATION Confirm that relevant states and transitions are complete,
consistent with scene/task definitions, and free of undefined dead ends.
Ensure that the model describes experience-level behavior rather than
prescribing code architecture.

TRANSITION Proceed when the learner's path through each task and scene
is clear, including relevant unsuccessful paths and the ending.

### STAGE LX-08 --- Establish Traceability and Experience Coverage

PRECONDITIONS The experience direction, scenes, tasks, content, and
states are defined.

INPUT Normalized objectives and requirements plus the complete
experience draft.

ACTION 1. Build a traceability matrix for every `LO-##` and every major
`LR-##`. 2. For each requirement, identify scene and task identifiers,
learner action or response, feedback or contextual consequence, and
expected learning contribution. 3. Mark coverage as `Covered`,
`Partially covered`, or `Not covered`. 4. Treat a requirement as
`Covered` only when the experience includes a meaningful learner-facing
representation and observable action/response appropriate to the
approved pedagogical approach. 5. Revise scenes, tasks, or feedback for
all partially covered or uncovered requirements. 6. Re-run the mapping
after revisions.

DECISION - If a requirement can be covered within the approved plan,
revise the experience and re-check it. - If covering it would require
changing the objective, scope, expected outcome, or approved genre,
escalate to Pedagogy. - If the plan explicitly requires exposure or
explanation rather than an active learner response, document that
rationale in the matrix.

OUTPUT A complete learning requirement traceability matrix and a list of
any remaining gaps.

VALIDATION Pass only when every objective and major requirement is
covered or has a clearly documented blocker requiring upstream
resolution.

TRANSITION Proceed to artifact consolidation when coverage passes or
when all remaining gaps are explicitly classified as blockers.

### STAGE LX-09 --- Produce the LX Experience Specification

PRECONDITIONS All prior stages are complete; coverage gaps have been
addressed or recorded as blockers.

INPUT Normalized context, design direction, world, journey, scenes,
tasks, content, states, traceability, assumptions, and review findings.

ACTION Consolidate the work into one complete Markdown artifact using
the exact section order in **Required Output Contract** below. Keep
identifiers consistent. Remove duplicated or contradictory definitions.
Make the artifact self-contained for the RT layer.

OUTPUT One **Learner-Experience Specification** in Markdown.

VALIDATION Confirm that every required section is present, all
referenced identifiers exist, the scene and task definitions agree
across sections, and the artifact specifies the intended learner
experience without requiring RT to invent missing experience decisions.

TRANSITION Proceed to LX-10.

### STAGE LX-10 --- Perform Internal Alignment and Safety Checks

PRECONDITIONS A complete draft of the LX Experience Specification
exists.

INPUT Completed draft, normalized pedagogical context, applicable safety
guides, project scope constraints.

ACTION --- ALIGNMENT Check: 1. Learning objectives and expected
outcomes. 2. Audience and language complexity. 3. Content scope,
exclusions, and required depth. 4. Approved game genre and learning
environment. 5. Narrative coherence and relevance. 6. Scene and task
completeness. 7. Consistency of instructions, expected responses, and
feedback. 8. Experience-state and transition completeness. 9.
Traceability and requirement coverage. 10. Feasibility within the
defined system scope and LX/RT boundary.

ACTION --- SAFETY 1. Identify every supplied safety guide applicable to
the experience. 2. Check narrative, characters, learner tasks, dialogue,
described visual content, and feedback against those guides. 3. Record
the relevant guide or constraint and the affected artifact section for
each issue. 4. Revise the affected content to comply. 5. If a guide is
ambiguous or contradictory, record the issue and escalate it rather than
inventing a replacement rule.

OUTPUT An alignment and safety review summary listing each check, result
(`Pass`, `Fail`, or `Blocked`), issue identifier where needed,
corrective action, and remaining blocker.

VALIDATION - `Pass`: the artifact meets the applicable criterion. -
`Fail`: the artifact does not meet the criterion and requires
revision. - `Blocked`: the criterion cannot be reliably evaluated
because a material dependency or clarification is missing.

DECISION - If any check fails and the issue can be corrected within LX
authority, revise the affected sections and repeat relevant checks. - If
a failure reveals a conflict with the approved pedagogical plan,
escalate to Pedagogy. - If a safety issue cannot be resolved under the
supplied guidance, escalate to the designated safety-control process. -
If a material user decision is required, request clarification through
the upstream conversational mechanism. - Do not mark a failed or blocked
check as passed merely to complete the artifact.

TRANSITION Complete internal review when all checks pass or outstanding
blockers are clearly documented. Internal review supports but does not
replace the larger workflow's external alignment validation, safety
validation, and user-confirmation gates.

## 6. Required Output Contract

OUTPUT Produce a single Markdown document titled **Learner-Experience
Specification**. Include the following sections in this order. Adapt
conditional content to the game, but retain every numbered section and
explain `Not applicable` when a section genuinely does not apply.

### 1. Document Metadata

Include document title, version/revision when available, source
pedagogical plan reference when available, and design status (`Draft`,
`Ready for Alignment Validation`, or `Blocked`).

### 2. Normalized Pedagogical Context

Include audience, topic and learning environment, learning goal and
objectives, learning requirements and content scope, expected outcomes,
approved genre, relevant constraints, and any material dependencies.

### 3. Experience Design Direction

Include core premise, learner role, experiential concept, genre
expression, relationship between learning goals and the experience, and
rationale for suitability.

### 4. Narrative and Game World

Include narrative overview, setting, relevant world context and rules,
characters and roles, plot, principal events, and the connection between
narrative and learning requirements.

### 5. Learner Journey and Scene Structure

Include overall journey, ordered scene sequence, scene purposes, scene
dependencies, entry and completion conditions, and transitions.

### 6. Scene Specifications

Provide one subsection per scene. For each scene include: - Scene
identifier and title. - Narrative context and learning purpose. - Entry
condition and initial state. - Characters and relevant objects. -
Information presented to the learner. - Task identifiers included in the
scene. - Learner-facing instructions. - Possible learner actions and
responses. - Feedback and narrative consequences. - Completion and
transition conditions.

### 7. Task and Interaction Specifications

Provide one subsection per task. Include task identifier and title,
learning-objective mapping, scene identifier, context and purpose, what
the learner must accomplish, presented information/objects, available
actions, expected response or outcome, incorrect/unsuccessful responses
where applicable, immediate feedback, resulting experience state,
completion conditions, and subsequent transition.

### 8. Learner-Facing Content

Organize dialogue, narration, instructions, hints, explanations, success
messages, unsuccessful-attempt messages, and other relevant displayed
text by scene/task and trigger. Label example text as learner-facing
copy rather than implementation code.

### 9. Experience State and Outcome Definitions

Use a table or structured list to define state identifier, state name,
entry trigger/condition, learner-visible experience, exit condition, and
next state. Include relevant success, unsuccessful-attempt, retry,
scene-completion, transition, and end-of-experience conditions.

### 10. Learning Requirement Traceability Matrix

Include columns for requirement identifier, learning objective or
requirement, associated scene/task identifiers, learner action or
response, feedback/contextual consequence, expected learning
contribution, and coverage status. Explain every partial, uncovered, or
blocked item.

### 11. Assumptions and Clarifications

List material assumptions made within LX authority, unresolved
ambiguities, questions awaiting clarification, decisions requiring
Pedagogy review, dependencies on supplied safety guidance, and relevant
limitations. If none, state `None identified`.

### 12. Alignment and Safety Review Summary

Summarize alignment and safety checks, results (`Pass`, `Fail`,
`Blocked`), identified issues and corrective actions, remaining
blockers, and whether the artifact is ready for external workflow gates.
Distinguish internal checks from external alignment validation, safety
validation, and user confirmation.

## 7. Escalation and Recovery Rules

ESCALATION Refer a decision to the Pedagogy stage when it materially
changes or conflicts with: - Learning objectives or their intended
meaning. - Learning requirements, included/excluded content, or required
depth. - Expected learning outcomes. - Approved game genre or
interaction format. - The pedagogical approach in a way that changes the
intended learning process.

ESCALATION Request clarification through the upstream conversational
mechanism when: - A missing requirement prevents a coherent
experience. - Two supplied constraints conflict and neither takes
precedence. - The intended audience or learning context is too ambiguous
to choose suitable language or scenarios. - A task's correctness depends
on subject-matter information not provided and not safely inferable
within scope. - A material decision cannot be made without user
preference or approval.

ESCALATION Refer unresolved safety-policy interpretation or
non-compliance to the designated safety-control process. Continue only
with unaffected work where doing so does not conceal or worsen the
blocker.

RECOVERY When a review finds a defect: 1. Identify the affected section
and linked identifiers. 2. Correct the smallest set of sections that
resolves the defect. 3. Update traceability and state/transition
definitions affected by the change. 4. Re-run relevant alignment and
safety checks. 5. Record unresolved issues accurately.

## 8. Completion Criteria

COMPLETION The LX execution is complete when: 1. The normalized learning
context preserves the approved plan. 2. The experience direction fits
the audience, objectives, environment, and approved genre. 3. Narrative,
journey, scenes, tasks, language, and experience states form a coherent
learner-facing whole. 4. Every learning objective and major requirement
is covered or has an explicit upstream blocker. 5. Stable identifiers
and cross-references are consistent. 6. All twelve output sections are
present in the required order. 7. Internal alignment and safety review
results are recorded accurately. 8. Any unresolved issue is documented
and escalated to the correct workflow gate. 9. The artifact leaves
implementation-level translation to RT.

FINAL RULE Deliver the **Learner-Experience Specification** as the
complete Markdown artifact. Do not substitute a conceptual explanation
of the design process for the artifact. State whether the specification
is `Ready for Alignment Validation` or `Blocked`, based on the recorded
checks and outstanding blockers.

The controlling architectural principle is:

**The LX layer defines the experience the learner should have; the RT
layer translates that experience into requirements the system can
implement.**
