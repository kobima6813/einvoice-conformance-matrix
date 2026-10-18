# Synthetic shop simulator: tax-inclusive carts (Shopify-like rounding, approximated) and
# several integrator strategies for turning a cart into EN 16931 amounts.
# The matrix uses cart() and S_en16931(); the other strategies are kept for experiments.
import random, json, os, sys
from decimal import Decimal as D, ROUND_HALF_UP
from ciiwriter import write
C=D('0.01'); r2=lambda x:x.quantize(C,ROUND_HALF_UP)
def cart(rng):
    lines=[]
    for k in range(rng.choice([1,1,2,2,3,3,4,5,6])):
        euros=rng.choice([rng.randint(1,30),rng.randint(1,30),rng.randint(30,200)])
        cents=rng.choice(['99','95','90','00','49'])
        rate=D(19) if rng.random()<0.8 else D(7)
        lines.append(dict(name=f"Artikel {k+1}",unit_gross=D(f"{euros-1 if cents!='00' and euros>1 else euros}.{cents}"),qty=(rng.choice([1,1,1,2,2,3,4]) if os.environ.get('QTY','b2c')=='b2c' else rng.choice([1,2,5,10,12,20,24,50,100])),rate=rate))
    pct=rng.choice([None,None,None,D(10),D(15),D(20)])
    ship=D('4.90') if rng.random()<0.7 else None
    # shop side (Shopify-like): discount allocated per line, rounded, remainder on last line; tax per line, rounded
    sub=[l['unit_gross']*l['qty'] for l in lines]
    if pct:
        disc_total=r2(sum(sub)*pct/100); alloc=[r2(s*pct/100) for s in sub]; alloc[-1]+=disc_total-sum(alloc)
    else: alloc=[D(0)]*len(lines)
    for l,s,a in zip(lines,sub,alloc):
        l['gross']=s-a; l['disc_gross']=a; l['shop_tax']=r2(l['gross']*l['rate']/(100+l['rate']))
    paid=sum(l['gross'] for l in lines)+(ship or 0)
    ship_tax=r2(ship*19/119) if ship else D(0)
    return dict(lines=lines,ship=ship,ship_tax=ship_tax,paid=paid,pct=pct)
def breakdown(items):  # items: (cat,rate,basis)
    g={}
    for c,r,b in items: g[(c,r)]=g.get((c,r),D(0))+b
    return g
def S_copy(o):  # copy shop's per-line net and per-line tax
    L=[];taxsum={}
    for l in o['lines']:
        net=l['gross']-l['shop_tax']; L.append(dict(name=l['name'],qty=D(l['qty']),net_price=r2(net/l['qty']),line_net=net,cat='S',rate=l['rate']))
        taxsum[l['rate']]=taxsum.get(l['rate'],D(0))+l['shop_tax']
    if o['ship']:
        net=o['ship']-o['ship_tax']; L.append(dict(name='Versand',qty=D(1),net_price=net,line_net=net,cat='S',rate=D(19))); taxsum[D(19)]=taxsum.get(D(19),D(0))+o['ship_tax']
    g=breakdown([(x['cat'],x['rate'],x['line_net']) for x in L])
    tax=[dict(cat='S',rate=r,basis=b,tax=taxsum[r]) for (c,r),b in g.items()]
    line=sum(x['line_net'] for x in L); tt=sum(t['tax'] for t in tax)
    return L,tax,dict(line=line,basis=line,tax=tt,grand=line+tt,due=line+tt),[]
def S_en16931(o,rounding=False):  # net unit price from gross, discount as line allowance, VAT per category (EN16931 way)
    L=[]
    for l in o['lines']:
        up=r2(l['unit_gross']*100/(100+l['rate'])); allow=r2(l['disc_gross']*100/(100+l['rate']))
        L.append(dict(name=l['name'],qty=D(l['qty']),net_price=up,allow=[allow] if allow else [],line_net=up*l['qty']-allow,cat='S',rate=l['rate']))
    if o['ship']:
        up=r2(o['ship']*100/119); L.append(dict(name='Versand',qty=D(1),net_price=up,line_net=up,cat='S',rate=D(19)))
    g=breakdown([(x['cat'],x['rate'],x['line_net']) for x in L])
    tax=[dict(cat='S',rate=r,basis=b,tax=r2(b*r/100)) for (c,r),b in g.items()]
    line=sum(x['line_net'] for x in L); tt=sum(t['tax'] for t in tax); grand=line+tt
    T=dict(line=line,basis=line,tax=tt,grand=grand,due=grand)
    if rounding and grand!=o['paid']:
        T['rounding']=o['paid']-grand; T['due']=o['paid']
    return L,tax,T,[]
