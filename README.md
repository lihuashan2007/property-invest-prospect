# Property Invest Prospect

A Codex skill for assessing a residential investment property by address or listing URL, with Victoria, Australia as its primary market.

- Compare nearby rents and the suburb median for the same bedroom count. Estimate rental yield, buyer cash contributions and break-even rent at 4%, 5% and 6%.
- Check parcel geometry, frontage, terrain and subdivision potential against planning and title evidence.
- Review the selling agent's claims against the listing documents and public records.

## Install in Codex

Download the installation archive from the [v1.0.0 release](https://github.com/lihuashan2007/property-invest-prospect/releases/tag/v1.0.0) and extract the `property-invest-prospect` folder into your personal Codex skills directory, usually `~/.codex/skills`. Then invoke it with an address or listing URL.

```text
Use $property-invest-prospect to assess this property: [address or listing URL]
```

The skill defaults to a Chinese report and uses current local evidence where available. Its bundled interest-only cash-flow calculator runs on Python 3 with the standard library.
