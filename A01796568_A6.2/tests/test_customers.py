import tempfile
import unittest
from pathlib import Path

from reservation_system.models import Customer
from reservation_system.services import build_services


class TestCustomerService(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.data_dir = Path(self.tmp.name)
        services = build_services(self.data_dir)
        self.customers = services["customers"]

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_create_and_get_customer(self) -> None:
        customer = Customer("C1", "Ana", "ana@test.com")
        self.customers.create_customer(customer)
        loaded = self.customers.get_customer("C1")
        self.assertEqual(loaded.email, "ana@test.com")

    def test_modify_customer(self) -> None:
        self.customers.create_customer(Customer("C1", "Ana", "ana@test.com"))
        self.customers.modify_customer("C1", name="Ana Maria")
        loaded = self.customers.get_customer("C1")
        self.assertEqual(loaded.name, "Ana Maria")

    def test_delete_customer(self) -> None:
        self.customers.create_customer(Customer("C1", "Ana", "ana@test.com"))
        self.customers.delete_customer("C1")
        self.assertEqual(self.customers.list_customers(), [])