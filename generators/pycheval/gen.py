"""PyCheval 0.3.3 driver (Factur-X EN 16931 profile, CII): writes the reference EN 16931 totals (the library computes no totals).
usage: python3 gen.py <corpus_dir> <out_dir>"""
import datetime, os, sys
from decimal import Decimal as D
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'common'))
from carts import load
from shop_sim import S_en16931
from pycheval import (EN16931Invoice, EN16931LineItem, LineAllowance, TradeParty, PostalAddress, Tax, PaymentMeans,
                      PaymentTerms, BankAccount, Money, generate_xml)
from pycheval.type_codes import DocumentTypeCode, PaymentMeansCode
from pycheval.quantities import QuantityCode
corpus, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True); TAG = 'pycheval0.3.3-en16931+ref-totals'
E_ = lambda x: Money(D(x).quantize(D('0.01')), "EUR"); nerr = 0
for seg in ('b2b', 'b2c'):
    for o in load(f'{corpus}/carts_{seg}.json'):
        L, tax, T, _ = S_en16931(o, rounding=True)
        items = [EN16931LineItem(id=str(i), name=l['name'], net_price=E_(l['net_price']), billed_quantity=(D(l['qty']), QuantityCode.PIECE),
                                 billed_total=E_(l['line_net']), tax_rate=D(l['rate']),
                                 allowances=[LineAllowance(E_(a), reason="Rabatt") for a in l.get('allow', [])]) for i, l in enumerate(L, 1)]
        try:
            inv = EN16931Invoice(invoice_number=o['id'], type_code=DocumentTypeCode.INVOICE, invoice_date=datetime.date(2026, 10, 18),
                seller=TradeParty("Muster Shop GmbH", PostalAddress("DE", None, "10115", "Berlin", "Musterstr. 1"), vat_id="DE123456788"),
                buyer=TradeParty("Kunde AG", PostalAddress("DE", None, "80331", "München")), currency_code="EUR",
                line_total_amount=E_(T['line']), tax_basis_total_amount=E_(T['basis']), tax_total_amounts=[E_(T['tax'])],
                grand_total_amount=E_(T['grand']), due_payable_amount=E_(T['due']),
                rounding_amount=E_(T['rounding']) if T.get('rounding') is not None else None,
                tax=[Tax(E_(x['tax']), E_(x['basis']), D(x['rate'])) for x in tax], buyer_reference="04011000-12345-03",
                payment_means=[PaymentMeans(PaymentMeansCode.SEPA_CREDIT_TRANSFER, BankAccount("DE79000000001234567890", None, None))],
                payment_terms=PaymentTerms(description="Zahlbar sofort"), line_items=items)
            x = generate_xml(inv)
        except Exception as e:
            nerr += 1; print('model-error', o['id'], repr(e)[:200], file=sys.stderr); continue
        open(f"{out}/{TAG}__{o['id']}.xml", "w", encoding="utf-8").write(x)
print('pycheval done, model errors:', nerr)
