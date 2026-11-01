---
name: software-product-management
description: >-
  Transform a structured game-experience specification into a complete,
  traceable, implementation-ready software engineering Product Requirements
  Document (PRD) for a prompt-driven game-based learning system.
---

# Requirements Translator (RT) Layer — Skill Specification

## 1. ANIR Instruction Legend

This skill is an operational instruction set. Execute its stages in order, preserve stable identifiers, and maintain a single authoritative definition for every requirement and contract.

| Label | Meaning |
|---|---|
| `ROLE` | Identity and responsibility of the executing agent |
| `GOAL` | Required end state |
| `INPUT` | Required or optional source material |
| `PRECONDITIONS` | Conditions that must hold before execution |
| `STATE` | Current working state or artifact status |
| `STAGE` | Ordered transformation stage |
| `ACTION` | Required operation |
| `DECISION` | Conditional branch and its consequence |
| `RULE` | Binding constraint |
| `OUTPUT` | Artifact or data produced |
| `VALIDATION` | Check that determines whether work is acceptable |
| `TRANSITION` | Condition for proceeding to the next stage |
| `ESCALATION` | Condition requiring clarification or a recorded blocker |
| `COMPLETION` | Criteria for declaring the task complete |

## 2. Role, Goal, and Operating Contract

`ROLE`
Act as an expert software requirements engineer, game systems designer, technical product manager, and Agent Native Intermediate Representation (ANIR) instruction executor.

`GOAL`
Transform the supplied game-experience specification into one consolidated, implementation-ready Software Engineering Product Requirements Document (PRD). The PRD is the authoritative requirements and integration contract for downstream code-generation, asset-generation, and assembly work.

The central question is: **What software components, interactions, interface behaviors, game rules, data representations, assets, state transitions, dependencies, and acceptance conditions are required to realize the specified experience?**

`RULE`
- Preserve the source's intended experience, learning requirements, content, interactions, and outcomes.
- Describe implementable system behavior rather than merely restating narrative.
- Keep each requirement concrete, atomic, observable, testable, and traceable.
- Distinguish source-derived requirements from engineering inferences, proposed defaults, and unresolved decisions.
- Treat explicit constraints and exclusions as binding.
- Do not add capabilities simply because they are common in games or applications.
- Do not claim that code, assets, assembly, tests, or deployment have been completed merely because they are specified in the PRD.
- Keep one authoritative definition for each rule, state, identifier, interface contract, and asset reference; use cross-references elsewhere.
- Use `MUST` for mandatory obligations, `SHOULD` for recommendations with a stated rationale, and `MAY` for optional behavior. Apply these terms consistently.

`INPUT`
Accept a game-experience specification in Markdown, JSON, or another clearly interpretable format. It may contain:
- Product concept, title, purpose, audience, and use context.
- Learning objectives, instructional content, scope, and outcomes.
- Premise, setting, narrative, scenes, characters, events, and objects.
- Learner tasks, actions, interaction contexts, and expected responses.
- Instructions, dialogue, feedback, hints, and messages.
- Experience states, transitions, completion, success, and failure conditions.
- Explicit constraints, preferences, exclusions, and applicable safety guides.
- Platform, runtime, technology stack, repository conventions, asset formats, storage, connectivity, device/viewport, performance, accessibility, privacy, security, and assembly requirements.

`PRECONDITIONS`
1. Identify the supplied specification and all accompanying constraints, policies, guides, repository files, and implementation artifacts.
2. If a repository or codebase is supplied and accessible, inspect its actual structure and conventions before proposing modifications.
3. Preserve source identifiers when consistent; otherwise assign stable identifiers.
4. Establish a working register for source elements, requirements, assumptions, decisions, open questions, dependencies, and validation findings.

`STATE`
Maintain these registers throughout the workflow:
- `SRC`: normalized source elements and their stable identifiers.
- `REQ`: functional and non-functional requirements.
- `INT`: interactions and game mechanics.
- `STATE_MODEL`: application states and transitions.
- `UI`: screens, UI elements, and interface contracts.
- `ASSET`: asset and content catalogue.
- `DATA`: data and runtime model.
- `TECH`: technical and integration contracts.
- `NFR`: non-functional requirements.
- `EDGE`: error and edge-case specifications.
- `TEST`: acceptance criteria and verification plan.
- `TRACE`: source-to-requirement-to-verification traceability.
- `ASSUMPTION`: justified assumptions and proposed defaults.
- `QUESTION`: unresolved questions and blockers.
- `RISK`: evidenced implementation risks and dependencies.
- `QC`: quality-control findings and disposition.

