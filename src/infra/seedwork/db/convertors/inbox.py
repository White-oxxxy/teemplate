from adaptix import P
from adaptix.conversion import get_converter, link

from infra.seedwork.adapters.inbox_outbox.message import InboxMessage
from infra.seedwork.db.models.inbox import InboxMessageModel


convert_inbox_message_to_model = get_converter(
    src=InboxMessage,
    dst=InboxMessageModel,
    recipe=[link(P[InboxMessage].created_at, P[InboxMessageModel].event_created_at)]
)

convert_inbox_model_to_message = get_converter(
    src=InboxMessageModel,
    dst=InboxMessage,
    recipe=[link(P[InboxMessageModel].event_created_at, P[InboxMessage].created_at)]
)


class InboxMessageModelConvertor:
    @staticmethod
    def to_orm(message: InboxMessage) -> InboxMessageModel:
        model: InboxMessageModel = convert_inbox_message_to_model(message,)

        return model

    @staticmethod
    def from_orm(model: InboxMessageModel) -> InboxMessage:
        message: InboxMessage = convert_inbox_model_to_message(model,)

        return message