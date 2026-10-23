// ZUGFeRD-csharp 18.0.1 driver. The library does not compute document totals, so the reference EN 16931 totals
// (ref_en16931_rounding.json) are supplied. Configs: XRechnung profile as CII, CII with a delivery date (BT-72), and UBL.
// usage: dotnet run -- <ref_en16931_rounding.json> <out_dir>
using System.Globalization; using System.Text.Json; using s2industries.ZUGFeRD;
var ci = CultureInfo.InvariantCulture; decimal D(JsonElement e) => decimal.Parse(e.GetString()!, ci);
var orders = JsonDocument.Parse(File.ReadAllText(args[0])).RootElement; Directory.CreateDirectory(args[1]);
foreach (var (fmt, cfg) in new[] { (ZUGFeRDFormats.CII, "xrechnung-cii"), (ZUGFeRDFormats.CII, "xrechnung-cii-deliverydate"), (ZUGFeRDFormats.UBL, "xrechnung-ubl") })
foreach (var o in orders.EnumerateArray()) {
  var id = o.GetProperty("id").GetString()!; var T = o.GetProperty("T");
  var d = InvoiceDescriptor.CreateInvoice(id, new DateTime(2026, 10, 18), CurrencyCodes.EUR);
  d.ReferenceOrderNo = null; d.BusinessProcess = "urn:fdc:peppol.eu:2017:poacc:billing:01:1.0";
  d.SetBuyerOrderReferenceDocument(null, null);
  d.ReferenceOrderNo = "04011000-12345-03";
  if (cfg.EndsWith("deliverydate")) d.ActualDeliveryDate = new DateTime(2026, 10, 17); // BT-72; works around the empty-delivery issue (PR #981)
  d.SetSeller("Muster Shop GmbH", "10115", "Berlin", "Musterstr. 1", CountryCodes.DE);
  d.AddSellerTaxRegistration("DE123456788", TaxRegistrationSchemeID.VA);
  d.SetSellerContact("Buchhaltung", null, "shop@example.com", "+49 30 000000");
  d.SetSellerElectronicAddress("shop@example.com", ElectronicAddressSchemeIdentifiers.ElectronicMailSmtp);
  d.SetBuyer("Kunde AG", "80331", "München", "Kundenweg 2", CountryCodes.DE);
  d.SetBuyerElectronicAddress("kunde@example.com", ElectronicAddressSchemeIdentifiers.ElectronicMailSmtp);
  d.SetPaymentMeans(PaymentMeansTypeCodes.SEPACreditTransfer); d.AddCreditorFinancialAccount("DE79000000001234567890", null);
  d.AddTradePaymentTerms("Zahlbar sofort");
  int n = 0;
  foreach (var l in o.GetProperty("L").EnumerateArray()) {
    var li = d.AddTradeLineItem((++n).ToString(), l.GetProperty("name").GetString()!, D(l.GetProperty("net_price")), QuantityCodes.H87,
      billedQuantity: D(l.GetProperty("qty")), lineTotalAmount: D(l.GetProperty("line_net")), taxType: TaxTypes.VAT,
      categoryCode: TaxCategoryCodes.S, taxPercent: D(l.GetProperty("rate")));
    if (l.TryGetProperty("allow", out var al)) foreach (var a in al.EnumerateArray()) li.AddSpecifiedTradeAllowance(CurrencyCodes.EUR, null, D(a), "Rabatt");
  }
  foreach (var x in o.GetProperty("tax").EnumerateArray())
    d.AddApplicableTradeTax(D(x.GetProperty("basis")), D(x.GetProperty("rate")), D(x.GetProperty("tax")), TaxTypes.VAT, TaxCategoryCodes.S);
  decimal? rnd = T.TryGetProperty("rounding", out var r) ? D(r) : null;
  d.SetTotals(D(T.GetProperty("line")), 0m, 0m, D(T.GetProperty("basis")), D(T.GetProperty("tax")), D(T.GetProperty("grand")), 0m, D(T.GetProperty("due")), rnd);
  using var fs = File.Create(Path.Combine(args[1], $"zugferdcs18.0.1-{cfg}+ref-totals__{id}.xml"));
  d.Save(fs, ZUGFeRDVersion.Version23, Profile.XRechnung, fmt);
}
Console.WriteLine("zugferd-csharp done");
