# `noria-messaging`

Reusable Python messaging SDK with channel-oriented gateway integrations.

The package is `httpx`-based and async-first, while still keeping a sync API for callers that do not want to run an event loop. The public surface is split by channel so SMS, WhatsApp, and future transports can evolve without being forced into one payload model.

## Install

```bash
pip install noria-messaging
```

Python requirement: `>=3.11`

## Current Scope

Implemented now:

- top-level sync and async messaging clients
- pluggable sync and async channel gateway protocols
- reusable `httpx` transport with retry and hooks
- SMS channel models and services
- Onfon SMS send
- Onfon balance lookup
- Onfon delivery-report parsing
- Onfon group management
- Onfon template management
- Meta official WhatsApp Cloud API text sends
- Meta official WhatsApp Cloud API template sends
- Meta WhatsApp delivery-status parsing
- FastAPI and Flask webhook helpers for Onfon and Meta

Not implemented yet:

- other SMS gateways
- richer WhatsApp message types beyond text and template sends
- inbound WhatsApp message normalization
- additional framework integrations beyond FastAPI and Flask

## Main Exports

```python
from noria_messaging import (
    AsyncMessagingClient,
    GatewayError,
    MetaWhatsAppGateway,
    OnfonSmsGateway,
    SmsGroupUpsertRequest,
    SmsSendRequest,
    SmsMessage,
    MessagingClient,
    SmsTemplateUpsertRequest,
    WhatsAppTemplateRequest,
    WhatsAppTextRequest
)
```

## Quick Start

### Async

```python
import asyncio

from noria_messaging import AsyncMessagingClient, OnfonSmsGateway, SmsMessage, SmsSendRequest


async def main() -> None:
    gateway = OnfonSmsGateway(
        access_key="your-access-key",
        api_key="your-api-key",
        client_id="your-client-id",
        default_sender_id="NORIA",
    )

    async with AsyncMessagingClient(sms=gateway) as messaging:
        result = await messaging.sms.send(
            SmsSendRequest(
                messages=[
                    SmsMessage(recipient="254712345678", text="Hello Alice", reference="user-1"),
                    SmsMessage(recipient="254722345678", text="Hello Bob", reference="user-2"),
                ],
                is_unicode=False,
                is_flash=False,
            )
        )

    for receipt in result.messages:
        print(receipt.recipient, receipt.status, receipt.provider_message_id)


asyncio.run(main())
```

### Sync Fallback

```python
from noria_messaging import MessagingClient, OnfonSmsGateway, SmsMessage, SmsSendRequest

gateway = OnfonSmsGateway(
    access_key="your-access-key",
    api_key="your-api-key",
    client_id="your-client-id",
    default_sender_id="NORIA",
)

messaging = MessagingClient(sms=gateway)

result = messaging.sms.send(
    SmsSendRequest(
        messages=[
            SmsMessage(recipient="254712345678", text="Hello Alice", reference="user-1"),
            SmsMessage(recipient="254722345678", text="Hello Bob", reference="user-2"),
        ],
        is_unicode=False,
        is_flash=False,
    )
)

for receipt in result.messages:
    print(receipt.recipient, receipt.status, receipt.provider_message_id)
```

## WhatsApp Quick Start

```python
from noria_messaging import (
    AsyncMessagingClient,
    MetaWhatsAppGateway,
    WhatsAppTemplateComponent,
    WhatsAppTemplateParameter,
    WhatsAppTemplateRequest,
    WhatsAppTextRequest,
)

gateway = MetaWhatsAppGateway(
    access_token="your-system-user-token",
    phone_number_id="your-phone-number-id",
    app_secret="your-meta-app-secret",
    webhook_verify_token="your-verify-token",
)

async with AsyncMessagingClient(whatsapp=gateway) as messaging:
    text_result = await messaging.whatsapp.send_text(
        WhatsAppTextRequest(
            recipient="254712345678",
            text="Hello from WhatsApp",
        )
    )

    template_result = await messaging.whatsapp.send_template(
        WhatsAppTemplateRequest(
            recipient="254712345678",
            template_name="shipment_update",
            language_code="en_US",
            components=[
                WhatsAppTemplateComponent(
                    type="body",
                    parameters=[
                        WhatsAppTemplateParameter(type="text", value="Alice"),
                        WhatsAppTemplateParameter(type="text", value="Order-123"),
                    ],
                )
            ],
        )
    )
```

## Balance

Async:

```python
balance = await messaging.sms.get_balance()

for entry in balance.entries:
    print(entry.label, entry.credits_raw, entry.credits)
```

Sync:

```python
balance = messaging.sms.get_balance()
```

## Onfon Group And Template Management

```python
group = messaging.sms.create_group(SmsGroupUpsertRequest(name="Customers"))
templates = messaging.sms.list_templates()

messaging.sms.create_template(
    SmsTemplateUpsertRequest(
        name="promo_offer",
        body="Hello ##Name##, use code SAVE10 today.",
    )
)
```

## Delivery Events

`OnfonSmsGateway` exposes a parser for the documented DLR query string shape and returns a normalized delivery event:

```python
event = messaging.sms.parse_delivery_report(
    {
        "messageId": "fc103131-5931-4530-ba8e-aa223c769536",
        "mobile": "254712345678",
        "status": "DELIVRD",
        "errorCode": "000",
        "submitDate": "2026-04-08 09:30",
        "doneDate": "2026-04-08 09:31",
    }
)
```

Meta WhatsApp Cloud API delivery callbacks are exposed as normalized delivery events as well:

```python
events = messaging.whatsapp.parse_events(meta_webhook_payload)
```

## Webhook Helpers

Meta verification and signature handling:

```python
from noria_messaging import (
    fastapi_parse_meta_delivery_events,
    fastapi_resolve_meta_subscription_challenge,
)
```

Onfon DLR parsing from Flask:

```python
from noria_messaging import flask_parse_onfon_delivery_report
```

## Channel Layout

Future providers should implement the channel gateway contracts and live under the relevant channel package:

- `noria_messaging.channels.sms.gateways`
- `noria_messaging.channels.whatsapp.gateways`

That keeps shared transport and retry behavior reusable while still letting each channel have its own request models.

## Source Reference

The first implementation was built from the local `ONFON_HTTP_SMS_API_GUIDE.md` guide.
