"""
order.py - Order management: OrderItem, state lifecycle, and Order class.

Order Status Lifecycle:
  Created -> Confirmed -> Preparing -> Ready -> Served -> Paid

Valid Transitions (State pattern):
  Created   -> Confirmed
  Confirmed -> Preparing
  Preparing -> Ready
  Ready     -> Served
  Served    -> Paid

Any other transition raises an InvalidTransitionError.
"""

from pricing import TaxStrategy, TipStrategy, PercentageDiscount, FixedAmountDiscount


# ─── Exceptions ──────────────────────────────────────────────────────────────

class InvalidTransitionError(Exception):
    """Raised when an invalid order state transition is attempted."""
    pass


# ─── Order State ─────────────────────────────────────────────────────────────

class OrderState:
    """
    Base class for order states.
    Subclasses represent each valid status and define allowed transitions.
    """
    name = "Base"

    def confirm(self, order):
        raise InvalidTransitionError(
            f"Cannot confirm order from state '{self.name}'.")

    def prepare(self, order):
        raise InvalidTransitionError(
            f"Cannot start preparing from state '{self.name}'.")

    def mark_ready(self, order):
        raise InvalidTransitionError(
            f"Cannot mark ready from state '{self.name}'.")

    def serve(self, order):
        raise InvalidTransitionError(
            f"Cannot serve from state '{self.name}'.")

    def pay(self, order):
        raise InvalidTransitionError(
            f"Cannot pay from state '{self.name}'.")

    def __str__(self):
        return self.name


class CreatedState(OrderState):
    name = "Created"

    def confirm(self, order):
        order._state = ConfirmedState()
        print(f"  [Order #{order.order_id}] Status: Created -> Confirmed")


class ConfirmedState(OrderState):
    name = "Confirmed"

    def prepare(self, order):
        order._state = PreparingState()
        print(f"  [Order #{order.order_id}] Status: Confirmed -> Preparing")


class PreparingState(OrderState):
    name = "Preparing"

    def mark_ready(self, order):
        order._state = ReadyState()
        print(f"  [Order #{order.order_id}] Status: Preparing -> Ready")


class ReadyState(OrderState):
    name = "Ready"

    def serve(self, order):
        order._state = ServedState()
        print(f"  [Order #{order.order_id}] Status: Ready -> Served")


class ServedState(OrderState):
    name = "Served"

    def pay(self, order):
        order._state = PaidState()
        print(f"  [Order #{order.order_id}] Status: Served -> Paid")


class PaidState(OrderState):
    name = "Paid"


# ─── OrderItem ───────────────────────────────────────────────────────────────

class OrderItem:
    """
    Represents a single line item in an order: a MenuItem + quantity.
    Composition: Order contains OrderItems.
    """

    def __init__(self, menu_item, quantity: int = 1):
        if quantity <= 0:
            raise ValueError("Quantity must be at least 1.")
        self._menu_item = menu_item
        self._quantity = quantity

    @property
    def menu_item(self):
        return self._menu_item

    @property
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, value: int):
        if value <= 0:
            raise ValueError("Quantity must be at least 1.")
        self._quantity = value

    def line_total(self) -> float:
        """Price * quantity for this line."""
        return round(self._menu_item.price * self._quantity, 2)

    def __repr__(self):
        return f"OrderItem({self._menu_item.name}, qty={self._quantity})"


# ─── Order ───────────────────────────────────────────────────────────────────

