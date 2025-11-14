from infra.seedwork.adapters.inbox_outbox.message import InboxMessage
from infra.seedwork.adapters.message_broker.integration_event import BaseIntegrationEvent


class IntegrationEventInboxMessageConvertor:
    def to_message(self, event: BaseIntegrationEvent) -> InboxMessage: ...

    def to_event(self, message: InboxMessage) -> BaseIntegrationEvent: ...