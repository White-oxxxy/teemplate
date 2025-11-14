from domain.seedwork.event import DomainEvent
from infra.seedwork.adapters.inbox_outbox.message import OutboxMessage
from infra.seedwork.adapters.message_broker.integration_event import BaseIntegrationEvent


class DomainEventOutboxMessageConvertor:
    def to_message(self, event: DomainEvent) -> OutboxMessage: ...


class OutboxMessageIntegrationEventConvertor:
    def to_event(self, message: OutboxMessage) -> BaseIntegrationEvent: ...