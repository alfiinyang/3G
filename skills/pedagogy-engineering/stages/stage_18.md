# Stage 18: Learning Plan Assembly & Static Schema

Assemble the synthesized pedagogical analysis into the final, standardized deliverable for the game designer.

---

## 1. The Static Output Schema Rule

> [!CAUTION]
> **Strict Structural Invariance**:
> The final Learning Plan **MUST** use the exact 22 top-level sections (A through V) listed below.
> Sections **must not be reordered, renamed, combined, or omitted**.

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

---

## 2. Detailed Field Specifications for Sections A–V

### A. Learning Plan Metadata
- Title, version, subject domain, intended audience, authoring context, document status, assumptions, and constraints summary.

### B. Audience and Context
- Audience demographic profile, reading/educational level, prior knowledge & misconceptions, learning environment (physical/digital), learning context, institutional constraints.

### C. Learning Problem
- Current learner state, target learner state, identified cognitive/practical gap, and standard Learning Problem Statement.

### D. Learning Goal
- Primary learning goal (learner-centered capability), supporting goals (if essential), and pedagogical rationale.

### E. Learning Objectives
- Enumeration of all `LO-xx` items with syntax: *Learner + measurable action + target knowledge/skill + condition*. Target type, prerequisites, and alignment.

### F. Knowledge and Skill Structure
- Declarative, Conceptual, Procedural, and Strategic knowledge breakdowns, each mapped to specific `LO-xx`.

### G. Content Scope
- Core content, Supporting content, Optional/Extension content, Prerequisite content, and Excluded content (with justification).

### H. Depth and Complexity
- Cognitive depth level, complexity level, independence expectations, and acceptable performance conditions per objective.

### I. Learning Progression
- Staged developmental sequence (Stage I Foundations $\to$ ... $\to$ Independent Mastery), prerequisites, milestones, and Mermaid dependency graph.

### J. Learning Scenario
- Operational situation, functional learner role, authentic problem, required knowledge/skill, target action, and meaningful consequences.

### K. Learning Activities
- Complete set of 10-point activity specifications (`ACT-xx`) addressing all objectives.

### L. Scaffolding
- Initial support, guided support, reduced support, independent execution, and explicit support-removal/fading triggers.

### M. Feedback Requirements
- Correctness, explanatory, consequence, corrective guidance, strategic, and progress feedback specifications mapped to activities.

### N. Evidence of Learning
- Observable evidence, target performance, success criteria, and assessment conditions mapped to every objective.

### O. Transfer Requirements
- Transfer expectations (near/far), novel application contexts, transfer tasks, and evidence of generalization.

### P. Pedagogical Approach
- Selected instructional framework(s) (e.g. deliberate practice, inquiry, mastery), defensible rationale, and instructional implications.

### Q. Game-Design Requirements
- Functional capability requirements (`GDR-xx`): interaction requirements, challenge characteristics, feedback behaviors, progression gating, and practice opportunities.

### R. Game-Form Requirements
- Interaction model analysis, candidate game forms evaluated, recommended game form with pedagogical justification, and essential mechanical characteristics.

### S. Game Designer Handoff
- Summary of learning requirements, non-negotiable pedagogical mandates, flexible design zones, design constraints, and open questions delegated to designer.

### T. Traceability Matrix
- Exhaustive cross-reference table ensuring end-to-end alignment:
  $$\mathbf{Goal} \longrightarrow \mathbf{Objective\ (LO)} \longrightarrow \mathbf{Content} \longrightarrow \mathbf{Activity\ (ACT)} \longrightarrow \mathbf{Evidence} \longrightarrow \mathbf{Game\ Req\ (GDR)}$$
  *Rule*: Every single LO must appear. Every GDR must trace back to pedagogy.

### U. Assumptions and Design Decisions
- Clear separation of: (1) User-provided information, (2) Agent-derived decisions, (3) Material assumptions and their implications, (4) Unresolved uncertainties.

### V. Pedagogical Validation
- Quality checklist results confirming all 40 criteria from Stage 19 have been met.
