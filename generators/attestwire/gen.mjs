// @attestwire/en16931 0.14.1 driver: library computes all totals from the net lines (XRechnung CII).
// usage: node gen.mjs <corpus_dir>/carts_net.json <out_dir>
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { generateCii, validateInput } from "@attestwire/en16931";
const [, , src, out] = process.argv; mkdirSync(out, { recursive: true });
const carts = JSON.parse(readFileSync(src, "utf8")); let bad = 0;
for (const c of carts) {
  const inv = {
    profile: "xrechnung-cii", invoiceNumber: c.id, issueDate: "2026-10-18", currency: "EUR",
    buyerReference: "04011000-12345-03", deliveryDate: "2026-10-18",
    seller: { name: "Muster Shop GmbH", vatId: "DE123456788",
      address: { line1: "Musterstr. 1", city: "Berlin", postalCode: "10115", countryCode: "DE" },
      electronicAddress: { schemeId: "EM", value: "rechnung@muster.example" },
      contact: { name: "Buchhaltung", phone: "+49 30 1234567", email: "rechnung@muster.example" } },
    buyer: { name: "Kunde AG", address: { line1: "Kundenweg 2", city: "München", postalCode: "80331", countryCode: "DE" },
      electronicAddress: { schemeId: "EM", value: "kunde@kunde.example" } },
    payment: { meansCode: "58", iban: "DE02120300000000202051" },
    lines: c.lines.map((l, i) => ({ id: String(i + 1), description: l.name, quantity: Number(l.qty), unitCode: "H87",
      unitPrice: Number(l.price), vatCategory: "S", vatRate: Number(l.rate),
      allowances: (l.allow || []).map(a => ({ amount: Number(a), reason: "Rabatt", reasonCode: "95" })) })),
  };
  const v = validateInput(inv); if (!v.valid) bad++;
  writeFileSync(`${out}/attestwire-en16931-0.14.1-auto-totals-xrechnung-cii__${c.id}.xml`, generateCii(inv));
}
console.log(`ok (${carts.length} written, ${bad} flagged by validateInput)`);