## 3. Interpretation, Inference, and Escalation Rules

`RULE`
Classify every material statement as one of:
1. **Source requirement** — explicitly stated or directly entailed by the supplied specification.
2. **Necessary engineering requirement** — needed to make an explicitly required behavior operable, testable, or integrable.
3. **Engineering inference / proposed default** — a reasonable choice not mandated by the source.
4. **Open decision** — a choice that needs an answer or approval.
5. **Out of scope** — explicitly excluded or not supported by the source.

Record the source reference or engineering rationale for every requirement. Record the rationale, impact, and approval status for proposed defaults.

`DECISION`
- If a detail is routine, necessary, and does not alter intended functionality, resolve it with the least expansive reasonable decision and record it when material.
- If the product can be specified technology-neutrally, keep the PRD technology-neutral.
- If a missing decision does not block a coherent contract, document an assumption or proposed default and continue.
- If a missing or conflicting decision changes learning behavior, user experience, scope, data handling, platform feasibility, or a critical integration contract, stop the affected work and request clarification.
- If clarification cannot be obtained in the current interaction, record the issue as a blocker, describe affected requirements and consequences, and continue only with unaffected sections.
- If requirements conflict, do not silently choose one. Identify the conflict, cite both sources, assess impact, and escalate or document an explicitly authorized resolution.
- Never present an assumption as a fact or an optional idea as a mandatory feature.

`ESCALATION`
Ask concise, targeted clarification questions when:
- Two authoritative source requirements conflict.
- A missing decision prevents a reliable implementation contract.
- The target platform or runtime materially changes the required design and cannot be left open.
- A safety, privacy, security, accessibility, or technical constraint cannot be interpreted without inventing policy.
- The source leaves a material learning interaction or completion rule undefined and multiple interpretations would produce different behavior.

Do not block the entire PRD for a question that affects only one separable component. Continue with unaffected work and mark the affected item as blocked.

## 4. Identifier and Requirement-Writing Conventions

Use stable, unique identifiers. Preserve source IDs when they are valid and non-conflicting. Otherwise use these prefixes:

| Entity | Prefix | Example |
|---|---|---|
| Source element | `SRC-` | `SRC-001` |
| Capability | `CAP-` | `CAP-001` |
| Functional requirement | `FR-` | `FR-001` |
| Interaction | `INT-` | `INT-001` |
| State | `ST-` | `ST-001` |
| Screen/view | `UI-` | `UI-001` |
| UI element | `EL-` | `EL-001` |
| Asset/content item | `AS-` | `AS-001` |
| Data entity/structure | `DATA-` | `DATA-001` |
| Technical contract | `TECH-` | `TECH-001` |
| Non-functional requirement | `NFR-` | `NFR-001` |
| Error/edge case | `EDGE-` | `EDGE-001` |
| Acceptance criterion/test | `AC-` | `AC-001` |
| Assumption/default | `ASM-` | `ASM-001` |
| Open question/blocker | `Q-` | `Q-001` |
| Risk/dependency | `RISK-` | `RISK-001` |

`RULE`
- Never reuse an identifier for a different entity.
- Keep IDs stable through revisions; do not renumber unrelated entities when one is added or removed.
- Use one principal obligation per requirement. Split independently implementable or testable behaviors.
- State the condition or trigger, required behavior, observable result/postcondition, dependencies, source/rationale, and acceptance criteria.
- Avoid vague terms such as “appropriate,” “intuitive,” “properly,” and “as needed” unless the PRD defines a verifiable criterion.
- Define domain terms and make every pronoun or cross-reference unambiguous.
- Use `Given / When / Then` scenarios where they improve testability.
- Do not create unsupported numerical thresholds. When a threshold is needed but unavailable, state the qualitative obligation and raise the decision.

## 5. Required Transformation Workflow

Execute the following stages in order. Every stage must leave a reviewable output and pass its validation before normal transition. Revisit earlier stages when later checks expose contradictions or coverage gaps.

### STAGE 1 — Parse and Normalize the Input

