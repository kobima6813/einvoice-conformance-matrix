"""Build the Battery Passport self-check test corpus (docs/battery/corpus).
Valid samples are hand-built from the Battery Pass data model v1.2.0 structure
(the upstream example payloads are random generator output, not usable as valid samples).
Each broken variant changes one thing and names the rule it must trigger."""
import json, copy, os
OUT=os.path.join(os.path.dirname(__file__),'..','docs','battery','corpus')
TS='2026-09-30T10:00:00+02:00'
def addr(c,s,p): return {"addressCountry":c,"streetAddress":s,"postalCode":p}
def contact(n,i,e,w,a): return {"contactName":n,"identifier":i,"emailAddress":e,"webAddress":w,"postalAddress":a}
def ev_nmc():
  return {
   "dataCarrier":"https://id.example-batteries.eu/01/04012345000016/21/EVP0001234",
   "generalProductInformation":{
    "productIdentifier":"(01)04012345000016(21)EVP0001234",
    "batteryPassportIdentifier":"urn:exampleoem:evp0001234",
    "batteryCategory":"ev",
    "manufacturerInformation":contact("Example Cells GmbH","DE123456789","passport@example-batteries.eu","https://example-batteries.eu",addr("DE","Musterstr. 1","10115")),
    "operatorInformation":contact("Example Cells GmbH","DE123456789","passport@example-batteries.eu","https://example-batteries.eu",addr("DE","Musterstr. 1","10115")),
    "manufacturingDate":"2026-06-02T08:00:00+02:00","manufacturingPlace":addr("DE","Werkstr. 5","01099"),
    "batteryStatus":"Original","batteryMass":450,"puttingIntoService":"2026-08-15T09:00:00+02:00","warrentyPeriod":"--08"},
   "carbonFootprint":{
    "batteryCarbonFootprint":0.065,
    "carbonFootprintPerLifecycleStage":[{"lifecycleStage":"RawMaterialExtraction","carbonFootprint":0.040},{"lifecycleStage":"MainProduction","carbonFootprint":0.020},{"lifecycleStage":"Distribution","carbonFootprint":0.002},{"lifecycleStage":"Recycling","carbonFootprint":0.003}],
    "carbonFootprintPerformanceClass":"B","carbonFootprintStudy":"https://example-batteries.eu/cfp/evp-75.pdf","absoluteCarbonFootprint":5850},
   "circularity":{
    "renewableContent":4,
    "recycledContent":[{"recycledMaterial":"Cobalt","preConsumerShare":10,"postConsumerShare":6},{"recycledMaterial":"Nickel","preConsumerShare":3,"postConsumerShare":2},{"recycledMaterial":"Lithium","preConsumerShare":2,"postConsumerShare":1}],
    "dismantlingAndRemovalInformation":[{"documentType":"DismantlingManual","mimeType":"application/pdf","documentURL":"https://example-batteries.eu/docs/dismantling.pdf"}],
    "sparePartSources":[{"nameOfSupplier":"Example Parts BV","addressOfSupplier":addr("NL","Kade 2","1011AA"),"emailAddressOfSupplier":"parts@example-parts.eu","supplierWebAddress":"https://example-parts.eu","components":[{"partName":"Module","partNumber":"MOD-12"}]}],
    "safetyMeasures":{"safetyInstructions":"https://example-batteries.eu/docs/safety.pdf","extinguishingAgent":["Water"]},
    "endOfLifeInformation":{"wastePrevention":"https://example-batteries.eu/eol/prevention","separateCollection":"https://example-batteries.eu/eol/collection","informationOnCollection":"https://example-batteries.eu/eol/points"}},
   "materialComposition":{
    "batteryChemistry":{"shortName":"NMC","clearName":"Lithium nickel manganese cobalt oxide"},
    "batteryMaterials":[
     {"batteryMaterialName":"Lithium","batteryMaterialIdentifier":"7439-93-2","batteryMaterialMass":7.5,"isCriticalRawMaterial":True,"batteryMaterialLocation":{"componentName":"Cathode"}},
     {"batteryMaterialName":"Nickel","batteryMaterialIdentifier":"7440-02-0","batteryMaterialMass":38,"isCriticalRawMaterial":True,"batteryMaterialLocation":{"componentName":"Cathode"}},
     {"batteryMaterialName":"Manganese","batteryMaterialIdentifier":"7439-96-5","batteryMaterialMass":5,"isCriticalRawMaterial":True,"batteryMaterialLocation":{"componentName":"Cathode"}},
     {"batteryMaterialName":"Cobalt","batteryMaterialIdentifier":"7440-48-4","batteryMaterialMass":5,"isCriticalRawMaterial":True,"batteryMaterialLocation":{"componentName":"Cathode"}},
     {"batteryMaterialName":"Graphite","batteryMaterialIdentifier":"7782-42-5","batteryMaterialMass":55,"isCriticalRawMaterial":True,"batteryMaterialLocation":{"componentName":"Anode"}}],
    "hazardousSubstances":[{"hazardousSubstanceClass":"AcuteToxicity","hazardousSubstanceName":"Lithium hexafluorophosphate","hazardousSubstanceIdentifier":"21324-40-3","hazardousSubstanceConcentration":1.2,"hazardousSubstanceImpact":["Toxic if swallowed"],"hazardousSubstanceLocation":{"componentName":"Electrolyte"}}]},
   "performance":{
    "batteryTechicalProperties":{
     "ratedCapacity":200,"nominalVoltage":375,"minimumVoltage":300,"maximumVoltage":420,"ratedEnergy":75,
     "originalPowerCapability":[{"atSoC":80,"powerCapabilityAt":250},{"atSoC":20,"powerCapabilityAt":180}],
     "ratedMaximumPower":250,"powerCapabilityRatio":3.33,"expectedNumberOfCycles":1500,"expectedLifetime":10,
     "initialSelfDischarge":2,"roundtripEfficiency":95,"initialInternalResistance":[{"ohmicResistance":0.08,"batteryComponent":"pack"}],
     "cRate":1,"capacityThresholdForExhaustion":70,"lifetimeReferenceTest":"https://example-batteries.eu/docs/lifetime-test.pdf","cRateLifeCycleTest":0.33,"temperatureRangeIdleState":45},
    "batteryCondition":{
     "energyThroughput":1200,"capacityThroughput":{"capacityThroughputValue":3200,"lastUpdate":TS},
     "numberOfFullCycles":{"numberOfFullCyclesValue":16,"lastUpdate":TS},
     "stateOfCertifiedEnergy":{"stateOfCertifiedEnergyValue":99,"lastUpdate":TS},
     "capacityFade":{"capacityFadeValue":1,"lastUpdate":TS},
     "remainingEnergy":{"remainingEnergyalue":74,"lastUpdate":TS},
     "remainingCapacity":{"remainingCapacityValue":198,"lastUpdate":TS},
     "negativeEvents":[],
     "temperatureInformation":{"timeExtremeHighTemp":0,"timeExtremeLowTemp":0,"timeExtremeHighTempCharging":0,"timeExtremeLowTempCharging":0,"lastUpdate":TS},
     "remainingPowerCapability":[{"remainingPowerCapabilityValue":{"atSoC":80,"powerCapabilityAt":248,"rPCLastUpdated":TS},"lastUpdate":TS}],
     "powerFade":1,"roundTripEfficiencyFade":0.2,
     "evolutionOfSelfDischarge":{"evolutionOfSelfDischargeEntityValue":0},
     "currentSelfDischargingRate":{"currentSelfDischargingRateEntity":2,"lastUpdate":TS},
     "internalResistanceIncrease":[{"internalResistanceIncreaseValue":1,"batteryComponent":"pack","lastUpdate":TS}],
     "roundTripEfficiencyat50PerCentCycleLife":93,
     "remainingRoundTripEnergyEfficiency":{"remainingRoundTripEnergyEfficiencyValue":94.8,"lastUpdate":TS},
     "stateOfCharge":{"stateOfChargeValue":60,"lastUpdate":TS}}},
   "supplyChainDueDiligence":{"supplyChainDueDiligenceReport":"https://example-batteries.eu/dd/report-2026.pdf"},
   "labels":{"declarationOfConformity":"https://example-batteries.eu/doc/eu-doc.pdf","resultOfTestReport":"https://example-batteries.eu/doc/tests.pdf",
     "labels":[{"labelingSubject":"SeparateCollection","labelingSymbol":"https://example-batteries.eu/img/bin.svg","labelingMeaning":{"en":"Separate collection"}}]}}
