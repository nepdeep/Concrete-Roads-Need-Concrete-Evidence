# Independent engineering and model consistency review

Review date: 19 October 2026. Reviewer: engineering research subagent. Scope: `road-decisions-nepal/dist/index.html`, `research/engineering-options.md`, `research/cost-methodology.md`, and `models/` source/results available during this review. The frontend is being revised concurrently; findings below distinguish observed snapshot issues from model changes verified afterwards. This review does not certify a road design or market prices.

**Resolved/updated for final synthesis:** `decision-report.md` standardizes the 9 km replicated experiment, 150 mm DLC model, and months 6–15 construction / 15–36 monitoring. The final pilot budget supersedes the preliminary table below: add NPR2 million explicit transition work and its 5% design/supervision allowance, producing a subtotal of NPR428.76 million and a reserved cash total of **NPR557.17362 million (55.72 crore)**. The NPR15 million incremental research allowance is split into protocol/axle survey3 million, external QA4 million, extra trials/mobilisation4 million and monitoring4 million. The older review table remains a dated reconciliation record, not the final funding figure. Frontend implementation and final packaging are separate release checks.

## Findings requiring final reconciliation

### 1. Use one experimental design throughout — 9 km recommended

The inspected website proposes one 1 km asphalt/concrete pair in each of three environments, totaling 6 km. The engineering report proposes three 500 m matched pairs per environment, totaling 9 km. These are different experiments, costs and procurement quantities.

Use the 9 km design consistently: **3 environments × 3 matched pairs × 2 materials × 0.5 km = 9 km**, comprising **4.5 km asphalt and 4.5 km concrete**. This adds replication within each environment. With only one pair, treatment and section-specific effects are difficult to distinguish. Nine pairs remain a screening programme, not a statistically powered national lifetime experiment. Estimate baseline variance, check power and revise replication before tender. Repeated measurements of the same section are not independent roads.

The pilot mix is 50/50 for comparison. It is different from the hypothetical 10 km, 70/30 portfolio used to illustrate implementation economics. Do not apply the portfolio's 30% concrete share to the trial budget. C is the policy for choosing A/B sections, not a third trial surface.

### 2. Match all layer diagrams, quantities and costs

The inspected HTML labels the asphalt granular base **250 mm**, but the cost model uses **200 mm wet-mix macadam**. Change the drawing/label to 200 mm, unless the whole model is deliberately redesigned.

The initial model used **100 mm dry lean concrete (DLC)**. Nepal's rigid guideline recommends **at least 150 mm DLC for major highways** (official 2021 guideline, p15, source E3). Because the study addresses medium/heavy-road candidates, the model author has now changed DLC to **150 mm** and regenerated results. Retain the statement that illustrative 250 mm slabs and asphalt layers are not structurally validated alternatives. A thicker DLC base does not by itself validate slab thickness or equivalence.

Verified updated B quantity: `7000 m² × 0.15 m = 1050 m³ DLC/km`; direct DLC cost `1050 × NPR9000 = NPR9.45 million/km`. Increase from the old model is NPR3.15 million/km direct, or NPR3.3075 million/km after the 5% design/supervision allowance.

### 3. Replace every stale numerical conclusion after the DLC change

Current reproducible model, NPR million per kilometre:

| Metric | A asphalt | B concrete | C 70/30 portfolio |
|---|---:|---:|---:|
| Direct works | 33.560 | 52.040 | 39.254 |
| Base capital including 5% design/supervision | 35.238 | 54.642 | 41.2167 |
| Initial cash with 15% contingency and 13% VAT reserve | 45.791781 | 71.007279 | 53.56110165 |
| 30-year agency present value | 55.308935 | 60.700807 | 53.976794 |

Consequences:

- C's modeled discounted agency advantage over A is **NPR1.33214 million/km**, or **NPR1.33214 crore over 10 km**, under the baseline assumptions.
- C's sustained modeled discounted cash crossing moves from the old year 16 to **year 20**.
- Concrete is cheaper on the modeled stressed section with **4-year** asphalt renewal; changing that to **5 years** already makes asphalt cheaper. At 5 years, concrete costs approximately **NPR0.76351 million/km more**. Do not retain the old “between 5 and 6 years” statement.
- Balanced matrix is **C4.12747, A3.82591, B3.56167**, out of 5.
- Of 243 deterministic scenarios: **A106, B45, C26 unique wins; 66 ties**. These counts are not probabilities.

Keep the break-even caveat visible in the compact view; do not hide the principal condition behind hover-only text. A reader should immediately understand that better asphalt performance can reverse the economic result.

### 4. Align the programme dates without weakening the opening rules

The engineering proposal uses construction in months 6–12; the website uses months 6–15. Prefer the more conservative **months 6–15** planning window and update the narrative consistently. Define months 0–3 protocol, 3–6 surveys/design, 6–15 procurement/trials/construction, and 15–36 monitoring/review. Procurement and trials can overlap design completion only when legally and practically permissible. An actual seasonal calendar is required after mobilisation is known.

