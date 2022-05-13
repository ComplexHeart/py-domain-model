from typing import List

from complexheart.domain.event import DomainEvent


class HasIdentity:
    pass


class HasEquality:
    pass


class HasInvariants:
    pass


class HasDomainEvents:
    def __init__(self):
        self.__domain_events = []

    def domain_events(self) -> List[DomainEvent]:
        return self.__domain_events
