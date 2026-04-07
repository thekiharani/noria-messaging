from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

import httpx

from ....events import DeliveryEvent
from ....exceptions import ConfigurationError, GatewayError
from ....http import AsyncHttpClient, HttpClient
from ....types import Hooks, HttpRequestOptions, RequestOptions, RetryPolicy
from ....utils import coerce_string, merge_headers, to_object
from ..models import (
    WhatsAppSendReceipt,
    WhatsAppSendResult,
    WhatsAppTemplateComponent,
    WhatsAppTemplateParameter,
    WhatsAppTemplateRequest,
    WhatsAppTextRequest,
)

META_GRAPH_BASE_URL = "https://graph.facebook.com"
META_GRAPH_API_VERSION = "v25.0"


@dataclass(slots=True)
class MetaWhatsAppGateway:
    access_token: str
    phone_number_id: str
    app_secret: str | None = None
    webhook_verify_token: str | None = None
    api_version: str = META_GRAPH_API_VERSION
    base_url: str = META_GRAPH_BASE_URL
    client: httpx.Client | Any | None = None
    async_client: httpx.AsyncClient | Any | None = None
    timeout_seconds: float | None = 30.0
    default_headers: Mapping[str, str] | None = None
    retry: RetryPolicy | None = None
    hooks: Hooks | None = None
    provider_name: str = field(init=False, default="meta")
    _transport_headers: dict[str, str] = field(init=False, repr=False)
    _http: HttpClient | None = field(init=False, repr=False, default=None)
    _async_http: AsyncHttpClient | None = field(init=False, repr=False, default=None)

    def __post_init__(self) -> None:
        self.access_token = _require_text(self.access_token, "access_token")
        self.phone_number_id = _require_text(self.phone_number_id, "phone_number_id")
        self.app_secret = coerce_string(self.app_secret)
        self.webhook_verify_token = coerce_string(self.webhook_verify_token)
        self.api_version = _require_text(self.api_version, "api_version")
        self._transport_headers = merge_headers(
            self.default_headers,
            {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
            },
        )

    def send_text(
        self,
        request: WhatsAppTextRequest,
        *,
        options: RequestOptions | None = None,
    ) -> WhatsAppSendResult:
        response = self._request(
            HttpRequestOptions(
                path=self._messages_path(),
                method="POST",
                body=_build_text_payload(request),
                headers=options.headers if options else None,
                timeout_seconds=options.timeout_seconds if options else None,
                retry=options.retry if options else None,
            )
        )
        return self._build_send_result(request.recipient, response)

    async def asend_text(
        self,
        request: WhatsAppTextRequest,
        *,
        options: RequestOptions | None = None,
    ) -> WhatsAppSendResult:
        response = await self._arequest(
            HttpRequestOptions(
                path=self._messages_path(),
                method="POST",
                body=_build_text_payload(request),
                headers=options.headers if options else None,
                timeout_seconds=options.timeout_seconds if options else None,
                retry=options.retry if options else None,
            )
        )
        return self._build_send_result(request.recipient, response)

    def send_template(
        self,
        request: WhatsAppTemplateRequest,
        *,
        options: RequestOptions | None = None,
    ) -> WhatsAppSendResult:
        response = self._request(
            HttpRequestOptions(
                path=self._messages_path(),
                method="POST",
                body=_build_template_payload(request),
                headers=options.headers if options else None,
                timeout_seconds=options.timeout_seconds if options else None,
                retry=options.retry if options else None,
            )
        )
        return self._build_send_result(request.recipient, response)

    async def asend_template(
        self,
        request: WhatsAppTemplateRequest,
        *,
        options: RequestOptions | None = None,
    ) -> WhatsAppSendResult:
        response = await self._arequest(
            HttpRequestOptions(
                path=self._messages_path(),
                method="POST",
                body=_build_template_payload(request),
                headers=options.headers if options else None,
                timeout_seconds=options.timeout_seconds if options else None,
                retry=options.retry if options else None,
            )
        )
        return self._build_send_result(request.recipient, response)

    def parse_events(self, payload: Mapping[str, object]) -> tuple[DeliveryEvent, ...]:
        root = to_object(payload)
        entries = root.get("entry")
        events: list[DeliveryEvent] = []

        if not isinstance(entries, list):
            return ()

        for entry in entries:
            entry_object = to_object(entry)
            changes = entry_object.get("changes")
            if not isinstance(changes, list):
                continue

            for change in changes:
                change_object = to_object(change)
                value = to_object(change_object.get("value"))
                statuses = value.get("statuses")
                if not isinstance(statuses, list):
                    continue

                for row in statuses:
                    status = to_object(row)
                    provider_message_id = coerce_string(status.get("id"))
                    if provider_message_id is None:
                        continue

                    error = _first_mapping(status.get("errors"))
                    conversation = to_object(status.get("conversation"))
                    pricing = to_object(status.get("pricing"))
                    provider_status = coerce_string(status.get("status"))

                    events.append(
                        DeliveryEvent(
                            channel="whatsapp",
                            provider=self.provider_name,
                            provider_message_id=provider_message_id,
                            state=_map_whatsapp_state(provider_status),
                            recipient=coerce_string(status.get("recipient_id")),
                            provider_status=provider_status,
                            error_code=coerce_string(error.get("code")),
                            error_description=(
                                coerce_string(error.get("message"))
                                or coerce_string(error.get("title"))
                                or coerce_string(error.get("details"))
                            ),
                            occurred_at=coerce_string(status.get("timestamp")),
                            metadata={
                                "conversation_id": coerce_string(conversation.get("id")),
                                "conversation_origin_type": coerce_string(
                                    to_object(conversation.get("origin")).get("type")
                                ),
                                "pricing_model": coerce_string(pricing.get("pricing_model")),
                                "billable": pricing.get("billable"),
                                "category": coerce_string(pricing.get("category")),
                            },
                            raw=status,
                        )
                    )

        return tuple(events)

    def parse_event(self, payload: Mapping[str, object]) -> DeliveryEvent | None:
        events = self.parse_events(payload)
        return events[0] if events else None

    def close(self) -> None:
        if self._http is not None:
            self._http.close()

    async def aclose(self) -> None:
        if self._async_http is not None:
            await self._async_http.aclose()

    def _messages_path(self) -> str:
        return f"/{self.api_version}/{self.phone_number_id}/messages"

    def _build_send_result(
        self,
        recipient: str,
        response: Mapping[str, object],
    ) -> WhatsAppSendResult:
        contacts = response.get("contacts")
        messages = response.get("messages")
        items = messages if isinstance(messages, list) else []
        contact = _first_mapping(contacts)
        message = _first_mapping(items)
        provider_message_id = coerce_string(message.get("id"))
        provider_status = coerce_string(message.get("message_status"))

        if provider_message_id is None:
            raise GatewayError(
                "Meta WhatsApp Cloud API did not return a message id.",
                provider=self.provider_name,
                response_body=response,
            )

        receipt = WhatsAppSendReceipt(
            provider=self.provider_name,
            recipient=coerce_string(contact.get("wa_id")) or recipient,
            status="submitted",
            provider_message_id=provider_message_id,
            provider_status=provider_status,
            raw=message or response,
        )
        return WhatsAppSendResult(
            provider=self.provider_name,
            accepted=True,
            error_code=None,
            error_description=None,
            messages=(receipt,),
            raw=response,
        )

    def _request(self, options: HttpRequestOptions) -> dict[str, Any]:
        response = self._get_http().request(options)
        return self._validate_response(response)

    async def _arequest(self, options: HttpRequestOptions) -> dict[str, Any]:
        response = await self._get_async_http().request(options)
        return self._validate_response(response)

    def _get_http(self) -> HttpClient:
        if self._http is None:
            self._http = HttpClient(
                base_url=self.base_url,
                client=self.client,
                timeout_seconds=self.timeout_seconds,
                default_headers=self._transport_headers,
                retry=self.retry,
                hooks=self.hooks,
            )
        return self._http

    def _get_async_http(self) -> AsyncHttpClient:
        if self._async_http is None:
            self._async_http = AsyncHttpClient(
                base_url=self.base_url,
                client=self.async_client,
                timeout_seconds=self.timeout_seconds,
                default_headers=self._transport_headers,
                retry=self.retry,
                hooks=self.hooks,
            )
        return self._async_http

    def _validate_response(self, response: object) -> dict[str, Any]:
        payload = to_object(response)
        if not payload:
            raise GatewayError(
                "Meta WhatsApp Cloud API returned a non-object response.",
                provider=self.provider_name,
                response_body=response,
            )

        error = to_object(payload.get("error"))
        if error:
            description = (
                coerce_string(error.get("error_user_msg"))
                or coerce_string(error.get("message"))
                or "Provider request failed."
            )
            raise GatewayError(
                f"Meta WhatsApp request failed: {description}",
                provider=self.provider_name,
                error_code=coerce_string(error.get("code")),
                error_description=description,
                response_body=payload,
            )

        return payload


