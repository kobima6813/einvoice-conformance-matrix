# Odoo 19.0 driver. Run inside "odoo-bin shell -d <db>" with account_edi_ubl_cii and l10n_de installed.
# env: N (carts per file), ROUND (round_per_line|round_globally), OUT (output dir), CARTS (comma list of carts_*.json)
import json,os,base64
from decimal import Decimal as D
N=int(os.environ.get('N','20')); ROUND=os.environ.get('ROUND','round_per_line'); OUT=os.environ['OUT']
os.makedirs(OUT+'/cii',exist_ok=True); os.makedirs(OUT+'/ubl',exist_ok=True)
Company=env['res.company']
co=Company.search([('name','=','Shop DE GmbH')],limit=1)
de=env.ref('base.de')
if not co:
    co=Company.create(dict(name='Shop DE GmbH',country_id=de.id,currency_id=env.ref('base.EUR').id,vat='DE123456788',street='Hauptstr. 1',zip='10115',city='Berlin',email='shop@example.de',phone='+49301234567'))
    env.user.company_ids|=co
    env['account.chart.template'].try_loading('de_skr03',co,install_demo=False)
    env.cr.commit()
env=env(context=dict(env.context,allowed_company_ids=[co.id]))
co=co.with_env(env); co.tax_calculation_rounding_method=ROUND
bank=env['res.partner.bank'].search([('partner_id','=',co.partner_id.id)],limit=1) or env['res.partner.bank'].create(dict(partner_id=co.partner_id.id,acc_number='DE89370400440532013000',allow_out_payment=True))
cust=env['res.partner'].search([('name','=','Kunde AG'),('company_id','in',[False,co.id])],limit=1) or env['res.partner'].create(dict(name='Kunde AG',is_company=True,country_id=de.id,vat='DE811907980',street='Marktplatz 5',zip='80331',city='München',email='ap@kunde.example',peppol_eas='9930',peppol_endpoint='DE811907980'))
def tax(rate):
    t=env['account.tax'].search([('company_id','=',co.id),('type_tax_use','=','sale'),('amount','=',rate),('amount_type','=','percent'),('price_include_override','=','tax_included')],limit=1)
    if not t:
        base=env['account.tax'].search([('company_id','=',co.id),('type_tax_use','=','sale'),('amount','=',rate),('amount_type','=','percent')],limit=1)
        t=base.copy(dict(name=f'{rate}% incl',price_include_override='tax_included'))
    return t
T={'19':tax(19),'7':tax(7)}
FMTS=[('ubl','account.edi.xml.ubl_bis3','bis3'),('ubl','account.edi.xml.ubl_de','xr'),('cii','account.edi.xml.cii','fx')]
rows=[]
for path in os.environ['CARTS'].split(','):
  for c in json.load(open(path))[:N]:
    lines=[(0,0,dict(name=l['name'],quantity=l['qty'],price_unit=float(l['unit_gross']),discount=float(c['pct']),tax_ids=[(6,0,T[l['rate']].ids)])) for l in c['lines']]
    if D(c['ship']): lines.append((0,0,dict(name='Versand',quantity=1,price_unit=float(c['ship']),tax_ids=[(6,0,T['19'].ids)])))
    mv=env['account.move'].create(dict(move_type='out_invoice',partner_id=cust.id,invoice_date='2026-10-01',partner_bank_id=bank.id,invoice_line_ids=lines,ref='PO-'+c['id']))
    mv.action_post()
    r=dict(id=c['id'],paid=c['paid'],odoo_total=str(D(str(mv.amount_total)).quantize(D('0.01'))),round=ROUND)
    for kind,model,tag in FMTS:
        xml,errs=env[model]._export_invoice(mv)
        fn=f"odoo19-{tag}-{ROUND}__{c['id']}.xml"; open(f"{OUT}/{kind}/{fn}",'wb').write(xml); r[tag]=fn; r[tag+'_errs']=sorted(errs)
    rows.append(r)
env.cr.commit()
json.dump(rows,open(f"{OUT}/gen_{ROUND}.json",'w'),indent=0); print('DONE',len(rows))
