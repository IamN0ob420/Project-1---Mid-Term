# Restaurant Ordering System

A command-line restaurant ordering system built in Python demonstrating OOP design patterns (encapsulation, inheritance, polymorphism, composition).

## Features

- **Menu Management** – Add food, drink, and combo items; toggle availability; update prices
- **Inventory Tracking** – Set and view stock levels; automatically decremented on order confirm
- **Order Lifecycle** – Full state machine: `Created → Confirmed → Preparing → Ready → Served → Paid`
- **Pricing Engine** – Subtotal, percentage/fixed discounts, category-based tax, configurable tip
- **Receipt Printing** – Itemized breakdown with all pricing components

## Project Structure

```
restaurant_project/
│
├── menu.py           # MenuItem, FoodItem, DrinkItem, Combo classes
├── inventory.py      # Inventory class (stock tracking)
├── order.py          # Order, OrderItem, OrderState classes
├── pricing.py        # TaxStrategy, TipStrategy, Discount classes
├── cli.py            # Interactive CLI (main entry point)
├── demo_scenario.py  # Required sample scenario (auto-run)
├── README.md
└── docs/
    └── report.md
```

## Setup

### Requirements
- Python 3.8 or later
- No external packages needed (standard library only)

### Run the Interactive CLI
```bash
python cli.py
```

### Run the Demo Scenario
```bash
python demo_scenario.py
```

## Example CLI Session

```
restaurant> menu add food F01 Burger 9.99
restaurant> menu add food F02 Fries 3.49
restaurant> menu add drink D01 Soda 2.49
restaurant> menu add combo C01 BurgerCombo F01,F02,D01 0.10
restaurant> menu list

restaurant> inv set F01 10
restaurant> inv set F02 8
restaurant> inv set D01 20
restaurant> inv set C01 5
restaurant> inv show

restaurant> order create
restaurant> order add F01 2
restaurant> order add D01 2
restaurant> order add C01 1
restaurant> order discount pct 10 Loyalty Discount
restaurant> order discount fixed 2 Coupon
restaurant> order tip 15
restaurant> order view

restaurant> order confirm
restaurant> order prepare
restaurant> order ready
restaurant> order serve
restaurant> order pay
restaurant> order receipt
```

## CLI Command Reference

| Command | Description |
|---|---|
| `menu list` | List all menu items |
| `menu add food <id> <name> <price>` | Add a food item |
| `menu add drink <id> <name> <price>` | Add a drink item |
| `menu add combo <id> <name> <id1,id2,...> [discount]` | Add a combo |
| `menu toggle <id>` | Toggle item availability |
| `menu update <id> <price>` | Update item price |
| `inv set <id> <qty>` | Set stock for item |
| `inv show` | Show all stock levels |
| `order create` | Create a new order |
| `order add <id> [qty]` | Add item to order |
| `order remove <id>` | Remove item from order |
| `order view` | View current order |
| `order discount pct <value>` | Add percentage discount |
| `order discount fixed <value>` | Add fixed $ discount |
| `order tip <pct>` | Set tip percentage |
| `order confirm` | Confirm order (checks stock) |
| `order prepare` | Mark as preparing |
| `order ready` | Mark as ready |
| `order serve` | Mark as served |
| `order pay` | Mark as paid |
| `order receipt` | Print full receipt |
| `help` | Show help menu |
| `quit` | Exit |

## Pricing Formula

```
Subtotal          = sum(item_price × quantity)
After Discounts   = Subtotal - pct_discount(Subtotal) - fixed_discount
Tax               = sum(item_subtotal × category_rate) adjusted for discount ratio
Tip               = (After Discounts + Tax) × tip_pct
Total             = After Discounts + Tax + Tip
```

Tax rates: Food = 6%, Drinks = 8%
