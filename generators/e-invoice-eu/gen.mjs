// @e-invoice-eu/core 3.4.2 driver: the library computes no totals, so the reference EN 16931 totals are supplied.
// Writes XRechnung UBL and XRechnung CII (the library maps its UBL-shaped model to CII).
// usage: node gen.mjs <corpus_dir>/ref_en16931_rounding.json <out_dir>
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { InvoiceService } from "@e-invoice-eu/core";
const [, , src, out] = process.argv;
const svc = new InvoiceService({ log() {}, warn() {}, error() {} });
const E = (v) => ({ v: String(v) });
const amt = (k, v) => ({ [k]: String(v), [k + "@currencyID"]: "EUR" });
const tax = (rate) => ({ "cbc:ID": "S", "cbc:Percent": String(rate), "cac:TaxScheme": { "cbc:ID": "VAT" } });
const addr = (street, city, zip) => ({ "cbc:StreetName": street, "cbc:CityName": city, "cbc:PostalZone": zip, "cac:Country": { "cbc:IdentificationCode": "DE" } });
const carts = JSON.parse(readFileSync(src, "utf8")); let err = 0;
const fmts = { "XRECHNUNG-UBL": "xrechnung-ubl", "XRECHNUNG-CII": "xrechnung-cii" };
for (const f of Object.values(fmts)) mkdirSync(`${out}/e-invoice-eu3.4.2-${f}+ref-totals`, { recursive: true });
for (const c of carts) {
  const T = c.T;
  const inv = { "ubl:Invoice": {
    "cbc:CustomizationID": "urn:cen.eu:en16931:2017#compliant#urn:xeinkauf.de:kosit:xrechnung_3.0",
    "cbc:ProfileID": "urn:fdc:peppol.eu:2017:poacc:billing:01:1.0",
    "cbc:ID": c.id, "cbc:IssueDate": "2026-10-18", "cbc:InvoiceTypeCode": "380", "cbc:DocumentCurrencyCode": "EUR",
    "cbc:BuyerReference": "04011000-12345-03",
    "cac:AccountingSupplierParty": { "cac:Party": {
      "cbc:EndpointID": "rechnung@muster.example", "cbc:EndpointID@schemeID": "EM",
      "cac:PartyName": { "cbc:Name": "Muster Shop GmbH" }, "cac:PostalAddress": addr("Musterstr. 1", "Berlin", "10115"),
      "cac:PartyTaxScheme": [{ "cbc:CompanyID": "DE123456788", "cac:TaxScheme": { "cbc:ID": "VAT" } }],
      "cac:PartyLegalEntity": { "cbc:RegistrationName": "Muster Shop GmbH" },
      "cac:Contact": { "cbc:Name": "Buchhaltung", "cbc:Telephone": "+49 30 1234567", "cbc:ElectronicMail": "rechnung@muster.example" } } },
    "cac:AccountingCustomerParty": { "cac:Party": {
      "cbc:EndpointID": "kunde@kunde.example", "cbc:EndpointID@schemeID": "EM",
      "cac:PostalAddress": addr("Kundenweg 2", "München", "80331"),
      "cac:PartyLegalEntity": { "cbc:RegistrationName": "Kunde AG" } } },
    "cac:Delivery": { "cbc:ActualDeliveryDate": "2026-10-18" },
    "cac:PaymentMeans": [{ "cbc:PaymentMeansCode": "58", "cac:PayeeFinancialAccount": { "cbc:ID": "DE02120300000000202051" } }],
    "cac:PaymentTerms": { "cbc:Note": "Zahlbar sofort" },
    "cac:TaxTotal": [{ ...amt("cbc:TaxAmount", T.tax), "cac:TaxSubtotal": c.tax.map(t => ({
      ...amt("cbc:TaxableAmount", t.basis), ...amt("cbc:TaxAmount", t.tax), "cac:TaxCategory": tax(t.rate) })) }],
    "cac:LegalMonetaryTotal": { ...amt("cbc:LineExtensionAmount", T.line), ...amt("cbc:TaxExclusiveAmount", T.basis),
      ...amt("cbc:TaxInclusiveAmount", T.grand), ...(T.rounding ? amt("cbc:PayableRoundingAmount", T.rounding) : {}),
      ...amt("cbc:PayableAmount", T.due) },
    "cac:InvoiceLine": c.L.map((l, i) => ({ "cbc:ID": String(i + 1),
      "cbc:InvoicedQuantity": String(l.qty), "cbc:InvoicedQuantity@unitCode": "H87", ...amt("cbc:LineExtensionAmount", l.line_net),
      ...((l.allow || []).length ? { "cac:AllowanceCharge": l.allow.map(a => ({ "cbc:ChargeIndicator": "false",
        "cbc:AllowanceChargeReasonCode": "95", "cbc:AllowanceChargeReason": "Rabatt", ...amt("cbc:Amount", a) })) } : {}),
      "cac:Item": { "cbc:Name": l.name, "cac:ClassifiedTaxCategory": tax(l.rate) },
      "cac:Price": amt("cbc:PriceAmount", l.net_price) })) } };
  for (const [fmt, tag] of Object.entries(fmts)) {
    try { const x = await svc.generate(inv, { format: fmt, lang: "de-de" });
      writeFileSync(`${out}/e-invoice-eu3.4.2-${tag}+ref-totals/e-invoice-eu3.4.2-${tag}+ref-totals__${c.id}.xml`, x); }
    catch (e) { err++; if (err < 4) console.error(c.id, fmt, String(e.message || e).slice(0, 400)); }
  }
}
console.log(`ok (${carts.length} carts, ${err} generation errors)`);
