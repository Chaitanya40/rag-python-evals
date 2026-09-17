# Refunds and disputes

This article explains how to refund a client and what happens when a client disputes a card payment.

## Issuing a refund

Open the paid invoice, select **More > Refund**, and choose a full or partial refund. For a partial refund, enter the amount and an optional note for your client. The refund goes back to the original payment method.

Refunds can be issued for up to 180 days after the original payment. After that, you need to return the money to your client outside Kestrel, for example by bank transfer, and record it as a manual refund.

## How long refunds take

Card refunds usually appear on the client's statement within 5 to 10 business days. ACH and SEPA refunds can take longer. Kestrel shows the refund as pending until Stripe confirms it.

## Refund fees

Stripe does not return the original processing fee when you refund a payment. On the Starter plan, the 0.5% Kestrel platform fee is also not returned.

## Disputes and chargebacks

If a client asks their bank to reverse a card payment, Stripe opens a dispute and the disputed amount plus a 15 USD dispute fee is withdrawn from your balance. Kestrel emails you and marks the invoice as disputed.

### Responding to a dispute

Go to **Payments > Disputes** and select the dispute. Upload evidence such as the signed contract, delivery confirmation or email correspondence. You must respond before the deadline shown on the dispute, which is usually 7 days before the bank's own deadline. If you win, the amount and the dispute fee are returned to your balance.
