import contextlib
import io
import json
from pathlib import Path
import re
import unittest


EXAMPLE_DIR = Path(__file__).resolve().parents[1] / "OOP-design"
EXAMPLES = (
    "designing_amazon_online_shopping_system.md",
    "designing_amazon_online_shopping_system.ipynb",
    "executed_amazon_system.ipynb",
)


def load_example(path):
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".ipynb":
        blocks = [
            "".join(cell["source"])
            for cell in json.loads(text)["cells"]
            if cell["cell_type"] == "code"
        ]
    else:
        blocks = re.findall(r"```python\n(.*?)```", text, re.DOTALL)
    namespace = {}
    with contextlib.redirect_stdout(io.StringIO()):
        for index, block in enumerate(blocks):
            # Run checked-in examples, not external input or a separate code copy.
            exec(  # nosec B102 # pylint: disable=exec-used
                compile(block, f"{path}:{index}", "exec"), namespace
            )
    return namespace


class ShoppingExampleTests(unittest.TestCase):
    def setUp(self):
        self.examples = [
            (name, load_example(EXAMPLE_DIR / name)) for name in EXAMPLES
        ]

    def test_account_preserves_supplied_state(self):
        for name, example in self.examples:
            with self.subTest(example=name):
                account = example["Account"](
                    "user", "password", "Buyer", "buyer@example.test",
                    "123", "address", example["AccountStatus"].BLOCKED,
                )
                self.assertEqual(account._status, example["AccountStatus"].BLOCKED)
                self.assertEqual(account._name, "Buyer")

    def test_customer_returns_its_cart(self):
        for name, example in self.examples:
            with self.subTest(example=name):
                cart = example["ShoppingCart"]()
                customer = example["Guest"](cart, None)
                self.assertIs(customer.get_shopping_cart(), cart)

    def test_member_initializes_inherited_state(self):
        for name, example in self.examples:
            with self.subTest(example=name):
                cart = example["ShoppingCart"]()
                order = example["Order"](1)
                member = example["Member"](None, cart=cart, order=order)
                self.assertIs(member.get_shopping_cart(), cart)
                self.assertIs(member._order, order)
                empty_member = example["Member"](None)
                self.assertIsNone(empty_member.get_shopping_cart())
                self.assertIsNone(empty_member._order)

    def test_product_preserves_supplied_inventory(self):
        for name, example in self.examples:
            with self.subTest(example=name):
                product = example["Product"](1, "Book", "Paperback", 10, "Books", 7)
                self.assertEqual(product._available_item_count, 7)
                self.assertEqual(product._description, "Paperback")

    def test_cart_updates_only_the_selected_item(self):
        for name, example in self.examples:
            with self.subTest(example=name):
                cart = example["ShoppingCart"]()
                item = example["Item"](1, 2, 10)
                other = example["Item"](2, 3, 20)
                cart.add_item(item)
                cart.add_item(other)
                cart.update_item_quantity(item, 5)
                self.assertEqual(item._quantity, 5)
                self.assertEqual(other._quantity, 3)

    def test_cart_rejects_updates_to_items_not_in_cart(self):
        for name, example in self.examples:
            with self.subTest(example=name):
                item = example["Item"](1, 2, 10)
                with self.assertRaises(ValueError):
                    example["ShoppingCart"]().update_item_quantity(item, 5)
                self.assertEqual(item._quantity, 2)

    def test_order_logs_are_recorded_on_the_correct_order(self):
        for name, example in self.examples:
            with self.subTest(example=name):
                order = example["Order"](1)
                other = example["Order"](2)
                first = example["OrderLog"](1)
                second = example["OrderLog"](1, example["OrderStatus"].SHIPPED)
                order.add_order_log(first)
                order.add_order_log(second)
                self.assertEqual(order._order_log, [first, second])
                self.assertEqual(other._order_log, [])

    def test_shipments_have_independent_default_logs(self):
        for name, example in self.examples:
            with self.subTest(example=name):
                first = example["Shipment"](1, "ground")
                second = example["Shipment"](2, "air")
                log = example["ShipmentLog"](1)
                first._shipment_logs.append(log)
                self.assertEqual(second._shipment_logs, [])

    def test_shipment_preserves_explicit_logs_and_method(self):
        for name, example in self.examples:
            with self.subTest(example=name):
                logs = [example["ShipmentLog"](1)]
                shipment = example["Shipment"](1, "ground", shipment_logs=logs)
                self.assertIs(shipment._shipment_logs, logs)
                self.assertEqual(shipment._shipment_method, "ground")


if __name__ == "__main__":
    unittest.main()
