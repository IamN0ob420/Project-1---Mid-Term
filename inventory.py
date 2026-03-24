"""
inventory.py - Manages stock quantities for menu items.
Prevents confirming orders when items are out of stock.
Decrements stock when an order is confirmed.
"""


class Inventory:
    """
    Tracks available stock for each menu item by item ID.
    Encapsulates stock data privately; exposes clean methods.
    """

    def __init__(self):
        self._stock = {}  # {item_id: quantity}

    def set_stock(self, item_id: str, quantity: int):
        """Set the stock level for an item."""
        if quantity < 0:
            raise ValueError("Stock quantity cannot be negative.")
        self._stock[item_id] = quantity
        print(f"  [Inventory] Stock set: item '{item_id}' = {quantity} units.")

    def get_stock(self, item_id: str) -> int:
        """Return current stock for an item (0 if not tracked)."""
        return self._stock.get(item_id, 0)

    def check_availability(self, item_id: str, quantity: int) -> bool:
        """Return True if enough stock is available."""
        return self.get_stock(item_id) >= quantity

    def decrement(self, item_id: str, quantity: int):
        """
        Reduce stock by the given quantity.
        Raises ValueError if insufficient stock.
        """
        current = self.get_stock(item_id)
        if current < quantity:
            raise ValueError(
                f"Insufficient stock for item '{item_id}': "
                f"requested {quantity}, available {current}."
            )
        self._stock[item_id] = current - quantity

    def validate_order(self, order_items: list) -> list:
        """
        Check all order items against stock.
        Returns a list of error strings for any items that cannot be fulfilled.
        order_items: list of OrderItem objects.
        """
        errors = []
        for order_item in order_items:
            item_id = order_item.menu_item.id
            qty = order_item.quantity
            available = self.get_stock(item_id)
            if available < qty:
                errors.append(
                    f"'{order_item.menu_item.name}' (id={item_id}): "
                    f"requested {qty}, only {available} in stock."
                )
        return errors

    def apply_order(self, order_items: list):
        """
        Decrement stock for all items in an order.
        Call only after validate_order passes.
        """
        for order_item in order_items:
            self.decrement(order_item.menu_item.id, order_item.quantity)

    def show_stock(self, menu_items: dict = None):
        """
        Print current stock levels.
        Optionally accepts a dict {item_id: MenuItem} to show names.
        """
        print("\n--- Inventory Stock Levels ---")
        if not self._stock:
            print("  (No stock data recorded.)")
            return
        for item_id, qty in sorted(self._stock.items()):
            name = ""
            if menu_items and item_id in menu_items:
                name = f" ({menu_items[item_id].name})"
            print(f"  Item {item_id}{name}: {qty} units")
        print("------------------------------")
