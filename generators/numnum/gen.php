<?php
// num-num/ubl-invoice 2.4.1 driver (Peppol BIS Billing 3.0 UBL, Belgian seller/buyer). The library computes no totals:
// the reference EN 16931 amounts from prep.py are passed as PHP floats, exactly as the library API expects.
// usage: php gen.php <ref.json> <out_dir>
require __DIR__ . '/vendor/autoload.php';
use NumNum\UBL as U;
[$_, $in, $out] = $argv; @mkdir($out, 0777, true);
$tag = 'numnum2.4.1-peppolbis3+ref-totals'; $g = new U\Generator(); $n = 0;
$vat = (new U\TaxScheme())->setId('VAT');
function party($name, $vatid, $street, $city, $zip, $ep, $vat) {
  $a = (new U\Address())->setStreetName($street)->setCityName($city)->setPostalZone($zip)->setCountry((new U\Country())->setIdentificationCode('BE'));
  return (new U\Party())->setName($name)->setEndpointId($ep, '0208')->setPostalAddress($a)
    ->setLegalEntity((new U\LegalEntity())->setRegistrationName($name)->setCompanyId($ep))
    ->setPartyTaxScheme((new U\PartyTaxScheme())->setTaxScheme($vat)->setCompanyId($vatid));
}
$sup = (new U\AccountingParty())->setParty(party('Voorbeeld Winkel BV', 'BE0123456749', 'Korenmarkt 1', 'Gent', '9000', '0123456749', $vat));
$cus = (new U\AccountingParty())->setParty(party('Klant NV', 'BE0987654394', 'Meir 2', 'Antwerpen', '2000', '0987654394', $vat));
$pm = (new U\PaymentMeans())->setPaymentMeansCode(58, [])->setPayeeFinancialAccount((new U\PayeeFinancialAccount())->setId('BE71096123456769'));
foreach (json_decode(file_get_contents($in), true) as $o) {
  $lines = [];
  foreach ($o['lines'] as $i => $l) {
    $cat = (new U\ClassifiedTaxCategory())->setId('S')->setPercent((float)$l['rate'])->setTaxScheme($vat);
    $ac = [];
    foreach ($l['allow'] as $a) $ac[] = (new U\AllowanceCharge())->setChargeIndicator(false)->setAllowanceChargeReason('Korting')->setAmount((float)$a);
    $li = (new U\InvoiceLine())->setId((string)($i + 1))->setInvoicedQuantity((float)$l['qty'])->setUnitCode('H87')->setLineExtensionAmount((float)$l['net'])
      ->setItem((new U\Item())->setName($l['name'])->setClassifiedTaxCategory($cat))
      ->setPrice((new U\Price())->setBaseQuantity(1)->setUnitCode('H87')->setPriceAmount((float)$l['price']));
    if ($ac) $li->setAllowanceCharges($ac);
    $lines[] = $li;
  }
  $tt = (new U\TaxTotal())->setTaxAmount((float)$o['tot']['tax']);
  foreach ($o['tax'] as $t) $tt->addTaxSubTotal((new U\TaxSubTotal())->setTaxableAmount((float)$t['basis'])->setTaxAmount((float)$t['tax'])
      ->setTaxCategory((new U\TaxCategory())->setId('S', [])->setPercent((float)$t['rate'])->setTaxScheme($vat)));
  $T = $o['tot'];
  $m = (new U\LegalMonetaryTotal())->setLineExtensionAmount((float)$T['line'])->setTaxExclusiveAmount((float)$T['basis'])
      ->setTaxInclusiveAmount((float)$T['grand'])->setPayableAmount((float)$T['due']);
  if ($T['rounding'] ?? null) $m->setPayableRoundingAmount((float)$T['rounding']);
  $inv = (new U\Invoice())->setCustomizationId('urn:cen.eu:en16931:2017#compliant#urn:fdc:peppol.eu:2017:poacc:billing:3.0')
    ->setProfileId('urn:fdc:peppol.eu:2017:poacc:billing:01:1.0')->setId($o['id'])->setIssueDate(new DateTime('2026-10-18'))->setDueDate(new DateTime('2026-11-17'))
    ->setBuyerReference('PO-' . $o['id'])->setAccountingSupplierParty($sup)->setAccountingCustomerParty($cus)
    ->setPaymentMeans([$pm])->setPaymentTerms((new U\PaymentTerms())->setNote('Onmiddellijk betaalbaar'))
    ->setInvoiceLines($lines)->setTaxTotal($tt)->setLegalMonetaryTotal($m);
  file_put_contents("$out/{$tag}__{$o['id']}.xml", $g->invoice($inv)); $n++;
}
echo "numnum: $n invoices\n";
