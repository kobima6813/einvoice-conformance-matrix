// invopop/gobl driver: tax-inclusive shop carts (prices include VAT, % coupon as line discount, shipping as a 19% line),
// German regime with the eu-en16931-v2017 addon. GOBL calculates all totals; exported with gobl.ubl (Peppol BIS 3) and gobl.cii (EN 16931).
// usage: go run . <carts.json> <out_dir>
package main

import (
	"encoding/json"
	"fmt"
	"os"

	"github.com/invopop/gobl"
	"github.com/invopop/gobl/bill"
	cii "github.com/invopop/gobl.cii"
	ubl "github.com/invopop/gobl.ubl"
)

type line struct {
	Name, UnitGross string `json:"unit_gross"`
	Qty             int    `json:"qty"`
	Rate            string `json:"rate"`
}
type cart struct {
	ID, Pct, Ship string
	Lines         []struct {
		Name      string `json:"name"`
		Qty       int    `json:"qty"`
		UnitGross string `json:"unit_gross"`
		Rate      string `json:"rate"`
	} `json:"lines"`
}

func party(name, street, code, city, vat, scheme, ep string) map[string]any {
	p := map[string]any{"name": name, "addresses": []any{map[string]any{"street": street, "code": code, "locality": city, "country": "DE"}},
		"inboxes": []any{map[string]any{"key": "peppol", "scheme": scheme, "code": ep}}, "emails": []any{map[string]any{"addr": "rechnung@" + ep + ".example"}}}
	if vat != "" {
		p["tax_id"] = map[string]any{"country": "DE", "code": vat}
	}
	return p
}

func main() {
	var carts []cart
	b, _ := os.ReadFile(os.Args[1])
	if err := json.Unmarshal(b, &carts); err != nil {
		panic(err)
	}
	out := os.Args[2]
	os.MkdirAll(out, 0o755)
	n := 0
	for _, c := range carts {
		var lines []any
		for _, l := range c.Lines {
			ln := map[string]any{"quantity": fmt.Sprint(l.Qty), "item": map[string]any{"name": l.Name, "price": l.UnitGross, "unit": "item"},
				"taxes": []any{map[string]any{"cat": "VAT", "rate": map[bool]string{true: "standard", false: "reduced"}[l.Rate == "19"], "percent": l.Rate + "%"}}}
			if c.Pct != "" && c.Pct != "0" {
				ln["discounts"] = []any{map[string]any{"percent": c.Pct + "%", "reason": "Gutschein"}}
			}
			lines = append(lines, ln)
		}
		if c.Ship != "" && c.Ship != "0" && c.Ship != "0.00" {
			lines = append(lines, map[string]any{"quantity": "1", "item": map[string]any{"name": "Versand", "price": c.Ship, "unit": "item"},
				"taxes": []any{map[string]any{"cat": "VAT", "rate": "standard", "percent": "19%"}}})
		}
		doc := map[string]any{"$regime": "DE", "$addons": []string{"eu-en16931-v2017"}, "type": "standard", "code": c.ID, "issue_date": "2026-10-18", "currency": "EUR",
			"tax": map[string]any{"prices_include": "VAT"},
			"supplier": party("Beispiel Shop GmbH", "Hauptstraße 1", "10115", "Berlin", "111111125", "9930", "DE111111125"),
			"customer": party("Kunde AG", "Marktplatz 2", "80331", "München", "", "9930", "DE282741168"),
			"ordering": map[string]any{"code": "PO-" + c.ID}, "lines": lines,
			"payment": map[string]any{"instructions": map[string]any{"key": "credit-transfer", "credit_transfer": []any{map[string]any{"iban": "DE02120300000000202051"}}}}}
		js, _ := json.Marshal(doc)
		inv := new(bill.Invoice)
		if err := json.Unmarshal(js, inv); err != nil {
			panic(err)
		}
		env, err := gobl.Envelop(inv)
		if err != nil {
			fmt.Fprintln(os.Stderr, c.ID, err)
			continue
		}
		if u, err := ubl.Export(env, ubl.WithFormat(ubl.FormatPeppol)); err != nil {
			fmt.Fprintln(os.Stderr, c.ID, "ubl", err)
		} else if x, err := ubl.Encode(u); err == nil {
			os.WriteFile(fmt.Sprintf("%s/gobl0.510.0-ubl0.97.0-peppolbis3__%s.xml", out, c.ID), x, 0o644)
			n++
		}
		if d, err := cii.Export(env, cii.WithFormat(cii.FormatEN16931)); err != nil {
			fmt.Fprintln(os.Stderr, c.ID, "cii", err)
		} else if x, err := cii.Encode(d); err == nil {
			os.WriteFile(fmt.Sprintf("%s/gobl0.510.0-cii0.80.0-en16931__%s.xml", out, c.ID), x, 0o644)
			n++
		}
	}
	fmt.Println("gobl:", n, "invoices")
}
