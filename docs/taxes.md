# Taxes on invoices

Kestrel calculates sales tax, VAT and GST on your invoices using the rates you configure. Kestrel does not file tax returns for you.

## Adding tax rates

Go to **Settings > Taxes** and select **Add tax rate**. Give the rate a name, such as "VAT 20%", and a percentage. You can create as many rates as you need and set one as the default for new line items.

## Applying multiple taxes

Each line item can have up to two taxes. This covers regions that charge a federal and a provincial tax at the same time. You can choose whether the second tax is calculated on the subtotal or compounded on top of the first tax.

## Tax-inclusive pricing

By default, unit prices exclude tax and Kestrel adds tax on top. To enter prices that already include tax, turn on **Prices include tax** in **Settings > Taxes**. The invoice then shows the tax portion of each price separately.

## Reverse charge and tax-exempt clients

For business clients in another EU country, mark the client as **Reverse charge**. Kestrel removes VAT from their invoices and adds the required reverse-charge note. For tax-exempt clients, add their exemption number to the client profile and Kestrel skips tax on new invoices.

## Tax reports

**Reports > Tax summary** shows the tax collected per rate for any date range, based on paid invoices. You can export the report to CSV and share it with your accountant.