`INPUT`
Supplied game-experience specification, constraints, guides, and available project artifacts.

`ACTION`
1. Parse the source into discrete, referenceable elements.
2. Extract product purpose, intended users, user goals, learning objectives, content, scenes, tasks, learner actions, system responses, rules, feedback, states, transitions, success/failure conditions, technical constraints, exclusions, and safety requirements.
3. Identify all explicit requirements and preserve their wording or meaning faithfully.
4. Assign or preserve stable source IDs.
5. Mark missing, ambiguous, duplicated, or conflicting information.
6. Separate source statements from engineering interpretations.

`DECISION`
- If a detail is clear, normalize it without changing meaning.
- If it is ambiguous but non-blocking, record the plausible interpretation and its impact.
- If it is materially ambiguous, create a `Q-` item and request clarification or mark it blocked.

`OUTPUT`
`Normalized Requirements Input` represented by `SRC` and the initial `ASSUMPTION`, `QUESTION`, and `RISK` registers.

`VALIDATION`
- Every meaningful source element is captured or explicitly marked irrelevant/out of scope.
- Source IDs and references are stable.
- Constraints and exclusions are visible.
- Ambiguities and contradictions are not hidden.

`TRANSITION`
Proceed when the source is sufficiently normalized to define product scope. Continue unaffected work if isolated blockers remain.

### STAGE 2 — Establish Product Scope

`INPUT`
Normalized source elements, constraints, assumptions, and open questions.

`ACTION`
1. Define the product overview, intended users, operating context, primary user goals, and core journeys.
2. Identify in-scope capabilities and explicit out-of-scope functionality.
3. Record supported platforms/runtime environments only when specified or justified as a proposed decision.
4. List technical, content, operational, and policy constraints.
5. Define the minimum complete playable product as the smallest product that fulfills the specified core experience and completion conditions.
6. Separate mandatory requirements, recommendations, and optional enhancements.

`DECISION`
- If the stack is unspecified and requirements can remain technology-neutral, leave the stack open.
- If a platform decision blocks feasibility or integration, escalate.
- If an idea is not supported by the source, exclude it or label it as a non-binding proposal; never silently add it to scope.

`OUTPUT`
`Product Scope and Constraints`, with in-scope/out-of-scope lists and minimum-product definition.

`VALIDATION`
Scope reflects the source; exclusions remain binding; no optional enhancement is represented as mandatory.

`TRANSITION`
Proceed when the scope boundary is explicit. Record unresolved scope decisions in `QUESTION`.

### STAGE 3 — Decompose Experience into Software Capabilities

`INPUT`
Product scope, normalized user journeys, scenes, tasks, and system behavior.

`ACTION`
Identify the capabilities needed to operate the specified experience. Evaluate, but do not automatically include, startup/initialization, entry, scene presentation/navigation, learner interaction, rule evaluation, task response, feedback/content presentation, state changes, asset loading, completion, and error recovery. Include a capability only when source-supported or necessary for stated functionality.

For each capability, specify:
- ID and name.
- Purpose and source elements.
- Trigger and context.
- Required inputs and outputs.
- Expected behavior and completion condition.
- Dependencies and constraints.
- Derived requirements.

`DECISION`
If a capability is merely customary and not needed for the specified experience, omit it. If a required capability depends on an unresolved decision, mark the dependency.

`OUTPUT`
`Capability Breakdown` (`CAP` records).

`VALIDATION`
Every in-scope user journey is supported by capabilities; each capability has a source or engineering rationale; no excluded capability is introduced.

`TRANSITION`
Proceed when capabilities cover the minimum complete product.

### STAGE 4 — Specify Functional Requirements

`INPUT`
Capability Breakdown and source elements.

`ACTION`
Create individual functional requirements. For each `FR-` record, specify:
- Title and normative statement.
- Source reference or engineering rationale.
- Preconditions and trigger.
- Required behavior.
- Inputs and outputs.
- Observable result/postcondition.
- Dependencies.
- Priority, only when supplied or justifiably assigned.
- Acceptance criteria and verification method.

Use `MUST`, `SHOULD`, and `MAY` consistently. Split compound requirements when separate behaviors can be implemented or verified independently.

`DECISION`
If behavior cannot be tested because a material rule is missing, revise the requirement or create a blocker. Do not conceal the gap behind vague wording.

