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
