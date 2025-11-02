from dataclasses import dataclass

from domain.seedwork.business_rules.rules import BaseBusinessRule
from domain.seedwork.business_rules.exception import BusinessRuleValidationException


@dataclass
class BusinessRuleValidationMixin:
    @staticmethod
    def check_rule(rule: BaseBusinessRule) -> None:
        if rule.is_broken():
            raise BusinessRuleValidationException(message=rule.get_message())