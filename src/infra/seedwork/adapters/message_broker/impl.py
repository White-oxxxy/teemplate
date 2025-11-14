from dataclasses import dataclass

from faststream.kafka import KafkaBroker


@dataclass
class KafkaMessageBrokerImpl:
    _broker: KafkaBroker
    ...