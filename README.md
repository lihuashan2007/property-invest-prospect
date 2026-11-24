# Property Invest Prospect

A Codex skill for assessing a residential investment property by address or listing URL, with Victoria, Australia as its primary market.

- Compare nearby rents and the suburb median for the same bedroom count. Estimate rental yield, buyer cash contributions and break-even rent at 4%, 5% and 6%.
- Check parcel geometry, frontage, terrain and subdivision potential against planning and title evidence.
- Review the selling agent's claims against the listing documents and public records.
- Visit public PremiumREA Suburb Stats pages for local market context and check property-level claims against official sources.
- Generate a sourced PDF with comparable sales and rents, cash-flow scenarios, planning and site findings, and checks before making an offer.

## Install in Codex

Download the installation archive from the [latest release](https://github.com/lihuashan2007/property-invest-prospect/releases/latest) and extract the `property-invest-prospect` folder into your personal Codex skills directory, usually `~/.codex/skills`. Then invoke it with an address or listing URL.

```text
Use $property-invest-prospect to assess [address or listing URL] and generate a PDF.
```

The skill defaults to a Chinese report and uses current local evidence where available. The interest-only cash-flow calculator uses Python 3 and its standard library. The bundled PDF renderer uses ReportLab and an embeddable Chinese font. See the [PDF workflow](property-invest-prospect/references/pdf-report.md) for details.
