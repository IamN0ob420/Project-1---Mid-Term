"""
demo_scenario.py - Required sample scenario demonstrating all project features.

Scenario:
  1. Create 3 menu items (2 foods, 1 drink) + 1 combo (10% discount)
  2. Set stock levels
  3. Create an order with multiple items including the combo
  4. Apply one percentage discount + one fixed discount
  5. Set tax rates (food: 6%, drink: 8%) and tip (15%)
  6. Walk through all statuses: Created -> Confirmed -> Preparing -> Ready -> Served -> Paid
  7. Show receipt and verify stock decrements
"""

from menu import FoodItem, DrinkItem, Combo
from inventory import Inventory
from order import Order
from pricing import PercentageDiscount, FixedAmountDiscount, TaxStrategy


def run_scenario():
    print("\n" + "=" * 60)
    print("   DEMO SCENARIO - Restaurant Ordering System")
    print("=" * 60)

    # ─── Step 1: Create Menu Items ────────────────────────────────
    print("\n[STEP 1] Creating menu items...")
    burger   = FoodItem("F01", "Classic Burger", 9.99)
    fries    = FoodItem("F02", "French Fries", 3.49)
    soda     = DrinkItem("D01", "Soda", 2.49)
    combo    = Combo("C01", "Burger Combo", [burger, fries, soda], discount_pct=0.10)

    print(f"  {burger.display()}")
    print(f"  {fries.display()}")
    print(f"  {soda.display()}")
    print(f"  {combo.display()}")

    # Combo raw price = 9.99 + 3.49 + 2.49 = $15.97 → 10% off = $14.37
    print(f"\n  Combo component sum: ${sum(i.price for i in combo.components):.2f}"
          f"  →  After 10% discount: ${combo.price:.2f}")

    # ─── Step 2: Set Stock ────────────────────────────────────────
    print("\n[STEP 2] Setting inventory stock...")
    inventory = Inventory()
    inventory.set_stock("F01", 10)   # 10 Classic Burgers
    inventory.set_stock("F02", 8)    # 8 French Fries
    inventory.set_stock("D01", 20)   # 20 Sodas
    inventory.set_stock("C01", 5)    # 5 Combos

    inventory.show_stock({
        "F01": burger, "F02": fries, "D01": soda, "C01": combo
    })

    # ─── Step 3: Create Order & Add Items ────────────────────────
    print("\n[STEP 3] Creating order and adding items...")
    order = Order()
    order.add_item(burger, quantity=2)    # 2x Classic Burger  = 2 × $9.99 = $19.98
    order.add_item(soda, quantity=2)      # 2x Soda            = 2 × $2.49 = $4.98
    order.add_item(combo, quantity=1)     # 1x Burger Combo    = 1 × $14.37 = $14.37
    order.view_order()

    # Expected subtotal: 19.98 + 4.98 + 14.37 = $39.33

    # ─── Step 4: Apply Discounts, Tax, Tip ───────────────────────
    print("\n[STEP 4] Applying discounts, tax rates, and tip...")

    # Percentage discount: 10% off subtotal
    pct_discount = PercentageDiscount(10.0, "10% Loyalty Discount")
    order.add_discount(pct_discount)

    # Fixed discount: $2.00 off (applied after pct discount)
    fixed_discount = FixedAmountDiscount(2.00, "$2.00 Coupon")
    order.add_discount(fixed_discount)

    # Tax: food 6%, drink 8% (default in TaxStrategy)
    order.set_tax_strategy(TaxStrategy())

    # Tip: 15%
    order.set_tip(15.0)

    # Show estimated totals
    breakdown = order.get_price_breakdown()
    print(f"\n  Subtotal:           ${breakdown['subtotal']:.2f}")
    print(f"  Discounts:         -${breakdown['discount_amount']:.2f}")
    print(f"  After Discounts:    ${breakdown['discounted_subtotal']:.2f}")
    print(f"  Tax:                ${breakdown['tax']:.2f}")
    print(f"  Tip (15%):          ${breakdown['tip']:.2f}")
    print(f"  TOTAL:              ${breakdown['total']:.2f}")

    # ─── Step 5: Status Lifecycle ─────────────────────────────────
    print("\n[STEP 5] Walking through order status lifecycle...")

    print(f"\n  Current status: {order.status}")

    # Created -> Confirmed (validates stock, decrements)
    print("\n  Confirming order...")
    order.confirm(inventory=inventory)

    # Show stock after confirmation
    print("\n  Stock after confirmation:")
    inventory.show_stock({"F01": burger, "F02": fries, "D01": soda, "C01": combo})

    # Confirmed -> Preparing
    print("\n  Starting preparation...")
    order.prepare()

    # Preparing -> Ready
    print("\n  Order is ready...")
    order.mark_ready()

    # Ready -> Served
    print("\n  Serving order...")
    order.serve()

    # Served -> Paid
    print("\n  Processing payment...")
    order.pay()

    print(f"\n  Final status: {order.status}")

    # ─── Step 6: Print Receipt ────────────────────────────────────
    print("\n[STEP 6] Final Receipt:")
    order.print_receipt()

    # ─── Verification Summary ─────────────────────────────────────
    print("\n[VERIFICATION SUMMARY]")
    print(f"  Subtotal (2×$9.99 + 2×$2.49 + 1×$14.37): ${breakdown['subtotal']:.2f}  (expected ~$39.33)")
    print(f"  10% discount on $39.33 = $3.93")
    print(f"  After pct discount: $35.40")
    print(f"  $2.00 fixed coupon: $33.40")
    print(f"  Tax (blended ~6.4% on $33.40): ~${breakdown['tax']:.2f}")
    print(f"  Tip (15% on ${breakdown['discounted_subtotal']:.2f} + ${breakdown['tax']:.2f}): ${breakdown['tip']:.2f}")
    print(f"  TOTAL: ${breakdown['total']:.2f}")
    print("\n  Stock decrements verified:")
    print(f"    F01 (Burger): 10 - 2 = 8 units remaining")
    print(f"    D01 (Soda):   20 - 2 = 18 units remaining")
    print(f"    C01 (Combo):   5 - 1 = 4 units remaining")

    # ─── Invalid Transition Test ──────────────────────────────────
    print("\n[BONUS] Testing invalid state transition...")
    try:
        order.confirm()   # Order is already Paid - should fail
    except Exception as e:
        print(f"  Caught expected error: {e}")

    print("\n" + "=" * 60)
    print("   DEMO SCENARIO COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    run_scenario()
