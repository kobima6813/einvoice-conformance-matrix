# Cross-ruleset oracle: KoSIT (XRechnung/EN16931) + Peppol BIS 3 schematron + exact-arithmetic checks.
import json,re,glob,collections,sys
from decimal import Decimal as D, ROUND_HALF_UP
import xml.etree.ElementTree as ET
r2=lambda x:x.quantize(D('0.01'),ROUND_HALF_UP)
NS={'ram':'urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100','rsm':'urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100',
    'cbc':'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2','cac':'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2'}
def dec(e): 
    try: return D(e.text.strip()) if e is not None and e.text and e.text.strip() else None
    except Exception: return None
def arith_cii(root):
    out=dict(lines=0,line_exact_fail=0,line_slack_fail=0,vat_exact_fail=0,vat_cats=0)
    for li in root.iter(f"{{{NS['ram']}}}IncludedSupplyChainTradeLineItem"):
        q=dec(li.find('.//ram:SpecifiedLineTradeDelivery/ram:BilledQuantity',NS)); p=dec(li.find('.//ram:NetPriceProductTradePrice/ram:ChargeAmount',NS))
        b=dec(li.find('.//ram:NetPriceProductTradePrice/ram:BasisQuantity',NS)) or D(1); lt=dec(li.find('.//ram:SpecifiedTradeSettlementLineMonetarySummation/ram:LineTotalAmount',NS))
        if None in (q,p,lt) or b==0: continue
        ac=D(0)
        for a in li.findall('.//ram:SpecifiedLineTradeSettlement/ram:SpecifiedTradeAllowanceCharge',NS):
            amt=dec(a.find('ram:ActualAmount',NS)) or D(0); ind=(a.findtext('ram:ChargeIndicator/{urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100}Indicator',default='',namespaces=NS) or '').strip().lower()
            ac+= amt if ind=='true' else -amt
        ex=q*p/b+ac; out['lines']+=1
        if r2(ex)!=lt: out['line_exact_fail']+=1
        if abs(ex-lt)>D('0.02'): out['line_slack_fail']+=1
    st=root.find('.//ram:ApplicableHeaderTradeSettlement',NS)
    if st is not None:
        for t in st.findall('ram:ApplicableTradeTax',NS):
            ca=dec(t.find('ram:CalculatedAmount',NS)); ba=dec(t.find('ram:BasisAmount',NS)); rt=dec(t.find('ram:RateApplicablePercent',NS))
            if None in (ca,ba,rt): continue
            out['vat_cats']+=1
            if r2(ba*rt/100)!=ca: out['vat_exact_fail']+=1
    return out
def arith_ubl(root):
    out=dict(lines=0,line_exact_fail=0,line_slack_fail=0,vat_exact_fail=0,vat_cats=0)
    for li in list(root.findall('cac:InvoiceLine',NS))+list(root.findall('cac:CreditNoteLine',NS)):
        q=dec(li.find('cbc:InvoicedQuantity',NS)) or dec(li.find('cbc:CreditedQuantity',NS)); p=dec(li.find('cac:Price/cbc:PriceAmount',NS))
        b=dec(li.find('cac:Price/cbc:BaseQuantity',NS)) or D(1); lt=dec(li.find('cbc:LineExtensionAmount',NS))
        if None in (q,p,lt) or b==0: continue
        ac=D(0)
        for a in li.findall('cac:AllowanceCharge',NS):
            amt=dec(a.find('cbc:Amount',NS)) or D(0); ind=(a.findtext('cbc:ChargeIndicator',default='',namespaces=NS) or '').strip().lower()
            ac+= amt if ind=='true' else -amt
        ex=q*p/b+ac; out['lines']+=1
        if r2(ex)!=lt: out['line_exact_fail']+=1
        if abs(ex-lt)>D('0.02'): out['line_slack_fail']+=1
    for t in root.findall('cac:TaxTotal/cac:TaxSubtotal',NS):
        ca=dec(t.find('cbc:TaxAmount',NS)); ba=dec(t.find('cbc:TaxableAmount',NS)); rt=dec(t.find('cac:TaxCategory/cbc:Percent',NS))
        if None in (ca,ba,rt): continue
        out['vat_cats']+=1
        if r2(ba*rt/100)!=ca: out['vat_exact_fail']+=1
    return out
def kosit(fid):
    s=open(f'out/kosit/{fid}-report.xml').read()
    acc='accept' if '<rep:accept' in s else 'reject'
    scen=re.search(r'<rep:scenarioMatched>\s*<s:name>([^<]*)',s) or re.search(r'<s:name>([^<]*)</s:name>',s)
    errs=sorted({c for l,c in re.findall(r'<rep:message[^>]*level="(\w+)"[^>]*code="([^"]+)"',s) if l=='error'})
    nomatch='noScenarioMatched' in s
    return acc,(scen.group(1) if scen else None),errs,nomatch
CTX={'PEPPOL-EN16931-R001','PEPPOL-EN16931-R004','PEPPOL-EN16931-R007','PEPPOL-EN16931-R020','PEPPOL-EN16931-R010','PEPPOL-EN16931-R003','PEPPOL-EN16931-R005','PEPPOL-EN16931-R002','PEPPOL-EN16931-R008','PEPPOL-EN16931-R006'}
def peppol(fid,kind):
    try: s=open(f'out/peppol_{kind}/{fid}.xml').read()
    except FileNotFoundError: return None
    return sorted(set(re.findall(r'failed-assert[^>]*\bid="([^"]+)"',s)))
def cen(fid,kind):
    try: s=open(f'out/cen_{kind}/{fid}.xml').read()
    except FileNotFoundError: return None
    return sorted(set(re.findall(r'failed-assert[^>]*\bid="([^"]+)"',s)))
idx=json.load(open('inputs/index.json')); rows=[]
for x in idx:
    fid=x['file'][:-4]; root=ET.parse(f"inputs/{x['kind']}/{x['file']}").getroot()
    prof=(root.findtext('.//rsm:ExchangedDocumentContext/ram:GuidelineSpecifiedDocumentContextParameter/ram:ID',namespaces=NS) or root.findtext('cbc:CustomizationID',namespaces=NS) or '').strip()
    ar=arith_cii(root) if x['kind']=='cii' else arith_ubl(root)
    acc,scen,errs,nomatch=kosit(fid); pp=peppol(fid,x['kind'])
    rows.append(dict(file=x['file'],origin=x['origin'],kind=x['kind'],profile=prof,kosit=acc,kosit_nomatch=nomatch,kosit_errors=errs,peppol_fails=pp,cen_fails=cen(fid,x['kind']),**ar))
json.dump(rows,open('out/oracle_rows.json','w'),indent=0)
