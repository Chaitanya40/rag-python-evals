# Creating and managing invoices

Invoices are the core of Kestrel. This article covers editing, numbering, reminders and recurring invoices.

## Editing a sent invoice

You can edit a sent invoice until it receives its first payment. Kestrel records every change in the activity timeline, and your client sees the updated version the next time they open the link. Once an invoice is partly or fully paid, it is locked. To correct a paid invoice, issue a credit note from the invoice's **More** menu and send a new invoice.

## Invoice numbering

Kestrel numbers invoices sequentially, starting at INV-0001. To change the prefix or the next number, open **Settings > Invoices > Numbering**. The next number must be higher than any invoice number already used, because many tax authorities require gapless, increasing sequences. Deleted draft invoices do not consume a number.

## Payment reminders

Automatic reminders are off by default. Turn them on in **Settings > Invoices > Reminders**. You can schedule up to three reminders, for example 3 days before the due date, on the due date, and 7 days after it. Reminders stop as soon as the invoice is paid in full.

## Recurring invoices

A recurring invoice is a template that Kestrel sends on a schedule: weekly, monthly, quarterly or yearly.

### Setting up a schedule

Open any invoice and choose **Make recurring**. Pick the frequency, the start date and an optional end date or number of occurrences. Each generated invoice gets its own invoice number.

### Automatic charging

If the client has saved a card through a previous payment, you can turn on **Charge automatically**. Kestrel then charges the saved card on the invoice date instead of emailing a payment link. If the charge fails, the invoice falls back to a normal emailed invoice and you receive a notification.

## Late fees

You can add a late fee as a fixed amount or a percentage of the outstanding balance. Late fees are applied once, the day after the due date, and are shown as a separate line on the invoice.