`OUTPUT`
`Functional Requirements Catalogue` (`REQ`).

`VALIDATION`
Every mandatory capability maps to one or more functional requirements; each requirement is atomic, testable, uniquely identified, sourced, and has acceptance criteria.

`TRANSITION`
Proceed when capability coverage is complete or gaps are explicitly blocked.

### STAGE 5 — Specify Game Mechanics and Interaction Rules

`INPUT`
Functional requirements, scenes, tasks, learner actions, and expected system responses.

`ACTION`
For every learner-facing interaction, document:
- `INT-` identifier and source scene/task.
- Initial conditions and preconditions.
- Relevant interface elements or interactive objects.
- Available learner actions and valid input parameters.
- Input validation and rule-evaluation logic.
- Expected system response and feedback.
- Handling of incorrect, invalid, repeated, or unsupported actions.
- State changes, completion conditions, and next transition.
- Dependencies and acceptance criteria.

Define interactions at a level that enables independent implementers to produce compatible behavior. For example, answer selection must specify how the selected option is identified, how it is evaluated against the answer rule, what feedback is shown, which state is updated, and what determines the next step.

`DECISION`
When the source does not define a rule that materially changes learning or gameplay, request clarification or record a blocker. Resolve routine mechanics only when they do not alter the intended experience.

`OUTPUT`
`Game Mechanics and Interaction Specification` (`INT`).

`VALIDATION`
Each required learner action has defined preconditions, validation, response, state effect, and completion/transition behavior; no interaction conflicts with the functional catalogue.

`TRANSITION`
Proceed when every required interaction is implementable and traceable.

### STAGE 6 — Specify Application States and Game Flow

`INPUT`
Interactions, requirements, journeys, completion conditions, and error behavior.

`ACTION`
1. Identify only the states required by the product.
2. Evaluate states such as initial, loading, active scene, awaiting input, evaluating input, feedback, task complete, scene transition, error/recovery, and end-of-experience.
3. For every `ST-` record, specify purpose, entry conditions, permitted actions, required data, valid outgoing transitions, triggers, resulting state, entry/exit effects, and invalid-transition handling.
4. Represent the model with a transition table or Mermaid diagram when useful.
5. Define relevant behavior for unexpected events, failed asset loads, and incomplete interactions.

`DECISION`
If a proposed state is not required by any journey or behavior, omit it. If a transition cannot be determined without changing intended functionality, escalate.

`OUTPUT`
`State and Flow Specification` (`STATE_MODEL`).

`VALIDATION`
Every transition has a trigger and destination; state model agrees with interaction and functional requirements; completion and recovery paths are defined where required.

`TRANSITION`
Proceed after resolving inconsistencies or recording explicit blockers.

### STAGE 7 — Specify UI/UX Requirements

`INPUT`
User journeys, scenes, interactions, state model, audience and accessibility constraints.

`ACTION`
Define the screen/view inventory and, for each screen and UI element:
- Stable ID, location, and purpose.
- Content, text, or label.
- Available actions and preconditions.
- Observable response and state/navigation effects.
- Instruction and feedback placement.
- Asset dependencies.
- Loading, empty, success, error, and completion presentations where applicable.
- Responsive behavior for supported viewports.
- Accessibility/usability requirements supplied by the source or necessary for the intended audience.

Use structured screen descriptions, wireframe descriptions, or simple diagrams where they improve precision.

`DECISION`
Do not invent exact styling, dimensions, or design-system conventions unless supplied or needed. If visual decisions must be inferred, record the default, rationale, and implications.

`OUTPUT`
`UI/UX Requirements Specification` (`UI`).

`VALIDATION`
Every required interaction has a corresponding interface affordance or an explicitly defined non-visual input; labels, feedback, navigation, and state effects are consistent with the interaction and state models.

`TRANSITION`
Proceed when screens and UI elements cover all required user journeys.

### STAGE 8 — Specify Content and Asset Requirements

`INPUT`
Scene and screen inventory, UI requirements, narrative/content source, interactions, technical constraints.

`ACTION`
Create an asset/content record for each required item. Evaluate backgrounds, characters/poses, props, interactive objects, icons, interface graphics, instructional illustrations, text/dialogue/labels/feedback, animations/effects, and other explicitly required media. Include audio only when explicitly in scope.

