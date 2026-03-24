"""
menu.py - Defines menu item classes using inheritance and polymorphism.
Classes: MenuItem (base), FoodItem, DrinkItem, Combo
"""


class MenuItem:
    """
    Base class for all menu items.
    Encapsulates common attributes: id, name, price, category, availability.
    """

    def __init__(self, item_id: str, name: str, price: float, category: str):
        self._id = item_id
        self._name = name
        self._price = price
        self._category = category
        self._available = True  # Available by default

    # --- Getters ---
    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def price(self):
        return self._price

    @property
    def category(self):
        return self._category

    @property
    def available(self):
        return self._available

    def toggle_availability(self):
        """Toggle item availability on/off."""
        self._available = not self._available

    def set_availability(self, status: bool):
        """Explicitly set availability."""
        self._available = status

    def get_tax_rate(self) -> float:
        """Override in subclasses to define category-specific tax rates."""
        return 0.0

    def display(self):
        """Display item info. Overridden in subclasses."""
        status = "Available" if self._available else "Unavailable"
        return (f"[{self._id}] {self._name} | ${self._price:.2f} "
                f"| Category: {self._category} | {status}")

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self._id}, name={self._name}, price={self._price})"


class FoodItem(MenuItem):
    """
    Represents a food menu item.
    Tax rate: 6% (food tax).
    """
    FOOD_TAX_RATE = 0.06

    def __init__(self, item_id: str, name: str, price: float, category: str = "Food"):
        super().__init__(item_id, name, price, category)

    def get_tax_rate(self) -> float:
        """Returns food tax rate (6%)."""
        return self.FOOD_TAX_RATE

    def display(self):
        return super().display() + f" | Tax: {self.FOOD_TAX_RATE*100:.0f}%"


class DrinkItem(MenuItem):
    """
    Represents a drink menu item.
    Tax rate: 8% (drink tax).
    """
    DRINK_TAX_RATE = 0.08

    def __init__(self, item_id: str, name: str, price: float, category: str = "Drink"):
        super().__init__(item_id, name, price, category)

    def get_tax_rate(self) -> float:
        """Returns drink tax rate (8%)."""
        return self.DRINK_TAX_RATE

    def display(self):
        return super().display() + f" | Tax: {self.DRINK_TAX_RATE*100:.0f}%"


class Combo(MenuItem):
    """
    Composite menu item made up of multiple MenuItems.
    Applies a combo discount to the sum of component prices.
    Uses the Composite pattern: acts as a MenuItem but contains others.
    """

    def __init__(self, item_id: str, name: str, items: list, discount_pct: float = 0.10):
        """
        Args:
            items: list of MenuItem objects in the combo
            discount_pct: fractional discount (e.g., 0.10 = 10% off)
        """
        self._components = list(items)  # Encapsulated component list
        self._discount_pct = discount_pct
        # Compute price as sum of components minus discount
        raw_price = sum(item.price for item in self._components)
        combo_price = round(raw_price * (1 - discount_pct), 2)
        super().__init__(item_id, name, combo_price, category="Combo")

    @property
    def components(self):
        return list(self._components)  # Return a copy to protect internal list

    @property
    def discount_pct(self):
        return self._discount_pct

    def get_tax_rate(self) -> float:
        """
        Weighted-average tax rate based on component prices.
        Blends food and drink tax rates proportionally.
        """
        total = sum(item.price for item in self._components)
        if total == 0:
            return 0.0
        weighted = sum(item.price * item.get_tax_rate() for item in self._components)
        return weighted / total

    def display(self):
        component_names = ", ".join(item.name for item in self._components)
        status = "Available" if self._available else "Unavailable"
        return (f"[{self._id}] {self._name} (Combo) | ${self._price:.2f} "
                f"| Includes: {component_names} | Discount: {self._discount_pct*100:.0f}% | {status}")
