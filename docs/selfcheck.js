/* E-Invoice Conformance Lab self-check. Runs entirely in your browser; the file is never uploaded.
   Checks a SUBSET of EN 16931 business rules (see RULES list on the page). Not a substitute for KoSIT/CEN/Peppol validation. */
(function(){
const NS={cbc:'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',cac:'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
rsm:'urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100',ram:'urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100',udt:'urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100'};
function res(x){return NS[x]||null}
function X(doc,ctx,p){return doc.evaluate(p,ctx,res,XPathResult.ORDERED_NODE_SNAPSHOT_TYPE,null)}
function all(doc,ctx,p){const r=X(doc,ctx,p),a=[];for(let i=0;i<r.snapshotLength;i++)a.push(r.snapshotItem(i));return a}
function txt(doc,ctx,p){const n=all(doc,ctx,p)[0];return n?n.textContent.trim():''}
function num(doc,ctx,p){const t=txt(doc,ctx,p);return t===''?null:Number(t)}
function sum(doc,ctx,p){return all(doc,ctx,p).reduce((s,n)=>s+Number(n.textContent.trim()||0),0)}
const r2=v=>Math.round(v*100)/100, eq=(a,b)=>Math.abs(r2(a)-r2(b))<0.005;
function near(a,b){return Math.abs(a-b)<=0.0100001}
function dec2(v){return Math.abs(v*100-Math.round(v*100))<1e-6}
function check(xml){
  const doc=new DOMParser().parseFromString(xml,'application/xml');
  if(doc.getElementsByTagName('parsererror').length) return {syntax:'Not well-formed XML',out:[{f:true}],n:1};
  const root=doc.documentElement, ns=root.namespaceURI, out=[];
  const req=(ok,f)=>out.push({ok:!!ok,f});
  let s;
  if(ns==='urn:oasis:names:specification:ubl:schema:xsd:Invoice-2'||ns==='urn:oasis:names:specification:ubl:schema:xsd:CreditNote-2'){
    s='UBL'; const L=root.localName==='Invoice'?'InvoiceLine':'CreditNoteLine', Q=root.localName==='Invoice'?'InvoicedQuantity':'CreditedQuantity';
    const t=p=>txt(doc,root,p), lm='cac:LegalMonetaryTotal/';
    req(t('cbc:CustomizationID'),1);req(t('cbc:ID'),1);req(t('cbc:IssueDate'),1);req(t('cbc:InvoiceTypeCode|cbc:CreditNoteTypeCode'),1);req(t('cbc:DocumentCurrencyCode'),1);
    req(t('cac:AccountingSupplierParty/cac:Party/cac:PartyLegalEntity/cbc:RegistrationName'),1);req(t('cac:AccountingCustomerParty/cac:Party/cac:PartyLegalEntity/cbc:RegistrationName'),1);
    req(all(doc,root,'cac:AccountingSupplierParty/cac:Party/cac:PostalAddress').length,1);req(t('cac:AccountingSupplierParty/cac:Party/cac:PostalAddress/cac:Country/cbc:IdentificationCode'),1);
    req(all(doc,root,'cac:AccountingCustomerParty/cac:Party/cac:PostalAddress').length,1);req(t('cac:AccountingCustomerParty/cac:Party/cac:PostalAddress/cac:Country/cbc:IdentificationCode'),1);
    ['LineExtensionAmount','TaxExclusiveAmount','TaxInclusiveAmount','PayableAmount'].forEach(e=>req(t(lm+'cbc:'+e)!=='',1));
    const lines=all(doc,root,'cac:'+L); req(lines.length,1);
    lines.forEach(l=>{req(txt(doc,l,'cbc:ID'),1);req(txt(doc,l,'cbc:'+Q),1);req(txt(doc,l,'cbc:'+Q+'/@unitCode'),1);req(txt(doc,l,'cbc:LineExtensionAmount'),1);req(txt(doc,l,'cac:Item/cbc:Name'),1);req(txt(doc,l,'cac:Price/cbc:PriceAmount'),1);req(txt(doc,l,'cac:Item/cac:ClassifiedTaxCategory/cbc:ID'),1)});
    const lx=num(doc,root,lm+'cbc:LineExtensionAmount'),te=num(doc,root,lm+'cbc:TaxExclusiveAmount'),ti=num(doc,root,lm+'cbc:TaxInclusiveAmount'),pa=num(doc,root,lm+'cbc:PayableAmount');
    const al=sum(doc,root,"cac:AllowanceCharge[cbc:ChargeIndicator='false']/cbc:Amount"),ch=sum(doc,root,"cac:AllowanceCharge[cbc:ChargeIndicator='true']/cbc:Amount");
    const cur=t('cbc:DocumentCurrencyCode'), vat=sum(doc,root,"cac:TaxTotal/cbc:TaxAmount[@currencyID='"+cur+"']"), pre=num(doc,root,lm+'cbc:PrepaidAmount')||0, rnd=num(doc,root,lm+'cbc:PayableRoundingAmount')||0;
    if(lx!==null) req(eq(lx,sum(doc,root,'cac:'+L+'/cbc:LineExtensionAmount')),1);
    if(lx!==null&&te!==null) req(eq(te,lx-al+ch),1);
    if(te!==null&&ti!==null) req(eq(ti,te+vat),1);
    if(ti!==null&&pa!==null) req(eq(pa,ti-pre+rnd),1);
    req(eq(vat,sum(doc,root,'cac:TaxTotal/cac:TaxSubtotal/cbc:TaxAmount')),1);
    req(all(doc,root,'cac:TaxTotal/cac:TaxSubtotal').length,1);
    // added 2026-10: BR-CO-11/12, line net, per-rate basis (BR-S-08 family), VAT per rate, decimals, rounding
    const alT=num(doc,root,lm+'cbc:AllowanceTotalAmount'),chT=num(doc,root,lm+'cbc:ChargeTotalAmount');
    const dacs=all(doc,root,'cac:AllowanceCharge');
    if(dacs.some(a=>txt(doc,a,'cbc:ChargeIndicator')==='false')||alT!==null) req(alT!==null&&eq(alT,al),1);
    if(dacs.some(a=>txt(doc,a,'cbc:ChargeIndicator')==='true')||chT!==null) req(chT!==null&&eq(chT,ch),1);
    const basis={},key=(c,r)=>c+'|'+Number(r||0);
    lines.forEach(l=>{const q=num(doc,l,'cbc:'+Q),p=num(doc,l,'cac:Price/cbc:PriceAmount'),bq=num(doc,l,'cac:Price/cbc:BaseQuantity')||1,n=num(doc,l,'cbc:LineExtensionAmount');
      const la=sum(doc,l,"cac:AllowanceCharge[cbc:ChargeIndicator='false']/cbc:Amount"),lc=sum(doc,l,"cac:AllowanceCharge[cbc:ChargeIndicator='true']/cbc:Amount");
      if(q!==null&&p!==null&&n!==null) req(near(n,q*p/bq-la+lc),0);
      const k=key(txt(doc,l,'cac:Item/cac:ClassifiedTaxCategory/cbc:ID'),txt(doc,l,'cac:Item/cac:ClassifiedTaxCategory/cbc:Percent'));basis[k]=(basis[k]||0)+(n||0)});
    dacs.forEach(a=>{const c=all(doc,a,'cac:TaxCategory');req(c.length===1,1);if(c.length){const k=key(txt(doc,c[0],'cbc:ID'),txt(doc,c[0],'cbc:Percent'));basis[k]=(basis[k]||0)+(txt(doc,a,'cbc:ChargeIndicator')==='true'?1:-1)*num(doc,a,'cbc:Amount')}});
    all(doc,root,'cac:TaxTotal/cac:TaxSubtotal').forEach(st=>{const k=key(txt(doc,st,'cac:TaxCategory/cbc:ID'),txt(doc,st,'cac:TaxCategory/cbc:Percent')),b=num(doc,st,'cbc:TaxableAmount'),v=num(doc,st,'cbc:TaxAmount'),r=Number(txt(doc,st,'cac:TaxCategory/cbc:Percent')||0);
      req(b!==null&&eq(b,basis[k]||0),1); if(b!==null&&v!==null){req(Math.abs(v-b*r/100)<=1.0000001,1);req(near(v,b*r/100),0)}});
    [lx,te,ti,pa,alT,chT].forEach(v=>{if(v!==null) req(dec2(v),1)});
    req(Math.abs(rnd)<1,1);
    req(t('cbc:BuyerReference')||t('cac:OrderReference/cbc:ID'),0);
    req(t('cac:AccountingSupplierParty/cac:Party/cbc:EndpointID'),0);
  } else if(ns===NS.rsm&&root.localName==='CrossIndustryInvoice'){
    s='CII'; const t=p=>txt(doc,root,p), A='rsm:SupplyChainTradeTransaction/ram:ApplicableHeaderTradeAgreement/', S='rsm:SupplyChainTradeTransaction/ram:ApplicableHeaderTradeSettlement/', M=S+'ram:SpecifiedTradeSettlementHeaderMonetarySummation/';
    req(t('rsm:ExchangedDocumentContext/ram:GuidelineSpecifiedDocumentContextParameter/ram:ID'),1);req(t('rsm:ExchangedDocument/ram:ID'),1);req(t('rsm:ExchangedDocument/ram:IssueDateTime/udt:DateTimeString'),1);req(t('rsm:ExchangedDocument/ram:TypeCode'),1);req(t(S+'ram:InvoiceCurrencyCode'),1);
    req(t(A+'ram:SellerTradeParty/ram:Name'),1);req(t(A+'ram:BuyerTradeParty/ram:Name'),1);
    req(all(doc,root,A+'ram:SellerTradeParty/ram:PostalTradeAddress').length,1);req(t(A+'ram:SellerTradeParty/ram:PostalTradeAddress/ram:CountryID'),1);
    req(all(doc,root,A+'ram:BuyerTradeParty/ram:PostalTradeAddress').length,1);req(t(A+'ram:BuyerTradeParty/ram:PostalTradeAddress/ram:CountryID'),1);
    ['LineTotalAmount','TaxBasisTotalAmount','GrandTotalAmount','DuePayableAmount'].forEach(e=>req(t(M+'ram:'+e)!=='',1));
    const lines=all(doc,root,'rsm:SupplyChainTradeTransaction/ram:IncludedSupplyChainTradeLineItem'); req(lines.length,1);
    lines.forEach(l=>{req(txt(doc,l,'ram:AssociatedDocumentLineDocument/ram:LineID'),1);req(txt(doc,l,'ram:SpecifiedLineTradeDelivery/ram:BilledQuantity'),1);req(txt(doc,l,'ram:SpecifiedLineTradeDelivery/ram:BilledQuantity/@unitCode'),1);req(txt(doc,l,'ram:SpecifiedLineTradeSettlement/ram:SpecifiedTradeSettlementLineMonetarySummation/ram:LineTotalAmount'),1);req(txt(doc,l,'ram:SpecifiedTradeProduct/ram:Name'),1);req(txt(doc,l,'ram:SpecifiedLineTradeAgreement/ram:NetPriceProductTradePrice/ram:ChargeAmount'),1);req(txt(doc,l,'ram:SpecifiedLineTradeSettlement/ram:ApplicableTradeTax/ram:CategoryCode'),1)});
    const lx=num(doc,root,M+'ram:LineTotalAmount'),te=num(doc,root,M+'ram:TaxBasisTotalAmount'),ti=num(doc,root,M+'ram:GrandTotalAmount'),pa=num(doc,root,M+'ram:DuePayableAmount');
    const al=sum(doc,root,S+"ram:SpecifiedTradeAllowanceCharge[ram:ChargeIndicator/udt:Indicator='false']/ram:ActualAmount"),ch=sum(doc,root,S+"ram:SpecifiedTradeAllowanceCharge[ram:ChargeIndicator/udt:Indicator='true']/ram:ActualAmount");
    const cur=t(S+'ram:InvoiceCurrencyCode'), vat=sum(doc,root,M+"ram:TaxTotalAmount[@currencyID='"+cur+"']"), pre=num(doc,root,M+'ram:TotalPrepaidAmount')||0, rnd=num(doc,root,M+'ram:RoundingAmount')||0;
    if(lx!==null) req(eq(lx,sum(doc,root,'rsm:SupplyChainTradeTransaction/ram:IncludedSupplyChainTradeLineItem/ram:SpecifiedLineTradeSettlement/ram:SpecifiedTradeSettlementLineMonetarySummation/ram:LineTotalAmount')),1);
    if(lx!==null&&te!==null) req(eq(te,lx-al+ch),1);
    if(te!==null&&ti!==null) req(eq(ti,te+vat),1);
    if(ti!==null&&pa!==null) req(eq(pa,ti-pre+rnd),1);
    req(eq(vat,sum(doc,root,S+'ram:ApplicableTradeTax/ram:CalculatedAmount')),1);
    req(all(doc,root,S+'ram:ApplicableTradeTax').length,1);
    // added 2026-10: BR-CO-11/12, line net, per-rate basis (BR-S-08 family), VAT per rate, decimals, rounding
    const alT=num(doc,root,M+'ram:AllowanceTotalAmount'),chT=num(doc,root,M+'ram:ChargeTotalAmount');
    const dacs=all(doc,root,S+'ram:SpecifiedTradeAllowanceCharge'),ci=a=>txt(doc,a,'ram:ChargeIndicator/udt:Indicator');
    if(dacs.some(a=>ci(a)==='false')||alT!==null) req(alT!==null&&eq(alT,al),1);
    if(dacs.some(a=>ci(a)==='true')||chT!==null) req(chT!==null&&eq(chT,ch),1);
    const basis={},key=(c,r)=>c+'|'+Number(r||0);
    lines.forEach(l=>{const q=num(doc,l,'ram:SpecifiedLineTradeDelivery/ram:BilledQuantity'),P='ram:SpecifiedLineTradeAgreement/ram:NetPriceProductTradePrice/',p=num(doc,l,P+'ram:ChargeAmount'),bq=num(doc,l,P+'ram:BasisQuantity')||1,LS='ram:SpecifiedLineTradeSettlement/',n=num(doc,l,LS+'ram:SpecifiedTradeSettlementLineMonetarySummation/ram:LineTotalAmount');
      const la=sum(doc,l,LS+"ram:SpecifiedTradeAllowanceCharge[ram:ChargeIndicator/udt:Indicator='false']/ram:ActualAmount"),lc=sum(doc,l,LS+"ram:SpecifiedTradeAllowanceCharge[ram:ChargeIndicator/udt:Indicator='true']/ram:ActualAmount");
      if(q!==null&&p!==null&&n!==null) req(near(n,q*p/bq-la+lc),0);
      const k=key(txt(doc,l,LS+'ram:ApplicableTradeTax/ram:CategoryCode'),txt(doc,l,LS+'ram:ApplicableTradeTax/ram:RateApplicablePercent'));basis[k]=(basis[k]||0)+(n||0)});
    dacs.forEach(a=>{const c=all(doc,a,'ram:CategoryTradeTax');req(c.length===1,1);if(c.length){const k=key(txt(doc,c[0],'ram:CategoryCode'),txt(doc,c[0],'ram:RateApplicablePercent'));basis[k]=(basis[k]||0)+(ci(a)==='true'?1:-1)*num(doc,a,'ram:ActualAmount')}});
    all(doc,root,S+'ram:ApplicableTradeTax').forEach(st=>{const k=key(txt(doc,st,'ram:CategoryCode'),txt(doc,st,'ram:RateApplicablePercent')),b=num(doc,st,'ram:BasisAmount'),v=num(doc,st,'ram:CalculatedAmount'),r=Number(txt(doc,st,'ram:RateApplicablePercent')||0);
      req(b!==null&&eq(b,basis[k]||0),1); if(b!==null&&v!==null){req(Math.abs(v-b*r/100)<=1.0000001,1);req(near(v,b*r/100),0)}});
    [lx,te,ti,pa,alT,chT].forEach(v=>{if(v!==null) req(dec2(v),1)});
    req(Math.abs(rnd)<1,1);
    req(t(A+'ram:BuyerReference')||t(A+'ram:BuyerOrderReferencedDocument/ram:IssuerAssignedID'),0);
    req(t(A+'ram:SellerTradeParty/ram:URIUniversalCommunication/ram:URIID'),0);
  } else return {syntax:'Not a UBL Invoice/CreditNote or CII CrossIndustryInvoice document',out:[{f:true}],n:1};
  const bad=out.filter(o=>!o.ok);
  return {syntax:s,n:out.length,fatal:bad.filter(o=>o.f).length,warn:bad.filter(o=>!o.f).length};
}
window.eicmCheck=check;
const inp=document.getElementById('f'), box=document.getElementById('result');
if(!inp) return;
inp.addEventListener('change',()=>{const file=inp.files[0]; if(!file) return;
  if(file.size>5e6){box.innerHTML='<p class="b fail">File too large (max 5 MB, one invoice).</p>';return}
  file.text().then(x=>{const r=check(x); box.hidden=false;
    if(r.fatal===undefined){box.innerHTML='<h3>Could not check</h3><p><span class="b fail">1 fatal</span> '+r.syntax+'.</p>'+cta();return}
    box.innerHTML='<h3>Result for one '+r.syntax+' invoice</h3><div class="cnt"><div><b>'+r.fatal+'</b><span class="b '+(r.fatal?'fail':'pass')+'">fatal errors</span></div><div><b>'+r.warn+'</b><span class="b '+(r.warn?'warn':'pass')+'">warnings</span></div><div><b>'+r.n+'</b><span class="b na">checks run</span></div></div><p class="small">'+(r.fatal||r.warn?'Rule IDs, the reason for each finding and how to fix it are part of the paid audit.':'No problems found in this subset. The full official validators check several hundred more rules.')+'</p>'+cta();});
});
function cta(){return '<div class="actions"><a class="btn" href="https://paypal.me/kobima6813/290EUR">One-time check: 290 € (up to 10 invoices)</a><a class="btn ghost" href="https://paypal.me/kobima6813/790EUR">Library / vendor audit: 790 €</a><a class="link" href="audit.html">What the audits include →</a></div>'}
})();
