<?php
// French scenarios via horstoeko/zugferd (EN16931 and EXTENDED profiles).
// usage: php gen_horstoeko.php <vendor_autoload.php> scenarios.json <out_dir> <version_tag>
require $argv[1];
use horstoeko\zugferd\ZugferdDocumentBuilder; use horstoeko\zugferd\ZugferdProfiles;
$S=json_decode(file_get_contents($argv[2]),true); $out=$argv[3]; $ver=$argv[4]; $log=[];
foreach(['EN16931'=>ZugferdProfiles::PROFILE_EN16931,'EXTENDED'=>ZugferdProfiles::PROFILE_EXTENDED] as $pn=>$p){
 @mkdir("$out/$pn",0777,true);
 foreach($S['scenarios'] as $sc){
  $e=['generator'=>"horstoeko-zugferd$ver",'profile'=>$pn,'scenario'=>$sc['id'],'errors'=>[]];
  try{
   $sl=$S['seller']; $by=$S[$sc['buyer']];
   $d=ZugferdDocumentBuilder::CreateNew($p);
   $d->setDocumentInformation('F-'.substr($sc['id'],0,4),"380",new DateTime("2026-10-20"),"EUR");
   foreach($S['notes'] as $n) $d->addDocumentNote($n['text'],null,$n['subject']);
   $d->setDocumentSeller($sl['name'])->addDocumentSellerGlobalId($sl['siret'],"0009")
     ->setDocumentSellerLegalOrganisation($sl['siren'],"0002",null)
     ->setDocumentSellerCommunication("0225",$sl['siren'])
     ->addDocumentSellerTaxRegistration("VA",$sl['vat'])
     ->setDocumentSellerAddress($sl['street'],null,null,$sl['postcode'],$sl['city'],"FR");
   $d->setDocumentBuyer($by['name'])->addDocumentBuyerTaxRegistration("VA",$by['vat'])
     ->setDocumentBuyerAddress($by['street'],null,null,$by['postcode'],$by['city'],$by['country']);
   if(isset($by['siren'])) $d->setDocumentBuyerLegalOrganisation($by['siren'],"0002",null)->setDocumentBuyerCommunication("0225",$by['siren']);
   else $d->setDocumentBuyerCommunication("9930",$by['vat']);
   foreach($sc["tax"] as $t) if($t["cat"]=="K"){ $d->setDocumentShipTo($by["name"]); $d->setDocumentShipToAddress("Kundenweg 2",null,null,"80331","München","DE"); $d->setDocumentSupplyChainEvent(new DateTime("2026-10-19")); }
   $d->addDocumentPaymentMeanToCreditTransfer("FR7630006000011234567890189")->addDocumentPaymentTerm("Paiement à 30 jours",new DateTime("2026-11-19"));
   foreach($sc['tax'] as $t) $d->addDocumentTax($t['cat'],"VAT",(float)$t['basis'],(float)$t['tax'],(float)$t['rate'],$t['reason']??null,$t['code']??null);
   $T=$sc['totals'];
   $d->setDocumentSummation((float)$T['grand'],(float)$T['grand'],(float)$T['line'],null,null,(float)$T['line'],(float)$T['tax']);
   $i=0; foreach($sc['lines'] as $l){ $i++;
    $d->addNewPosition((string)$i)->setDocumentPositionProductDetails($l['name'])->setDocumentPositionNetPrice((float)$l['price'])
      ->setDocumentPositionQuantity((float)$l['qty'],"H87")->addDocumentPositionTax($l['cat'],"VAT",(float)$l['rate'])
      ->setDocumentPositionLineSummation((float)$l['qty']*(float)$l['price']); }
   $fn="$out/$pn/horstoeko$ver"."__".$sc['id'].".xml"; file_put_contents($fn,$d->getContent()); $e['file']=$fn;
  }catch(\Throwable $ex){ $e['errors'][]=get_class($ex).': '.substr($ex->getMessage(),0,300); }
  $log[]=$e;
 }
}
file_put_contents("$out/gen_log_horstoeko$ver.json",json_encode($log,JSON_PRETTY_PRINT|JSON_UNESCAPED_UNICODE));
echo "horstoeko $ver done\n";
