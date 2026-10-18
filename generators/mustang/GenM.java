// Mustang 2.26.0 driver: gives Mustang net line prices and allowances and lets it compute all totals
// (XRechnung profile). usage: java -cp Mustang-CLI-2.26.0.jar:. GenM <corpus_dir>/carts_net.json <out_dir>
import org.mustangproject.*; import org.mustangproject.ZUGFeRD.*; import com.fasterxml.jackson.databind.*;
import java.math.BigDecimal; import java.nio.file.*; import java.util.*; import java.text.SimpleDateFormat;
public class GenM { public static void main(String[] a) throws Exception {
  JsonNode carts=new ObjectMapper().readTree(new java.io.File(a[0])); Files.createDirectories(Paths.get(a[1]));
  Date d=new SimpleDateFormat("yyyy-MM-dd").parse("2026-10-18");
  for (JsonNode c: carts) {
    TradeParty seller=new TradeParty("Muster Shop GmbH","Musterstr. 1","10115","Berlin","DE").addVATID("DE123456789").setEmail("shop@example.de")
      .setContact(new Contact("Max Muster","+49 1234 5678","shop@example.de")).addBankDetails(new BankDetails("DE79000000001234567890"));
    TradeParty buyer=new TradeParty("Kunde AG","Kundenweg 2","80331","München","DE").setEmail("buyer@example.de");
    Invoice inv=new Invoice().setNumber(c.get("id").asText()).setReferenceNumber("04011000-12345-03").setIssueDate(d).setDueDate(d).setDeliveryDate(d)
      .setSender(seller).setRecipient(buyer).setPaymentTermDescription("Zahlbar sofort.");
    for (JsonNode l: c.get("lines")) {
      Item it=new Item(new Product(l.get("name").asText(),"","H87",new BigDecimal(l.get("rate").asText())), new BigDecimal(l.get("price").asText()), new BigDecimal(l.get("qty").asText()));
      for (JsonNode al: l.get("allow")) it.addAllowance(new Allowance(new BigDecimal(al.asText())).setReason("Rabatt"));
      inv.addItem(it);
    }
    ZUGFeRD2PullProvider p=new ZUGFeRD2PullProvider(); p.setProfile(Profiles.getByName("XRechnung")); p.generateXML(inv);
    Files.write(Paths.get(a[1], "mustang2.26.0-auto-totals-xrechnung__"+c.get("id").asText()+".xml"), p.getXML());
  }}}
