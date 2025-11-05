from adaptix import P
from adaptix.conversion import get_converter, link

from infra.seedwork.adapters.inbox_outbox.message import OutboxMessage
from infra.seedwork.db.models.outbox import OutboxMessageModel


convert_outbox_message_to_model = get_converter(
    src=OutboxMessage,
    dst=OutboxMessageModel,
    recipe=[link(P[OutboxMessage].created_at, P[OutboxMessageModel].event_created_at)]
)

convert_outbox_model_to_message = get_converter(
    src=OutboxMessageModel,
    dst=OutboxMessage,
    recipe=[link(P[OutboxMessageModel].event_created_at, P[OutboxMessage].created_at)]
)