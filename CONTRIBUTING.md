# Contributing

Thanks for helping. Corrections from generator maintainers are especially welcome.

## Adding a generator or configuration

1. Create `generators/<name>/` with a `run.sh <corpus_dir> <out_dir>` and the driver code. Pin the exact
   generator version (package version, release URL + SHA-256, or commit).
2. Name outputs `<name><version>-<config>__<cart-id>.xml`, e.g. `mylib1.2.3-en16931__b2b0042.xml`. The part
   before `__` is the matrix row.
3. Use the carts in `corpus/` as they are. If the generator computes totals, feed it the shop view
   (`carts_b2b.json`, `carts_b2c.json`) or the net view (`carts_net.json`). If it does not, feed it
   `ref_en16931_rounding.json`. If the platform charges its own order total, add it to
   `invoices/platform_order_totals.json`.
4. Pack the outputs reproducibly:
   `tar --sort=name --mtime=@0 --owner=0 --group=0 --numeric-owner -C out -cf - <dirs> | xz -9e > invoices/<name>.tar.xz`
5. Run `bash scripts/run_matrix.sh`, copy `work/matrix.csv`, `work/matrix.md` and `work/matrix_totals.json`
   into `results/`, then update the README table.
6. If the generator can run on a stock Ubuntu runner, add it to the `regenerate` job in
   `.github/workflows/conformance.yml`.

## For vendors and maintainers: getting listed

* Free and neutral: any open-source or commercially available EN 16931 generator can be listed.
* Easiest path: open an issue `Listing request: <project>` with the version, the output format (XRechnung UBL/CII,
  ZUGFeRD/Factur-X profile, Peppol BIS 3) and a minimal example of how amounts are set. We will write the driver.
* Or open a PR following "Adding a generator" above. Please pin the version; we re-test on new releases on request.
* We contact maintainers with reproducible examples before highlighting a failure, and configuration issues
  (e.g. a non-default setting) are labelled as such, never as bugs.
* Fixed in a release? Open an issue with the version; we re-run and update the "Upstream reports" table.

## Reporting a wrong result

Open an issue with the invoice file name, the rule id and why you think the finding is wrong. Please be
specific and neutral: the goal is consistent invoices, not blame.

## Ground rules

* No real customer data in the corpus or in invoices.
* Do not vendor third-party validators or schemas; add them to `validators/pins.txt` (URL + SHA-256).
* Changes to validator versions must come with a re-run of the whole matrix.
