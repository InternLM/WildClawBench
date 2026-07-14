# Golden Trajectory Final Answer (GTFA)

**Task**: `matt_garcia_research_methods_problem_set_01`
**Use**: Evaluator reference only. NOT agent-visible. Never place in `data/`.

---

## Authoritative Source Resolution

1. **Classroom announcements are authoritative over the printed PDF** (prompt rule).
   - `ann_ps4_errata_n36`: Problem 3(b) sample size is **36**, not the printed 30.
   - `ann_ps4_errata_p5_twotailed`: Problem 5 is **two-tailed**, not the printed one-tailed instruction; the p-value is defined as the probability of the data given the null, not the probability the null is true.
2. **Grace's note overrides her own transcription** for Problem 1(c): the second value is **37** (her work page shows the miscopied 27); the photographed textbook Table 8.2 confirms 23, 37, 19, 31, 22, 18, 24, 29.
3. **Ignore as sources of truth**: Brianna's Instagram reel (claims the leading question alone suffices for Problem 4), TA_Marcus's YouTube comment (claims n=30 stays in the test formula), Grace's old Pinterest AP-Stats board.
4. **Due date**: Friday, June 5, 2026 (Classroom; PDF agrees).

---

## Correct Solutions (the worked solutions document must contain)

### Problem 1

| Part | Correct answer | Grace's error |
|---|---|---|
| (a) | Mean = (12+15+11+14+13)/5 = 65/5 = **13.00** minutes | correct |
| (b) | Sample SD: squared deviations 1, 4, 4, 1, 0; sum 10; 10/(5-1) = 2.5; sqrt(2.5) = **1.58** | used population formula: sqrt(10/5) = 1.41 |
| (c) | Corrected textbook dataset 23, **37**, 19, 31, 22, 18, 24, 29 (use 37, the value Grace flagged; not her miscopied 27): Mean = 203/8 = **25.38**; Sample SD = sqrt(293.875/7) = **6.48** | used 27 and the population formula: mean 24.13, SD 4.31 |

### Problem 2

| Part | Correct answer | Grace's error |
|---|---|---|
| (a) | H0: mu1 = mu2; H1: mu1 != mu2 (**two-tailed**, because the question asks whether screen-time DIFFERS) | wrote one-tailed mu1 > mu2 |
| (b) | Independent-samples t-test | correct |

### Problem 3

| Part | Correct answer | Grace's error |
|---|---|---|
| (a) | One sentence: "We are 95% confident that the interval 4.2 to 5.8 hours captures the true mean; in repeated sampling, 95% of intervals constructed this way would contain it." The CI is a statement about the procedure's long-run behavior, NOT a 95% probability that the fixed true mean lies in this particular interval | used the probability-about-the-true-mean wording |
| (b) | Per errata, n = **36** (printed 30 is a typo): SE = 1.8 / sqrt(36) = **0.30**; t = (5.0 - 4.5) / 0.30 = **1.67**. Trap values if the superseded n=30 is used: SE 0.33, t 1.52 | did not attempt |

### Problem 4

BOTH flaws required: (1) **leading question** ("Don't you think the dining hall food is terrible?"), and (2) **selection bias / non-representative sampling** (recruiting only from the "Dining Hall Lovers" Facebook group).
Grace's error: named only the leading question.

### Problem 5

- Sentence 1 (p-value): p = 0.013 is the probability of obtaining a test statistic **at least as extreme as t(28) = 2.65 IF the null hypothesis is true**. It is NOT the probability that the null hypothesis is true (Grace's definition).
- Sentence 2 (conclusion): under the **two-tailed** reading required by the errata (the printed one-tailed instruction is withdrawn), since 0.013 < 0.05, **reject H0**.

---

## Deliverables

1. **Worked solutions document**: one labeled section per problem, each in the professor's four-part structure (restatement, worked steps, labeled final-answer line, plain-language interpretation), values as above, two-decimal rounding.
2. **Error-analysis CSV**: one row per problem. P1: population-formula SD (and the 1(c) miscopy of 37 as 27); P2: one-tailed H1; P3: probability-style CI interpretation in (a), (b) not attempted; P4: only the leading-question flaw named; P5: p-value stated as probability the null is true.
3. **Chart image**: per-problem visualization distinguishing components Grace got right from those she got wrong.
4. **Submission**: attach the worked solutions document to `sub_grace_ps4` (assignment `cw_problemset4_2026`, course `rm305_s26`) and turn it in. No mutations to any other Classroom resource or to YouTube, Instagram, Pinterest, or Spotify.

---

## Known Failure Modes (negative criteria anchors)

- Using n=30 in Problem 3(b) (printed PDF / TA comment trap).
- One-tailed conclusion for Problem 5 (printed PDF trap).
- p-value described as probability the null is true (Grace's error echoed).
- Adopting Brianna's single-flaw reasoning for Problem 4.
- Using 27 instead of the flagged 37 in Problem 1(c).
- Population formula for sample SD.
- Inventing handwritten steps Grace never wrote.
- Submitting to the wrong course/assignment.
