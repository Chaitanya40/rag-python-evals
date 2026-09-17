# Troubleshooting common problems

Solutions to the issues Kestrel users report most often.

## Clients are not receiving invoice emails

First, open the invoice's activity timeline. If it shows **Bounced**, the client's email address is wrong or their mailbox is full; correct the address and resend. If it shows **Delivered** but the client cannot find the email, ask them to check spam and to allow messages from invoices@kestrel.example.

On the Scale plan you can send invoices from your own domain. Add the SPF and DKIM records shown in **Settings > Email domain** to improve deliverability.

## A client's card payment failed

Card payments usually fail because the bank declined the charge, the card has expired, or the billing address does not match. The client sees the reason on the payment page and can try another card. Kestrel does not store card numbers, so you cannot retry the charge on the client's behalf unless automatic charging is set up for a recurring invoice.

## The invoice total looks wrong

Check the tax settings on each line item and whether a discount is applied before or after tax, which you can change in **Settings > Invoices > Tax calculation**. Rounding is applied per line by default. Switch to rounding on the invoice total if your accounting software calculates tax that way.

## The page will not load or shows an error

Kestrel supports the latest two versions of Chrome, Firefox, Safari and Edge. Clear your browser cache, disable browser extensions and try again. You can check for ongoing incidents on the Kestrel status page.

## Contacting support

Email support from the address on your account, or use the chat in the bottom-right corner of the app. Starter and Growth customers get a reply within 1 business day. Scale customers get priority support with a reply within 4 business hours.
