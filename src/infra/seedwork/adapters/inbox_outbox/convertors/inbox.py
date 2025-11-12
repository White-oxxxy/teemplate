from infra.seedwork.adapters.inbox_outbox.message import InboxMessage
from infra.seedwork.adapters.message_broker.integration_event import BaseIntegrationEvent


class IntegrationEventToInboxMessageConvertor:
    def convert(self, event: BaseIntegrationEvent) -> InboxMessage: ...


class InboxMessageToIntegrationEvnetConvertor:
    def convert(self, message: InboxMessage) -> BaseIntegrationEvent: ...