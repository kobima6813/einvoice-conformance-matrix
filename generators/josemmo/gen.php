<?php
// josemmo/einvoicing 0.3.1 driver: the library computes all totals from net line prices (carts_net.json).
// usage: php gen.php <carts_net.json> <out_dir> <config: default|round2>
require __DIR__ . '/vendor/autoload.php';
use Einvoicing\{Invoice, InvoiceLine, Party, Identifier, AllowanceOrCharge};
use Einvoicing\Payments\{Payment, Transfer};
use Einvoicing\Writers\UblWriter;
[$_, $in, $out, $cfg] = $argv; @mkdir($out, 0777, true);
$tag = "josemmo0.3.1-xrechnung-$cfg"; $w = new UblWriter(); $n = 0;
foreach (json_decode(file_get_contents($in), true) as $o) {
  $inv = new Invoice();
  $inv->setSpecification('urn:cen.eu:en16931:2017#compliant#urn:xeinkauf.de:kosit:xrechnung_3.0');
  $inv->setBusinessProcess('urn:fdc:peppol.eu:2017:poacc:billing:01:1.0');
  if ($cfg === 'round2') $inv->setRoundingMatrix(['' => 2]);
  $inv->setNumber($o['id'])->setIssueDate(new DateTime('2026-10-18'))->setCurrency('EUR')->setBuyerReference('04011000-12345-03');
  $s = (new Party())->setName('Muster Shop GmbH')->setVatNumber('DE123456788')->setAddress(['Musterstr. 1'])->setCity('Berlin')->setPostalCode('10115')->setCountry('DE')
      ->setElectronicAddress(new Identifier('shop@example.com', 'EM'))->setContactName('Buchhaltung')->setContactPhone('+49 30 000000')->setContactEmail('shop@example.com');
  $b = (new Party())->setName('Kunde AG')->setAddress(['Kundenweg 2'])->setCity('München')->setPostalCode('80331')->setCountry('DE')->setElectronicAddress(new Identifier('kunde@example.com', 'EM'));
  $inv->setSeller($s)->setBuyer($b);
  $inv->setPaymentTerms('Zahlbar sofort')->addPayment((new Payment())->setMeansCode('58')->addTransfer((new Transfer())->setAccountId('DE79000000001234567890')));
  foreach ($o['lines'] as $l) {
    $li = (new InvoiceLine())->setName($l['name'])->setQuantity((float)$l['qty'])->setUnit('H87')->setPrice((float)$l['price'])->setVatCategory('S')->setVatRate((float)$l['rate']);
    foreach ($l['allow'] as $a) $li->addAllowance((new AllowanceOrCharge())->setAmount((float)$a)->setReason('Rabatt'));
    $inv->addLine($li);
  }
  file_put_contents("$out/{$tag}__{$o['id']}.xml", $w->export($inv)); $n++;
}
echo "josemmo $cfg: $n invoices\n";
