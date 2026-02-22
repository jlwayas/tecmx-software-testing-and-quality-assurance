"""Unit tests for CustomerService."""

from reservation_system.models import Customer
from tests.base_test_case import BaseServiceTestCase


class TestCustomerService(BaseServiceTestCase):
    """Tests for customer CRUD operations."""

    def test_create_and_get_customer(self) -> None:
        """Creating a customer persists it and it can be retrieved."""
        customer = Customer("C1", "Ana", "ana@test.com")
        self.customers.create_customer(customer)

        loaded = self.customers.get_customer("C1")
        self.assertEqual(loaded.email, "ana@test.com")

    def test_modify_customer(self) -> None:
        """Modifying an existing customer updates persisted fields."""
        self.customers.create_customer(Customer("C1", "Ana", "ana@test.com"))
        self.customers.modify_customer("C1", {"name": "Ana Maria"})

        loaded = self.customers.get_customer("C1")
        self.assertEqual(loaded.name, "Ana Maria")

    def test_delete_customer(self) -> None:
        """Deleting a customer removes it from storage."""
        self.customers.create_customer(Customer("C1", "Ana", "ana@test.com"))
        self.customers.delete_customer("C1")

        self.assertEqual(self.customers.list_customers(), [])
