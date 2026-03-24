# Restaurant Ordering System — Project Report

---

## 1. Project Overview

### What It Does

The Restaurant Ordering System is a command-line Python application that simulates a restaurant point-of-sale workflow. It allows a user to build a menu, track ingredient stock, compose customer orders, apply pricing rules, and walk an order through a defined lifecycle from creation to payment.

### How to Run

```bash
# Interactive CLI
python cli.py

# Automated demo scenario
python demo_scenario.py
```

No external packages are required — the project uses only the Python standard library.

---

## 2. Code Structure

```
restaurant_project/
│
├── menu.py           # MenuItem, FoodItem, DrinkItem, Combo
├── inventory.py      # Inventory (stock tracking)
├── order.py          # Order, OrderItem, OrderState hierarchy
├── pricing.py        # TaxStrategy, TipStrategy, Discount hierarchy
├── cli.py            # RestaurantCLI (interactive command-line interface)
├── demo_scenario.py  # Required sample scenario
├── README.md         # Setup and command reference
└── docs/
    └── report.md     # This report
```

Each module has a single clear responsibility. `menu.py` defines what can be ordered; `inventory.py` tracks how many are available; `order.py` manages the lifecycle of a customer order; `pricing.py` encapsulates all financial calculations; and `cli.py` glues everything into an interactive shell.

---

## 3. Class Descriptions

### `menu.py`

**`MenuItem` (base class)**
Encapsulates the shared properties of every item on the menu: `id`, `name`, `price`, `category`, and `available`. Exposes `get_tax_rate()` and `display()` as overridable polymorphic hooks. Internal fields are private (prefixed `_`); access is through properties.

**`FoodItem(MenuItem)`**
Concrete subclass for food items. Overrides `get_tax_rate()` to return 6% and appends the rate to `display()`.

**`DrinkItem(MenuItem)`**
Concrete subclass for drink items. Overrides `get_tax_rate()` to return 8%.

**`Combo(MenuItem)`**
Composite item built from a list of `MenuItem` components. Applies a percentage discount to the component sum to set its own price. Overrides `get_tax_rate()` with a weighted-average rate across all components. The internal `_components` list is private; a copy is returned via the `components` property.

---

### `inventory.py`

**`Inventory`**
Stores stock levels in a private `_stock` dictionary keyed by item ID. Exposes `set_stock`, `get_stock`, `check_availability`, `decrement`, `validate_order`, and `apply_order`. `validate_order` returns a list of error strings so callers can decide whether to block confirmation. `apply_order` performs the actual decrements atomically after validation passes.

---

### `order.py`

**`OrderState` (base class) + concrete states**
Implements a lightweight State pattern. Six state classes (`CreatedState`, `ConfirmedState`, `PreparingState`, `ReadyState`, `ServedState`, `PaidState`) each override only the transitions they allow and raise `InvalidTransitionError` for all others. The `Order` class delegates state-change calls to the current state object.

**`OrderItem`**
Wraps a `MenuItem` with a quantity. Computes `line_total()` as price × quantity. `quantity` has a setter that validates the value.

**`Order`**
The central composition class. Holds a private list of `OrderItem` objects, the current `OrderState`, a list of `Discount` objects, a `TaxStrategy`, and a `TipStrategy`. Exposes clean methods for each phase of the workflow. `get_price_breakdown()` returns a structured dict with all pricing components; `print_receipt()` formats and prints that breakdown.

---

### `pricing.py`

**`Discount` (abstract base)**
Defines the `apply(subtotal) -> float` interface. All subclasses return the discount *amount* (not the reduced total), which makes chaining predictable.

**`PercentageDiscount(Discount)`**
Returns `subtotal × (pct / 100)`. Validates that percentage is between 0 and 100.

**`FixedAmountDiscount(Discount)`**
Returns the fixed amount, capped at the subtotal so the result never goes negative.

**`TaxStrategy`**
Holds a dict of category-to-rate mappings (Food = 6%, Drink = 8% by default). `compute_tax()` iterates `OrderItem` objects and calls `menu_item.get_tax_rate()` polymorphically, multiplying each item's discounted subtotal by its rate.

