# Stage 2: Learning Problem Diagnosis

Determine the actual learning problem by diagnosing the deficit between the learner's current state and their target state.

---

## 1. The Core Diagnostic Questions

The agent must answer three questions:

1. **Current Learner State**: *What does the learner currently know, do, or struggle with?*
2. **Target Learner State**: *What should the learner know or be able to execute afterward?*
3. **The Pedagogical Gap**: *What exact capability deficit, misconception, procedural flaw, or cognitive gap separates these two states?*

---

## 2. Topic vs. Learning Problem

> [!CAUTION]
> **Strict Prohibition**: A learning problem **must never** be reduced to the name of a topic.
> - *Invalid*: "Teach fractions", "Explain Ohm's Law", "Cover Python functions".
> - *Valid*: Inability to decompose non-integer parts, difficulty troubleshooting open-circuit faults, failure to structure reusable logic with parameter passing.

Target deficits typically reflect an inability to:
- **Recognize** patterns or discrepancies;
- **Explain** underlying causal mechanisms;
- **Compare** and contrast competing alternatives;
- **Calculate** or estimate values accurately;
- **Apply** rules, principles, or procedures under variable conditions;
- **Diagnose** errors, malfunctions, or edge cases;
- **Construct** valid arguments, code, circuits, or models;
- **Evaluate** options against formal criteria;
- **Transfer** knowledge to novel or complex situations.

---

## 3. Required Output: Problem Statement Template

The diagnostic output must include current state, desired state, gap analysis, and conclude with the mandatory **Learning Problem Statement**:

```markdown
### 2. Learning Problem Diagnosis
- **Current Learner State**: [Prior knowledge, misconceptions, baseline limitations]
- **Target Learner State**: [Proficient capabilities, accurate conceptual models, fluent behaviors]
- **Identified Gap**: [Exact nature of cognitive/practical deficit]

#### Learning Problem Statement
> **Given** [learner current state and prior background], **the learner needs to develop** [target capability or cognitive mechanism] **so that they can** [target performance] **in** [relevant context or operating environment].
```