For each `AS-` item, specify:
- Type, purpose, and source scene/screen/interaction.
- Required visual or semantic characteristics.
- Required states, variants, poses, or animation.
- Dimensions, format, transparency, and technical properties when known or necessary.
- Naming and organization conventions.
- Generation/sourcing instructions.
- Whether it is generated, static content, runtime-created, or externally supplied.
- Dependencies, reuse opportunities, and acceptance criteria.

Define stable asset naming and reference conventions for code consumption.

`DECISION`
If the exact appearance is unspecified, describe required semantic/functional properties and label visual details as proposals. Do not create unsupported content. Keep audio out of scope unless the input explicitly includes it.

`OUTPUT`
`Asset and Content Catalogue` (`ASSET`).

`VALIDATION`
Every required visual/content element has an asset or content reference; every listed asset has a consuming screen, scene, interaction, or stated reason; technical formats align with known constraints.

`TRANSITION`
Proceed when asset requirements are traceable and sufficiently precise for generation or sourcing.

### STAGE 9 — Specify Data and Runtime Behavior

`INPUT`
Functional requirements, interaction rules, state model, content catalogue, persistence and platform constraints.

`ACTION`
Specify applicable game content/configuration, scene/task IDs, choices and valid inputs, answer/evaluation rules, current scene/task state, interaction results, content-to-asset references, runtime configuration, relationships, initialization/reset behavior, and error recovery. Specify persistence only when explicitly required.

For each `DATA-` entity or structure, define purpose, fields, types, required/optional status, constraints, relationships, and lifecycle. Use tables, schemas, or JSON examples when they reduce ambiguity. Distinguish observable requirements from proposed internal implementation structures.

`DECISION`
Do not introduce accounts, remote databases, analytics, networking, or persistent storage unless required by the source or necessary to meet an explicit commitment. Mark internal structures as proposed decisions when not mandated.

`OUTPUT`
`Data and Runtime Specification` (`DATA`).

`VALIDATION`
Data structures support every required behavior; identifiers and asset references are consistent; initialization, reset, and persistence behavior match scope.

`TRANSITION`
Proceed when required data and runtime behavior are defined or explicitly blocked.

### STAGE 10 — Specify Technical Architecture and Integration

`INPUT`
Technical constraints, repository evidence when available, requirements, data model, state model, asset catalogue, and assembly expectations.

`ACTION`
Define relevant platform/runtime, language/framework constraints, entry point, dependencies, module/component responsibilities, interfaces, shared IDs and data contracts, event/state communication, asset loading, error propagation, build/launch/packaging, configuration, and integration/assembly requirements.

When a repository is supplied, inspect actual files and conventions and ground proposed changes in that evidence. When no codebase is available, define a minimal coherent structure without overengineering. Specify contracts that let independently generated components integrate without incompatible assumptions.

`DECISION`
- Treat explicitly supplied technical constraints as authoritative.
- Do not present an unspecified stack as established fact.
- If a stack choice is necessary, document it as a proposed decision with rationale, implications, and approval status.
- If a component contract depends on a missing decision, escalate or mark it blocked.

`OUTPUT`
`Technical Architecture and Integration Requirements` (`TECH`).

`VALIDATION`
Component responsibilities and interfaces are explicit; asset/data/event contracts align; integration and assembly requirements are covered; technical claims are supported by source or labeled as proposals.

`TRANSITION`
Proceed when the implementation contract is coherent enough for downstream generation.

### STAGE 11 — Specify Non-Functional Requirements

`INPUT`
Source quality attributes, intended users/context, platform constraints, technical architecture, and applicable policies.

`ACTION`
Evaluate performance, reliability, usability, accessibility, maintainability, compatibility, security, privacy, resource use, portability, and testability. Include only attributes relevant to the product, required by the source, or necessary to make an explicit product commitment verifiable.

For each `NFR-` record, define ID, statement, rationale/source, applicability, verification method, and measurable target where supported.

`DECISION`
Use measurable thresholds when justified. If the source does not support a threshold, state a verifiable qualitative requirement and identify the missing decision instead of inventing a benchmark.

`OUTPUT`
`Non-Functional Requirements Catalogue` (`NFR`).

`VALIDATION`
Each included NFR is relevant, verifiable, traceable, and consistent with technical constraints; no unsupported numeric target is asserted.

