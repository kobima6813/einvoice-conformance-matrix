// node-zugferd 0.1.1-beta.1 driver: Factur-X EN 16931 (CII). The library computes no totals; reference totals supplied.
// usage: node gen.mjs <corpus_dir>/ref_en16931_rounding.json <out_dir>
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { zugferd } from "node-zugferd";
import { EN16931 } from "node-zugferd/profile/en16931";
const [, , src, out] = process.argv;
const invoicer = zugferd({ profile: EN16931 });
const tag = "node-zugferd0.1.1-beta.1-en16931+ref-totals"; mkdirSync(`${out}/${tag}`, { recursive: true });
const addr = (line1, city, postCode) => ({ postCode, line1, city, countryCode: "DE" });
let err = 0;
for (const c of JSON.parse(readFileSync(src, "utf8"))) {
  const T = c.T;
  const data = {
    number: c.id, typeCode: "380", issueDate: new Date("2026-10-18"),
    transaction: {
      line: c.L.map((l, i) => ({
        identifier: String(i + 1), tradeProduct: { name: l.name },
        tradeAgreement: { netTradePrice: { chargeAmount: l.net_price } },
        tradeDelivery: { billedQuantity: { amount: l.qty, unitMeasureCode: "H87" } },
        tradeSettlement: {
          tradeTax: { typeCode: "VAT", categoryCode: "S", rateApplicablePercent: l.rate },
          ...((l.allow || []).length ? { allowances: l.allow.map(a => ({ actualAmount: a, reasonCode: "95", reason: "Rabatt" })) } : {}),
          monetarySummation: { lineTotalAmount: l.line_net },
        },
      })),
      tradeAgreement: {
        buyerReference: "04011000-12345-03",
        seller: { name: "Muster Shop GmbH", postalAddress: addr("Musterstr. 1", "Berlin", "10115"),
          taxRegistration: { vatIdentifier: "DE123456788" } },
        buyer: { name: "Kunde AG", postalAddress: addr("Kundenweg 2", "München", "80331") },
      },
      tradeDelivery: { information: { deliveryDate: new Date("2026-10-18") } },
      tradeSettlement: {
        currencyCode: "EUR",
        paymentInstruction: { typeCode: "58", transfers: [{ paymentAccountIdentifier: "DE02120300000000202051" }] },
        vatBreakdown: c.tax.map(t => ({ calculatedAmount: t.tax, typeCode: "VAT", basisAmount: t.basis, categoryCode: "S", rateApplicablePercent: t.rate })),
        paymentTerms: { description: "Zahlbar sofort" },
        monetarySummation: { lineTotalAmount: T.line, taxBasisTotalAmount: T.basis,
          taxTotal: { amount: T.tax, currencyCode: "EUR" }, grandTotalAmount: T.grand,
          ...(T.rounding ? { roundingAmount: T.rounding } : {}), duePayableAmount: T.due },
      },
    },
  };
  try { writeFileSync(`${out}/${tag}/${tag}__${c.id}.xml`, await invoicer.create(data).toXML()); }
  catch (e) { err++; if (err < 4) console.error(c.id, String(e.message || e).slice(0, 600)); }
}
console.log(`ok (${err} generation errors)`);
