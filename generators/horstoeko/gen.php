<?php
// horstoeko/zugferd 1.0.133 driver: writes the reference EN 16931 totals (library computes no totals).
// usage: php gen.php <corpus_dir>/ref_en16931_rounding.json <out_dir>
require __DIR__.'/vendor/autoload.php';
use horstoeko\zugferd\ZugferdDocumentBuilder; use horstoeko\zugferd\ZugferdProfiles;
$R=json_decode(file_get_contents($argv[1]),true); @mkdir($argv[2],0777,true);
foreach($R as $c){
 $T=$c['T'];
 $d=ZugferdDocumentBuilder::CreateNew(ZugferdProfiles::PROFILE_EN16931);
 $d->setDocumentInformation($c['id'],"380",new DateTime("2026-10-18"),"EUR")
   ->setDocumentSeller("Muster Shop GmbH")->addDocumentSellerTaxRegistration("VA","DE123456788")
   ->setDocumentSellerAddress("Musterstr. 1",null,null,"10115","Berlin","DE")
   ->setDocumentBuyer("Kunde AG")->setDocumentBuyerReference("04011000-12345-03")
   ->setDocumentBuyerAddress("Kundenweg 2",null,null,"80331","München","DE")
   ->addDocumentPaymentMeanToCreditTransfer("DE79000000001234567890")->addDocumentPaymentTerm("Zahlbar sofort");
 foreach($c['tax'] as $t) $d->addDocumentTax("S","VAT",(float)$t['basis'],(float)$t['tax'],(float)$t['rate']);
 $d->setDocumentSummation((float)$T['grand'],(float)$T['due'],(float)$T['line'],null,null,(float)$T['basis'],(float)$T['tax'],isset($T['rounding'])?(float)$T['rounding']:null);
 $i=0;
 foreach($c['L'] as $l){ $i++;
  $d->addNewPosition((string)$i)->setDocumentPositionProductDetails($l['name'])->setDocumentPositionNetPrice((float)$l['net_price'])
    ->setDocumentPositionQuantity((float)$l['qty'],"H87")->addDocumentPositionTax("S","VAT",(float)$l['rate']);
  foreach(($l['allow']??[]) as $a) $d->addDocumentPositionAllowanceCharge((float)$a,false,null,null,"95","Rabatt");
  $d->setDocumentPositionLineSummation((float)$l['line_net']);
 }
 file_put_contents($argv[2]."/horstoeko-zugferd1.0.133-en16931+ref-totals__".$c["id"].".xml",$d->getContent());
}
echo "ok\n";