**Two post-construction monsoons is the evidence gate; 36 elapsed months is a planning target.** A month-15 finish may or may not allow two full monsoons before month36. The site already says to extend if necessary; preserve that condition.

Current DoR 2082 clauses verified in research:

- DLC to slab: at least 7 days.
- New concrete pavement: no vehicle traffic within 28 days of slab construction; sealed/cured joints, completed shoulders and written Engineer permission are also required.
- Concrete trial: one month before main paving; method statement one month before the trial.
- Asphalt: cooled to ambient and Engineer approval. This is a release condition for completed paving, not total road construction time.

The website's indicative 6–10 weeks/asphalt-km and 10–16 weeks/concrete-km must remain explicitly **resource and access assumptions**. They are not established Nepal rates. Do not multiply independent per-km windows by 9 to derive a critical path, or imply they follow solely from curing. Spread across three regions, mobilisation and available crews may dominate.

### 5. Pilot funding must include the experiment and maintenance

The inspected page excludes future routine maintenance from the pilot envelope while the programme relies on fair, maintained comparison. Separate longer-term network maintenance from **upkeep during the pilot**, and budget the latter. Monitoring unpaid repairs would confound material performance with maintenance neglect.

Use the transparent provisional budget below as a planning scenario. These are assumptions, not quotations, an appropriation or official unit rates. Do not describe this as a validated total until surveys and a project BOQ include off-road trial strips, treatment transitions and repeated regional mobilisation.

| Item | Parameter | NPR million |
|---|---|---:|
| Comparative road works | 4.5 km × (33.56 + 52.04 million/km) | 385.20 |
| Existing design/supervision allowance | 5% of road works | 19.26 |
| Research, instruments, extra independent testing/data and monitoring | Provisional 15; test 10–20 | 15.00 |
| Two years of pilot routine upkeep | 9 km × 0.40 million/km-year × 2 | 7.20 |
| Subtotal | Before reserves | 426.66 |
| Contingency reserve | 15% of subtotal | 63.999 |
| VAT cash reserve | 13% of subtotal + contingency | 63.78567 |
| **Illustrative cash envelope** | **NPR55.44 crore** | **554.44467** |

Do not add another 5% design/supervision to the research allowance automatically; its scope must be distinguished from the existing 5% and contractor QA already in road works. The upkeep assumption includes common drain/shoulder/safety and surface maintenance, not a second sum per pavement type. Two years is an explicit costing convention; extend upkeep and monitoring funding if the seasonal gate requires it. VAT is a conservative taxable-spend reserve; payroll or other actual non-taxable items must be separated in a real estimate.

At research allowance NPR10–20 million, this envelope ranges **NPR54.79–56.09 crore**, before any additional out-of-scope works. The research-only variation is not a confidence interval for the overall project. Land, major structures, deep ground treatment, exceptional slopes and utility relocation remain unpriced. Off-road trial strips, transitions and extra regional mobilisation must be explicitly included or shown as additional provisional sums; the above arithmetic does not establish that these fit inside the contingency.

### 6. Preserve the distinction between evidence, calculations and judgment

The HTML describes all matrix scores as analyst judgments, whereas the first two are ratios calculated from the baseline model and the others are judgment. Suggested wording: **“Cost scores are calculated from the baseline assumptions; other scores and all weights are judgments.”** If cost sliders do not recompute matrix scores, keep this plainly stated beside the matrix. Prefer re-calculation if the frontend supports it; otherwise identify baseline scores clearly.

The overall recommendation is a conditional policy architecture. It is reasonable because it permits site-specific choices, but C's best “fit” score is a judgment, not an independent field result proving its superiority. A sound matrix must be able to return A or B when priorities/conditions differ.

Source guidance supports more than these two pavement systems, including cement-treated bases and low-volume treatments. These do not invalidate the focused comparison; describe the chosen three as **two construction systems plus one deployment strategy**, not an exhaustive list of Nepal's materials.

## Checks completed

- Read current Python/JavaScript calculation sources and generated rate/quantity schedule.
- Independently reconciled each baseline year's net cashflow and discounted total against `results.json`.
- Independently verified cash reserve formula `base × 1.15 × 1.13`.
- Ran `node models/verify_model.mjs`: **834 comparisons passed** across baseline and 243 scenarios after the DLC150 change.
- Recomputed the nine-kilometre trial budget from A/B direct costs rather than portfolio totals.

These checks establish internal arithmetic consistency, not engineering adequacy, local market prices or actual intervention lives. The model's 30-year initial structure and residual-service convention remains an explicit scenario. A future investment appraisal should add alternative horizons/residual assumptions and user-delay costs.

Frontend `app.js` and download assets were not present at the first read, apparently while the root agent was rebuilding. That is not recorded here as a final release defect. Final browser functionality, accessible hover/focus/tap details and packaged-download consistency remain the root agent's release checks.