def lmt_lfp():
  p=ev_nmc(); g=p["generalProductInformation"]
  p["dataCarrier"]="https://id.example-batteries.eu/01/04012345000023/21/LMT-778"
  g.update(productIdentifier="(01)04012345000023(21)LMT-778",batteryPassportIdentifier="urn:exampleoem:lmt778",batteryCategory="lmt",batteryMass=4.2)
  t=p["performance"]["batteryTechicalProperties"]
  t.update(ratedCapacity=20,nominalVoltage=48,minimumVoltage=40,maximumVoltage=54.6,ratedEnergy=0.96,ratedMaximumPower=1.5,powerCapabilityRatio=1.56,expectedNumberOfCycles=2000,originalPowerCapability=[{"atSoC":80,"powerCapabilityAt":1.5}])
  c=p["performance"]["batteryCondition"]; c["remainingCapacity"]["remainingCapacityValue"]=19.8; c["remainingEnergy"]["remainingEnergyalue"]=0.95; c["remainingPowerCapability"][0]["remainingPowerCapabilityValue"]["powerCapabilityAt"]=1.48
  c["energyThroughput"]=15; c["capacityThroughput"]["capacityThroughputValue"]=320
  p["materialComposition"]["batteryChemistry"]={"shortName":"LFP","clearName":"Lithium iron phosphate"}
  p["materialComposition"]["batteryMaterials"]=[
     {"batteryMaterialName":"Lithium","batteryMaterialIdentifier":"7439-93-2","batteryMaterialMass":0.05,"isCriticalRawMaterial":True,"batteryMaterialLocation":{"componentName":"Cathode"}},
     {"batteryMaterialName":"Iron","batteryMaterialIdentifier":"7439-89-6","batteryMaterialMass":0.35,"isCriticalRawMaterial":False,"batteryMaterialLocation":{"componentName":"Cathode"}},
     {"batteryMaterialName":"Phosphorus","batteryMaterialIdentifier":"7723-14-0","batteryMaterialMass":0.2,"isCriticalRawMaterial":True,"batteryMaterialLocation":{"componentName":"Cathode"}},
     {"batteryMaterialName":"Graphite","batteryMaterialIdentifier":"7782-42-5","batteryMaterialMass":0.6,"isCriticalRawMaterial":True,"batteryMaterialLocation":{"componentName":"Anode"}}]
  p["circularity"]["recycledContent"]=[{"recycledMaterial":"Lithium","preConsumerShare":2,"postConsumerShare":1}]
  # lifetime energy 0.96 kWh * 2000 cycles = 1920 kWh; 0.07 kg/kWh -> 134.4 kg
  cf=p["carbonFootprint"]; cf.update(batteryCarbonFootprint=0.07,absoluteCarbonFootprint=134.4)
  cf["carbonFootprintPerLifecycleStage"]=[{"lifecycleStage":"RawMaterialExtraction","carbonFootprint":0.04},{"lifecycleStage":"MainProduction","carbonFootprint":0.025},{"lifecycleStage":"Distribution","carbonFootprint":0.002},{"lifecycleStage":"Recycling","carbonFootprint":0.003}]
  return p
