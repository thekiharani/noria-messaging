# `noria-messaging`

Channel-oriented Python SDK for application messaging.

`noria-messaging` is async-first, built on `httpx`, and designed so each messaging channel keeps its own request models while sharing transport, retries, hooks, error handling, and webhook utilities.

Current supported providers:

- SMS: Onfon
- WhatsApp: Meta WhatsApp Cloud API only

Third-party WhatsApp relays such as Twilio are intentionally out of scope.

## Project Links

- Repository: `https://github.com/thekiharani/noria-messaging`
- Issue tracker: `https://github.com/thekiharani/noria-messaging/issues`

## Install

```bash
pip install noria-messaging
```

Python requirement: `>=3.11`

For local development:

```bash
uv sync --extra dev
```

## What This Package Covers

Implemented now:

- sync and async top-level clients
- reusable `httpx` transport with retry and lifecycle management
- request-level timeout, headers, and retry overrides
- request/response hooks for observability
- normalized error types
- SMS service with Onfon send, balance, delivery reports, groups, and templates
- WhatsApp service with Meta Cloud API text, template, media, location, contacts, reaction, button/list interactive sends, product/catalog/product-list/flow interactive sends, and media ID helpers
- normalized Meta delivery-status parsing
- normalized Meta inbound message parsing
- FastAPI and Flask webhook helpers for Onfon and Meta

Not implemented yet:

- additional SMS gateways
- extra framework helpers beyond FastAPI and Flask

## Design

The package is split into three layers:

- clients: `MessagingClient` and `AsyncMessagingClient`
- channel services: `messaging.sms` and `messaging.whatsapp`
- gateway adapters: provider-specific implementations such as `OnfonSmsGateway` and `MetaWhatsAppGateway`

That keeps application code stable even as more providers are added.

## Main Exports

```python
from noria_messaging import (
    AsyncMessagingClient,
    MessagingClient,
    OnfonSmsGateway,
    MetaWhatsAppGateway,
    RequestOptions,
    RetryPolicy,
    Hooks,
    SmsMessage,
    SmsSendRequest,
    SmsGroupUpsertRequest,
    SmsTemplateUpsertRequest,
    WhatsAppTextRequest,
    WhatsAppTemplateRequest,
    WhatsAppTemplateComponent,
    WhatsAppTemplateParameter,
    WhatsAppMediaRequest,
    WhatsAppMediaUploadRequest,
    WhatsAppMediaInfo,
    WhatsAppLocationRequest,
    WhatsAppContact,
    WhatsAppContactName,
    WhatsAppContactPhone,
    WhatsAppContactsRequest,
    WhatsAppReactionRequest,
    WhatsAppInteractiveButton,
    WhatsAppInteractiveRequest,
    WhatsAppInteractiveRow,
    WhatsAppInteractiveSection,
    WhatsAppCatalogMessageRequest,
    WhatsAppProductMessageRequest,
    WhatsAppProductItem,
    WhatsAppProductListRequest,
    WhatsAppProductSection,
    WhatsAppFlowMessageRequest,
    GatewayError,
    ConfigurationError,
    ApiError,
    NetworkError,
    TimeoutError,
    WebhookVerificationError,
)
```

## Core Concepts

### Clients

Use `AsyncMessagingClient` when your app already runs async code. Use `MessagingClient` only when you need sync calls.

```python
from noria_messaging import AsyncMessagingClient, MetaWhatsAppGateway, OnfonSmsGateway

messaging = AsyncMessagingClient(
    sms=OnfonSmsGateway(
        access_key="your-access-key",
        api_key="your-api-key",
        client_id="your-client-id",
        default_sender_id="NORIA",
    ),
    whatsapp=MetaWhatsAppGateway(
        access_token="your-meta-token",
        phone_number_id="your-meta-phone-number-id",
    ),
)
```

### Services

Each client exposes one service per channel:

- `messaging.sms`
- `messaging.whatsapp`

### Gateway Adapters

Each channel service delegates to a gateway implementation:

- `OnfonSmsGateway`
- `MetaWhatsAppGateway`

Future providers should implement the same gateway protocol for their channel.

### Request Models

Every outbound operation uses an explicit request model. That is deliberate.

Examples:

- `SmsSendRequest`
- `WhatsAppTextRequest`
- `WhatsAppTemplateRequest`
- `WhatsAppMediaRequest`
- `WhatsAppInteractiveRequest`
- `WhatsAppCatalogMessageRequest`
- `WhatsAppProductMessageRequest`
- `WhatsAppProductListRequest`
- `WhatsAppFlowMessageRequest`
- `WhatsAppMediaUploadRequest`