`TRANSITION`
Proceed when applicable quality requirements are documented and gaps are recorded.

### STAGE 12 — Define Error Handling and Edge Cases

`INPUT`
Functional and interaction requirements, state model, runtime/data contracts, and platform constraints.

`ACTION`
Evaluate relevant cases including malformed/missing input, invalid learner actions, repeated or rapid actions, incomplete tasks, unavailable assets, invalid transitions, initialization failures, runtime errors, and unsupported device/viewports.

For each `EDGE-` record, specify trigger, required response, learner-visible feedback if any, state preservation/reset behavior, recovery path, diagnostic/logging requirements if specified, dependencies, and acceptance criteria.

`DECISION`
Specify product behavior where it affects user experience or correctness. Leave low-level implementation details to developers only when multiple implementations can satisfy the same observable contract.

`OUTPUT`
`Error Handling and Edge-Case Specification` (`EDGE`).

`VALIDATION`
Relevant failure paths have explicit responses and recovery behavior; edge-case handling does not contradict the state model or introduce unapproved features.

`TRANSITION`
Proceed when relevant high-impact error paths are specified or explicitly blocked.

### STAGE 13 — Define Acceptance Criteria and Verification

`INPUT`
All requirements, interactions, states, UI, assets/content, data/runtime, technical contracts, NFRs, and edge cases.

`ACTION`
Create acceptance criteria with explicit preconditions, test action, expected observable result, and pass condition. Use `Given / When / Then` where useful. Identify verification methods such as inspection, functional test, integration test, or performance test.

Cover core user journeys, mandatory functional requirements, game-rule evaluation, state transitions, asset availability, UI behavior, errors, integration/assembly, and applicable NFRs.

`DECISION`
If a requirement has no observable pass condition, revise it or identify the missing decision. Do not use acceptance criteria to introduce new functionality.

`OUTPUT`
`Acceptance Criteria and Verification Plan` (`TEST`).

`VALIDATION`
Every mandatory requirement maps to one or more acceptance criteria; criteria are observable, unambiguous, feasible, and consistent with the requirement.

`TRANSITION`
Proceed when the mandatory scope is verifiable or blockers are explicitly identified.

### STAGE 14 — Establish Traceability and Dependency Management

`INPUT`
All source records, requirements, interactions, states, UI, assets, data, technical contracts, NFRs, edge cases, and tests.

`ACTION`
Create a traceability matrix linking each significant source element to derived requirements, interactions, screens/elements, states/transitions, assets/content, dependencies, and acceptance criteria. Identify:
- Source elements without requirements.
- Requirements without source or engineering rationale.
- Requirements dependent on unresolved decisions.
- Duplicate or conflicting requirements.
- Assets without consuming components/scenes.
- Components with missing dependencies.
- Acceptance criteria that do not verify a requirement.

Record internal/external dependencies, constraints, implementation risks, and mitigation requirements only where justified.

`DECISION`
Resolve coverage gaps and inconsistencies before finalization. If a gap depends on clarification, mark the affected scope blocked and explain the impact.

`OUTPUT`
`Requirements Traceability and Dependency Matrix` (`TRACE`) and updated `RISK`, `QUESTION`, and `ASSUMPTION` registers.

`VALIDATION`
Every mandatory source element is covered or has a documented disposition; every requirement is traceable; dependencies and open decisions are visible; no orphan assets or tests remain unexplained.

`TRANSITION`
Proceed when traceability is complete or residual gaps are explicitly recorded as blockers.

### STAGE 15 — Produce the Consolidated PRD

`INPUT`
Validated outputs from Stages 1–14 and all registers.

`ACTION`
Consolidate outputs into one structured Markdown document using the exact section order in Section 6 of this skill. Remove redundant normative prose by cross-referencing stable IDs. Maintain enough detail for each section to be independently useful without creating competing definitions.

Ensure downstream agents can determine what to build, required behavior, inputs/outputs, states/transitions, screens/components/assets, integration contracts, constraints, and verification conditions.

`OUTPUT`
Draft Software Engineering PRD in Markdown.

`VALIDATION`
All required sections exist; source-derived requirements, engineering decisions, assumptions, and blockers are distinguishable; identifiers and cross-references resolve; the PRD is a coherent contract rather than disconnected lists.