class Order:
    """
    Represents a customer order.
    Manages items, state transitions, pricing, and receipt printing.
    Composition: Order contains OrderItems.
    """

    _counter = 1  # Auto-increment order IDs

    def __init__(self):
        self._order_id = Order._counter
        Order._counter += 1
        self._items = []           # List of OrderItem (private)
        self._state = CreatedState()
        self._discounts = []       # List of Discount objects
        self._tax_strategy = TaxStrategy()
        self._tip_strategy = TipStrategy(percentage=0.0)
        print(f"  [Order #{self._order_id}] Created.")

    # --- Properties ---
    @property
    def order_id(self):
        return self._order_id

    @property
    def status(self):
        return str(self._state)

    @property
    def items(self):
        return list(self._items)  # Return copy

    # --- Item Management ---
    def add_item(self, menu_item, quantity: int = 1):
        """
        Add a menu item to the order. If already present, increase quantity.
        Only allowed in 'Created' state.
        """
        if not isinstance(self._state, CreatedState):
            raise InvalidTransitionError(
                "Items can only be added when order is in 'Created' state.")
        if not menu_item.available:
            raise ValueError(f"'{menu_item.name}' is not currently available.")
        # Check if item already in order
        for oi in self._items:
            if oi.menu_item.id == menu_item.id:
                oi.quantity += quantity
                print(f"  [Order #{self._order_id}] Updated '{menu_item.name}' qty to {oi.quantity}.")
                return
        self._items.append(OrderItem(menu_item, quantity))
        print(f"  [Order #{self._order_id}] Added '{menu_item.name}' x{quantity}.")

    def remove_item(self, item_id: str):
        """
        Remove an item from the order by item ID.
        Only allowed in 'Created' state.
        """
        if not isinstance(self._state, CreatedState):
            raise InvalidTransitionError(
                "Items can only be removed when order is in 'Created' state.")
        for oi in self._items:
            if oi.menu_item.id == item_id:
                self._items.remove(oi)
                print(f"  [Order #{self._order_id}] Removed '{oi.menu_item.name}'.")
                return
        raise ValueError(f"Item ID '{item_id}' not found in order.")

    # --- Pricing Setup ---
    def add_discount(self, discount):
        """Add a Discount (PercentageDiscount or FixedAmountDiscount) to the order."""
        self._discounts.append(discount)
        print(f"  [Order #{self._order_id}] Discount added: {discount.description}")

    def set_tax_strategy(self, strategy: TaxStrategy):
        self._tax_strategy = strategy

    def set_tip(self, percentage: float):
        """Set tip percentage (e.g., 15.0 for 15%)."""
        self._tip_strategy = TipStrategy(percentage)
        print(f"  [Order #{self._order_id}] Tip set to {percentage:.1f}%.")

    # --- State Transitions ---
    def confirm(self, inventory=None):
        """
        Confirm the order.
        If inventory provided, validates and decrements stock.
        """
        if not self._items:
            raise ValueError("Cannot confirm an empty order.")
        if inventory:
            errors = inventory.validate_order(self._items)
            if errors:
                raise ValueError("Cannot confirm order due to stock issues:\n  " +
                                 "\n  ".join(errors))
            inventory.apply_order(self._items)
            print(f"  [Order #{self._order_id}] Stock decremented.")
        self._state.confirm(self)

    def prepare(self):
        self._state.prepare(self)

    def mark_ready(self):
        self._state.mark_ready(self)

    def serve(self):
        self._state.serve(self)

    def pay(self):
        self._state.pay(self)

    # --- Pricing Calculations ---
    def compute_subtotal(self) -> float:
        """Sum of all line item totals before discounts."""
        return round(sum(oi.line_total() for oi in self._items), 2)

    def compute_discounts(self, subtotal: float) -> tuple:
        """
        Apply all discounts in order: percentage discounts first, then fixed.
        Returns (total_discount_amount, discounted_subtotal).
        """
        # Sort: percentage discounts first, then fixed
        sorted_discounts = sorted(
            self._discounts,
            key=lambda d: 0 if isinstance(d, PercentageDiscount) else 1
        )
        total_discount = 0.0
        running = subtotal
        for discount in sorted_discounts:
            amt = discount.apply(running)
            total_discount += amt
            running -= amt
        return round(total_discount, 2), round(running, 2)

    def compute_tax(self, discounted_subtotal: float, subtotal: float) -> float:
        """
        Compute tax on discounted subtotal.
        Discount ratio preserves per-item proportionality.
        """
        if subtotal == 0:
            return 0.0
        ratio = discounted_subtotal / subtotal
        return self._tax_strategy.compute_tax(self._items, discount_ratio=ratio)

    def compute_tip(self, base: float) -> float:
        """Compute tip on (discounted subtotal + tax)."""
        return self._tip_strategy.compute_tip(base)

    def get_price_breakdown(self) -> dict:
        """
        Returns a full price breakdown dict:
          subtotal, discount_amount, discounted_subtotal,
          tax, tip, total
        """
        subtotal = self.compute_subtotal()
        discount_amount, discounted_subtotal = self.compute_discounts(subtotal)
        tax = self.compute_tax(discounted_subtotal, subtotal)
        tip_base = discounted_subtotal + tax
        tip = self.compute_tip(tip_base)
        total = round(discounted_subtotal + tax + tip, 2)
        return {
            "subtotal": subtotal,
            "discount_amount": discount_amount,
            "discounted_subtotal": discounted_subtotal,
            "tax": tax,
            "tip_pct": self._tip_strategy.percentage,
            "tip": tip,
            "total": total,
        }

    # --- Receipt ---
    def print_receipt(self):
        """Print a formatted receipt with full breakdown."""
        breakdown = self.get_price_breakdown()
        width = 52

        print("\n" + "=" * width)
        print(f"{'RECEIPT':^{width}}")
        print(f"{'Order #' + str(self._order_id):^{width}}")
        print(f"{'Status: ' + self.status:^{width}}")
        print("=" * width)
        print(f"{'ITEM':<24} {'QTY':>4} {'PRICE':>8} {'TOTAL':>10}")
        print("-" * width)

        for oi in self._items:
            name = oi.menu_item.name[:22]
            print(f"{name:<24} {oi.quantity:>4} "
                  f"${oi.menu_item.price:>7.2f} ${oi.line_total():>9.2f}")

        print("-" * width)
        print(f"{'Subtotal':<38} ${breakdown['subtotal']:>9.2f}")

        if breakdown['discount_amount'] > 0:
            print(f"{'Discounts':<38}-${breakdown['discount_amount']:>8.2f}")
            for d in self._discounts:
                print(f"  - {d.description}")
            print(f"{'After Discounts':<38} ${breakdown['discounted_subtotal']:>9.2f}")

        print(f"{'Tax':<38} ${breakdown['tax']:>9.2f}")
        print(f"{'Tip (' + str(breakdown['tip_pct']) + '%)':<38} ${breakdown['tip']:>9.2f}")
        print("=" * width)
        print(f"{'TOTAL':<38} ${breakdown['total']:>9.2f}")
        print("=" * width)

    def view_order(self):
        """Print a summary of current order items and status."""
        print(f"\n--- Order #{self._order_id} | Status: {self.status} ---")
        if not self._items:
            print("  (No items added yet.)")
            return
        for oi in self._items:
            print(f"  {oi.menu_item.name:<25} x{oi.quantity}  ${oi.line_total():.2f}")
        breakdown = self.get_price_breakdown()
        print(f"  {'Subtotal':<35} ${breakdown['subtotal']:.2f}")
        print(f"  {'Est. Total':<35} ${breakdown['total']:.2f}")
        print("-" * 44)