### Normalized Events

Webhook payloads are normalized into package models instead of leaking provider payloads through your app:

- `DeliveryEvent`
- `WhatsAppInboundMessage`

The raw provider payload is still attached on each normalized object as `raw`.

## Quick Start

### Async SMS

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

### Sync SMS

```python
from noria_messaging import MessagingClient, OnfonSmsGateway, SmsMessage, SmsSendRequest

with MessagingClient(
    sms=OnfonSmsGateway(
        access_key="your-access-key",
        api_key="your-api-key",
        client_id="your-client-id",
        default_sender_id="NORIA",
    )
) as messaging:
    result = messaging.sms.send(
        SmsSendRequest(
            messages=[
                SmsMessage(recipient="254712345678", text="Hello Alice"),
            ]
        )
    )

print(result.submitted_count)
```

### Async WhatsApp

```python
import asyncio

from noria_messaging import AsyncMessagingClient, MetaWhatsAppGateway, WhatsAppTextRequest


async def main() -> None:
    gateway = MetaWhatsAppGateway(
        access_token="your-system-user-token",
        phone_number_id="your-phone-number-id",
        app_secret="your-meta-app-secret",
        webhook_verify_token="your-meta-verify-token",
    )

    async with AsyncMessagingClient(whatsapp=gateway) as messaging:
        result = await messaging.whatsapp.send_text(
            WhatsAppTextRequest(
                recipient="254712345678",
                text="Hello from WhatsApp",
            )
        )

    print(result.messages[0].provider_message_id)


asyncio.run(main())
```

## SMS

### Send SMS

```python
from datetime import datetime

from noria_messaging import SmsMessage, SmsSendRequest

request = SmsSendRequest(
    messages=[
        SmsMessage(recipient="254712345678", text="Order received", reference="order-123"),
        SmsMessage(recipient="254722345678", text="Order received", reference="order-124"),
    ],
    sender_id="NORIA",
    schedule_at=datetime(2026, 4, 8, 9, 30),
    is_unicode=False,
    is_flash=False,
)

result = await messaging.sms.send(request)
```

Notes:

- `sender_id` on `SmsSendRequest` overrides the gateway default for that call.
- `schedule_at` accepts either `datetime` or a formatted string.
- `provider_options` lets you pass provider-specific fields through when needed.

### Balance

```python
balance = await messaging.sms.get_balance()

for entry in balance.entries:
    print(entry.label, entry.credits_raw, entry.credits)
```

### Groups

```python
from noria_messaging import SmsGroupUpsertRequest

groups = await messaging.sms.list_groups()
created = await messaging.sms.create_group(SmsGroupUpsertRequest(name="Customers"))
updated = await messaging.sms.update_group("12", SmsGroupUpsertRequest(name="VIP Customers"))
deleted = await messaging.sms.delete_group("12")
```

### Templates

```python
from noria_messaging import SmsTemplateUpsertRequest

templates = await messaging.sms.list_templates()
created = await messaging.sms.create_template(
    SmsTemplateUpsertRequest(
        name="promo_offer",
        body="Hello ##Name##, use code SAVE10 today.",
    )
)
updated = await messaging.sms.update_template(
    "44",
    SmsTemplateUpsertRequest(
        name="promo_offer",
        body="Hello ##Name##, use code SAVE15 today.",
    ),
)
deleted = await messaging.sms.delete_template("44")
```

### Onfon Delivery Report Parsing

```python
event = messaging.sms.parse_delivery_report(
    {
        "messageId": "fc103131-5931-4530-ba8e-aa223c769536",
        "mobile": "254712345678",
        "status": "DELIVRD",
        "errorCode": "000",
        "submitDate": "2026-04-08 09:30",
        "doneDate": "2026-04-08 09:31",
        "shortMessage": "Hello Alice",
    }
)

print(event.state, event.provider_message_id, event.recipient)
```

## WhatsApp

This package supports Meta's official WhatsApp Cloud API only.

### Send Text Messages

```python
from noria_messaging import WhatsAppTextRequest

result = await messaging.whatsapp.send_text(
    WhatsAppTextRequest(
        recipient="254712345678",
        text="Hello from WhatsApp",
        preview_url=False,
        reply_to_message_id="wamid.previous-message",
    )
)
```

### Send Template Messages

