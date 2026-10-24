"""French scenarios via drafthorse 2025.2.0 (CII) + akretion factur-x 7.7 (PDF embed, XSD check, read-back).
usage: python3 gen_drafthorse.py scenarios.json <out_dir>   -> <out_dir>/<profile>/drafthorse__<id>.xml + gen_log.json"""
import datetime, io, json, os, sys
from decimal import Decimal as D
from drafthorse.models.accounting import ApplicableTradeTax
from drafthorse.models.document import Document
from drafthorse.models.note import IncludedNote
from drafthorse.models.party import TaxRegistration
from drafthorse.models.payment import PaymentMeans, PaymentTerms
from drafthorse.models.tradelines import LineItem
import facturx
from pypdf import PdfWriter
_w = PdfWriter(); _w.add_blank_page(595, 842); _b = io.BytesIO(); _w.write(_b); BLANK = _b.getvalue()
S = json.load(open(sys.argv[1])); out = sys.argv[2]
PROF = {'EN16931': ('urn:cen.eu:en16931:2017', 'FACTUR-X_EN16931', 'en16931'),
        'EXTENDED': ('urn:cen.eu:en16931:2017#conformant#urn:factur-x.eu:1p0:extended', 'FACTUR-X_EXTENDED', 'extended')}
log = []
for prof, (guid, schema, level) in PROF.items():
    os.makedirs(f'{out}/{prof}', exist_ok=True)
    for sc in S['scenarios']:
        e = dict(generator='drafthorse2025.2.0+factur-x7.7', profile=prof, scenario=sc['id'], errors=[])
        sl, by = S['seller'], S[sc['buyer']]
        d = Document(); d.context.guideline_parameter.id = guid
        d.header.id = 'F-' + sc['id'][:4]; d.header.type_code = '380'; d.header.issue_date_time = datetime.date(2026, 10, 20)
        for n in S['notes']:
            note = IncludedNote(); note.subject_code = n['subject']; note.content.add(n['text']) if hasattr(note.content, 'add') else setattr(note, 'content', n['text']); d.header.notes.add(note)
        s = d.trade.agreement.seller; s.name = sl['name']
        s.global_id.add(('0009', sl['siret']))
        s.legal_organization.id = ('0002', sl['siren'])
        s.electronic_address.uri_ID = ('0225', sl['siren'])
        s.address.line_one = sl['street']; s.address.postcode = sl['postcode']; s.address.city_name = sl['city']; s.address.country_id = 'FR'
        s.tax_registrations.add(TaxRegistration(id=('VA', sl['vat'])))
        b = d.trade.agreement.buyer; b.name = by['name']
        if 'siren' in by:
            b.legal_organization.id = ('0002', by['siren']); b.electronic_address.uri_ID = ('0225', by['siren'])
        else:
            b.electronic_address.uri_ID = ('9930', by['vat'])
        b.address.line_one = by['street']; b.address.postcode = by['postcode']; b.address.city_name = by['city']; b.address.country_id = by['country']
        b.tax_registrations.add(TaxRegistration(id=('VA', by['vat'])))
        if any(t['cat'] == 'K' for t in sc['tax']):
            d.trade.delivery.ship_to.address.country_id = by['country']
            d.trade.delivery.event.occurrence = datetime.date(2026, 10, 19)
        st = d.trade.settlement; st.currency_code = 'EUR'
        pm = PaymentMeans(type_code='58'); pm.payee_account.iban = 'FR7630006000011234567890189'; st.payment_means.add(pm)
        t = PaymentTerms(); t.description = 'Paiement à 30 jours'; t.due = datetime.date(2026, 11, 19); st.terms.add(t)
        for i, l in enumerate(sc['lines'], 1):
            li = LineItem(); li.document.line_id = str(i); li.product.name = l['name']
            li.agreement.net.amount = D(l['price']); li.delivery.billed_quantity = (D(l['qty']), 'H87')
            li.settlement.trade_tax.type_code = 'VAT'; li.settlement.trade_tax.category_code = l['cat']; li.settlement.trade_tax.rate_applicable_percent = D(l['rate'])
            li.settlement.monetary_summation.total_amount = D(l['qty']) * D(l['price']); d.trade.items.add(li)
        for x in sc['tax']:
            tt = ApplicableTradeTax(); tt.calculated_amount = D(x['tax']); tt.basis_amount = D(x['basis']); tt.type_code = 'VAT'; tt.category_code = x['cat']; tt.rate_applicable_percent = D(x['rate'])
            if 'reason' in x: tt.exemption_reason = x['reason']; tt.exemption_reason_code = x['code']
            st.trade_tax.add(tt)
        T = sc['totals']; m = st.monetary_summation
        m.line_total = D(T['line']); m.tax_basis_total = D(T['line']); m.tax_total = (D(T['tax']), 'EUR'); m.grand_total = D(T['grand']); m.due_amount = D(T['grand'])
        try: x = d.serialize(schema=schema)
        except Exception as ex:
            e['errors'].append('drafthorse-xsd: ' + str(ex)[:300]); x = d.serialize(schema=None)
        try: pdf = facturx.generate_from_binary(BLANK, x, flavor='factur-x', level=level, check_xsd=True)
        except Exception as ex:
            e['errors'].append('factur-x-xsd: ' + str(ex)[:300]); pdf = facturx.generate_from_binary(BLANK, x, flavor='factur-x', level=level, check_xsd=False)
        _, xml = facturx.get_xml_from_pdf(pdf, check_xsd=False)
        e['pdf_roundtrip_identical'] = (xml == x)
        fn = f'{out}/{prof}/drafthorse__{sc["id"]}.xml'; open(fn, 'wb').write(xml); e['file'] = fn; log.append(e)
json.dump(log, open(f'{out}/gen_log_drafthorse.json', 'w'), indent=1, ensure_ascii=False)
print('drafthorse done', sum(1 for e in log if e['errors']), 'with generator errors of', len(log))
