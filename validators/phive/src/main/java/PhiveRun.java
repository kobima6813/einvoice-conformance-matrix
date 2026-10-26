// Validate every XML in <dir> with phive-rules 4.6.3: XRechnung 3.0.2 when the document declares an XRechnung
// guideline (BT-24), otherwise plain EN 16931 1.3.16 (CII or UBL by root). Write JSON lines.
// usage: java -cp <classpath> PhiveRun <dir> <out.jsonl>
import java.io.*; import java.nio.file.*; import java.util.*;
import com.helger.phive.api.execute.ValidationExecutionManager; import com.helger.phive.api.executorset.*;
import com.helger.phive.api.result.ValidationResultList; import com.helger.phive.api.validity.IValidityDeterminator;
import com.helger.phive.xml.source.*; import com.helger.phive.xrechnung.XRechnungValidation; import com.helger.xml.serialize.read.DOMReader;
public class PhiveRun { public static void main(String[] a) throws Exception {
  ValidationExecutorSetRegistry<IValidationSourceXML> reg = new ValidationExecutorSetRegistry<>(); com.helger.phive.en16931.EN16931Validation.initEN16931(reg); XRechnungValidation.initXRechnung(reg);
  var cii = reg.getOfID(XRechnungValidation.VID_XRECHNUNG_CII_302); var ubl = reg.getOfID(XRechnungValidation.VID_XRECHNUNG_UBL_INVOICE_302);
  var enCii = reg.getOfID(com.helger.phive.en16931.EN16931Validation.VID_CII_1316); var enUbl = reg.getOfID(com.helger.phive.en16931.EN16931Validation.VID_UBL_INVOICE_1316);
  try (PrintWriter w = new PrintWriter(new FileWriter(a[1])); var ds = Files.newDirectoryStream(Paths.get(a[0]), "*.xml")) {
    List<Path> ps = new ArrayList<>(); ds.forEach(ps::add); Collections.sort(ps);
    for (Path p : ps) {
      var doc = DOMReader.readXMLDOM(p.toFile()); boolean isUbl = doc.getDocumentElement().getNamespaceURI().contains("ubl"); boolean xr = Files.readString(p).contains("urn:xeinkauf.de:kosit:xrechnung");
      ValidationResultList r = ValidationExecutionManager.executeValidation(IValidityDeterminator.createDefault(), xr ? (isUbl ? ubl : cii) : (isUbl ? enUbl : enCii), ValidationSourceXML.create(null, doc));
      TreeSet<String> ids = new TreeSet<>(); r.getAllErrors().forEach(e -> { if (e.getErrorLevel().isError()) ids.add(e.getErrorID()!=null?e.getErrorID():("TEXT:"+e.getErrorText(java.util.Locale.ENGLISH))); });
      w.println("{\"file\":\"" + p.getFileName() + "\",\"rule_set\":\"" + (xr ? "xrechnung-3.0.2" : "en16931-1.3.16") + "\",\"valid\":" + r.containsNoError() + ",\"errors\":[" + String.join(",", ids.stream().map(s -> "\"" + s.replace("\"","") + "\"").toList()) + "]}");
    }
  }
}}