**`TipStrategy`**
Computes tip as a percentage of the passed-in base amount (discounted subtotal + tax).

---

### `cli.py`

**`RestaurantCLI`**
Holds the menu catalog (`dict`), an `Inventory`, and an `orders` dict. `run()` implements a REPL loop that reads commands, parses tokens, and dispatches to the appropriate `cmd_*` methods. All `cmd_*` methods wrap their logic in try/except so errors print cleanly without crashing the loop.

---

## 4. Pricing Formula and Discount Application Order

Pricing proceeds in five deterministic steps:

1. **Subtotal** — sum of `item_price × quantity` for every `OrderItem` in the order.
2. **Discounts** — percentage discounts are sorted before fixed discounts and applied in sequence. Each discount is computed on the *running* total after the previous one, so they compound correctly. The total discount amount and the resulting discounted subtotal are both recorded.
3. **Tax** — computed per-item using the polymorphic `get_tax_rate()` call (Food: 6%, Drink: 8%, Combo: weighted average). A *discount ratio* (`discounted_subtotal / subtotal`) scales each item's contribution proportionally so the tax reflects the actual amount paid per item.
4. **Tip** — applied as a percentage of `(discounted subtotal + tax)`, matching industry convention of tipping on the pre-tip total including tax.
5. **Final Total** — `discounted_subtotal + tax + tip`.

This order is consistent, documented, and verified in the demo scenario.

---

## 5. Test Plan and Results

### 5.1 Menu and Inventory Tests

| Test | Expected | Result |
|------|----------|--------|
| Add FoodItem to menu | Item appears in menu list with 6% tax | ✅ Pass |
| Add DrinkItem to menu | Item appears with 8% tax | ✅ Pass |
| Add Combo with 10% discount | Price = sum × 0.90 | ✅ Pass ($15.97 → $14.37) |
| Toggle availability off | Item shows "Unavailable"; adding to order raises ValueError | ✅ Pass |
| Set stock via Inventory | Stock stored and visible in `inv show` | ✅ Pass |
| Confirm order decrements stock | Stock counts reduced by ordered quantities | ✅ Pass |
| Confirm with insufficient stock | `ValueError` raised, order blocked | ✅ Pass |

### 5.2 Order and State Tests

| Test | Expected | Result |
|------|----------|--------|
| Created → Confirmed | Succeeds when items present and stock available | ✅ Pass |
| Confirmed → Preparing | Succeeds | ✅ Pass |
| Preparing → Ready | Succeeds | ✅ Pass |
| Ready → Served | Succeeds | ✅ Pass |
| Served → Paid | Succeeds | ✅ Pass |
| Paid → Confirm (invalid) | `InvalidTransitionError` raised | ✅ Pass |
| Created → Paid (skip states) | `InvalidTransitionError` raised | ✅ Pass |
| Add item to Confirmed order | `InvalidTransitionError` raised | ✅ Pass |
| Add then remove item; subtotal updates | Subtotal reflects only remaining items | ✅ Pass |

### 5.3 Pricing Tests

| Test | Expected | Result |
|------|----------|--------|
| Subtotal = Σ(price × qty) | $9.99×2 + $2.49×2 + $14.37×1 = $39.33 | ✅ $39.33 |
| 10% pct discount on $39.33 | $3.93 off → $35.40 | ✅ $3.93 |
| $2.00 fixed on $35.40 | $2.00 off → $33.40 | ✅ $2.00 |
| Tax on $33.40 (blended ~6.4%) | ~$2.13 | ✅ $2.13 |
| Tip 15% on ($33.40 + $2.13) = $35.53 | $5.33 | ✅ $5.33 |
| Final total | $33.40 + $2.13 + $5.33 = $40.86 | ✅ $40.86 |
| Fixed discount capped at subtotal | Discount = min(amount, subtotal) | ✅ Pass |
| Zero tip | Tip = $0.00 | ✅ Pass |

