from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol, runtime_checkable

from ....events import DeliveryEvent
from ....types import RequestOptions
from ..models import (
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


@runtime_checkable
class WhatsAppGateway(Protocol):
    provider_name: str

    def send_text(
        self,
        request: WhatsAppTextRequest,
        *,
        options: RequestOptions | None = None,
    ) -> WhatsAppSendResult: ...

    def send_template(
        self,
        request: WhatsAppTemplateRequest,
        *,
        options: RequestOptions | None = None,
    ) -> WhatsAppSendResult: ...

    def send_media(
        self,
        request: WhatsAppMediaRequest,
        *,
        options: RequestOptions | None = None,
    ) -> WhatsAppSendResult: ...

    def send_location(
        self,
        request: WhatsAppLocationRequest,
        *,
        options: RequestOptions | None = None,
    ) -> WhatsAppSendResult: ...

    def send_contacts(
        self,
        request: WhatsAppContactsRequest,
        *,
        options: RequestOptions | None = None,
    ) -> WhatsAppSendResult: ...

    def send_reaction(
        self,
        request: WhatsAppReactionRequest,
        *,
        options: RequestOptions | None = None,
    ) -> WhatsAppSendResult: ...

    def send_interactive(
        self,
        request: WhatsAppInteractiveRequest,
        *,
        options: RequestOptions | None = None,
    ) -> WhatsAppSendResult: ...

    def parse_events(self, payload: Mapping[str, object]) -> tuple[DeliveryEvent, ...]: ...

    def parse_event(self, payload: Mapping[str, object]) -> DeliveryEvent | None: ...

    def parse_inbound_messages(
        self,
        payload: Mapping[str, object],
    ) -> tuple[WhatsAppInboundMessage, ...]: ...

    def parse_inbound_message(
        self,
        payload: Mapping[str, object],
    ) -> WhatsAppInboundMessage | None: ...

    def close(self) -> None: ...


@runtime_checkable
class AsyncWhatsAppGateway(Protocol):
    provider_name: str

    async def asend_text(
        self,
        request: WhatsAppTextRequest,
        *,
        options: RequestOptions | None = None,
    ) -> WhatsAppSendResult: ...

    async def asend_template(
        self,
        request: WhatsAppTemplateRequest,
        *,
        options: RequestOptions | None = None,
    ) -> WhatsAppSendResult: ...

    async def asend_media(
        self,
        request: WhatsAppMediaRequest,
        *,
        options: RequestOptions | None = None,
    ) -> WhatsAppSendResult: ...

    async def asend_location(
        self,
        request: WhatsAppLocationRequest,
        *,
        options: RequestOptions | None = None,
    ) -> WhatsAppSendResult: ...

    async def asend_contacts(
        self,
        request: WhatsAppContactsRequest,
        *,
        options: RequestOptions | None = None,
    ) -> WhatsAppSendResult: ...

    async def asend_reaction(
        self,
        request: WhatsAppReactionRequest,
        *,
        options: RequestOptions | None = None,
    ) -> WhatsAppSendResult: ...

    async def asend_interactive(
        self,
        request: WhatsAppInteractiveRequest,
        *,
        options: RequestOptions | None = None,
    ) -> WhatsAppSendResult: ...

    def parse_events(self, payload: Mapping[str, object]) -> tuple[DeliveryEvent, ...]: ...

    def parse_event(self, payload: Mapping[str, object]) -> DeliveryEvent | None: ...

    def parse_inbound_messages(
        self,
        payload: Mapping[str, object],
    ) -> tuple[WhatsAppInboundMessage, ...]: ...

    def parse_inbound_message(
        self,
        payload: Mapping[str, object],
    ) -> WhatsAppInboundMessage | None: ...

    async def aclose(self) -> None: ...
