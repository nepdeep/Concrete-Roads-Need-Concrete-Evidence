# Nepal Road Decisions

Research cutoff: 18 October 2026. Delivery revision: 19 October 2026.

Open **study.html** directly in a browser. It contains its own styling, research data and calculations and works offline. Hover a dotted term or marked diagram region for the explanation; click/tap or press Enter to pin it. Escape closes the explanation. Use **Show full reading** for the expanded narrative. External sources and hosted downloadable reports require a connection.

The website is also prepared for private publication at https://nepal-road-decisions.nimble-lake-3747.chatgpt.site/ . See `road-decisions-nepal/.openai/hosting.json` for the saved Site identity.

## Contents

- `study.html`: self-contained interactive reading copy.
- `research/decision-report.md`: complete analysis, three options, recommendation and delivery plan.
- `research/nepal-evidence.md`: Nepal policy, trade and source verification.
- `research/engineering-options.md`: first principles, engineering methods and experimental design.
- `research/cost-methodology.md`: quantities, rates, lifecycle calculations, scoring and sensitivity.
- `research/sources/`: preserved original policy PDF and Customs workbook, plus policy page images used for verification.
- `research/sources-nepal.json`, `research/sources-engineering.json`: source provenance and limitations.
- `models/`: reproducible Python and JavaScript model, cashflows, quantities, selection matrix and 243 deterministic sensitivity cases.
- `road-decisions-nepal/dist/`: complete static website and downloadable package.
- `scripts/build_site.py`: regenerates browser data, downloads and standalone HTML from the research/model files.

## Reproduce

From this folder with Python 3 and Node.js installed:

```powershell
python models/pavement_model.py
node models/verify_model.mjs
python scripts/build_site.py
python -m http.server 8765 --bind 127.0.0.1 --directory road-decisions-nepal/dist
```

Then open http://127.0.0.1:8765/ . There are no application dependencies or external font/image requests.

## Main finding

Use a segment-specific portfolio of properly drained flexible asphalt and engineered jointed concrete, after non-negotiable safety, support, drainage and constructability checks. This is a preferred decision architecture, not a mandatory national concrete quota. A road can select entirely asphalt or entirely concrete when its appraisal supports that result.

The official directive already conditions domestic pavement alternatives on technical appropriateness. Design guidance exists for both systems. A national comparative appraisal specifically supporting the October 2026 policy was not located in the reviewed sources; that does not establish that none exists.

For the hypothetical 10 km, 7 m-wide mixed corridor, initial cash budgets are A 45.79, B 71.01 and C 53.56 crore NPR; 30-year discounted agency costs are A 55.31, B 60.70 and C 53.98 crore. These are different accounting boundaries and must not be added together. C uses 70% asphalt and 30% concrete as a scenario assumption. At baseline rates, changing stressed asphalt renewal from four to five years reverses the cost preference toward asphalt.

The proposed 9 km replicated pilot is a separate programme: its provisional funding envelope is NPR 55.72 crore, including extra research, two years of routine upkeep, contingency and VAT allowance. It needs two post-construction monsoons and longer follow-up. It is not an approved or funded government scheme.

All installed rates, maintenance schedules, productivity and programme allowances are explicit screening assumptions. No selected road has been structurally designed or priced from verified quotations. Major structures, land, exceptional slope works, utility relocation and escalation need separate appraisal. The model's 834 consistency checks establish arithmetic agreement, not field performance.
