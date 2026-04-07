from __future__ import annotations

from collections.abc import Mapping

from ...events import DeliveryEvent
from ...exceptions import ConfigurationError
from ...types import RequestOptions
from .gateways.base import AsyncWhatsAppGateway, WhatsAppGateway
from .models import (
    WhatsAppContactsRequest,
    WhatsAppInboundMessage,
    WhatsAppInteractiveRequest,
    WhatsAppLocationRequest,
    WhatsAppMediaRequest,
    WhatsAppReactionRequest,
    WhatsAppSendResult,
    WhatsAppTemplateRequest,
    WhatsAppTextRequest,
)


class WhatsAppService:
    def __init__(self, gateway: WhatsAppGateway | None) -> None:
        self.gateway = gateway

    @property
    def configured(self) -> bool:
        return self.gateway is not None

    @property
    def provider(self) -> str | None:
        if self.gateway is None:
            return None
        return self.gateway.provider_name

    def send_text(
        self,
        request: WhatsAppTextRequest,
        *,
        options: RequestOptions | None = None,
    ) -> WhatsAppSendResult:
        return _require_gateway(self.gateway).send_text(request, options=options)

    def send_template(
        self,
        request: WhatsAppTemplateRequest,
        *,
        options: RequestOptions | None = None,
    ) -> WhatsAppSendResult:
        return _require_gateway(self.gateway).send_template(request, options=options)

    def send_media(
        self,
        request: WhatsAppMediaRequest,
        *,
        options: RequestOptions | None = None,
    ) -> WhatsAppSendResult:
        return _require_gateway(self.gateway).send_media(request, options=options)

    def send_location(
        self,
        request: WhatsAppLocationRequest,
        *,
        options: RequestOptions | None = None,
    ) -> WhatsAppSendResult:
        return _require_gateway(self.gateway).send_location(request, options=options)

    def send_contacts(
        self,
        request: WhatsAppContactsRequest,
        *,
        options: RequestOptions | None = None,
    ) -> WhatsAppSendResult:
        return _require_gateway(self.gateway).send_contacts(request, options=options)

    def send_reaction(
        self,
        request: WhatsAppReactionRequest,
        *,
        options: RequestOptions | None = None,
    ) -> WhatsAppSendResult:
        return _require_gateway(self.gateway).send_reaction(request, options=options)

    def send_interactive(
        self,
        request: WhatsAppInteractiveRequest,
        *,
        options: RequestOptions | None = None,
    ) -> WhatsAppSendResult:
        return _require_gateway(self.gateway).send_interactive(request, options=options)

    def parse_events(self, payload: Mapping[str, object]) -> tuple[DeliveryEvent, ...]:
        return _require_gateway(self.gateway).parse_events(payload)

    def parse_event(self, payload: Mapping[str, object]) -> DeliveryEvent | None:
        events = self.parse_events(payload)
        return events[0] if events else None

    def parse_inbound_messages(
        self,
        payload: Mapping[str, object],
    ) -> tuple[WhatsAppInboundMessage, ...]:
        return _require_gateway(self.gateway).parse_inbound_messages(payload)

    def parse_inbound_message(self, payload: Mapping[str, object]) -> WhatsAppInboundMessage | None:
        messages = self.parse_inbound_messages(payload)
        return messages[0] if messages else None

    def close(self) -> None:
        if self.gateway is not None:
            self.gateway.close()


class AsyncWhatsAppService:
    def __init__(self, gateway: AsyncWhatsAppGateway | None) -> None:
        self.gateway = gateway

    @property
    def configured(self) -> bool:
        return self.gateway is not None

    @property
    def provider(self) -> str | None:
        if self.gateway is None:
            return None
        return self.gateway.provider_name

    async def send_text(
        self,
        request: WhatsAppTextRequest,
        *,
        options: RequestOptions | None = None,
    ) -> WhatsAppSendResult:
        return await _require_async_gateway(self.gateway).asend_text(request, options=options)

    async def send_template(
        self,
        request: WhatsAppTemplateRequest,
        *,
        options: RequestOptions | None = None,
    ) -> WhatsAppSendResult:
        return await _require_async_gateway(self.gateway).asend_template(request, options=options)

    async def send_media(
        self,
        request: WhatsAppMediaRequest,
        *,
        options: RequestOptions | None = None,
    ) -> WhatsAppSendResult:
        return await _require_async_gateway(self.gateway).asend_media(request, options=options)

    async def send_location(
        self,
        request: WhatsAppLocationRequest,
        *,
        options: RequestOptions | None = None,
    ) -> WhatsAppSendResult:
        return await _require_async_gateway(self.gateway).asend_location(request, options=options)

    async def send_contacts(
        self,
        request: WhatsAppContactsRequest,
        *,
        options: RequestOptions | None = None,
    ) -> WhatsAppSendResult:
        return await _require_async_gateway(self.gateway).asend_contacts(request, options=options)

    async def send_reaction(
        self,
        request: WhatsAppReactionRequest,
        *,
        options: RequestOptions | None = None,
    ) -> WhatsAppSendResult:
        return await _require_async_gateway(self.gateway).asend_reaction(request, options=options)

    async def send_interactive(
        self,
        request: WhatsAppInteractiveRequest,
        *,
        options: RequestOptions | None = None,
    ) -> WhatsAppSendResult:
        return await _require_async_gateway(self.gateway).asend_interactive(
            request,
            options=options,
        )

    def parse_events(self, payload: Mapping[str, object]) -> tuple[DeliveryEvent, ...]:
        return _require_async_gateway(self.gateway).parse_events(payload)

    def parse_event(self, payload: Mapping[str, object]) -> DeliveryEvent | None:
        events = self.parse_events(payload)
        return events[0] if events else None

    def parse_inbound_messages(
        self,
        payload: Mapping[str, object],
    ) -> tuple[WhatsAppInboundMessage, ...]:
        return _require_async_gateway(self.gateway).parse_inbound_messages(payload)

    def parse_inbound_message(self, payload: Mapping[str, object]) -> WhatsAppInboundMessage | None:
        messages = self.parse_inbound_messages(payload)
        return messages[0] if messages else None

    async def aclose(self) -> None:
        if self.gateway is not None:
            await self.gateway.aclose()


def _require_gateway(gateway: WhatsAppGateway | None) -> WhatsAppGateway:
    if gateway is None:
        raise ConfigurationError("WhatsApp gateway is not configured on this client.")
    return gateway


def _require_async_gateway(gateway: AsyncWhatsAppGateway | None) -> AsyncWhatsAppGateway:
    if gateway is None:
        raise ConfigurationError("WhatsApp gateway is not configured on this client.")
    return gateway
