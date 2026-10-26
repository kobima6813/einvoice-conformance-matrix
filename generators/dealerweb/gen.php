<?php
// dealerweb/einvoice 1.2.1 driver: library calculates line nets, VAT breakdown and totals (XRechnung CII).
// usage: php gen.php <corpus_dir>/carts_net.json <out_dir>
require __DIR__.'/vendor/autoload.php';
use Dealerweb\EInvoice\Invoice; use Dealerweb\EInvoice\Profile;
use Dealerweb\EInvoice\Model\{Line,AllowanceCharge,Identifier,PaymentMeans};
$C=json_decode(file_get_contents($argv[1]),true); @mkdir($argv[2],0777,true); $err=0;
foreach($C as $c){
 $i=new Invoice(); $i->number=$c['id']; $i->typeCode='380'; $i->issueDate='2026-10-18'; $i->currency='EUR';
 $i->businessProcess='urn:fdc:peppol.eu:2017:poacc:billing:01:1.0'; $i->buyerReference='04011000-12345-03';
 $i->paymentTerms='Zahlbar sofort';
 $s=$i->seller; $s->name='Muster Shop GmbH'; $s->vatId='DE123456788'; $s->electronicAddress=new Identifier('rechnung@muster.example','EM');
 $s->address->line1='Musterstr. 1'; $s->address->postcode='10115'; $s->address->city='Berlin'; $s->address->country='DE';
 $s->contact->name='Buchhaltung'; $s->contact->phone='+49 30 1234567'; $s->contact->email='rechnung@muster.example';
 $b=$i->buyer; $b->name='Kunde AG'; $b->electronicAddress=new Identifier('kunde@kunde.example','EM');
 $b->address->line1='Kundenweg 2'; $b->address->postcode='80331'; $b->address->city='München'; $b->address->country='DE';
 $i->paymentMeans[]=new PaymentMeans(typeCode:'58',accountId:'DE02120300000000202051');
 $n=0; foreach($c['lines'] as $l){ $n++;
  $i->lines[]=new Line(id:(string)$n,name:$l['name'],quantity:$l['qty'],unit:'H87',netPrice:$l['price'],vatCategory:'S',vatRate:$l['rate'],
    allowances:array_map(fn($a)=>new AllowanceCharge(amount:$a,reason:'Rabatt',reasonCode:'95'),$l['allow']??[]));
 }
 try { file_put_contents($argv[2]."/dealerweb-einvoice1.2.1-auto-totals-xrechnung__".$c['id'].".xml",$i->toXml(Profile::XRechnung)); }
 catch(Throwable $e){ $err++; if($err<4) fwrite(STDERR,$c['id'].": ".$e->getMessage()."\n"); }
}
echo "ok (".count($C)." carts, $err refused by the library)\n";
