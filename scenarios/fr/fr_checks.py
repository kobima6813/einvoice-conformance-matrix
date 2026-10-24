"""Collect validator verdicts + French field checks into <out>/fr_results.json.
French checks (ours, structural; they test that the field the French rules ask for survives into the XML):
 F-SIREN   seller BT-30 SpecifiedLegalOrganization/ID schemeID=0002, 9 digits, Luhn-valid
 F-SIRET   seller BT-29 GlobalID schemeID=0009, 14 digits, starts with the SIREN
 F-BSIREN  buyer BT-47 schemeID=0002 when the buyer is French
 F-EADDR   seller BT-34 URIID schemeID=0225 (SIREN-based routing id)
 F-NOTES   header notes with subject codes PMT, PMD, AAB (late-payment penalties, EUR 40 recovery fee, early-payment discount)
 F-EXEMPT  every E/AE/K header VAT breakdown carries BT-120 text and BT-121 code, matching the scenario
"""
import glob, json, os, re, sys
from lxml import etree
O, T = sys.argv[1], sys.argv[2]
NS = {'ram': 'urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100',
      'rsm': 'urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100', 'svrl': 'http://purl.oclc.org/dsdl/svrl'}
H = os.path.dirname(os.path.abspath(__file__)); S = json.load(open(f'{H}/scenarios.json')); SC = {s['id']: s for s in S['scenarios']}
XSD = {p: etree.XMLSchema(etree.parse(f'{T}/optional/facturx/{p}/1xsd/Factur-X_{p}.xsd')) for p in ('EN16931', 'EXTENDED')}
def luhn(s):
    t = 0
    for i, c in enumerate(reversed(s)):
        d = int(c) * (2 if i % 2 else 1); t += d - 9 if d > 9 else d
    return t % 10 == 0
def svrl(path):
    if not os.path.exists(path): return None
    r = etree.parse(path); out = []
    for f in r.iterfind('.//svrl:failed-assert', NS):
        if (f.get('flag') or 'fatal') in ('fatal', 'error'): out.append(f.get('id') or f.get('test')[:60])
    return sorted(set(out))
def kosit(path):
    if not os.path.exists(path): return None
    s = open(path, encoding='utf-8').read()
    errs = sorted({c for l, c in re.findall(r'<rep:message[^>]*level="(\w+)"[^>]*code="([^"]+)"', s) if l == 'error'})
    m = re.search(r'<rep:scenarioMatched>\s*<s:name>([^<]*)', s)
    if 'noScenarioMatched' in s: return dict(accept=None, scenario=None, errors=[], note='no KoSIT scenario for this profile (not applicable)')
    return dict(accept='<rep:accept' in s, scenario=m.group(1) if m else None, errors=errs)
logs = []
for f in glob.glob(f'{O}/gen_log_*.json'): logs += json.load(open(f))
rows = []
for e in logs:
    r = dict(generator=e['generator'], profile=e['profile'], scenario=e['scenario'], generator_errors=e['errors'])
    fn = e.get('file')
    if not fn or not os.path.exists(fn): r['verdict'] = 'not generated'; rows.append(r); continue
    base = os.path.basename(fn)[:-4]; doc = etree.parse(fn); x = lambda q: doc.xpath(q, namespaces=NS)
    xs = XSD[e['profile']]; r['xsd_valid'] = xs.validate(doc); r['xsd_errors'] = [str(m.message)[:160] for m in xs.error_log][:3]
    r['cen_errors'] = svrl(f'{O}/val/cen_{e["profile"]}/{base}.xml')
    r['fx_extended_errors'] = svrl(f'{O}/val/fx_EXTENDED/{base}.xml') if e['profile'] == 'EXTENDED' else None
    r['kosit'] = kosit(f'{O}/val/kosit_{e["profile"]}/{base}-report.xml')
    sc = SC[e['scenario']]; sl = S['seller']; by = S[sc['buyer']]; fr = {}
    seller = '//ram:SellerTradeParty'; buyer = '//ram:BuyerTradeParty'
    v = x(f'{seller}/ram:SpecifiedLegalOrganization/ram:ID[@schemeID="0002"]/text()')
    fr['F-SIREN'] = bool(v) and v[0] == sl['siren'] and luhn(v[0])
    v = x(f'{seller}/ram:GlobalID[@schemeID="0009"]/text()'); fr['F-SIRET'] = bool(v) and v[0] == sl['siret'] and v[0].startswith(sl['siren'])
    if 'siren' in by:
        v = x(f'{buyer}/ram:SpecifiedLegalOrganization/ram:ID[@schemeID="0002"]/text()'); fr['F-BSIREN'] = bool(v) and v[0] == by['siren']
    v = x(f'{seller}/ram:URIUniversalCommunication/ram:URIID[@schemeID="0225"]/text()'); fr['F-EADDR'] = bool(v) and v[0] == sl['siren']
    subj = set(x('//rsm:ExchangedDocument/ram:IncludedNote/ram:SubjectCode/text()')); fr['F-NOTES'] = {'PMT', 'PMD', 'AAB'} <= subj
    ex = [t for t in sc['tax'] if 'reason' in t]
    if ex:
        ok = True
        for t in ex:
            hit = [n for n in x('//ram:ApplicableHeaderTradeSettlement/ram:ApplicableTradeTax') if n.findtext('ram:CategoryCode', namespaces=NS) == t['cat']]
            ok &= bool(hit) and hit[0].findtext('ram:ExemptionReason', namespaces=NS) == t['reason'] and hit[0].findtext('ram:ExemptionReasonCode', namespaces=NS) == t['code']
        fr['F-EXEMPT'] = ok
    r['fr_checks'] = fr
    fails = []
    if not r['xsd_valid']: fails.append('XSD')
    if r['cen_errors']: fails.append('CEN:' + ','.join(r['cen_errors']))
    if r['fx_extended_errors']: fails.append('FX-EXT:' + ','.join(r['fx_extended_errors']))
    if r['kosit'] and r['kosit']['accept'] is False: fails.append('KoSIT:' + ','.join(r['kosit']['errors']))
    fails += [k for k, ok in fr.items() if not ok]
    r['failures'] = fails; r['verdict'] = 'pass' if not fails and not e['errors'] else 'fail'
    rows.append(r)
rows.sort(key=lambda r: (r['generator'], r['profile'], r['scenario']))
json.dump(rows, open(f'{O}/fr_results.json', 'w'), indent=1, ensure_ascii=False)
for r in rows: print(r['generator'], r['profile'], r['scenario'], r['verdict'], r.get('failures'))
