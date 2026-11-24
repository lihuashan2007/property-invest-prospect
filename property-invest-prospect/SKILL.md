---
name: property-invest-prospect
description: Assess a residential investment property from an address, listing link, or property documents. Use for sourced property due-diligence PDFs, rental comparables, break-even rent, interest-rate scenarios, land and subdivision potential, or verification of listing claims. Prioritises Melbourne and the rest of Victoria, Australia.
metadata:
  version: "1.1.0"
---

# Property Invest Prospect

Evaluate one property as an investment. Answer in Chinese by default and keep original address, planning, permit and contract terms where useful. Use AUD for Australian properties.

## Set up the assessment

1. Identify the exact property and jurisdiction from the address, URL or documents. Establish the assessment date, current listing status and price guide, dwelling type and bedroom count. Preserve a price range. Note differences between the current listing and historical records for the same address. Ask for clarification only if ambiguity about the property prevents a meaningful assessment.
2. For a current assessment, research the underlying sources. Use Agent Reach when requested or available, and switch to available web search or official portals if it fails. Use the property listing and any supplied documents as evidence of their stated contents. For current planning controls, parcel geometry or approvals, use the appropriate government or council sources. Victoria is the default jurisdiction for confirmed Victorian addresses. For another jurisdiction, use its own sources, currency and rules when available.
3. For a full assessment, dispatch the three roles below in parallel when subagents are available. Give each the same address, date, listing, known inputs and its own reference. Keep each task independent. Each role should return findings with source links, dates, evidence limitations and any unresolved inputs. If dispatch is unavailable, apply the three role briefs in sequence. For a narrowly scoped request, use the relevant role.
4. For suburb-level context or a property report, use the [Suburb Stats source workflow](references/suburb-stats.md). Use the matched bedroom and dwelling type for rental modelling. Keep each source's geography and period with its figure.

| Role | Brief |
|---|---|
| Rental and cash flow | [Rental and cash flow](references/rental-cashflow.md) |
| Land and investment potential | [Land and investment potential](references/land-potential.md) |
| Listing claims | [Listing claims](references/listing-review.md) |

## Use a common cash-flow model

- Default financing is a **20% deposit, 80% loan, interest-only**. Compare **4%, 5% and 6%** under otherwise identical assumptions. Apply the user's explicit inputs and label changes to the comparison. Annual out-of-pocket cost is a calculated result.
- Use documented or quoted costs where available. For gaps, label the screening assumptions of **50 paid weeks per year, management at 7.7% of rent collected, and $6,500 per year in other recurring holding costs**. Use the $6,500 as a whole allowance for rates, owner water costs, insurance, maintenance and land tax, or replace it with an itemised total that states any estimates for missing items. Keep stamp duty, conveyancing and one-off works separate.
- Run the [calculator](scripts/cashflow.py) from the skill directory, or call it by full path. Pass the selected weekly rent and asking price, or both ends of the price guide. Multiple weekly rents produce a separate scenario for each price, rent and rate combination.

  ```sh
  python3 scripts/cashflow.py --price 650000 --weekly-rent 535
  ```

- If the exact price or a defensible rent remains unavailable, show the missing input and report the supported findings. A clearly labelled user-provided scenario or a defensible comparable-sales scenario can still be useful. For a different loan structure, use the applicable repayment schedule and label it. The bundled calculator models interest-only loans.

## Synthesize one report

- Lead with whether the property merits inspection, the main investment reason and the uncertainty that could change the conclusion. Show the price and rent inputs, then a 4%/5%/6% table with annual interest, annual total outgoings, annual and monthly pre-tax cash flow, and break-even and positive-cash-flow weekly rent. For a deficit, show the amount the buyer would cover. For a surplus, show the amount left over. Show gross yield with its price and rent basis.
- Present nearby rental comparisons and the matching suburb median in the same report. Include the land assessment and the claim checks. Reconcile conflicting sources using the current lot/plan, current contracts and applicable official documents. Distinguish an advertised development possibility, a lodged application and an approval. Label terrain as unverified when the evidence supports only an impression.
- End with the documents or site checks that could change the assessment, such as the title and plan, Section 32, leases, approval or occupancy documents and actual outgoings. Draft agent questions where useful. Use public sources and materials the user supplies for the assessment.
- For a full property assessment, deliver a sourced PDF and a short chat summary by default when PDF generation is available. Follow [Property report PDF](references/pdf-report.md). For a quick check or a requested chat-only answer, use the requested scope and format.
