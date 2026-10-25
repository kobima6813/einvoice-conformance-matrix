"""invinet/python-en16931 0.2 driver (Peppol BIS 3 UBL): the library computes all totals from net line prices (carts_net.json).
The library has no line-level allowances; its only discount mechanism is one document-level discount
(Invoice.discount_amount), so the coupon is passed as the sum of the cart's net line allowances.
usage: python3 gen.py <carts_net.json> <out_dir>"""
import os, sys, json
from decimal import Decimal as D
from en16931.entity import Entity
from en16931.invoice import Invoice
from en16931.invoice_line import InvoiceLine
from en16931.bank_info import BankInfo
src, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True); TAG = 'en16931py0.2-peppolbis3-docdiscount'; n = nerr = 0
for o in json.load(open(src)):
    try:
        inv = Invoice(invoice_id=o['id'])
        inv.seller_party = Entity(name="Muster Shop GmbH", tax_scheme="VAT", tax_scheme_id="DE123456788", country="DE", party_legal_entity_id="DE123456788",
            registration_name="Muster Shop GmbH", mail="shop@example.com", endpoint="DE123456788", endpoint_scheme="9930",
            address="Musterstr. 1", address2="EG", postalzone="10115", city="Berlin", province="Berlin")
        inv.seller_party.bank_info = BankInfo(iban="DE79000000001234567890", bic="COBADEFFXXX"); inv.payment_means_code = "31"
        inv.buyer_party = Entity(name="Kunde AG", tax_scheme="VAT", tax_scheme_id="DE987654321", country="DE", party_legal_entity_id="DE987654321",
            registration_name="Kunde AG", mail="kunde@example.com", endpoint="DE987654321", endpoint_scheme="9930",
            address="Kundenweg 2", postalzone="80331", address2="EG", city="München", province="Bayern")
        inv.issue_date = "2026-10-18"; inv.due_date = "2026-11-18"
        for l in o['lines']:
            inv.add_line(InvoiceLine(quantity=int(l['qty']), unit_code="EA", price=l['price'], item_name=l['name'], currency="EUR",
                                     tax_percent=float(D(l['rate']) / 100), tax_category="S"))
        disc = sum((D(a) for l in o['lines'] for a in l['allow']), D(0))
        if disc: inv.discount_amount = str(disc)
        x = inv.to_xml()
    except Exception as e:
        nerr += 1; print('error', o['id'], repr(e)[:200], file=sys.stderr); continue
    open(f"{out}/{TAG}__{o['id']}.xml", "w", encoding="utf-8").write(x if isinstance(x, str) else x.decode()); n += 1
print('en16931py done:', n, 'errors:', nerr)
