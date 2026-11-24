# Property report PDF

Use a residential due-diligence layout with the address, assessment date, main metrics and decision on the first page. Follow with price and comparable transactions, rental comparisons and matched median, interest-rate sensitivity, parcel/terrain/planning, suburb measures, listing claims and buyer checks. Combine sections for shorter reports and include school zones, service access, mapped hazards or permits when they affect the decision and evidence supports them. Use the source reference as a design brief only. Draw a parcel diagram from licensed or official boundary coordinates where supported and attribute it. Mark map dimensions as estimates. Use a current title or survey for legal geometry.

Create UTF-8 JSON and run:

    python3 scripts/render_report.py assessment.json assessment.pdf

Requires Python 3 and ReportLab. The renderer uses the Mac system's simplified Chinese Heiti TrueType collection by default. On other hosts use --font /path/to/regular.ttf and optionally --bold-font /path/to/bold.ttf with embeddable TrueType fonts covering the report's characters. If the script runtime is unavailable, use another local PDF-capable tool with this section structure and render-check the final PDF.

## Renderer input

- Top level fields are address, assessment_date, subtitle, summary (rows of [label, value]), verdict (title and text), sources, and sections. Optional currency_symbol defaults to "$".
- sources maps stable IDs to objects with label and url. Use an HTTP(S) URL and write the source as a concise title. Cite IDs near claims, such as [R1], and include the key in the section's sources array to create the matching clickable link.
- Each section has title, optional intro, blocks, and an optional sources array of IDs. Sections start on a new page. Keep cover summary and contents short.
- Block types are text (text, optional title, optional note boolean), callout (title, text), table (headers, rows, optional positive relative column weights), cashflow, and parcel.
- A cashflow block uses price and weekly-rent arrays. It accepts the same optional keys as cashflow.py, without leading dashes. The renderer invokes that calculator so displayed values match the V1 cash-flow model. Use supported price/rent scenarios or show missing inputs as text. Keep rent evidence, sale price status, annual negative cash flow as buyer subsidy, and costs clear in the report. For an alternative repayment structure, calculate using the appropriate model and include a labelled table instead.
- A parcel block accepts points as a list of [easting, northing] pairs, front_edge as a pair of zero-based point indices, and caption as text. Use one projected geometry in a consistent coordinate reference system. The diagram faces grid north. Give the geometry source and limitations in its caption or immediately below it.

Render all pages to images where possible. Check Chinese glyphs, table breaks, links, pages with overflow and property/period labels. Confirm the report's inputs, cited cash flow values and any comparison with the calculator. Return the saved PDF and a short conclusion with the key uncertainty.
