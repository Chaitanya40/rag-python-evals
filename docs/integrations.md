# Integrations

Kestrel connects to the tools you already use for payments, accounting and automation.

## Stripe

Stripe processes all online payments in Kestrel. Go to **Settings > Integrations > Stripe** and select **Connect**. You can connect an existing Stripe account or create a new one. Each workspace can connect only one Stripe account.

## QuickBooks Online and Xero

The accounting integrations sync paid invoices, clients and payments to your accounting software once every hour. Draft invoices are not synced. To trigger a sync immediately, select **Sync now** on the integration page. Kestrel can connect to either QuickBooks Online or Xero, but not both at the same time.

If a sync fails, Kestrel shows the affected invoices on the integration page with the error returned by the accounting software.

## Zapier

Use the Kestrel app on Zapier to trigger workflows when an invoice is sent, viewed, paid or becomes overdue. Zapier is available on every plan.

## Webhooks

Webhooks are available on the Scale plan. Add an endpoint URL in **Settings > Developers > Webhooks** and select the events you want to receive. Kestrel signs every request with an HMAC-SHA256 signature in the `Kestrel-Signature` header, using your endpoint's signing secret.

Failed deliveries are retried with exponential backoff for up to 24 hours. After 24 hours of failures, the endpoint is disabled and the workspace owner receives an email.

## REST API

The REST API is available on the Scale plan. Create an API key in **Settings > Developers > API keys**. Requests are limited to 100 per minute per key.
