import pytest

from dataclasses import dataclass

from complexheart.domain.models import has_invariants, invariant, InvariantViolation


@dataclass
@has_invariants
class OrderLine:
    name: str
    unit_price: float
    quantity: int = 0

    @invariant
    def quantity_must_be_greater_than_zero(self) -> bool:
        return self.quantity >= 0

    @invariant
    def price_must_be_positive_value(self) -> bool:
        return self.unit_price >= 0

    def total_cost(self) -> float:
        return self.unit_price * self.quantity


def test_invariant_should_raise_error_on_invariant_violation():
    with pytest.raises(InvariantViolation):
        OrderLine(
            name='nintendo Switch',
            unit_price=-250.0,
            quantity=1,
        )


@dataclass
@has_invariants
class FullName:
    first_name: str
    last_name: str

    def __post_init__(self):
        if not self.last_name:
            self.last_name = 'Doe'

    @invariant
    def first_name_must_not_be_empty(self) -> bool:
        return len(self.first_name.strip()) > 0

    @invariant
    def last_name_must_not_be_empty(self) -> bool:
        return len(self.last_name.strip()) > 0


def test_invariant_should_raise_error_on_invariant_violation_extending_post_init():
    with pytest.raises(InvariantViolation):
        FullName(
            first_name='',
            last_name='Vega',
        )


def test_invariant_should_not_raise_error_on_valid_data():
    name = FullName(
        first_name='Vincent',
        last_name='Vega',
    )

    assert isinstance(name, FullName)