```python
from noria_messaging import (
    WhatsAppTemplateComponent,
    WhatsAppTemplateParameter,
    WhatsAppTemplateRequest,
)

result = await messaging.whatsapp.send_template(
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
            ),
            WhatsAppTemplateComponent(
                type="button",
                sub_type="quick_reply",
                index=0,
                parameters=[
                    WhatsAppTemplateParameter(type="payload", value="track-order-123"),
                ],
            ),
        ],
    )
)
```

If you need provider-specific component payloads, pass them through `provider_options` on `WhatsAppTemplateParameter`.

### Send Media

Use either a Meta media ID or a public link, not both.

```python
from noria_messaging import WhatsAppMediaRequest

image_result = await messaging.whatsapp.send_media(
    WhatsAppMediaRequest(
        recipient="254712345678",
        media_type="image",
        link="https://cdn.example.com/poster.png",
        caption="Promo poster",
    )
)

document_result = await messaging.whatsapp.send_media(
    WhatsAppMediaRequest(
        recipient="254712345678",
        media_type="document",
        media_id="meta-media-id",
        filename="invoice.pdf",
        caption="Your invoice",
    )
)
```

Supported media types:

- `image`
- `audio`
- `document`
- `sticker`
- `video`

### Upload, Inspect, and Delete Meta Media

Use this when you want Meta-hosted media IDs before sending a message.

```python
from noria_messaging import WhatsAppMediaUploadRequest

upload = await messaging.whatsapp.upload_media(
    WhatsAppMediaUploadRequest(
        filename="poster.png",
        content=b"...binary image bytes...",
        mime_type="image/png",
    )
)

media = await messaging.whatsapp.get_media(upload.media_id)
deleted = await messaging.whatsapp.delete_media(upload.media_id)

print(upload.media_id)
print(media.url, media.mime_type, media.file_size)
print(deleted.deleted)
```

### Send Location

```python
from noria_messaging import WhatsAppLocationRequest

result = await messaging.whatsapp.send_location(
    WhatsAppLocationRequest(
        recipient="254712345678",
        latitude=-1.2921,
        longitude=36.8219,
        name="Noria HQ",
        address="Westlands, Nairobi",
    )
)
```

### Send Contacts

```python
from noria_messaging import (
    WhatsAppContact,
    WhatsAppContactAddress,
    WhatsAppContactEmail,
    WhatsAppContactName,
    WhatsAppContactOrg,
    WhatsAppContactPhone,
    WhatsAppContactsRequest,
    WhatsAppContactUrl,
)

result = await messaging.whatsapp.send_contacts(
    WhatsAppContactsRequest(
        recipient="254712345678",
        contacts=[
            WhatsAppContact(
                name=WhatsAppContactName(
                    formatted_name="Alice Example",
                    first_name="Alice",
                    last_name="Example",
                ),
                phones=[
                    WhatsAppContactPhone(
                        phone="+254712345678",
                        type="CELL",
                        wa_id="254712345678",
                    )
                ],
                emails=[
                    WhatsAppContactEmail(email="alice@example.com", type="WORK"),
                ],
                urls=[
                    WhatsAppContactUrl(url="https://example.com/alice", type="WORK"),
                ],
                addresses=[
                    WhatsAppContactAddress(
                        street="1 Main Street",
                        city="Nairobi",
                        state="Nairobi",
                        zip="00100",
                        country="Kenya",
                        country_code="KE",
                        type="HOME",
                    )
                ],
                org=WhatsAppContactOrg(
                    company="Noria",
                    department="Operations",
                    title="Manager",
                ),
                birthday="1990-01-01",
            )
        ],
    )
)
```

### Send Reactions

```python
from noria_messaging import WhatsAppReactionRequest

result = await messaging.whatsapp.send_reaction(
    WhatsAppReactionRequest(
        recipient="254712345678",
        message_id="wamid.original-message",
        emoji="👍",
    )
)
```

### Send Interactive Button and List Messages

Use `send_interactive(...)` for button and list messages only.

Button messages:

```python
from noria_messaging import WhatsAppInteractiveButton, WhatsAppInteractiveRequest

result = await messaging.whatsapp.send_interactive(
    WhatsAppInteractiveRequest(
        recipient="254712345678",
        interactive_type="button",
        body_text="Choose next step",
        buttons=[
            WhatsAppInteractiveButton(identifier="pay-now", title="Pay now"),
            WhatsAppInteractiveButton(identifier="talk-to-sales", title="Talk to sales"),
        ],
        footer_text="Noria Support",
    )
)
```

