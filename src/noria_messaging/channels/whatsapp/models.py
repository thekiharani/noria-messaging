from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Literal

WhatsAppSendStatus = Literal["submitted", "failed"]
WhatsAppComponentType = Literal["header", "body", "button"]


@dataclass(slots=True)
class WhatsAppTextRequest:
    recipient: str
    text: str
    preview_url: bool | None = None
    reply_to_message_id: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    provider_options: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class WhatsAppTemplateParameter:
    type: str
    value: str | None = None
    provider_options: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class WhatsAppTemplateComponent:
    type: WhatsAppComponentType
    parameters: Sequence[WhatsAppTemplateParameter] = ()
    sub_type: str | None = None
    index: int | None = None


@dataclass(slots=True)
class WhatsAppTemplateRequest:
    recipient: str
    template_name: str
    language_code: str
    components: Sequence[WhatsAppTemplateComponent] = ()
    reply_to_message_id: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    provider_options: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class WhatsAppSendReceipt:
    provider: str
    recipient: str
    status: WhatsAppSendStatus
    provider_message_id: str | None = None
    provider_status: str | None = None
    conversation_id: str | None = None
    error_code: str | None = None
    error_description: str | None = None
    raw: object = None


@dataclass(slots=True)
class WhatsAppSendResult:
    provider: str
    accepted: bool
    error_code: str | None
    error_description: str | None
    messages: tuple[WhatsAppSendReceipt, ...]
    raw: object = None

    @property
    def submitted_count(self) -> int:
        return sum(1 for message in self.messages if message.status == "submitted")

    @property
    def failed_count(self) -> int:
        return sum(1 for message in self.messages if message.status == "failed")