def _build_text_payload(request: WhatsAppTextRequest) -> dict[str, Any]:
    recipient = _require_text(request.recipient, "recipient")
    body = _require_text(request.text, "text")
    payload = dict(request.provider_options or {})
    text_payload: dict[str, Any] = {"body": body}
    if request.preview_url is not None:
        text_payload["preview_url"] = request.preview_url
    payload.update(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": text_payload,
        }
    )
    if request.reply_to_message_id is not None:
        payload["context"] = {"message_id": request.reply_to_message_id}
    return payload


def _build_template_payload(request: WhatsAppTemplateRequest) -> dict[str, Any]:
    recipient = _require_text(request.recipient, "recipient")
    template_name = _require_text(request.template_name, "template_name")
    language_code = _require_text(request.language_code, "language_code")

    payload = dict(request.provider_options or {})
    template_payload: dict[str, Any] = {
        "name": template_name,
        "language": {"code": language_code},
    }
    if request.components:
        template_payload["components"] = [
            _build_template_component(component) for component in request.components
        ]

    payload.update(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "template",
            "template": template_payload,
        }
    )
    if request.reply_to_message_id is not None:
        payload["context"] = {"message_id": request.reply_to_message_id}
    return payload


def _build_template_component(component: WhatsAppTemplateComponent) -> dict[str, Any]:
    payload: dict[str, Any] = {"type": component.type}
    if component.sub_type is not None:
        payload["sub_type"] = component.sub_type
    if component.index is not None:
        payload["index"] = component.index
    if component.parameters:
        payload["parameters"] = [
            _build_template_parameter(parameter) for parameter in component.parameters
        ]
    return payload


def _build_template_parameter(parameter: WhatsAppTemplateParameter) -> dict[str, Any]:
    payload = dict(parameter.provider_options or {})
    payload["type"] = parameter.type

    if parameter.value is not None:
        if parameter.type == "text":
            payload.setdefault("text", parameter.value)
        elif parameter.type == "payload":
            payload.setdefault("payload", parameter.value)
        elif parameter.type in {"image", "video", "document"}:
            nested = to_object(payload.get(parameter.type))
            if not nested:
                payload[parameter.type] = {"id": parameter.value}
        elif parameter.type not in payload:
            payload["text"] = parameter.value

    return payload


def _first_mapping(value: object) -> dict[str, Any]:
    if isinstance(value, list):
        return to_object(value[0]) if value else {}
    return to_object(value)


def _map_whatsapp_state(status: str | None) -> str:
    normalized = (status or "").lower()
    if normalized in {"accepted", "sent"}:
        return "submitted"
    if normalized == "delivered":
        return "delivered"
    if normalized == "read":
        return "read"
    if normalized == "failed":
        return "failed"
    return "unknown"


def _require_text(value: str | None, field_name: str) -> str:
    text = coerce_string(value)
    if text is None:
        raise ConfigurationError(f"{field_name} is required.")
    return text
