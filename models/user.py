"""Typed customer data and isolated test-data generation."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from uuid import uuid4

from faker import Faker

fake = Faker("en_US")


@dataclass(frozen=True)
class User:
    """Represent all customer fields required by the ParaBank form."""

    first_name: str
    last_name: str
    street: str
    city: str
    state: str
    zip_code: str
    phone: str
    ssn: str
    username: str
    password: str
    confirmation: str

    def as_dict(self) -> dict[str, str]:
        """Return the immutable user data as a serializable dictionary."""
        return asdict(self)


class UserFactory:
    """Build unique users so scenarios do not collide between executions."""

    @staticmethod
    def valid() -> User:
        """Generate a valid customer with credentials unique to this run."""
        suffix = uuid4().hex[:10]
        password = f"Qa!{suffix}"
        return User(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            street=fake.street_address(),
            city=fake.city(),
            state=fake.state_abbr(),
            zip_code=fake.postcode(),
            phone=fake.numerify("##########"),
            ssn=fake.numerify("#########"),
            username=f"qa_{suffix}",
            password=password,
            confirmation=password,
        )
