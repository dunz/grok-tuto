import { zodResponseFormat } from "openai/helpers/zod";
import { z } from "zod";
import client from "./clinet.js";

const CurrencyEnum = z.enum(["USD", "EUR", "GBP"]);

const LineItemSchema = z.object({
  description: z.string().describe("Description of the item or service"),
  quantity: z.number().int().min(1).describe("Number of units"),
  unit_price: z.number().min(0).describe("Price per unit"),
});

const AddressSchema = z.object({
  street: z.string().describe("Street address"),
  city: z.string().describe("City"),
  postal_code: z.string().describe("Postal/ZIP code"),
  country: z.string().describe("Country"),
});

const InvoiceSchema = z.object({
  vendor_name: z.string().describe("Name of the vendor"),
  vendor_address: AddressSchema.describe("Vendor's address"),
  invoice_number: z.string().describe("Unique invoice identifier"),
  invoice_date: z.string().date().describe("Date the invoice was issued"),
  line_items: z.array(LineItemSchema).describe("List of purchased items/services"),
  total_amount: z.number().min(0).describe("Total amount due"),
  currency: CurrencyEnum.describe("Currency of the invoice"),
});

const completion = await client.beta.chat.completions.parse({
  model: "grok-2-latest",
  messages: [
    { role: "system", content: "Given a raw invoice, carefully analyze the text and extract the invoice data into JSON format." },
    { role: "user", content: `
      Vendor: Acme Corp, 123 Main St, Springfield, IL 62704
      Invoice Number: INV-2025-001
      Date: 2025-02-10
      Items:
      - Widget A, 5 units, $10.00 each
      - Widget B, 2 units, $15.00 each
      Total: $80.00 USD
    ` },
  ],
  response_format: zodResponseFormat(InvoiceSchema, "invoice"),
});

const invoice = completion.choices[0].message.parsed;
console.log(completion.choices[0].message);
