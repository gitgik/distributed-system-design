# Designing Amazon - Online Shopping System
Let's design an online retail store.
For the sake of this problem, we'll focus on Amazon's retail business where users can buy/sell products.


## Requirements and Goals of the System
1. Users should be able to:
    - Add new products to sell.
    - Search products by name or category.
    - Buy products only if they are registered members.
    - Remove/modify product items in their shopping cart.
    - Checkout and buy items in the shopping cart.
    - Rate and review a product.
    - Specify a shipping address where their order will be delivered.
    - Cancel and order if it hasn't been shipped.
    - Pay via debit or credit cards
    - Track their shipment to see the current state of their order.
2. The system should be able to:
    - Send a notification whenever the shipping status of the order changes.

## Use Case Diagram
We have four main actors in the system:

- **Admin:** Mainly responsible for account management, adding and modifying new product categories.

- **Guest:** All guests can search the catalog, add/remove items on the shopping cart, and also become registered members.
- **Member:** In addition to what guests can do, members can place orders and add new products to sell
- **System:** Mainly responsible for sending notifications for orders and shipping updates.


Top use cases therefore include:
1. Add/Update products: whenever a product is added/modified, update the catalog.
2. Search for products by their name or category.
3. Add/remove product items from shopping cart.
4. Checkout to buy a product item in the shopping cart.
5. Make a payment to place an order.
6. Add a new product category.
7. Send notifications about order shipment updates to members.


### Code

This is a class-design sketch. Cart updates and order logs are implemented; checkout, payment, registration, and other methods marked `pass` or `NotImplementedError` remain incomplete.

First we define the enums, datatypes and constants that'll be used by the rest of the classes:


```python
from enum import Enum


class AccountStatus(Enum):
    ACTIVE, BLOCKED, BANNED, COMPROMISED, ARCHIVED, UNKNOWN = 1, 2, 3, 4, 5, 6

class OrderStatus(Enum):
    UNSHIPPED, SHIPPED, PENDING, COMPLETED, CANCELED, REFUND_APPLIED = 1, 2, 3, 4, 5, 6

class ShipmentStatus(Enum):
    PENDING, SHIPPED, DELIVERED, ON_HOLD = 1, 2, 3, 4

class PaymentStatus(Enum):
    UNPAID, PENDING, COMPLETED, FILLED, DECLINED = 1, 2, 3, 4, 5
    CANCELLED, ABANDONED, SETTLING, SETTLED, REFUNDED = 6, 7, 8, 9, 10

```

#### Account, Customer, Admin and Guest classes
These classes represent different people that interact with the system.


```python
from abc import ABC, abstractmethod


class Account:
    """Python strives to adhere to Uniform Access Principle.

    So there's no need for getter and setter methods.
    """

    def __init__(self, username, password, name, email, phone, shipping_address, status:AccountStatus):
        # "private" attributes
        self._username = username
        self._password = password
        self._name = name
        self._email = email
        self._phone = phone
        self._shipping_address = shipping_address
        self._status = status
        self._credit_cards = []
        self._bank_accounts = []

    def add_product(self, product):
        pass

    def add_product_review(self, review):
        pass

    def reset_password(self):
        pass


class Customer(ABC):
    def __init__(self, cart, order):
        self._cart = cart
        self._order = order

    def get_shopping_cart(self):
        return self._cart

    def add_item_to_cart(self, item):
        raise NotImplementedError

    def remove_item_from_cart(self, item):
        raise NotImplementedError


class Guest(Customer):
    def register_account(self):
        pass


class Member(Customer):
    def __init__(self, account:Account, cart=None, order=None):
        super().__init__(cart, order)
        self._account = account

    def place_order(self, order):
        pass

```


```python
# Test class definition
g = Guest(cart="Cart1", order="Order1")
print(hasattr(g, "remove_item_from_cart"))
print(isinstance(g, Customer))
```

    True
    True


#### Product Category, Product and Product Review
The classes below are related to a product:


```python
class Product:
    def __init__(self, product_id, name, description, price, category, available_item_count):
        self._product_id = product_id
        self._name = name
        self._description = description
        self._price = price
        self._category = category
        self._available_item_count = available_item_count

    def update_price(self, new_price):
        self._price = new_price


class ProductCategory:
    def __init__(self, name, description):
        self._name = name
        self._description = description


class ProductReview:
    def __init__(self, rating, review, reviewer):
        self._rating = rating
        self._review = review
        self._reviewer = reviewer

```

#### ShoppingCart, Item, Order and OrderLog
Users will add items to the shopping cart and place an order to buy all the items in the cart.


```python
class Item:
    def __init__(self, item_id, quantity, price):
        self._item_id = item_id
        self._quantity = quantity
        self._price = price

    def update_quantity(self, quantity):
        self._quantity = quantity

    def __repr__(self):
        return f"ItemID:<{self._item_id}>"


class ShoppingCart:
    """We can still access items by calling items instead of having getter method
    """
    def __init__(self):
        self._items = []

    def add_item(self, item):
        self._items.append(item)

    def remove_item(self, item):
        self._items.remove(item)

    def update_item_quantity(self, item, quantity):
        if item not in self._items:
            raise ValueError("Item is not in the shopping cart")
        item.update_quantity(quantity)

```


```python
item = Item(item_id=1, quantity=2, price=300)
cart = ShoppingCart()
cart.add_item(item)
```


```python
# shopping cart now has items
cart._items
```




    [ItemID:<1>]




```python
import datetime


class OrderLog:
    def __init__(self, order_number, status=OrderStatus.PENDING):
        self._order_number = order_number
        self._creation_date = datetime.date.today()
        self._status = status


class Order:
    def __init__(self, order_number, status=OrderStatus.PENDING):
        self._order_number = order_number
        self._status = status
        self._order_date = datetime.date.today()
        self._order_log = []

    def send_for_shipment(self):
        pass

    def make_payment(self, payment):
        pass

    def add_order_log(self, order_log):
        self._order_log.append(order_log)
```

#### Shipment and Notification
After successfully placing an order and processing the payment, a shipment record will be created.
Let's define the Shipment and Notification classes:


```python
import datetime


class ShipmentLog:
    def __init__(self, shipment_id, status=ShipmentStatus.PENDING):
        self._shipment_id = shipment_id
        self.shipment_status = status


class Shipment:
    def __init__(self, shipment_id, shipment_method, eta=None, shipment_logs=None):
        self._shipment_id = shipment_id
        self._shipment_method = shipment_method
        self._shipment_date = datetime.date.today()
        self._eta = eta
        self._shipment_logs = [] if shipment_logs is None else shipment_logs


class Notification(ABC):
    def __init__(self, notification_id, content):
        self._notification_id = notification_id
        self._created_on = datetime.datetime.now()
        self._content = content

```
