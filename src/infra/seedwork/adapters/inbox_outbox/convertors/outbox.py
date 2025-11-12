from domain.seedwork.event import DomainEvent
from infra.seedwork.adapters.inbox_outbox.message import OutboxMessage
from infra.seedwork.adapters.message_broker.integration_event import BaseIntegrationEvent


class DomainEventToOutboxMessageConvertor:
    def convert(self, event: DomainEvent) -> OutboxMessage: ...


class OutboxMessageToIntegrationEventConvertor:
    def convert(self, message: OutboxMessage) -> BaseIntegrationEvent: ...