### 5.4 Receipt Test

| Test | Expected | Result |
|------|----------|--------|
| All items listed with qty and line total | Each OrderItem shown | ✅ Pass |
| Discounts listed with descriptions | Both discounts itemized | ✅ Pass |
| Tax, tip, total columns align | Formatted receipt matches breakdown dict | ✅ Pass |

---

## 6. Sample Scenario Execution Results

### Scenario Setup

| Item | ID | Price | Stock |
|------|----|-------|-------|
| Classic Burger (Food) | F01 | $9.99 | 10 |
| French Fries (Food) | F02 | $3.49 | 8 |
| Soda (Drink) | D01 | $2.49 | 20 |
| Burger Combo (Combo) | C01 | $14.37 | 5 |

Combo price = ($9.99 + $3.49 + $2.49) × 0.90 = $15.97 × 0.90 = **$14.37** ✅

### Order Items

| Item | Qty | Unit Price | Line Total |
|------|-----|-----------|------------|
| Classic Burger | 2 | $9.99 | $19.98 |
| Soda | 2 | $2.49 | $4.98 |
| Burger Combo | 1 | $14.37 | $14.37 |
| **Subtotal** | | | **$39.33** |

### Pricing Breakdown

| Step | Calculation | Amount |
|------|-------------|--------|
| Subtotal | | $39.33 |
| 10% Loyalty Discount | $39.33 × 10% | −$3.93 |
| Running after pct | | $35.40 |
| $2.00 Coupon | fixed | −$2.00 |
| Discounted Subtotal | | $33.40 |
| Tax (blended) | ~6.37% × $33.40 | $2.13 |
| Tip (15%) | 15% × $35.53 | $5.33 |
| **TOTAL** | | **$40.86** |

All calculated values match the program's output. ✅

### Status Lifecycle Output

```
Created -> Confirmed  (stock validated and decremented)
Confirmed -> Preparing
Preparing -> Ready
Ready -> Served
Served -> Paid
```

### Stock After Confirmation

| Item | Before | Ordered | After |
|------|--------|---------|-------|
| F01 Classic Burger | 10 | 2 | **8** ✅ |
| D01 Soda | 20 | 2 | **18** ✅ |
| C01 Burger Combo | 5 | 1 | **4** ✅ |
| F02 French Fries | 8 | 0 | **8** (unchanged) ✅ |

### Invalid Transition Test

Attempting `order.confirm()` on a Paid order raised:
```
InvalidTransitionError: Cannot confirm order from state 'Paid'.
```
This confirms the state machine correctly rejects illegal transitions. ✅

---

## 7. Discussion and Conclusion

### Findings

- The **State pattern** for order lifecycle proved highly effective. Each state class is small and independent; adding a new state (e.g., "Cancelled") requires only a new class and one transition method change — no conditional chains to update.
- **Polymorphism via `get_tax_rate()`** cleanly separates tax logic from the pricing engine. The `TaxStrategy` never needs to check item types; it simply calls the method and trusts the subclass.
- The **Composite pattern** in `Combo` allowed it to be treated identically to a `FoodItem` or `DrinkItem` from the `Order` perspective. The weighted-average tax rate in `Combo.get_tax_rate()` ensures tax correctness without any special casing.
- **Encapsulation** was consistently applied: all internal collections (`_items`, `_stock`, `_discounts`) are private and exposed only through validated methods, preventing accidental corruption.

### Challenges

- **Discount ordering** needed explicit documentation. Applying percentage discounts before fixed ones is a design choice, not a universal standard. This is now stated clearly in the pricing formula section.


### Possible Improvements

- **Persistence** — Save orders and inventory to JSON or SQLite so data survives between sessions.
- **Multi-order management** — Allow viewing all orders simultaneously, not just the active one.
- **Kitchen display** — A separate "kitchen view" showing all Confirmed/Preparing orders.
- **Split payments** — Support multiple payment methods per order.
- **Undo/redo** — Allow undoing the last item addition or discount.


