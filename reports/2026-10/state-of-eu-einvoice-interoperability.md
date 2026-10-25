# State of EU e-invoice interoperability — October 2026

*Monthly report of the [e-invoice conformance matrix](https://github.com/kobima6813/einvoice-conformance-matrix). Data as of 25 Oct 2026. All numbers come from files in this repository; every upstream status links to its source.*

## Summary

- **Update 25 Oct 2026:** two generators were added after the first snapshot: easybill/zugferd-php 6.0.0 (XRechnung CII, 600/600 pass) and invopop/gobl 0.510.0 (CII + UBL, 1,200/1,200 pass; on 22/600 orders the amount due is €0.01 above the charged total). Totals below include them.
- **Update 25 Oct 2026 (2):** two Python generators were added: PyCheval 0.3.3 (Factur-X EN 16931 CII, 600/600 pass) and python-en16931 0.2 (Peppol BIS 3 UBL). python-en16931 has no line allowances, so the coupon goes in as one document discount. On the 138 orders that mix 19 % and 7 % VAT and carry a coupon, the library books the whole discount against the first VAT rate. That gives a wrong VAT breakdown (57 invoices even show a negative 19 % taxable amount) and an amount due €0.42–€535.50 below the correct figure. The CEN calculation rules still pass, because the invoice is internally consistent. Every file also fails Peppol rules R003/R005, because the template always writes TaxCurrencyCode and has no BuyerReference.
- **16,200 synthetic invoices** from **14 open-source generators** (27 configurations × 600 orders: 300 B2B + 300 B2C) were checked against KoSIT 1.6.3 (XRechnung 3.0.2 configuration), the CEN EN 16931 rules and Peppol BIS 3.0.20. Source: [`results/matrix_totals.json`](../../results/matrix_totals.json).
- **21 of 27 configurations** are clean (pass every matrix validator check). **6** have validator failures: josemmo default config, Odoo 19 Factur-X (both rounding modes), WooCommerce PDF Invoices Factur-X (both settings), ZUGFeRD-csharp CII without a delivery date. Definition: a configuration is *clean* when, in both segments, every file is accepted by KoSIT or has no applicable KoSIT scenario, and has 0 XSD failures, 0 CEN EN 16931 calculation-rule failures and 0 Peppol R120 failures. These are the matrix columns in `results/matrix.csv`. python-en16931 0.2 is clean by this definition, but every one of its files also fails the full Peppol BIS rules PEPPOL-EN16931-R003/R005, which are not a matrix column.
- **Passing the validator is not enough:** 7 of the 21 clean configurations still state an amount due (BT-115) that differs from what the order charged: 4 of them on **472 of 600** invoices each (Mustang 2.26.0 library totals, speedata 0.0.23 CII and UBL, josemmo 0.3.1 with 2-decimal rounding), python-en16931 0.2 on 494 of 600, and invopop/gobl CII and UBL on 22 of 600 each. These are tax-inclusive shop orders converted to EN 16931 net arithmetic; no validator checks the original order total.
- **New this month: French scenarios.** 5 French-mandate scenarios × 2 Factur-X profiles (EN16931, EXTENDED) × 3 generator versions = **30 invoices, 30 pass** (details below).

## Upstream fixes and reports

| Project | What we found | Status (source) |
|---|---|---|
| Odoo (18.0) | CII grand total included cash rounding | PR [#295442](https://github.com/odoo/odoo/pull/295442) opened by an Odoo developer citing matrix data; merged by Odoo's merge bot into 18.0, closed 23 Oct 2026 |
| Odoo (18.0) | PEPPOL-EN16931-R120 (line net ≠ qty × price − allowances) on 242/300 B2B invoices | PR [#297750](https://github.com/odoo/odoo/pull/297750): we tested it, R120 drops to 0, no new XSD/CEN errors ([our results](https://github.com/odoo/odoo/pull/297750#issuecomment-6389712174)); maintainer confirmed. Open. |
| Odoo (18.0) | BR-CO-10 / BR-S-08 with `round_globally`: 93/98 of 300 B2B, 125/128 of 300 B2C | PR [#297752](https://github.com/odoo/odoo/pull/297752): we tested it, both go to 0 ([our results](https://github.com/odoo/odoo/pull/297752#issuecomment-6389712351)); the remaining difference moves into BT-114 on 218/600 invoices, which the maintainer confirmed is intended. Open. |
| WooCommerce PDF Invoices & Packing Slips 5.16.4 | Factur-X `ram:RoundingAmount` out of XSD order: 109/300 B2B and 129/300 B2C invoices XSD-invalid | Issue [#1662](https://github.com/wpovernight/woocommerce-pdf-invoices-packing-slips/issues/1662), open; independently reproduced by another user with the KoSIT validator on 23 Oct 2026 |
| speedata/einvoice | UBL element order and BT-27/BT-28 swap (≤ v0.0.20) | Issue [#185](https://github.com/speedata/einvoice/issues/185) fixed by PR #186, released in v0.0.23; now 600/600 KoSIT-accepted for both CII and UBL |
| horstoeko/zugferd | VAT breakdown for exempt categories E/AE/K/G/O | Issue [#390](https://github.com/horstoeko/zugferd/issues/390), released in [v1.0.133](https://github.com/horstoeko/zugferd/releases/tag/v1.0.133) on 20 Oct 2026 |
| Mustang 2.26.0 | Library-computed totals differ from the charged amount (472/600) | Issue [#1316](https://github.com/ZUGFeRD/mustangproject/issues/1316); fix [PR #1318](https://github.com/ZUGFeRD/mustangproject/pull/1318) merged 20 Oct 2026, not yet released |
| josemmo/einvoicing 0.3.1 | Default config: BR-CO-10, 590/600 CEN failures | Issue [#93](https://github.com/josemmo/einvoicing/issues/93), open; setting a rounding preset gives 600/600 KoSIT accept |
| ZUGFeRD-csharp 18.0.1 | CII without a delivery date drops a required empty element: 600/600 XSD-invalid; 600/600 pass with BT-72 set | Known upstream, [PR #981](https://github.com/stephanstapel/ZUGFeRD-csharp/pull/981) open (not ours) |

Full per-version history with dates: [`results/history/version_history.json`](../../results/history/version_history.json) (also [CSV](../../results/history/version_history.csv)).

## Matrix results by generator

| Generator / configuration | Invoices | Validator result | Amount due ≠ order total |
|---|---|---|---|
| drafthorse 2025.2.0 (EN16931 CII) | 600 | all pass | 0 |
| akretion factur-x 7.7 (FR, Factur-X PDF round trip) | 600 | all pass | 0 |
| horstoeko/zugferd (EN16931) | 600 | all pass | 0 |
| num-num/ubl-invoice 2.4.1 (Peppol BIS 3, BE parties) | 600 | all pass | 0 |
| ZUGFeRD-csharp 18.0.1 UBL, and CII with BT-72 | 1,200 | all pass | 0 |
| ZUGFeRD-csharp 18.0.1 CII without BT-72 | 600 | 600 XSD-invalid | 0 |
| speedata 0.0.23 (CII, UBL) | 1,200 | all pass | 944 |
| Mustang 2.26.0 (library totals) | 600 | all pass | 472 |
| josemmo 0.3.1 default / round2 | 1,200 | 590 CEN fail / all pass | 597 / 472 |
| Odoo 19 XRechnung, Peppol BIS 3 (4 configs) | 2,400 | all pass | 0 |
| Odoo 19 Factur-X `round_globally` | 600 | 226 CEN fail, 242 Peppol R120 fail | 20 |
| Odoo 19 Factur-X `round_per_line` | 600 | 242 Peppol R120 fail | 0 |
| WooCommerce PDF Invoices 5.16.4 Factur-X (2 settings) | 1,200 | 476 XSD-invalid | 0 |
| WooCommerce PDF Invoices 5.16.4 Peppol BIS 3 (2 settings) | 1,200 | all pass | 0 |

Source: [`results/matrix.csv`](../../results/matrix.csv), [`results/matrix_totals.json`](../../results/matrix_totals.json).

## France: new Factur-X scenarios

France's receiving obligation and the issuing obligation for large and mid-size companies started on 1 Sep 2026, through approved platforms; accepted formats are UBL, CII and Factur-X. We added 5 French scenarios ([`scenarios/fr/scenarios.json`](../../scenarios/fr/scenarios.json)):

1. Standard 20 % + 5.5 % VAT
2. VAT franchise ("TVA non applicable, art. 293 B du CGI", category E, code VATEX-FR-FRANCHISE)
3. Domestic reverse charge (autoliquidation, category AE)
4. Intra-EU supply to Germany (category K, art. 262 ter I CGI, delivery country and date)
5. All four French rates: 20, 10, 5.5 and 2.1 %

Each invoice carries the seller SIREN (BT-30, scheme 0002), SIRET (BT-29, scheme 0009), a SIREN-based electronic address (scheme 0225), the buyer SIREN, and header notes for late-payment penalties (PMT), the EUR 40 recovery fee (PMD) and the early-payment discount (AAB).

Checks: Factur-X 1.09.2 XSD for the profile, CEN EN 16931 CII rules, the official Factur-X EXTENDED schematron for EXTENDED, KoSIT (EN16931 profile only, since KoSIT has no EXTENDED scenario), and our structural checks that each French field reaches the XML.

| Generator | EN16931 | EXTENDED |
|---|---|---|
| drafthorse 2025.2.0 + factur-x 7.7 (PDF embed and read-back) | 5/5 pass | 5/5 pass |
| horstoeko/zugferd 1.0.132 | 5/5 pass | 5/5 pass |
| horstoeko/zugferd 1.0.133 | 5/5 pass | 5/5 pass |

Notes:
- With horstoeko, the ship-to address (needed for BR-IC-12 on intra-EU invoices) is silently dropped unless `setDocumentShipTo()` is called before `setDocumentShipToAddress()`. Our first driver did this and produced a BR-IC-12 failure; that was our usage error, not a library bug.
- horstoeko 1.0.132 passes these scenarios because we pass the exemption reason text explicitly; issue #390 (fixed in 1.0.133) was in the `ZugferdQuickDescriptor` helper, while our driver uses `ZugferdDocumentBuilder` with the reason text set explicitly.
- We have not yet tested the French platform-specific (PA/PPF) rule sets, since they are not available as free, pinned validators. Results: [`results/fr/fr_results.json`](../../results/fr/fr_results.json).

## Regulatory calendar

| Country | Obligation | Date | Source |
|---|---|---|---|
| Belgium | B2B structured e-invoicing (EN 16931 / Peppol) mandatory; tolerance period ended 31 Mar 2026 | 1 Jan 2026 | [EC eInvoicing country sheet, Belgium 2026](https://ec.europa.eu/digital-building-blocks/sites/spaces/einvoicingCFS/pages/956171273/2026+Belgium+2026+eInvoicing+Country+Sheet) |
| France | All companies must receive e-invoices; large and mid-size companies must issue | 1 Sep 2026 | [service-public.gouv.fr](https://entreprendre.service-public.gouv.fr/actualites/A15683?lang=en) |
| France | SMEs and micro-companies must issue | 1 Sep 2027 | same |
| Germany | Receiving required since 1 Jan 2025; issuing mandatory for prior-year turnover > EUR 800k | 1 Jan 2027 | [BMF FAQ e-Rechnung](https://www.bundesfinanzministerium.de/Content/DE/FAQ/e-rechnung.html) |
| Germany | Issuing mandatory for all B2B | 1 Jan 2028 | same |
| EU (ViDA) | Intra-EU B2B e-invoicing and digital reporting | 1 Jul 2030 | [European Commission, VAT in the Digital Age](https://taxation-customs.ec.europa.eu/taxation/vat/vat-digital-age-vida_en) |

## Method

Deterministic corpus of 600 synthetic orders (tax-inclusive shop carts with % discounts and shipping), generated per library with the library's own API. Validators are pinned by SHA-256 in [`validators/pins.txt`](../../validators/pins.txt). Reproduce with `scripts/run_matrix.sh` and `scenarios/fr/run_fr.sh`. Corrections: see CONTRIBUTING.md.