# EV check: 75 kWh*1500 = 112500 kWh; 0.065*112500=7312.5 -> fix absolute
def ev():
  p=ev_nmc(); p["carbonFootprint"]["absoluteCarbonFootprint"]=7312.5; return p
V={}
def var(name,rule,desc,fn,base=ev):
  p=base(); fn(p); V[name]=(rule,desc,p)
G=lambda p:p["generalProductInformation"]; T=lambda p:p["performance"]["batteryTechicalProperties"]
var("cf-stages-dont-sum","BP-CF-02","Lifecycle stages add up to 0.085 but declared total is 0.065",lambda p:p["carbonFootprint"]["carbonFootprintPerLifecycleStage"][0].update(carbonFootprint=0.060))
var("cf-absolute-mismatch","BP-CF-03","Absolute footprint 2 t does not match 0.065 kg/kWh x lifetime energy",lambda p:p["carbonFootprint"].update(absoluteCarbonFootprint=2000))
var("cf-per-rated-kwh","BP-CF-04","Footprint declared per kWh of rated energy (78 kg/kWh) instead of per kWh delivered over life",lambda p:p["carbonFootprint"].update(batteryCarbonFootprint=78,carbonFootprintPerLifecycleStage=[{"lifecycleStage":"RawMaterialExtraction","carbonFootprint":48},{"lifecycleStage":"MainProduction","carbonFootprint":24},{"lifecycleStage":"Distribution","carbonFootprint":2.4},{"lifecycleStage":"Recycling","carbonFootprint":3.6}],absoluteCarbonFootprint=5850))
var("recycled-over-100","BP-RC-01","Cobalt pre- + post-consumer recycled share = 120 %",lambda p:p["circularity"]["recycledContent"][0].update(preConsumerShare=70,postConsumerShare=50))
var("recycled-out-of-range","SCHEMA","Recycled share 140 % (schema range 0-100)",lambda p:p["circularity"]["recycledContent"][1].update(preConsumerShare=140))
var("recycled-duplicate-material","BP-RC-02","Cobalt listed twice in recycled content",lambda p:p["circularity"]["recycledContent"].append({"recycledMaterial":"Cobalt","preConsumerShare":1,"postConsumerShare":1}))
var("missing-manufacturer","SCHEMA","Mandatory public field manufacturerInformation removed",lambda p:G(p).pop("manufacturerInformation"))
var("missing-chemistry","SCHEMA","Mandatory public field batteryChemistry removed",lambda p:p["materialComposition"].pop("batteryChemistry"))
var("energy-in-wh","BP-PF-02","Rated energy given in Wh (75000) where the model expects kWh",lambda p:T(p).update(ratedEnergy=75000))
var("capacity-voltage-energy-mismatch","BP-PF-01","Rated energy 100 kWh but 200 Ah x 375 V = 75 kWh",lambda p:T(p).update(ratedEnergy=100))
var("voltage-order","BP-PF-03","Minimum voltage above nominal voltage",lambda p:T(p).update(minimumVoltage=390))
var("manufactured-in-future","BP-GP-02","Manufacturing date in 2031",lambda p:G(p).update(manufacturingDate="2031-01-01T00:00:00+01:00"))
var("service-before-manufacture","BP-GP-03","Put into service before it was manufactured",lambda p:G(p).update(puttingIntoService="2026-01-01T00:00:00+01:00"))
var("cas-check-digit","BP-MC-01","CAS number 7440-48-5 for cobalt has a wrong check digit (pattern still matches)",lambda p:p["materialComposition"]["batteryMaterials"][3].update(batteryMaterialIdentifier="7440-48-5"))
var("chemistry-without-lithium","BP-MC-02","Chemistry NMC but no lithium/nickel/cobalt in material list",lambda p:p["materialComposition"].update(batteryMaterials=[m for m in p["materialComposition"]["batteryMaterials"] if m["batteryMaterialName"]=="Graphite"]))
var("lfp-with-cobalt-recycled","BP-MC-03","LFP battery declares recycled cobalt content",lambda p:p["circularity"]["recycledContent"].append({"recycledMaterial":"Cobalt","preConsumerShare":5,"postConsumerShare":5}),base=lmt_lfp)
var("materials-heavier-than-battery","BP-MC-04","Declared material masses (110.5 kg) exceed battery mass (50 kg)",lambda p:G(p).update(batteryMass=50))
var("hazardous-concentration-over-100","BP-MC-05","Hazardous substance concentration 250 %",lambda p:p["materialComposition"]["hazardousSubstances"][0].update(hazardousSubstanceConcentration=250))
var("passport-id-malformed","SCHEMA","batteryPassportIdentifier is not a URN",lambda p:G(p).update(batteryPassportIdentifier="EVP0001234"))
var("bad-category","SCHEMA","batteryCategory 'car' not in lmt/ev/industrial/stationary",lambda p:G(p).update(batteryCategory="car"))
var("gtin-check-digit","BP-DL-02","GS1 Digital Link GTIN check digit wrong",lambda p:p.update(dataCarrier="https://id.example-batteries.eu/01/04012345000011/21/EVP0001234"))
var("dl-not-https","BP-DL-01","Data carrier URL is not an https Digital Link URI",lambda p:p.update(dataCarrier="id.example-batteries.eu/gtin=04012345000016"))
var("dl-no-serial","BP-DL-03","Digital Link identifies the model only (no /21/ serial) - passport is per battery",lambda p:p.update(dataCarrier="https://id.example-batteries.eu/01/04012345000016"))
var("dl-mismatch-product-id","BP-DL-05","Digital Link serial differs from productIdentifier",lambda p:p.update(dataCarrier="https://id.example-batteries.eu/01/04012345000016/21/EVP0009999"))
var("dl-bad-serial-chars","BP-DL-04","Serial contains characters outside GS1 AI set 82",lambda p:p.update(dataCarrier="https://id.example-batteries.eu/01/04012345000016/21/EVP%C3%A9%5E1"))
var("remaining-capacity-above-rated","BP-PF-05","Remaining capacity 230 Ah above rated 200 Ah",lambda p:p["performance"]["batteryCondition"]["remainingCapacity"].update(remainingCapacityValue=230))
var("soc-over-100","BP-PF-04","State of charge 160 %",lambda p:p["performance"]["batteryCondition"]["stateOfCharge"].update(stateOfChargeValue=160))
var("lastupdate-in-future","BP-GP-04","Dynamic data lastUpdate in 2030",lambda p:p["performance"]["batteryCondition"]["stateOfCharge"].update(lastUpdate="2030-01-01T00:00:00Z"))
var("industrial-under-2kwh","BP-GP-05","Industrial battery of 0.96 kWh: Art. 77 passport only applies above 2 kWh",lambda p:G(p).update(batteryCategory="industrial"),base=lmt_lfp)
var("renewable-over-100","BP-RC-03","Renewable content 130 %",lambda p:p["circularity"].update(renewableContent=130))
var("cf-class-not-letter","BP-CF-05","Performance class 'excellent' instead of a class letter",lambda p:p["carbonFootprint"].update(carbonFootprintPerformanceClass="excellent"))
var("cf-missing-stage","BP-CF-01","Lifecycle stage 'Recycling' missing",lambda p:p["carbonFootprint"]["carbonFootprintPerLifecycleStage"].pop())
var("bad-email","BP-GP-06","Manufacturer e-mail not an address",lambda p:G(p)["manufacturerInformation"].update(emailAddress="passport(at)example"))
for f in os.listdir(OUT): os.remove(os.path.join(OUT,f))
man={"valid":[],"broken":[]}
for n,f in (("valid-ev-nmc",ev),("valid-lmt-lfp",lmt_lfp)):
  json.dump(f(),open(f"{OUT}/{n}.json","w"),indent=1); man["valid"].append(n+".json")
for n,(r,d,p) in V.items():
  json.dump(p,open(f"{OUT}/broken-{n}.json","w"),indent=1); man["broken"].append({"file":f"broken-{n}.json","expect":r,"what":d})
json.dump(man,open(f"{OUT}/manifest.json","w"),indent=1)
print(len(man["valid"]),"valid",len(V),"broken")
