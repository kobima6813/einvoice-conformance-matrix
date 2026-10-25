/* Battery Passport self-check. Runs entirely in the browser; nothing is uploaded.
   Unofficial pre-check against Regulation (EU) 2023/1542 (Art. 77-78, Annex XIII) and the
   Battery Pass Data Model v1.2.0. Not a certification or conformity assessment. */
(function(){
'use strict';
const ASPECTS={generalProductInformation:'GeneralProductInformation',carbonFootprint:'CarbonFootprint',circularity:'Circularity',materialComposition:'MaterialComposition',performance:'Performance',supplyChainDueDiligence:'SupplyChainDueDiligence',labels:'Labels'};
const isNum=v=>typeof v==='number'&&isFinite(v);
function validate(root,sch,val,path,errs){
  if(!sch) return;
  if(sch.$ref){const n=sch.$ref.split('/').pop();return validate(root,root.components.schemas[n],val,path,errs)}
  (sch.allOf||[]).forEach(s=>validate(root,s,val,path,errs));
  const t=sch.type;
  if(t==='object'){if(typeof val!=='object'||val===null||Array.isArray(val)){errs.push(path+': not an object');return}
    (sch.required||[]).forEach(k=>{if(!(k in val)||val[k]===null) errs.push(path+'.'+k+': missing')});
    Object.entries(sch.properties||{}).forEach(([k,s])=>{if(k in val&&val[k]!==null) validate(root,s,val[k],path+'.'+k,errs)});return}
  if(t==='array'){if(!Array.isArray(val)){errs.push(path+': not an array');return} val.forEach((v,i)=>validate(root,sch.items,v,path+'['+i+']',errs));return}
  if(t==='number'){if(!isNum(val)){errs.push(path+': not a number');return}
    if(sch.minimum!==undefined&&val<sch.minimum) errs.push(path+': below minimum');
    if(sch.maximum!==undefined&&val>sch.maximum) errs.push(path+': above maximum');return}
  if(t==='boolean'){if(typeof val!=='boolean') errs.push(path+': not a boolean');return}
  if(t==='string'){if(typeof val!=='string'){errs.push(path+': not a string');return}
    if(sch.enum&&!sch.enum.includes(val)) errs.push(path+': not an allowed value');
    if(sch.pattern&&!new RegExp(sch.pattern).test(val)) errs.push(path+': pattern');
    if(sch.format==='uri'&&!/^[a-z][a-z0-9+.-]*:\S+$/i.test(val)) errs.push(path+': not a URI');
    if(sch.format==='date-time'&&!isDT(val)) errs.push(path+': not a date-time');}
}
const isDT=s=>typeof s==='string'&&/^\d{4}-\d\d-\d\dT\d\d:\d\d(:\d\d(\.\d+)?)?(Z|[+-]\d\d:\d\d)?$/.test(s)&&!isNaN(Date.parse(s));
function casOk(c){const m=/^(\d{2,7})-(\d{2})-(\d)$/.exec(String(c).trim());if(!m) return false;const d=(m[1]+m[2]).split('').reverse();let s=0;d.forEach((x,i)=>s+=(i+1)*+x);return s%10===+m[3]}
function gtinOk(g){if(!/^\d{8}$|^\d{12,14}$/.test(g)) return false;const d=g.padStart(14,'0').split('').map(Number);let s=0;for(let i=0;i<13;i++) s+=d[i]*(i%2?1:3);return (10-s%10)%10===d[13]}
const near=(a,b,rel)=>Math.abs(a-b)<=rel*Math.max(Math.abs(a),Math.abs(b),1e-9);
// chemistry -> elements that must appear in the material list
const CHEM={NMC:['lithium','nickel','manganese','cobalt'],NCA:['lithium','nickel','cobalt','aluminium'],LFP:['lithium','iron','phosph'],LMFP:['lithium','iron','manganese','phosph'],LCO:['lithium','cobalt'],LMO:['lithium','manganese'],LTO:['lithium','titan'],PBA:['lead'],'PB-ACID':['lead'],NIMH:['nickel'],NICD:['nickel','cadmium'],NAION:['sodium'],'NA-ION':['sodium'],SIB:['sodium']};
const SYN={aluminium:['alumin'],phosph:['phosph'],titan:['titan']};
function check(text,dlInput,now){
  now=now?new Date(now):new Date();
  const out=[];let syntax=null;
  const R=(id,draft,ok,warn)=>{out.push({id,draft:!!draft,ok:!!ok,f:!warn})};
  let p;try{p=JSON.parse(text)}catch(e){return {syntax:'Not valid JSON',n:1,errors:1,warnings:0,draftN:0,out:[{id:'JSON',ok:false,f:true}]}}
  if(typeof p!=='object'||p===null||Array.isArray(p)) return {syntax:'JSON is not an object',n:1,errors:1,warnings:0,draftN:0,out:[{id:'JSON',ok:false,f:true}]};
  // accept keys case-insensitively
  const pick=k=>{const kk=Object.keys(p).find(x=>x.toLowerCase()===k.toLowerCase());return kk?p[kk]:undefined};
  const A={};Object.keys(ASPECTS).forEach(k=>A[k]=pick(k));
  if(!Object.values(A).some(v=>v!==undefined)) return {syntax:'No Battery Pass aspects found (expected keys such as generalProductInformation, materialComposition, performance)',n:1,errors:1,warnings:0,draftN:0,out:[{id:'NOASPECT',ok:false,f:true}]};
  const S=window.BP_SCHEMAS||{};
  // 1. schema per aspect (missing aspect = error: all seven carry Annex XIII public or restricted data)
  Object.entries(ASPECTS).forEach(([k,n])=>{const e=[];if(A[k]===undefined) e.push(k+': aspect missing');else validate(S[n],S[n],A[k],k,e);R('SCHEMA:'+k,false,e.length===0)});
  const g=A.generalProductInformation||{},cf=A.carbonFootprint||{},ci=A.circularity||{},mc=A.materialComposition||{},pf=A.performance||{},tp=pf.batteryTechicalProperties||{},bc=pf.batteryCondition||{};
  const ts=s=>isDT(s)?Date.parse(s):null, future=s=>{const t=ts(s);return t!==null&&t>now.getTime()+864e5};
  // General product information (Annex VI Part A, Annex XIII 1(a))
  R('BP-GP-02',0,!future(g.manufacturingDate));
  {const a=ts(g.manufacturingDate),b=ts(g.puttingIntoService);R('BP-GP-03',0,!(a!==null&&b!==null&&b<a))}
  {const bad=[];(function walk(o){if(o&&typeof o==='object'){for(const [k,v] of Object.entries(o)){if((k==='lastUpdate'||k==='rPCLastUpdated')&&future(v)) bad.push(k);walk(v)}}})(pf);R('BP-GP-04',0,bad.length===0)}
  {const e=isNum(tp.ratedEnergy)?tp.ratedEnergy:null;R('BP-GP-05',0,!(g.batteryCategory==='industrial'&&e!==null&&e<=2),true)}
  {const em=[g.manufacturerInformation,g.operatorInformation].concat((ci.sparePartSources||[]).map(s=>({emailAddress:s&&s.emailAddressOfSupplier}))).map(x=>x&&x.emailAddress).filter(x=>x!==undefined);R('BP-GP-06',0,em.every(x=>typeof x==='string'&&/^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$/.test(x)),true)}
  R('BP-GP-01',0,isNum(g.batteryMass)&&g.batteryMass>0);
  // Performance and durability (Annex IV, Annex XIII 1(g)-(h))
  const cap=tp.ratedCapacity,nv=tp.nominalVoltage,re=tp.ratedEnergy;let unitFlag=false;
  if(isNum(cap)&&isNum(nv)&&isNum(re)&&re>0&&cap>0&&nv>0){const calc=cap*nv/1000,ratio=re/calc;unitFlag=ratio>500&&ratio<2000;R('BP-PF-02',0,!unitFlag);R('BP-PF-01',0,unitFlag||near(re,calc,0.10))}else{R('BP-PF-02',0,true);R('BP-PF-01',0,true)}
  {const a=tp.minimumVoltage,b=nv,c=tp.maximumVoltage;R('BP-PF-03',0,!(isNum(a)&&isNum(b)&&isNum(c))||(a<b&&b<c))}
  {const pct=[tp.roundtripEfficiency,tp.capacityThresholdForExhaustion,tp.initialSelfDischarge,bc.stateOfCharge&&bc.stateOfCharge.stateOfChargeValue,bc.stateOfCertifiedEnergy&&bc.stateOfCertifiedEnergy.stateOfCertifiedEnergyValue,bc.roundTripEfficiencyat50PerCentCycleLife].filter(isNum);R('BP-PF-04',0,pct.every(v=>v>=0&&v<=100))}
  {const rc=bc.remainingCapacity&&bc.remainingCapacity.remainingCapacityValue,ren=bc.remainingEnergy&&bc.remainingEnergy.remainingEnergyalue;R('BP-PF-05',0,!(isNum(rc)&&isNum(cap)&&rc>cap*1.05)&&!(isNum(ren)&&isNum(re)&&ren>re*1.05))}
  R('BP-PF-06',0,[tp.expectedNumberOfCycles,tp.expectedLifetime,tp.ratedMaximumPower].filter(v=>v!==undefined).every(v=>isNum(v)&&v>0));
  // Material composition (Annex XIII 1(b)-(d))
  const mats=Array.isArray(mc.batteryMaterials)?mc.batteryMaterials:[],haz=Array.isArray(mc.hazardousSubstances)?mc.hazardousSubstances:[];
  {const ids=mats.map(m=>m&&m.batteryMaterialIdentifier).concat(haz.map(h=>h&&h.hazardousSubstanceIdentifier)).filter(x=>typeof x==='string'&&/^\s*\d{2,7}-\d{2}-\d\s*$/.test(x));R('BP-MC-01',0,ids.every(casOk))}
  const names=mats.map(m=>String(m&&m.batteryMaterialName||'').toLowerCase()).concat(haz.map(h=>String(h&&h.hazardousSubstanceName||'').toLowerCase())).join(' | ');
  const chem=String(mc.batteryChemistry&&mc.batteryChemistry.shortName||'').toUpperCase().replace(/[\s_]/g,'');
  const need=CHEM[chem];
  R('BP-MC-02',0,!need||need.every(el=>names.includes(el)));
  {const hasCo=names.includes('cobalt')||chem==='NMC'||chem==='NCA'||chem==='LCO',hasNi=names.includes('nickel')||['NMC','NCA','NIMH','NICD'].includes(chem),hasPb=names.includes('lead')||chem.startsWith('PB'),hasLi=names.includes('lithium')||chem.startsWith('L')||chem==='NMC'||chem==='NCA';
   const rcm=(Array.isArray(ci.recycledContent)?ci.recycledContent:[]).map(r=>r&&r.recycledMaterial);
   R('BP-MC-03',0,rcm.every(m=>!(m==='Cobalt'&&!hasCo||m==='Nickel'&&!hasNi||m==='Lead'&&!hasPb||m==='Lithium'&&!hasLi)),true)}
  {const tot=mats.reduce((s,m)=>s+(m&&isNum(m.batteryMaterialMass)?m.batteryMaterialMass:0),0);R('BP-MC-04',0,!(isNum(g.batteryMass)&&tot>g.batteryMass*1.01))}
  R('BP-MC-05',0,haz.every(h=>!h||!isNum(h.hazardousSubstanceConcentration)||(h.hazardousSubstanceConcentration>=0&&h.hazardousSubstanceConcentration<=100)));
  // Recycled & renewable content (Art. 8, Annex XIII 1(e)-(f)) - calculation/verification methodology still pending => draft
  const rcs=Array.isArray(ci.recycledContent)?ci.recycledContent:[];
  R('BP-RC-01',1,rcs.every(r=>!r||!(isNum(r.preConsumerShare)&&isNum(r.postConsumerShare))||r.preConsumerShare+r.postConsumerShare<=100));
  {const m=rcs.map(r=>r&&r.recycledMaterial);R('BP-RC-02',1,new Set(m).size===m.length)}
  R('BP-RC-03',1,!isNum(ci.renewableContent)||(ci.renewableContent>=0&&ci.renewableContent<=100));
  // Carbon footprint (Art. 7, Annex II) - methodology delegated act not adopted => draft
  const st=Array.isArray(cf.carbonFootprintPerLifecycleStage)?cf.carbonFootprintPerLifecycleStage:[];
  {const have=new Set(st.map(s=>s&&s.lifecycleStage));R('BP-CF-01',1,!cf.carbonFootprintPerLifecycleStage||['RawMaterialExtraction','MainProduction','Distribution','Recycling'].every(x=>have.has(x))&&have.size===st.length)}
  {const sum=st.reduce((s,x)=>s+(x&&isNum(x.carbonFootprint)?x.carbonFootprint:0),0);R('BP-CF-02',1,!isNum(cf.batteryCarbonFootprint)||!st.length||near(sum,cf.batteryCarbonFootprint,0.02))}
  {const pk=cf.batteryCarbonFootprint,ab=cf.absoluteCarbonFootprint,life=isNum(re)&&isNum(tp.expectedNumberOfCycles)&&!unitFlag?re*tp.expectedNumberOfCycles:null;
   const perRated=isNum(pk)&&isNum(ab)&&isNum(re)&&re>0&&!unitFlag&&near(ab/re,pk,0.05);
   R('BP-CF-04',1,!perRated);
   R('BP-CF-03',1,perRated||!(isNum(pk)&&isNum(ab)&&life)||near(ab,pk*life,0.25),true)}
  R('BP-CF-05',1,cf.carbonFootprintPerformanceClass===undefined||/^[A-G]$/.test(String(cf.carbonFootprintPerformanceClass)),true);
  // Data carrier / unique identifier (Art. 77(3), EN 18219/18220, GS1 Digital Link profile) - draft
  const dl=(dlInput&&dlInput.trim())||(typeof p.dataCarrier==='string'?p.dataCarrier.trim():'');
  if(dl){let u=null;try{u=/^https:\/\//i.test(dl)?new URL(dl):null}catch(e){}
    const seg=u?u.pathname.split('/').filter(Boolean):[];const i01=seg.indexOf('01');const gtin=i01>=0?seg[i01+1]:null;
    R('BP-DL-01',1,!!u&&!!gtin);
    R('BP-DL-02',1,!gtin||gtinOk(gtin));
    const i21=seg.indexOf('21');let ser=i21>=0?seg[i21+1]:null;try{if(ser!==null) ser=decodeURIComponent(ser)}catch(e){ser='\u0000'}
    R('BP-DL-03',1,!u||!gtin||ser!==null,true);
    R('BP-DL-04',1,ser===null||(/^[!"%&'()*+,\-./0-9:;<=>?A-Z_a-z]{1,20}$/.test(ser)));
    const pid=String(g.productIdentifier||'');
    R('BP-DL-05',1,!gtin||!pid||(pid.replace(/\D/g,'').includes(gtin.padStart(14,'0').slice(-13))&&(ser===null||pid.includes(ser))),true);
  }
  const bad=out.filter(o=>!o.ok);
  return {syntax:'Battery Pass JSON',n:out.length,draftN:out.filter(o=>o.draft).length,errors:bad.filter(o=>o.f).length,warnings:bad.filter(o=>!o.f).length,draftFindings:bad.filter(o=>o.draft).length,failed:bad.map(o=>o.id.split(':')[0]),out};
}
window.bpCheck=check;
const ta=document.getElementById('bp'),dlI=document.getElementById('dl'),fi=document.getElementById('bpf'),btn=document.getElementById('run'),box=document.getElementById('result');
if(!btn) return;
fi.addEventListener('change',()=>{const f=fi.files[0];if(!f) return;if(f.size>5e6){box.hidden=false;box.innerHTML='<p class="b fail">File too large (max 5 MB, one passport).</p>';return}f.text().then(t=>{ta.value=t;run()})});
btn.addEventListener('click',run);
const sample=document.getElementById('sample');if(sample) sample.addEventListener('click',e=>{e.preventDefault();fetch('battery/corpus/valid-ev-nmc.json').then(r=>r.text()).then(t=>{ta.value=t;dlI.value='';run()})});
function run(){const r=check(ta.value,dlI.value);box.hidden=false;
  if(r.syntax!=='Battery Pass JSON'){box.innerHTML='<h3>Could not check</h3><p><span class="b fail">1 error</span> '+r.syntax+'.</p>'+cta();return}
  box.innerHTML='<h3>Result for one battery passport</h3><div class="cnt"><div><b>'+r.errors+'</b><span class="b '+(r.errors?'fail':'pass')+'">errors</span></div><div><b>'+r.warnings+'</b><span class="b '+(r.warnings?'warn':'pass')+'">warnings</span></div><div><b>'+r.n+'</b><span class="b na">checks run</span></div></div><p class="small">'+(r.n-r.draftN)+' checks are based on final requirements, '+r.draftN+' on rules that are still draft (pending EU delegated/implementing acts or a chosen identifier profile)'+(r.draftFindings?'; '+r.draftFindings+' of the findings come from draft checks':'')+'. '+(r.errors||r.warnings?'Which fields failed, why, and how to fix them is part of the paid review.':'No problems found in this subset. This is not a conformity assessment.')+'</p>'+cta()}
function cta(){return '<div class="actions"><a class="btn" href="https://paypal.me/kobima6813/290EUR">Passport review: 290 €</a><a class="link" href="mailto:conformance@mail.grokbot.com?subject=Battery%20passport%20review">Ask what the review includes →</a></div>'}
})();
