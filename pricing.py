"""
pricing.py - Pricing strategies: tax, tip, and discounts.

Discount application order (documented):
  1. Subtotal = sum(item_price * quantity)
  2. Discounts applied to subtotal (percentage first, then fixed)
  3. Tax computed on discounted subtotal, per item category rate
  4. Tip computed on (discounted_subtotal + tax)
  5. Final total = discounted_subtotal + tax + tip

Classes:
  Discount (base) -> PercentageDiscount, FixedAmountDiscount
  TaxStrategy
  TipStrategy
"""


# ─── Discount Base & Subclasses ─────────────────────────────────────────────

class Discount:
    """
    Abstract base class for discounts.
    Subclasses override apply() to return the discount amount.
    """

    def __init__(self, description: str):
        self._description = description

    @property
    def description(self):
        return self._description

    def apply(self, subtotal: float) -> float:
        """Return the discount AMOUNT (not the reduced total)."""
        raise NotImplementedError("Subclasses must implement apply().")

    def __repr__(self):
        return f"{self.__class__.__name__}(description={self._description})"


class PercentageDiscount(Discount):
    """
    Discount as a percentage of the subtotal.
    E.g., 10% discount on a $50 subtotal = $5.00 off.
    """

    def __init__(self, percentage: float, description: str = None):
        """
        Args:
            percentage: e.g., 10.0 means 10%
        """
        if not 0 <= percentage <= 100:
            raise ValueError("Percentage must be between 0 and 100.")
        self._percentage = percentage
        desc = description or f"{percentage:.1f}% Discount"
        super().__init__(desc)

    @property
    def percentage(self):
        return self._percentage

    def apply(self, subtotal: float) -> float:
        """Returns discount amount."""
        return round(subtotal * (self._percentage / 100), 2)


class FixedAmountDiscount(Discount):
    """
    Discount as a fixed dollar amount.
    E.g., $3.00 off regardless of subtotal.
    Discount cannot exceed the subtotal (floors at 0).
    """

    def __init__(self, amount: float, description: str = None):
        if amount < 0:
            raise ValueError("Fixed discount amount cannot be negative.")
        self._amount = amount
        desc = description or f"${amount:.2f} Off"
        super().__init__(desc)

    @property
    def amount(self):
        return self._amount

    def apply(self, subtotal: float) -> float:
        """Returns discount amount, capped at subtotal."""
        return round(min(self._amount, subtotal), 2)


# ─── Tax Strategy ────────────────────────────────────────────────────────────

class TaxStrategy:
    """
    Computes tax based on item category rates.
    Default rates: Food = 6%, Drink = 8%, Other = 6%.
    """

    DEFAULT_RATES = {
        "Food":  0.06,
        "Drink": 0.08,
        "Combo": None,   # Combo uses weighted average from Combo.get_tax_rate()
    }

    def __init__(self, rates: dict = None):
        """
        Args:
            rates: Optional override dict {category: rate}
        """
        self._rates = dict(self.DEFAULT_RATES)
        if rates:
            self._rates.update(rates)

    def get_rate(self, category: str) -> float:
        """Return tax rate for a category. Falls back to 6% if unknown."""
        return self._rates.get(category, 0.06)

    def compute_tax(self, order_items: list, discount_ratio: float = 1.0) -> float:
        """
        Compute total tax on order items.
        Tax is applied to the discounted subtotal per item.

        Args:
            order_items: list of OrderItem objects
            discount_ratio: fraction remaining after discounts (e.g., 0.9 = 10% off applied)
        Returns:
            Total tax amount (float)
        """
        total_tax = 0.0
        for oi in order_items:
            item_subtotal = oi.menu_item.price * oi.quantity * discount_ratio
            rate = oi.menu_item.get_tax_rate()  # Polymorphic call
            total_tax += item_subtotal * rate
        return round(total_tax, 2)


# ─── Tip Strategy ────────────────────────────────────────────────────────────

class TipStrategy:
    """
    Computes tip as a percentage of (discounted subtotal + tax).
    Common rates: 0%, 15%, 18%, 20%.
    """

    def __init__(self, percentage: float = 0.0):
        """
        Args:
            percentage: e.g., 15.0 means 15%
        """
        if not 0 <= percentage <= 100:
            raise ValueError("Tip percentage must be between 0 and 100.")
        self._percentage = percentage

    @property
    def percentage(self):
        return self._percentage

    def compute_tip(self, base_amount: float) -> float:
        """
        Compute tip on the given base amount.
        Tip base = discounted subtotal + tax.
        """
        return round(base_amount * (self._percentage / 100), 2)