def S_en16931_4dp(o):  # unit net price kept to 4 decimals (BT-146 allows it), line net rounded to 2
    C4=D('0.0001'); L=[]
    for l in o['lines']:
        up=(l['unit_gross']*100/(100+l['rate'])).quantize(C4,ROUND_HALF_UP); allow=r2(l['disc_gross']*100/(100+l['rate']))
        L.append(dict(name=l['name'],qty=D(l['qty']),net_price=up,allow=[allow] if allow else [],line_net=r2(up*l['qty'])-allow,cat='S',rate=l['rate']))
    if o['ship']:
        up=r2(o['ship']*100/119); L.append(dict(name='Versand',qty=D(1),net_price=up,line_net=up,cat='S',rate=D(19)))
    g=breakdown([(x['cat'],x['rate'],x['line_net']) for x in L])
    tax=[dict(cat='S',rate=r,basis=b,tax=r2(b*r/100)) for (c,r),b in g.items()]
    line=sum(x['line_net'] for x in L); tt=sum(t['tax'] for t in tax)
    return L,tax,dict(line=line,basis=line,tax=tt,grand=line+tt,due=line+tt),[]
def S_float(o):  # same as S_en16931 but binary floats, printed with repr (JS/Python default)
    L,tax,T,_=S_en16931(o)
    f=lambda x:float(x)
    Lf=[]
    for l in o['lines']:
        up=round(f(l['unit_gross'])/(1+f(l['rate'])/100),2); allow=round(f(l['disc_gross'])/(1+f(l['rate'])/100),2)
        Lf.append(dict(name=l['name'],qty=l['qty'],net_price=up,allow=[allow] if allow else [],line_net=up*l['qty']-allow,cat='S',rate=f(l['rate'])))
    if o['ship']:
        up=round(f(o['ship'])/1.19,2); Lf.append(dict(name='Versand',qty=1,net_price=up,line_net=up,cat='S',rate=19.0))
    g={}
    for x in Lf: g[x['rate']]=g.get(x['rate'],0.0)+x['line_net']
    tax=[dict(cat='S',rate=r,basis=b,tax=round(b*r/100,2)) for r,b in g.items()]
    line=sum(x['line_net'] for x in Lf); tt=sum(t['tax'] for t in tax)
    return Lf,tax,dict(line=line,basis=line,tax=tt,grand=line+tt,due=line+tt),[]
if __name__=='__main__':
    N=int(sys.argv[1]) if len(sys.argv)>1 else 300
    rng=random.Random(42); out=os.environ.get('OUT','out/shop_sim'); os.makedirs(out,exist_ok=True); meta=[]
    import ciiwriter
    ciiwriter.amt=lambda x: repr(x) if isinstance(x,float) else (str(x) if isinstance(x,int) else format(x,'f'))
    for i in range(N):
        o=cart(rng)
        for name,fn in [('copy',S_copy),('en16931',S_en16931),('en16931_rounding',lambda o:S_en16931(o,True)),('float',S_float),('en16931_4dp',S_en16931_4dp)]:
            L,tax,T,ac=fn(o); fid=f"c{i:04d}_{name}"
            open(f"{out}/{fid}.xml",'w').write(write(dict(id=fid,lines=L,tax=tax,tot=T,doc_ac=ac)))
            inc=sum(1 for x in L if (round(float(x['net_price'])*float(x['qty']),2)-sum(map(float,x.get('allow',[]))) - float(x['line_net']))**2>1e-8)
            meta.append(dict(price_incons=inc,id=fid,cart=i,strategy=name,paid=str(o['paid']),grand=str(T['grand']),due=str(T['due']),nlines=len(o['lines']),pct=str(o['pct']),ship=bool(o['ship'])))
    json.dump(meta,open(out+'_meta.json','w'),indent=0)
    print(len(meta))