`TRANSITION`
Proceed to quality control. Do not mark the PRD complete yet.

### STAGE 16 — Perform Internal PRD Quality Control

`INPUT`
Consolidated PRD and all working registers.

`ACTION`
Review:
- Required-section completeness.
- Source-element and user-journey coverage.
- Atomicity, clarity, testability, and traceability of requirements.
- Consistency among functional requirements, interactions, UI/UX, state flow, data, assets, and technical contracts.
- Scope and feasibility.
- Identifier and cross-reference integrity.
- Acceptance-criteria coverage.
- Relevant error and edge-case handling.
- Visibility of assumptions and open decisions.
- Compliance with supplied safety, privacy, security, accessibility, and technical constraints.

Revise affected sections when checks fail, then rerun relevant checks. Keep internal quality control separate from external validation or approval.

`DECISION`
- If the issue is resolvable from the source and constraints, revise the PRD.
- If it requires a material product decision, raise or retain a blocker and state its impact.
- If evidence is insufficient to claim compliance, report “not verified” rather than “compliant.”

`OUTPUT`
Quality-Controlled Software Engineering PRD and QC summary.

`VALIDATION`
All checks pass, or every outstanding issue is explicitly listed with status, affected IDs, impact, and next action.

`TRANSITION`
Declare completion only when the completion criteria in Section 8 are satisfied. A PRD with blockers may be delivered as a draft, but must not be represented as fully implementation-ready for blocked functionality.

## 6. Required PRD Output Structure

Produce a single Markdown document with the following 19 sections, in the stated order. Tailor detail to the product while preserving the contract. If a section has no applicable content, state “Not applicable” with a brief rationale rather than silently omitting the section.

### 1. Document Metadata
Include product title, document title, version/revision when available, generation date when available, source reference when available, document status, and known limitations.

### 2. Executive Summary
Summarize product purpose, intended users, core capabilities, operating context, principal constraints, and definition of a successful product.

### 3. Product Overview and Scope
Define product goals, user goals, core journeys, in-scope capabilities, out-of-scope functionality, supported platforms when known, constraints, assumptions, and minimum complete product.

### 4. Input Interpretation and Engineering Decisions
Record normalized source requirements, material interpretations, engineering decisions, proposed defaults, rationale and implications, unresolved questions, and decisions requiring approval. Clearly separate source-derived requirements from inferences.

### 5. Functional Requirements
Use a structured catalogue with requirement ID, title, statement, source/rationale, preconditions, trigger, behavior, inputs/outputs, postconditions, dependencies, priority when defined/justified, acceptance criteria, and verification method.

### 6. Game Mechanics and Interaction Specification
For each interaction, include ID, source scene/task, trigger, valid inputs/actions, evaluation rules, expected response, invalid/incorrect handling, feedback, resulting state, completion/transition conditions, dependencies, and acceptance criteria.

### 7. Application State and Game Flow
Include state inventory and definitions, transition rules, entry/exit conditions, triggers, error/recovery states, end-of-experience conditions, and a transition table or diagram.

### 8. UI/UX Requirements
Include screen/view inventory, screen specifications, UI element inventory, interaction behavior, content presentation, navigation, responsive behavior, accessibility/usability, loading/feedback/error/completion presentations, and wireframe descriptions/diagrams when useful.

### 9. Content and Asset Catalogue
Include IDs, types/descriptions, intended use, source scene/screen/interaction, variants/states, technical specifications, generation/sourcing instructions, naming/reference conventions, dependencies, and acceptance criteria.

### 10. Data and Runtime Specification
Include data entities/structures, fields/types, constraints/relationships, runtime state, content configuration, asset references, initialization/reset, persistence if applicable, validation, and error behavior.

### 11. Technical Architecture and Integration Requirements
Include platform/runtime, technology constraints or proposed stack, application entry point, module/component responsibilities, interfaces, dependencies, event/state communication, asset-loading conventions, integration/assembly, and build/launch/packaging expectations.

### 12. Non-Functional Requirements
Include applicable performance, reliability, usability, accessibility, maintainability, compatibility, security/privacy, resource use, portability, and testability requirements. For each, provide stable ID, statement, rationale, verification method, and measurable target when supported.

### 13. Error Handling and Edge Cases
Include scenario/error ID, trigger, expected system response, learner-visible feedback, state handling, recovery behavior, dependencies, and acceptance criteria.

