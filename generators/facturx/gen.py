"""akretion factur-x 7.7 row (France): drafthorse builds an EN 16931 CII with reference totals for a French seller/buyer,
factur-x embeds it into a PDF (generate_from_binary, level en16931, its own XSD check), then the XML is read back
from the PDF with get_xml_from_pdf and that extracted XML is what gets validated.
usage: python3 gen.py <corpus_dir> <out_dir>"""
import datetime, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'common'))
from carts import load
from shop_sim import S_en16931
from drafthorse.models.accounting import ApplicableTradeTax, TradeAllowanceCharge
from drafthorse.models.document import Document
from drafthorse.models.party import TaxRegistration
from drafthorse.models.payment import PaymentMeans, PaymentTerms
from drafthorse.models.tradelines import LineItem
import io, facturx
from pypdf import PdfWriter
_w = PdfWriter(); _w.add_blank_page(595, 842); _b = io.BytesIO(); _w.write(_b); BLANK = _b.getvalue()
corpus, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True); TAG = 'facturx7.7-fr-en16931+ref-totals'
nerr = nfx = ndiff = 0
for seg in ('b2b', 'b2c'):
    for o in load(f'{corpus}/carts_{seg}.json'):
        L, tax, T, _ = S_en16931(o, rounding=True)
        d = Document(); d.context.guideline_parameter.id = "urn:cen.eu:en16931:2017"
        d.header.id = o['id']; d.header.type_code = "380"; d.header.issue_date_time = datetime.date(2026, 10, 18)
        s = d.trade.agreement.seller; s.name = "Boutique Exemple SAS"; s.address.country_id = "FR"; s.address.postcode = "75002"; s.address.city_name = "Paris"; s.address.line_one = "1 rue de la Paix"
        s.tax_registrations.add(TaxRegistration(id=("VA", "FR32123456789")))
        b = d.trade.agreement.buyer; b.name = "Client SA"; b.address.country_id = "FR"; b.address.postcode = "69001"; b.address.city_name = "Lyon"
        d.trade.agreement.buyer_reference = "04011000-12345-03"
        st = d.trade.settlement; st.currency_code = "EUR"; pm = PaymentMeans(type_code="58"); pm.payee_account.iban = "FR7630006000011234567890189"; st.payment_means.add(pm)
        t = PaymentTerms(); t.description = "Paiement à réception"; st.terms.add(t)
        for i, l in enumerate(L, 1):
            li = LineItem(); li.document.line_id = str(i); li.product.name = l['name']
            li.agreement.net.amount = l['net_price']; li.delivery.billed_quantity = (l['qty'], "H87")
            li.settlement.trade_tax.type_code = "VAT"; li.settlement.trade_tax.category_code = "S"; li.settlement.trade_tax.rate_applicable_percent = l['rate']
            for a in l.get('allow', []):
                ac = TradeAllowanceCharge(); ac.indicator = False; ac.actual_amount = a; ac.reason = "Remise"; li.settlement.allowance_charge.add(ac)
            li.settlement.monetary_summation.total_amount = l['line_net']; d.trade.items.add(li)
        for x in tax:
            tt = ApplicableTradeTax(); tt.calculated_amount = x['tax']; tt.basis_amount = x['basis']; tt.type_code = "VAT"; tt.category_code = "S"; tt.rate_applicable_percent = x['rate']; st.trade_tax.add(tt)
        m = st.monetary_summation; m.line_total = T['line']; m.tax_basis_total = T['basis']; m.tax_total = (T['tax'], "EUR")
        if T.get('rounding') is not None: m.rounding_amount = T['rounding']
        m.grand_total = T['grand']; m.due_amount = T['due']
        try: x = d.serialize(schema="FACTUR-X_EN16931")
        except Exception as e:
            nerr += 1; x = d.serialize(schema=None); print('schema-error', o['id'], str(e)[:200], file=sys.stderr)
        try: pdf = facturx.generate_from_binary(BLANK, x, flavor='factur-x', level='en16931', check_xsd=True)
        except Exception as e:
            nfx += 1; print('facturx-error', o['id'], str(e)[:200], file=sys.stderr); pdf = facturx.generate_from_binary(BLANK, x, flavor='factur-x', level='en16931', check_xsd=False)
        _, xml = facturx.get_xml_from_pdf(pdf, check_xsd=False)
        if xml != x: ndiff += 1
        open(f"{out}/{TAG}__{o['id']}.xml", "wb").write(xml)
print('facturx done, drafthorse schema errors:', nerr, 'factur-x XSD rejects:', nfx, 'xml changed by PDF round-trip:', ndiff)