List messages:

```python
from noria_messaging import (
    WhatsAppInteractiveRequest,
    WhatsAppInteractiveRow,
    WhatsAppInteractiveSection,
)

result = await messaging.whatsapp.send_interactive(
    WhatsAppInteractiveRequest(
        recipient="254712345678",
        interactive_type="list",
        body_text="Choose a branch",
        button_text="Open list",
        sections=[
            WhatsAppInteractiveSection(
                title="Nairobi",
                rows=[
                    WhatsAppInteractiveRow(
                        identifier="westlands",
                        title="Westlands",
                        description="Visit the Westlands office",
                    ),
                    WhatsAppInteractiveRow(
                        identifier="kilimani",
                        title="Kilimani",
                        description="Visit the Kilimani office",
                    ),
                ],
            )
        ],
    )
)
```

Interactive headers support:

- `text`
- `image`
- `video`
- `document`

Example with a document header:

```python
from noria_messaging import (
    WhatsAppInteractiveButton,
    WhatsAppInteractiveHeader,
    WhatsAppInteractiveRequest,
)

result = await messaging.whatsapp.send_interactive(
    WhatsAppInteractiveRequest(
        recipient="254712345678",
        interactive_type="button",
        body_text="Review the attached guide",
        header=WhatsAppInteractiveHeader(
            type="document",
            link="https://cdn.example.com/guide.pdf",
            filename="guide.pdf",
        ),
        buttons=[
            WhatsAppInteractiveButton(identifier="ack", title="Understood"),
        ],
    )
)
```

### Send Catalog Messages

```python
from noria_messaging import WhatsAppCatalogMessageRequest

result = await messaging.whatsapp.send_catalog(
    WhatsAppCatalogMessageRequest(
        recipient="254712345678",
        body_text="Browse the latest collection",
        thumbnail_product_retailer_id="sku-1",
    )
)
```

### Send Single-Product Messages

```python
from noria_messaging import WhatsAppProductMessageRequest

result = await messaging.whatsapp.send_product(
    WhatsAppProductMessageRequest(
        recipient="254712345678",
        catalog_id="catalog-1",
        product_retailer_id="sku-1",
        body_text="Featured product",
    )
)
```

### Send Product-List Messages

```python
from noria_messaging import (
    WhatsAppInteractiveHeader,
    WhatsAppProductItem,
    WhatsAppProductListRequest,
    WhatsAppProductSection,
)

result = await messaging.whatsapp.send_product_list(
    WhatsAppProductListRequest(
        recipient="254712345678",
        catalog_id="catalog-1",
        header=WhatsAppInteractiveHeader(type="text", text="Store"),
        body_text="Choose a bundle",
        sections=[
            WhatsAppProductSection(
                title="Popular",
                product_items=[
                    WhatsAppProductItem(product_retailer_id="sku-1"),
                    WhatsAppProductItem(product_retailer_id="sku-2"),
                ],
            )
        ],
    )
)
```

### Send Flow Messages

```python
from noria_messaging import WhatsAppFlowMessageRequest

result = await messaging.whatsapp.send_flow(
    WhatsAppFlowMessageRequest(
        recipient="254712345678",
        flow_id="flow-123",
        flow_cta="Open flow",
        body_text="Complete onboarding",
        flow_token="customer-123",
        flow_action_payload={
            "screen": "DETAILS",
            "data": {"customer_id": "cust-1"},
        },
    )
)
```

`WhatsAppFlowMessageRequest` supports either `flow_id` or `flow_name`, but not both.

## Request-Level Customization

All gateway methods accept `options=RequestOptions(...)`.

```python
from noria_messaging import RequestOptions, RetryPolicy

result = await messaging.whatsapp.send_text(
    WhatsAppTextRequest(
        recipient="254712345678",
        text="Hello with request overrides",
    ),
    options=RequestOptions(
        headers={"X-Correlation-ID": "msg-123"},
        timeout_seconds=10.0,
        retry=RetryPolicy(
            max_attempts=3,
            retry_methods=("POST",),
            retry_on_statuses=(429, 500, 502, 503, 504),
            retry_on_network_error=True,
            base_delay_seconds=0.25,
            max_delay_seconds=3.0,
            backoff_multiplier=2.0,
        ),
    ),
)
```

`RequestOptions.retry` supports three modes:

