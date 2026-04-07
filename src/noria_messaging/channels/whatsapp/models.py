from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Literal

WhatsAppSendStatus = Literal["submitted", "failed"]
WhatsAppComponentType = Literal["header", "body", "button"]
WhatsAppMediaType = Literal["image", "audio", "document", "sticker", "video"]
WhatsAppInteractiveType = Literal["button", "list"]
WhatsAppInteractiveHeaderType = Literal["text", "image", "video", "document"]
WhatsAppFlowActionType = Literal["navigate", "data_exchange"]
WhatsAppInboundMessageType = Literal[
    "text",
    "image",
    "audio",
    "document",
    "sticker",
    "video",
    "location",
    "contacts",
    "button",
    "interactive",
    "reaction",
    "unsupported",
]
WhatsAppInboundReplyType = Literal["button", "button_reply", "list_reply"]


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
class WhatsAppMediaRequest:
    recipient: str
    media_type: WhatsAppMediaType
    media_id: str | None = None
    link: str | None = None
    caption: str | None = None
    filename: str | None = None
    reply_to_message_id: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    provider_options: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class WhatsAppLocationRequest:
    recipient: str
    latitude: float
    longitude: float
    name: str | None = None
    address: str | None = None
    reply_to_message_id: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    provider_options: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class WhatsAppContactName:
    formatted_name: str
    first_name: str | None = None
    last_name: str | None = None
    middle_name: str | None = None
    suffix: str | None = None
    prefix: str | None = None


@dataclass(slots=True)
class WhatsAppContactPhone:
    phone: str
    type: str | None = None
    wa_id: str | None = None


@dataclass(slots=True)
class WhatsAppContactEmail:
    email: str
    type: str | None = None


@dataclass(slots=True)
class WhatsAppContactUrl:
    url: str
    type: str | None = None


@dataclass(slots=True)
class WhatsAppContactAddress:
    street: str | None = None
    city: str | None = None
    state: str | None = None
    zip: str | None = None
    country: str | None = None
    country_code: str | None = None
    type: str | None = None


@dataclass(slots=True)
class WhatsAppContactOrg:
    company: str | None = None
    department: str | None = None
    title: str | None = None


@dataclass(slots=True)
class WhatsAppContact:
    name: WhatsAppContactName
    phones: Sequence[WhatsAppContactPhone] = ()
    emails: Sequence[WhatsAppContactEmail] = ()
    urls: Sequence[WhatsAppContactUrl] = ()
    addresses: Sequence[WhatsAppContactAddress] = ()
    org: WhatsAppContactOrg | None = None
    birthday: str | None = None


@dataclass(slots=True)
class WhatsAppContactsRequest:
    recipient: str
    contacts: Sequence[WhatsAppContact]
    reply_to_message_id: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    provider_options: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class WhatsAppReactionRequest:
    recipient: str
    message_id: str
    emoji: str
    metadata: Mapping[str, Any] = field(default_factory=dict)
    provider_options: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class WhatsAppInteractiveHeader:
    type: WhatsAppInteractiveHeaderType
    text: str | None = None
    media_id: str | None = None
    link: str | None = None
    filename: str | None = None
    provider_options: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class WhatsAppInteractiveButton:
    identifier: str
    title: str


@dataclass(slots=True)
class WhatsAppInteractiveRow:
    identifier: str
    title: str
    description: str | None = None


@dataclass(slots=True)
class WhatsAppInteractiveSection:
    rows: Sequence[WhatsAppInteractiveRow]
    title: str | None = None


@dataclass(slots=True)
class WhatsAppInteractiveRequest:
    recipient: str
    interactive_type: WhatsAppInteractiveType
    body_text: str
    header: WhatsAppInteractiveHeader | None = None
    footer_text: str | None = None
    buttons: Sequence[WhatsAppInteractiveButton] = ()
    button_text: str | None = None
    sections: Sequence[WhatsAppInteractiveSection] = ()
    reply_to_message_id: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    provider_options: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class WhatsAppCatalogMessageRequest:
    recipient: str
    body_text: str | None = None
    header: WhatsAppInteractiveHeader | None = None
    footer_text: str | None = None
    thumbnail_product_retailer_id: str | None = None
    reply_to_message_id: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    provider_options: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class WhatsAppProductItem:
    product_retailer_id: str


@dataclass(slots=True)
class WhatsAppProductMessageRequest:
    recipient: str
    catalog_id: str
    product_retailer_id: str
    body_text: str | None = None
    footer_text: str | None = None
    reply_to_message_id: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    provider_options: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class WhatsAppProductSection:
    title: str
    product_items: Sequence[WhatsAppProductItem]


@dataclass(slots=True)
class WhatsAppProductListRequest:
    recipient: str
    catalog_id: str
    sections: Sequence[WhatsAppProductSection]
    header: WhatsAppInteractiveHeader
    body_text: str | None = None
    footer_text: str | None = None
    reply_to_message_id: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    provider_options: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class WhatsAppFlowMessageRequest:
    recipient: str
    flow_cta: str
    flow_id: str | None = None
    flow_name: str | None = None
    body_text: str | None = None
    header: WhatsAppInteractiveHeader | None = None
    footer_text: str | None = None
    flow_token: str | None = None
    flow_action: WhatsAppFlowActionType = "navigate"
    flow_action_payload: Mapping[str, Any] = field(default_factory=dict)
    flow_message_version: str = "3"
    reply_to_message_id: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    provider_options: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class WhatsAppMediaUploadRequest:
    filename: str
    content: bytes | bytearray | memoryview
    mime_type: str
    metadata: Mapping[str, Any] = field(default_factory=dict)
    provider_options: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class WhatsAppMediaUploadResult:
    provider: str
    media_id: str
    raw: object = None


@dataclass(slots=True)
class WhatsAppMediaInfo:
    provider: str
    media_id: str
    url: str | None = None
    mime_type: str | None = None
    sha256: str | None = None
    file_size: int | None = None
    raw: object = None


@dataclass(slots=True)
class WhatsAppMediaDeleteResult:
    provider: str
    media_id: str
    deleted: bool
    raw: object = None


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


@dataclass(slots=True)
class WhatsAppInboundMedia:
    media_type: WhatsAppMediaType
    media_id: str | None = None
    mime_type: str | None = None
    sha256: str | None = None
    caption: str | None = None
    filename: str | None = None
    raw: object = None


@dataclass(slots=True)
class WhatsAppInboundLocation:
    latitude: float | None
    longitude: float | None
    name: str | None = None
    address: str | None = None
    url: str | None = None
    raw: object = None


@dataclass(slots=True)
class WhatsAppInboundReply:
    reply_type: WhatsAppInboundReplyType
    identifier: str | None = None
    title: str | None = None
    description: str | None = None
    payload: str | None = None
    raw: object = None


@dataclass(slots=True)
class WhatsAppInboundReaction:
    emoji: str | None = None
    related_message_id: str | None = None
    raw: object = None


@dataclass(slots=True)
class WhatsAppInboundMessage:
    provider: str
    sender_id: str
    message_id: str
    message_type: WhatsAppInboundMessageType
    timestamp: str | None = None
    profile_name: str | None = None
    context_message_id: str | None = None
    forwarded: bool | None = None
    frequently_forwarded: bool | None = None
    text: str | None = None
    media: WhatsAppInboundMedia | None = None
    location: WhatsAppInboundLocation | None = None
    contacts: tuple[WhatsAppContact, ...] = ()
    reply: WhatsAppInboundReply | None = None
    reaction: WhatsAppInboundReaction | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    raw: object = None
