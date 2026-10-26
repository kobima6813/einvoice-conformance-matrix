# DRAFT — not posted

**Note:** this bug is already reported upstream as
[jslno/node-zugferd#116](https://github.com/jslno/node-zugferd/issues/116)
("line[].tradeSettlement.allowances is missing ChargeIndicator"). It was opened on 17 Jun 2026, is still open and has no comments.
A new issue would be a duplicate. **Recommended:** post the text below as a comment on #116, not as a new issue.
The text works either way: for a standalone issue, use the title below.

Title (only if filed as a new issue): `EN16931: line allowance (BG-27) fails XSD — ActualAmount written before ChargeIndicator`

---

Additional repro for this, on node-zugferd **0.1.1-beta.1** (Node 20.19.2, EN16931 profile).

Any invoice line with `tradeSettlement.allowances` fails the library's own XSD check, so `toXML()` rejects it:

```
invalid xml (status=WITH_ERRORS)
  [error] cvc-complex-type.2.4.a: Invalid content was found starting with element
  '{"urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100":ActualAmount}'.
  One of '{"...:100":ChargeIndicator}' is expected.
```

Inside `ram:SpecifiedTradeAllowanceCharge`, the CII XSD requires `ram:ChargeIndicator` before `ram:ActualAmount`.
The schema declares `chargeIndicator` (BG-27-0) as `additionalXml` of `actualAmount` (BT-136), but it is not emitted
before `ActualAmount`. Passing `chargeIndicator: false` explicitly makes no difference, as #116 also says.

Minimal repro (`node repro.mjs`):

```js
import { zugferd } from "node-zugferd";
import { EN16931 } from "node-zugferd/profile/en16931";

const invoicer = zugferd({ profile: EN16931 });
const addr = { postCode: "10115", line1: "Musterstr. 1", city: "Berlin", countryCode: "DE" };
const data = {
  number: "R-1", typeCode: "380", issueDate: new Date("2026-10-26"),
  transaction: {
    line: [{
      identifier: "1", tradeProduct: { name: "Item" },
      tradeAgreement: { netTradePrice: { chargeAmount: "100.00" } },
      tradeDelivery: { billedQuantity: { amount: 1, unitMeasureCode: "H87" } },
      tradeSettlement: {
        tradeTax: { typeCode: "VAT", categoryCode: "S", rateApplicablePercent: "19" },
        allowances: [{ actualAmount: "10.00", reasonCode: "95", reason: "Discount" }], // remove this line -> OK
        monetarySummation: { lineTotalAmount: "90.00" },
      },
    }],
    tradeAgreement: {
      seller: { name: "Seller GmbH", postalAddress: addr, taxRegistration: { vatIdentifier: "DE123456788" } },
      buyer: { name: "Buyer AG", postalAddress: addr },
    },
    tradeDelivery: { information: { deliveryDate: new Date("2026-10-26") } },
    tradeSettlement: {
      currencyCode: "EUR",
      vatBreakdown: [{ calculatedAmount: "17.10", typeCode: "VAT", basisAmount: "90.00", categoryCode: "S", rateApplicablePercent: "19" }],
      paymentTerms: { dueDate: new Date("2026-11-25") },
      monetarySummation: { lineTotalAmount: "90.00", taxBasisTotalAmount: "90.00",
        taxTotal: { amount: "17.10", currencyCode: "EUR" }, grandTotalAmount: "107.10", duePayableAmount: "107.10" },
    },
  },
};
console.log(await invoicer.create(data).toXML());
```

- **With the `allowances` line:** the call throws the error above.
- **Without it:** the call succeeds.

**Expected:** inside each `ram:SpecifiedTradeAllowanceCharge`, `<ram:ChargeIndicator><udt:Indicator>false</udt:Indicator></ram:ChargeIndicator>`
is written first, followed by `ram:ActualAmount`, `ram:ReasonCode` and `ram:Reason`.

**Impact in a larger test:** we generated 600 synthetic shop carts (EN 16931, 19 %/7 % VAT) with node-zugferd.
- The 302 carts with a line-level discount all fail with this error.
- The other 298 are accepted by the KoSIT validator and by phive-rules (EN 16931 1.3.16).

#85 (closed) covered the same element-order problem for document-level allowances; the line-level path still shows it.
