// Validate every XML in <dir> with phive-rules 4.6.3, XRechnung 3.0.2 (CII or UBL by root), write JSON lines.
// usage: java -cp <classpath> PhiveRun <dir> <out.jsonl>
import java.io.*; import java.nio.file.*; import java.util.*;
import com.helger.phive.api.execute.ValidationExecutionManager; import com.helger.phive.api.executorset.*;
import com.helger.phive.api.result.ValidationResultList; import com.helger.phive.api.validity.IValidityDeterminator;
import com.helger.phive.xml.source.*; import com.helger.phive.xrechnung.XRechnungValidation; import com.helger.xml.serialize.read.DOMReader;
public class PhiveRun { public static void main(String[] a) throws Exception {
  ValidationExecutorSetRegistry<IValidationSourceXML> reg = new ValidationExecutorSetRegistry<>(); com.helger.phive.en16931.EN16931Validation.initEN16931(reg); XRechnungValidation.initXRechnung(reg);
  var cii = reg.getOfID(XRechnungValidation.VID_XRECHNUNG_CII_302); var ubl = reg.getOfID(XRechnungValidation.VID_XRECHNUNG_UBL_INVOICE_302);
  try (PrintWriter w = new PrintWriter(new FileWriter(a[1])); var ds = Files.newDirectoryStream(Paths.get(a[0]), "*.xml")) {
    List<Path> ps = new ArrayList<>(); ds.forEach(ps::add); Collections.sort(ps);
    for (Path p : ps) {
      var doc = DOMReader.readXMLDOM(p.toFile()); boolean isUbl = doc.getDocumentElement().getNamespaceURI().contains("ubl");
      ValidationResultList r = ValidationExecutionManager.executeValidation(IValidityDeterminator.createDefault(), isUbl ? ubl : cii, ValidationSourceXML.create(null, doc));
      TreeSet<String> ids = new TreeSet<>(); r.getAllErrors().forEach(e -> { if (e.getErrorLevel().isError()) ids.add(e.getErrorID()!=null?e.getErrorID():("TEXT:"+e.getErrorText(java.util.Locale.ENGLISH))); });
      w.println("{\"file\":\"" + p.getFileName() + "\",\"valid\":" + r.containsNoError() + ",\"errors\":[" + String.join(",", ids.stream().map(s -> "\"" + s.replace("\"","") + "\"").toList()) + "]}");
    }
  }
}}
