<?php
// easybill/zugferd-php 6.0.0 driver (XRechnung 3.0 CII, German seller/buyer). The library is a pure data model + serializer
// (computes no totals): the reference EN 16931 amounts from prep.py are passed as decimal strings.
// usage: php gen.php <ref.json> <out_dir>
require __DIR__ . '/vendor/autoload.php';
use Easybill\ZUGFeRD2\Builder; use Easybill\ZUGFeRD2\Model as M;
[$_, $in, $out] = $argv; @mkdir($out, 0777, true);
$tag = 'easybill-zugferd6.0.0-xrechnung+ref-totals'; $b = Builder::create(); $n = 0;
function party($name, $street, $zip, $city, $vat, $mail) {
  $p = new M\TradeParty(); $p->name = $name; $a = new M\TradeAddress(); $a->postcodeCode = $zip; $a->lineOne = $street; $a->cityName = $city; $a->countryID = 'DE';
  $p->postalTradeAddress = $a; $u = new M\UniversalCommunication(); $u->uriid = M\Id::create($mail, 'EM'); $p->uriUniversalCommunication = $u;
  if ($vat) $p->taxRegistrations[] = M\TaxRegistration::create($vat, 'VA'); return $p;
}
function vat($rate, $basis = null, $tax = null) { $t = new M\TradeTax(); $t->typeCode = 'VAT'; $t->categoryCode = 'S'; $t->rateApplicablePercent = $rate;
  if ($basis !== null) { $t->basisAmount = M\Amount::create($basis); $t->calculatedAmount = M\Amount::create($tax); } return $t; }
foreach (json_decode(file_get_contents($in), true) as $o) {
  $inv = new M\CrossIndustryInvoice(); $inv->exchangedDocumentContext = $c = new M\ExchangedDocumentContext();
  $c->documentContextParameter = M\DocumentContextParameter::create(Builder::GUIDELINE_SPECIFIED_DOCUMENT_CONTEXT_ID_XRECHNUNG);
  $c->businessProcessSpecifiedDocumentContextParameter = M\DocumentContextParameter::create('urn:fdc:peppol.eu:2017:poacc:billing:01:1.0');
  $inv->exchangedDocument = $d = new M\ExchangedDocument(); $d->id = $o['id']; $d->typeCode = '380'; $d->issueDateTime = M\DateTime::create(102, '20261018');
  $inv->supplyChainTradeTransaction = $tx = new M\SupplyChainTradeTransaction();
  foreach ($o['lines'] as $i => $l) {
    $it = new M\SupplyChainTradeLineItem(); $it->associatedDocumentLineDocument = M\DocumentLineDocument::create((string)($i + 1));
    $it->specifiedTradeProduct = new M\TradeProduct(); $it->specifiedTradeProduct->name = $l['name'];
    $it->tradeAgreement = new M\LineTradeAgreement(); $it->tradeAgreement->netPrice = M\TradePrice::create($l['price']);
    $it->delivery = new M\LineTradeDelivery(); $it->delivery->billedQuantity = M\Quantity::create($l['qty'], 'H87');
    $it->specifiedLineTradeSettlement = $s = new M\LineTradeSettlement(); $s->tradeTax[] = vat($l['rate']);
    foreach ($l['allow'] as $a) { $ind = new M\Indicator(); $ind->indicator = false; $s->specifiedTradeAllowanceCharge[] = M\TradeAllowanceCharge::create(actualAmount: M\Amount::create($a), indicator: $ind, reason: 'Rabatt'); }
    $s->monetarySummation = M\TradeSettlementLineMonetarySummation::create($l['net']);
    $tx->lineItems[] = $it;
  }
  $tx->applicableHeaderTradeAgreement = $ag = new M\HeaderTradeAgreement(); $ag->buyerReference = 'PO-' . $o['id'];
  $ag->sellerTradeParty = party('Beispiel Shop GmbH', 'Hauptstraße 1', '10115', 'Berlin', 'DE123456789', 'rechnung@beispiel-shop.de');
  $ct = new M\TradeContact(); $ct->personName = 'Buchhaltung'; $ct->telephoneUniversalCommunication = new M\UniversalCommunication(); $ct->telephoneUniversalCommunication->completeNumber = '+49301234567';
  $ct->emailURIUniversalCommunication = new M\UniversalCommunication(); $ct->emailURIUniversalCommunication->uriid = M\Id::create('rechnung@beispiel-shop.de'); $ag->sellerTradeParty->definedTradeContact[] = $ct;
  $ag->buyerTradeParty = party('Kunde AG', 'Marktplatz 2', '80331', 'München', null, 'einkauf@kunde.example');
  $tx->applicableHeaderTradeDelivery = $dl = new M\HeaderTradeDelivery(); $dl->actualDeliverySupplyChainEvent = new M\SupplyChainEvent(); $dl->actualDeliverySupplyChainEvent->occurrenceDateTime = M\DateTime::create(102, '20261017');
  $tx->applicableHeaderTradeSettlement = $st = new M\HeaderTradeSettlement(); $st->invoiceCurrencyCode = 'EUR';
  $st->specifiedTradeSettlementPaymentMeans[] = $pm = new M\TradeSettlementPaymentMeans(); $pm->typeCode = '58';
  $pm->payeePartyCreditorFinancialAccount = new M\CreditorFinancialAccount(); $pm->payeePartyCreditorFinancialAccount->ibanId = M\Id::create('DE02120300000000202051');
  foreach ($o['tax'] as $t) $st->tradeTaxes[] = vat($t['rate'], $t['basis'], $t['tax']);
  $st->specifiedTradePaymentTerms[] = $pt = new M\TradePaymentTerms(); $pt->description = 'Zahlbar sofort ohne Abzug';
  $T = $o['tot']; $st->specifiedTradeSettlementHeaderMonetarySummation = $sm = new M\TradeSettlementHeaderMonetarySummation();
  $sm->lineTotalAmount = M\Amount::create($T['line']); $sm->taxBasisTotalAmount[] = M\Amount::create($T['basis']); $sm->taxTotalAmount[] = M\Amount::create($T['tax'], 'EUR');
  if ($T['rounding'] ?? null) $sm->roundingAmount = M\Amount::create($T['rounding']);
  $sm->grandTotalAmount[] = M\Amount::create($T['grand']); $sm->duePayableAmount = M\Amount::create($T['due']);
  file_put_contents("$out/{$tag}__{$o['id']}.xml", $b->transform($inv)); $n++;
}
echo "easybill: $n invoices\n";