- `None`: use the gateway default
- `True`: explicitly use the gateway default retry policy
- `False`: disable retries for that call
- `RetryPolicy(...)`: override with a request-specific policy

## Gateway-Level Customization

Both built-in gateways accept transport-level customization:

- `client`
- `async_client`
- `timeout_seconds`
- `default_headers`
- `retry`
- `hooks`
- `base_url`

Meta also accepts:

- `api_version`
- `app_secret`
- `webhook_verify_token`

Onfon also accepts:

- `default_sender_id`

Example:

```python
import httpx

from noria_messaging import Hooks, OnfonSmsGateway, RetryPolicy


def log_before_request(context) -> None:
    print(context.method, context.url, context.attempt)


gateway = OnfonSmsGateway(
    access_key="your-access-key",
    api_key="your-api-key",
    client_id="your-client-id",
    default_sender_id="NORIA",
    client=httpx.Client(),
    timeout_seconds=20.0,
    retry=RetryPolicy(
        max_attempts=2,
        retry_methods=("POST",),
        retry_on_statuses=(500, 502, 503, 504),
        retry_on_network_error=True,
        base_delay_seconds=0.2,
    ),
    hooks=Hooks(before_request=log_before_request),
)
```

## Hooks

Hooks are synchronous callbacks that run around transport execution:

- `before_request`
- `after_response`
- `on_error`

```python
from noria_messaging import Hooks


def before_request(context) -> None:
    print("sending", context.method, context.url, context.headers)


def after_response(context) -> None:
    print("received", context.response_body)


def on_error(context) -> None:
    print("failed", type(context.error).__name__)


gateway = MetaWhatsAppGateway(
    access_token="your-meta-token",
    phone_number_id="your-phone-number-id",
    hooks=Hooks(
        before_request=before_request,
        after_response=after_response,
        on_error=on_error,
    ),
)
```

## Error Handling

Common error types:

- `ConfigurationError`: missing or invalid local config
- `ApiError`: HTTP response was non-successful
- `NetworkError`: request failed before a response was received
- `TimeoutError`: request timed out
- `GatewayError`: provider returned an invalid or provider-level failure payload
- `WebhookVerificationError`: webhook signature verification failed

```python
from noria_messaging import (
    ApiError,
    ConfigurationError,
    GatewayError,
    NetworkError,
    TimeoutError,
)

try:
    await messaging.whatsapp.send_text(
        WhatsAppTextRequest(recipient="254712345678", text="Hello")
    )
except ConfigurationError:
    ...
except TimeoutError:
    ...
except NetworkError:
    ...
except ApiError as exc:
    print(exc.status_code, exc.response_body)
except GatewayError as exc:
    print(exc.provider, exc.error_code, exc.error_description)
```

## Normalized Webhook Parsing

### WhatsApp Delivery Events

```python
events = messaging.whatsapp.parse_events(meta_webhook_payload)

for event in events:
    print(event.state, event.provider_message_id, event.recipient)
```

### WhatsApp Inbound Messages

```python
messages = messaging.whatsapp.parse_inbound_messages(meta_webhook_payload)

for message in messages:
    print(message.message_type, message.sender_id, message.profile_name)
    print(message.text)
    print(message.context_message_id)
```

`WhatsAppInboundMessage` may contain:

- `text`
- `media`
- `location`
- `contacts`
- `reply`
- `reaction`

Supported normalized inbound message types:

- `text`
- `image`
- `audio`
- `document`
- `sticker`
- `video`
- `location`
- `contacts`
- `button`
- `interactive`
- `reaction`
- `unsupported`

### Onfon Delivery Reports

```python
from noria_messaging import parse_onfon_delivery_report

event = parse_onfon_delivery_report(onfon_query_params, sms_gateway)
```

## Framework Helpers

The package does not depend on FastAPI or Flask directly. It only provides helper functions that work with request objects from those frameworks.

### FastAPI

Subscription verification:

