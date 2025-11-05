from domain.seedwork.event import DomainEvent
from infra.seedwork.adapters.inbox_outbox.message import OutboxMessage


def convert_domain_event_to_outbox_message(event: DomainEvent) -> OutboxMessage: ...