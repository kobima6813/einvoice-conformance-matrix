# Third-party components

Nothing in this table is redistributed in this repository. `validators/fetch_pinned.sh` downloads each
artefact from its official source and verifies the SHA-256 in `validators/pins.txt`.

| component | version / pin | source | license |
|---|---|---|---|
| KoSIT validator | 1.6.3 | github.com/itplr-kosit/validator | Apache-2.0 |
| XRechnung validator configuration | 3.0.2 (release 2026-08-31) | github.com/itplr-kosit/validator-configuration-xrechnung | Apache-2.0 |
| Peppol BIS Billing 3 schematron | v3.0.20 | github.com/OpenPEPPOL/peppol-bis-invoice-3 | see upstream (no license file in the repository) |
| CEN EN 16931 validation artefacts | commit 6e35e0a | github.com/ConnectingEurope/eInvoicing-EN16931 | EUPL-1.2 |
| FNFE Factur-X 1.09.2 XSD / schematron (optional) | commit 97ba0f3 | github.com/fnfempe/France_RFE | Apache-2.0 |
| Saxon-HE | 12.10 | Maven Central | MPL-2.0 |
| xmlresolver | 5.3.3 | Maven Central | Apache-2.0 |
| SchXslt | 1.10.1 | Maven Central | see upstream |
| Mustang (generator and optional validator) | 2.26.0 | github.com/ZUGFeRD/mustangproject | Apache-2.0 |
| horstoeko/zugferd (generator) | 1.0.133 | Packagist | MIT |
| drafthorse (generator) | 2025.2.0 | PyPI | Apache-2.0 |
| WordPress / WooCommerce / PDF Invoices & Packing Slips (generator) | 7.1.3 / 11.2.1 / 5.16.4 | wordpress.org | GPL-2.0+ / GPL-3.0 / GPL-3.0 |
| Odoo Community (generator) | 19.0 @ 53ec5874 | github.com/odoo/odoo | LGPL-3.0 |

## Shipped generator outputs

`invoices/*.tar.xz` contain XML invoices **produced by** the generators above from the synthetic corpus. They
contain no code from those projects, only the corpus data in the EN 16931 / UBL / CII syntaxes. They are
included so results can be reproduced without installing WordPress or Odoo, and are provided under this
repository's license.

The driver scripts in `generators/woocommerce` and `generators/odoo` run inside the respective
applications and call their public APIs. They are licensed under Apache-2.0, which is compatible with GPL-3.0
and LGPL-3.0.