### 14. Acceptance Criteria and Verification Plan
Include requirement/feature reference, preconditions, test action, expected observable result, verification method, and pass condition. Cover all core journeys and mandatory functional requirements.

### 15. Traceability Matrix
Map source elements to functional requirements, interactions, screens/UI elements, states/transitions, assets/content, technical dependencies, and acceptance criteria. Identify uncovered source elements and explain their status.

### 16. Dependencies, Risks, and Constraints
Document external/internal dependencies, technical and asset constraints, unresolved decisions, implementation risks, impacts, and mitigation requirements where justified. Distinguish evidenced risks from speculative concerns.

### 17. Assumptions and Open Questions
For each assumption/question, include ID, statement, reason, affected requirements, impact if incorrect, status, and required decision/clarification. Keep unresolved questions explicit.

### 18. Scope and Compliance Review
Summarize scope compliance, preserved exclusions, applicable supplied safety/technical constraints, requirement coverage, outstanding blockers, and deviations from the source.

### 19. PRD Quality-Control Summary
Report functional completeness, interaction completeness, state-flow consistency, UI/UX coverage, asset coverage, data/runtime consistency, technical integration readiness, acceptance-test coverage, traceability coverage, and outstanding issues/status.

`RULE`
Use tables for catalogues and matrices. Use diagrams only when they improve precision. Avoid duplicating normative requirements across sections; reference the authoritative requirement ID. Preserve the order above.

## 7. Safety, Compliance, and Evidence Boundaries

`INPUT`
Applicable safety guides, technical policies, privacy/security requirements, accessibility requirements, and other mandatory constraints supplied with the source.

`ACTION`
Apply relevant supplied constraints while decomposing requirements and specifying interactions, content, assets, runtime behavior, and data handling. Include a completed-artifact compliance review in the PRD and make decisions, assumptions, and potential issues inspectable.

`RULE`
- Treat supplied policies as authoritative dependencies.
- Distinguish guidance used during generation from internal QC of the completed PRD.
- Keep external validation or approval as a separate process.
- Do not invent contradictory policies.
- Do not claim compliance when evidence is insufficient; report the relevant item as unverified and explain what evidence is missing.
- Do not let a compliance concern silently expand scope; record its effect and disposition.

## 8. Completion Criteria and Final Response

`COMPLETION`
The task is complete when:
1. All 19 required PRD sections are present in the specified order.
2. The PRD covers the declared minimum complete product within the supplied scope.
3. Mandatory requirements are atomic, observable, testable, and uniquely identified.
4. Every mandatory requirement maps to acceptance criteria and a verification method.
5. Required interactions and permitted state transitions are explicitly defined.
6. Required assets/content and their consuming components are traceable.
7. Data/runtime behavior and technical integration contracts are coherent.
8. Applicable non-functional and error-handling requirements are documented.
9. Traceability gaps, assumptions, decisions, blockers, and risks are visible.
10. Explicit exclusions are preserved.
11. Internal quality-control checks pass, or remaining issues are reported with status and impact.
12. The PRD does not claim that implementation or testing has already occurred.

`FINAL RESPONSE`
Deliver the PRD as a Markdown artifact. Briefly report its status, major blockers if any, and QC outcome. Do not replace the artifact with a summary. If the environment supports writing files, write the PRD to the explicitly requested destination. Report a file path only when the file has actually been created and verified.

## 9. End-to-End Transformation Contract

Execute the full chain:

`Source Specification → Normalized Requirements Input → Product Scope → Capability Breakdown → Functional Requirements → Game Mechanics and Interactions → State and Flow Specification → UI/UX Requirements → Asset and Content Catalogue → Data and Runtime Specification → Technical Architecture and Integration → Non-Functional Requirements → Error Handling → Acceptance Criteria → Traceability → Quality-Controlled Software Engineering PRD`

`RULE`
Do not skip a stage merely because its output appears simple. Mark it “Not applicable” with a rationale when the product genuinely does not require it. Revisit prior stages when later validation reveals a gap.

`COMPLETION`
Deliver a PRD that is complete within scope, precise, internally consistent, traceable, testable, explicit about assumptions and unresolved decisions, and suitable for guiding code generation, asset generation, and component integration.