```python
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse

from noria_messaging import (
    MetaWhatsAppGateway,
    fastapi_parse_meta_delivery_events,
    fastapi_parse_meta_inbound_messages,
    fastapi_resolve_meta_subscription_challenge,
)

app = FastAPI()
gateway = MetaWhatsAppGateway(
    access_token="your-meta-token",
    phone_number_id="your-phone-number-id",
    app_secret="your-meta-app-secret",
    webhook_verify_token="your-meta-verify-token",
)


@app.get("/webhooks/meta")
async def verify_meta(request: Request) -> PlainTextResponse:
    challenge = fastapi_resolve_meta_subscription_challenge(
        request,
        gateway.webhook_verify_token or "",
    )
    return PlainTextResponse(challenge or "", status_code=200 if challenge else 403)


@app.post("/webhooks/meta")
async def receive_meta(request: Request) -> dict[str, bool]:
    delivery_events = await fastapi_parse_meta_delivery_events(
        request,
        gateway,
        require_signature=True,
    )
    inbound_messages = await fastapi_parse_meta_inbound_messages(
        request,
        gateway,
        require_signature=True,
    )

    for event in delivery_events:
        print("delivery", event.state, event.provider_message_id)

    for message in inbound_messages:
        print("inbound", message.message_type, message.sender_id)

    return {"ok": True}
```

Onfon DLR in FastAPI:

```python
from noria_messaging import fastapi_parse_onfon_delivery_report


@app.get("/webhooks/onfon")
async def receive_onfon(request: Request) -> dict[str, bool]:
    event = await fastapi_parse_onfon_delivery_report(request, sms_gateway)
    print(event.provider_message_id if event else None)
    return {"ok": True}
```

### Flask

```python
from flask import Flask, Response, request

from noria_messaging import (
    MetaWhatsAppGateway,
    flask_parse_meta_delivery_events,
    flask_parse_meta_inbound_messages,
    flask_resolve_meta_subscription_challenge,
    flask_parse_onfon_delivery_report,
)

app = Flask(__name__)
whatsapp_gateway = MetaWhatsAppGateway(
    access_token="your-meta-token",
    phone_number_id="your-phone-number-id",
    app_secret="your-meta-app-secret",
    webhook_verify_token="your-meta-verify-token",
)


@app.get("/webhooks/meta")
def verify_meta() -> Response:
    challenge = flask_resolve_meta_subscription_challenge(
        request,
        whatsapp_gateway.webhook_verify_token or "",
    )
    return Response(challenge or "", status=200 if challenge else 403)


@app.post("/webhooks/meta")
def receive_meta() -> dict[str, bool]:
    delivery_events = flask_parse_meta_delivery_events(
        request,
        whatsapp_gateway,
        require_signature=True,
    )
    inbound_messages = flask_parse_meta_inbound_messages(
        request,
        whatsapp_gateway,
        require_signature=True,
    )

    print(len(delivery_events), len(inbound_messages))
    return {"ok": True}


@app.get("/webhooks/onfon")
def receive_onfon() -> dict[str, bool]:
    event = flask_parse_onfon_delivery_report(request, sms_gateway)
    print(event.provider_message_id if event else None)
    return {"ok": True}
```

## Direct Meta Verification Helpers

If you do not want to use the framework wrappers, use the raw helpers directly:

```python
from noria_messaging import (
    require_valid_meta_signature,
    resolve_meta_subscription_challenge,
    verify_meta_signature,
)

challenge = resolve_meta_subscription_challenge(query_params, "verify-token")
is_valid = verify_meta_signature(payload_bytes, signature_header, "app-secret")
require_valid_meta_signature(payload_bytes, signature_header, "app-secret")
```

## Provider-Specific Escape Hatches

Request models include `provider_options` when you need to pass provider-specific payload fields without changing the package abstraction.

Examples:

- `SmsSendRequest.provider_options`
- `SmsGroupUpsertRequest.provider_options`
- `SmsTemplateUpsertRequest.provider_options`
- `WhatsAppTextRequest.provider_options`
- `WhatsAppTemplateParameter.provider_options`
- `WhatsAppInteractiveHeader.provider_options`
- `WhatsAppFlowMessageRequest.provider_options`
- `WhatsAppMediaUploadRequest.provider_options`

Use these sparingly. Prefer the typed request fields first.

## Sync vs Async Guidance

Prefer async when:

- your app already uses `asyncio`
- you are sending messages in API handlers or background workers
- you want to share one event loop across network work

Use sync when:

- your app is synchronous
- you are calling the SDK from scripts or management commands

Both APIs expose the same channel-level operations where practical.

## Extending The Package

New providers should be added under the relevant channel:

- `noria_messaging.channels.sms.gateways`
- `noria_messaging.channels.whatsapp.gateways`

For example, a new SMS provider should implement the SMS gateway protocol and return the same normalized models used by `SmsService`.

Do not force non-SMS channels into the SMS gateway abstraction. WhatsApp already has its own service and models for that reason.

## Notes

The WhatsApp implementation targets Meta's official Cloud API shape only.
