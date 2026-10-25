# Battery Passport self-check: rules and test corpus

Live tool: https://kobima6813.github.io/einvoice-conformance-matrix/battery.html (runs in the browser; nothing is uploaded).

**Unofficial pre-check, not a certification.** It does not replace conformity assessment, a notified body or legal advice.

Input: one passport as a JSON object with the seven [Battery Pass Data Model v1.2.0](https://github.com/batterypass/BatteryPassDataModel) aspects as top-level keys
(`generalProductInformation`, `carbonFootprint`, `circularity`, `materialComposition`, `performance`, `supplyChainDueDiligence`, `labels`), plus an optional `dataCarrier` (GS1 Digital Link URI) or a link typed into the page.

## Rules (37 = 24 final + 13 draft)

"Final" = based on text that is in force (Regulation (EU) 2023/1542) or on the published Battery Pass model. "Draft" = depends on EU delegated/implementing acts not yet adopted (as of Oct 2026), or on an identifier profile the law does not mandate.

| ID | Status | Severity | Check |
|---|---|---|---|
| SCHEMA (×7) | final (model) | error | Each aspect present and valid against the Battery Pass v1.2.0 JSON schema (required, types, enums, patterns, ranges) |
| BP-GP-01 | final | error | Battery mass > 0 (Annex VI Part A) |
| BP-GP-02 | final | error | Manufacturing date not in the future |
| BP-GP-03 | final | error | Put into service not before manufacture |
| BP-GP-04 | final | error | Dynamic data `lastUpdate` not in the future (Annex XIII 4) |
| BP-GP-05 | final | warning | Industrial battery ≤ 2 kWh: outside the Art. 77(1) passport scope |
| BP-GP-06 | final | warning | Contact e-mails are well-formed |
| BP-PF-01 | final | error | Rated energy ≈ rated capacity × nominal voltage (±10 %) |
| BP-PF-02 | final | error | Rated energy given in Wh instead of kWh (factor ~1000) |
| BP-PF-03 | final | error | Minimum < nominal < maximum voltage |
| BP-PF-04 | final | error | Percent values (efficiency, SoC, SoCE, thresholds) within 0–100 |
| BP-PF-05 | final | error | Remaining capacity/energy not above rated (+5 %) |
| BP-PF-06 | final | error | Expected cycles, lifetime, rated max power > 0 |
| BP-MC-01 | final | error | CAS numbers have a correct check digit |
| BP-MC-02 | final | error | Chemistry (NMC, NCA, LFP, LCO, LMO, LTO, Pb, NiMH, NiCd, Na-ion) vs elements in the material list |
| BP-MC-03 | final | warning | Recycled content declared for a metal the chemistry does not contain |
| BP-MC-04 | final | error | Sum of declared material masses ≤ battery mass |
| BP-MC-05 | final | error | Hazardous substance concentration within 0–100 % |
| BP-RC-01 | draft | error | Pre- + post-consumer recycled share ≤ 100 % (Art. 8 methodology pending) |
| BP-RC-02 | draft | error | Each recycled material listed once |
| BP-RC-03 | draft | error | Renewable content within 0–100 % |
| BP-CF-01 | draft | error | All four life-cycle stages present once (Annex II; Art. 7 delegated act pending) |
| BP-CF-02 | draft | error | Stages sum to the declared footprint (±2 %) |
| BP-CF-03 | draft | warning | Absolute footprint ≈ per-kWh footprint × rated energy × expected cycles (±25 %) |
| BP-CF-04 | draft | error | Footprint declared per kWh of rated energy instead of per kWh delivered over the service life |
| BP-CF-05 | draft | warning | Performance class is a single class letter (classes not yet defined) |
| BP-DL-01 | draft | error | Data carrier link is an https GS1 Digital Link URI with `/01/` GTIN |
| BP-DL-02 | draft | error | GTIN check digit |
| BP-DL-03 | draft | warning | Serial (`/21/`) present – the passport is per individual battery (Art. 77(3)) |
| BP-DL-04 | draft | error | Serial uses GS1 AI encodable set 82, max 20 characters |
| BP-DL-05 | draft | warning | GTIN and serial match `productIdentifier` |

DL rules run only when a Digital Link is given. The page shows only counts (errors, warnings, checks run).

## Corpus

`corpus/` holds 2 valid passports (EV/NMC 75 kWh, LMT/LFP 0.96 kWh) and 33 broken variants, each changing one thing. They are synthetic, built by `scripts/battery_corpus.py` from the model structure (the upstream example payloads are random generator output with placeholder values, not usable as valid samples). `corpus/manifest.json` lists the rule each variant must trigger.

| File | Must trigger | What is wrong |
|---|---|---|
| `broken-cf-stages-dont-sum.json` | BP-CF-02 | Lifecycle stages add up to 0.085 but declared total is 0.065 |
| `broken-cf-absolute-mismatch.json` | BP-CF-03 | Absolute footprint 2 t does not match 0.065 kg/kWh x lifetime energy |
| `broken-cf-per-rated-kwh.json` | BP-CF-04 | Footprint declared per kWh of rated energy (78 kg/kWh) instead of per kWh delivered over life |
| `broken-recycled-over-100.json` | BP-RC-01 | Cobalt pre- + post-consumer recycled share = 120 % |
| `broken-recycled-out-of-range.json` | SCHEMA | Recycled share 140 % (schema range 0-100) |
| `broken-recycled-duplicate-material.json` | BP-RC-02 | Cobalt listed twice in recycled content |
| `broken-missing-manufacturer.json` | SCHEMA | Mandatory public field manufacturerInformation removed |
| `broken-missing-chemistry.json` | SCHEMA | Mandatory public field batteryChemistry removed |
| `broken-energy-in-wh.json` | BP-PF-02 | Rated energy given in Wh (75000) where the model expects kWh |
| `broken-capacity-voltage-energy-mismatch.json` | BP-PF-01 | Rated energy 100 kWh but 200 Ah x 375 V = 75 kWh |
| `broken-voltage-order.json` | BP-PF-03 | Minimum voltage above nominal voltage |
| `broken-manufactured-in-future.json` | BP-GP-02 | Manufacturing date in 2031 |
| `broken-service-before-manufacture.json` | BP-GP-03 | Put into service before it was manufactured |
| `broken-cas-check-digit.json` | BP-MC-01 | CAS number 7440-48-5 for cobalt has a wrong check digit (pattern still matches) |
| `broken-chemistry-without-lithium.json` | BP-MC-02 | Chemistry NMC but no lithium/nickel/cobalt in material list |
| `broken-lfp-with-cobalt-recycled.json` | BP-MC-03 | LFP battery declares recycled cobalt content |
| `broken-materials-heavier-than-battery.json` | BP-MC-04 | Declared material masses (110.5 kg) exceed battery mass (50 kg) |
| `broken-hazardous-concentration-over-100.json` | BP-MC-05 | Hazardous substance concentration 250 % |
| `broken-passport-id-malformed.json` | SCHEMA | batteryPassportIdentifier is not a URN |
| `broken-bad-category.json` | SCHEMA | batteryCategory 'car' not in lmt/ev/industrial/stationary |
| `broken-gtin-check-digit.json` | BP-DL-02 | GS1 Digital Link GTIN check digit wrong |
| `broken-dl-not-https.json` | BP-DL-01 | Data carrier URL is not an https Digital Link URI |
| `broken-dl-no-serial.json` | BP-DL-03 | Digital Link identifies the model only (no /21/ serial) - passport is per battery |
| `broken-dl-mismatch-product-id.json` | BP-DL-05 | Digital Link serial differs from productIdentifier |
| `broken-dl-bad-serial-chars.json` | BP-DL-04 | Serial contains characters outside GS1 AI set 82 |
| `broken-remaining-capacity-above-rated.json` | BP-PF-05 | Remaining capacity 230 Ah above rated 200 Ah |
| `broken-soc-over-100.json` | BP-PF-04 | State of charge 160 % |
| `broken-lastupdate-in-future.json` | BP-GP-04 | Dynamic data lastUpdate in 2030 |
| `broken-industrial-under-2kwh.json` | BP-GP-05 | Industrial battery of 0.96 kWh: Art. 77 passport only applies above 2 kWh |
| `broken-renewable-over-100.json` | BP-RC-03 | Renewable content 130 % |
| `broken-cf-class-not-letter.json` | BP-CF-05 | Performance class 'excellent' instead of a class letter |
| `broken-cf-missing-stage.json` | BP-CF-01 | Lifecycle stage 'Recycling' missing |
| `broken-bad-email.json` | BP-GP-06 | Manufacturer e-mail not an address |

Test: serve `docs/` and open `battery/selftest.html` in a browser (we use headless Chrome). Result on 2026-10-25: 2/2 valid passports give 0 errors and 0 warnings; 33/33 broken variants trigger their rule.

## Sources

- Regulation (EU) 2023/1542, Art. 7, 8, 38, 77, 78, Annexes II, VI, XIII: https://eur-lex.europa.eu/eli/reg/2023/1542/oj
- Battery Pass Data Model v1.2.0 (aligned with DIN DKE SPEC 99100:2025-02): https://github.com/batterypass/BatteryPassDataModel ; content guidance: https://thebatterypass.eu
- Carbon footprint methodology status (EV draft delegated act April 2024, not adopted): https://eplca.jrc.ec.europa.eu/EU_BatteryRegulation_Art7.html
- CEN/CENELEC JTC 24 DPP standards EN 18216, 18219–18223 (2026): https://www.cencenelec.eu/news-events/news/2026/en-in-the-spotlight/2026-07-15-dpp/ (standards texts are paid; only public summaries were used)
- GS1 Digital Link URI syntax 1.x and GS1 General Specifications (GTIN check digit, AI 21 / set 82): https://ref.gs1.org/standards/digital-link/

## Known upstream issue

The Battery Pass v1.2.0 GeneralProductInformation schema's e-mail pattern is `^[w.-]+@[w.-]+.[A-Za-z]{2,}$` (backslashes lost), which rejects normal addresses. We drop that pattern and check e-mails with BP-GP-06 instead.
