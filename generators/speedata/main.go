// speedata/einvoice v0.0.23 driver. Line net amounts (BT-131) are set by the integrator (price*qty - line allowances);
// the library computes the VAT breakdown (UpdateApplicableTradeTax) and document totals (UpdateTotals).
// usage: go run . <carts_net.json> <out_dir>
package main

import (
	"encoding/json"; "fmt"; "os"; "path/filepath"; "time"
	"github.com/shopspring/decimal"
	ei "github.com/speedata/einvoice"
)

type line struct{ Name, Qty, Price, Rate string; Allow []string }
type order struct{ ID string; Lines []line }

func main() {
	var orders []order
	b, _ := os.ReadFile(os.Args[1]); if err := json.Unmarshal(b, &orders); err != nil { panic(err) }
	os.MkdirAll(os.Args[2], 0o755)
	for _, st := range []struct{ t ei.CodeSchemaType; cfg string }{{ei.CII, "xrechnung-cii"}, {ei.UBL, "xrechnung-ubl"}} {
		for _, o := range orders {
			inv := &ei.Invoice{
				GuidelineSpecifiedDocumentContextParameter: "urn:cen.eu:en16931:2017#compliant#urn:xeinkauf.de:kosit:xrechnung_3.0",
				BPSpecifiedDocumentContextParameter:        "urn:fdc:peppol.eu:2017:poacc:billing:01:1.0",
				InvoiceNumber: o.ID, InvoiceTypeCode: 380, InvoiceDate: time.Date(2026, 10, 18, 0, 0, 0, 0, time.UTC),
				InvoiceCurrencyCode: "EUR", TaxTotalCurrency: "EUR", BuyerReference: "04011000-12345-03", SchemaType: st.t,
				Seller: ei.Party{Name: "Muster Shop GmbH", VATaxRegistration: "DE123456788", URIUniversalCommunication: "shop@example.com", URIUniversalCommunicationScheme: "EM",
					PostalAddress: &ei.PostalAddress{CountryID: "DE", PostcodeCode: "10115", Line1: "Musterstr. 1", City: "Berlin"},
					DefinedTradeContact: []ei.DefinedTradeContact{{PersonName: "Buchhaltung", EMail: "shop@example.com", PhoneNumber: "+49 30 000000"}}},
				Buyer: ei.Party{Name: "Kunde AG", URIUniversalCommunication: "kunde@example.com", URIUniversalCommunicationScheme: "EM",
					PostalAddress: &ei.PostalAddress{CountryID: "DE", PostcodeCode: "80331", Line1: "Kundenweg 2", City: "München"}},
				PaymentMeans: []ei.PaymentMeans{{TypeCode: 58, PayeePartyCreditorFinancialAccountIBAN: "DE79000000001234567890"}},
				SpecifiedTradePaymentTerms: []ei.SpecifiedTradePaymentTerms{{Description: "Zahlbar sofort"}},
			}
			for i, l := range o.Lines {
				q, p, r := decimal.RequireFromString(l.Qty), decimal.RequireFromString(l.Price), decimal.RequireFromString(l.Rate)
				tot := q.Mul(p); var al []ei.AllowanceCharge
				for _, a := range l.Allow { d := decimal.RequireFromString(a); tot = tot.Sub(d); al = append(al, ei.AllowanceCharge{ActualAmount: d, Reason: "Rabatt"}) }
				inv.InvoiceLines = append(inv.InvoiceLines, ei.InvoiceLine{LineID: fmt.Sprint(i + 1), ItemName: l.Name, NetPrice: p, BilledQuantity: q, BilledQuantityUnit: "H87",
					TaxTypeCode: "VAT", TaxCategoryCode: "S", TaxRateApplicablePercent: r, Total: tot, InvoiceLineAllowances: al})
			}
			inv.UpdateApplicableTradeTax(nil); inv.UpdateTotals()
			f, _ := os.Create(filepath.Join(os.Args[2], fmt.Sprintf("speedata0.0.23-%s__%s.xml", st.cfg, o.ID)))
			if err := inv.Write(f); err != nil { panic(err) }; f.Close()
		}
	}
	fmt.Println("speedata done")
}
