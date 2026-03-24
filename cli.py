"""
cli.py - Command-line interface for the Restaurant Ordering System.
Provides an interactive menu-driven CLI to manage items, orders, and pricing.
"""

from menu import FoodItem, DrinkItem, Combo
from inventory import Inventory
from order import Order, InvalidTransitionError
from pricing import PercentageDiscount, FixedAmountDiscount, TaxStrategy


class RestaurantCLI:
  

    def __init__(self):
        self._menu = {}       # {item_id: MenuItem}
        self._inventory = Inventory()
        self._orders = {}     # {order_id: Order}
        self._active_order = None  # Currently selected order

    # ─── Menu Management ─────────────────────────────────────────────────────

    def cmd_menu_add_food(self, item_id, name, price, category="Food"):
        """Add a FoodItem to the menu."""
        price = float(price)
        item = FoodItem(item_id, name, price, category)
        self._menu[item_id] = item
        print(f"  [Menu] Added food item: {item.display()}")

    def cmd_menu_add_drink(self, item_id, name, price, category="Drink"):
        """Add a DrinkItem to the menu."""
        price = float(price)
        item = DrinkItem(item_id, name, price, category)
        self._menu[item_id] = item
        print(f"  [Menu] Added drink item: {item.display()}")

    def cmd_menu_add_combo(self, item_id, name, component_ids, discount_pct=0.10):
        """Add a Combo to the menu using existing item IDs."""
        components = []
        for cid in component_ids:
            if cid not in self._menu:
                print(f"  [Error] Item ID '{cid}' not found in menu.")
                return
            components.append(self._menu[cid])
        combo = Combo(item_id, name, components, float(discount_pct))
        self._menu[item_id] = combo
        print(f"  [Menu] Added combo: {combo.display()}")

    def cmd_menu_list(self):
        """List all menu items."""
        print("\n--- Menu ---")
        if not self._menu:
            print("  (No items in menu.)")
            return
        for item in self._menu.values():
            print(f"  {item.display()}")
        print("------------")

    def cmd_menu_toggle(self, item_id):
        """Toggle availability of a menu item."""
        if item_id not in self._menu:
            print(f"  [Error] Item '{item_id}' not found.")
            return
        self._menu[item_id].toggle_availability()
        status = "Available" if self._menu[item_id].available else "Unavailable"
        print(f"  [Menu] '{self._menu[item_id].name}' is now {status}.")

    def cmd_menu_update_price(self, item_id, new_price):
        """Update price of a menu item."""
        if item_id not in self._menu:
            print(f"  [Error] Item '{item_id}' not found.")
            return
        self._menu[item_id]._price = float(new_price)
        print(f"  [Menu] Updated '{self._menu[item_id].name}' price to ${float(new_price):.2f}.")

    # ─── Inventory Management ────────────────────────────────────────────────

    def cmd_inventory_set(self, item_id, quantity):
        """Set stock for an item."""
        if item_id not in self._menu:
            print(f"  [Warning] Item '{item_id}' not in menu, but stock set anyway.")
        self._inventory.set_stock(item_id, int(quantity))

    def cmd_inventory_show(self):
        """Display all stock levels."""
        self._inventory.show_stock(menu_items=self._menu)

    # ─── Order Management ────────────────────────────────────────────────────

    def cmd_order_create(self):
        """Create a new order and set it as active."""
        order = Order()
        self._orders[order.order_id] = order
        self._active_order = order
        print(f"  [CLI] Active order set to Order #{order.order_id}.")
        return order

    def cmd_order_select(self, order_id):
        """Select an existing order as the active order."""
        oid = int(order_id)
        if oid not in self._orders:
            print(f"  [Error] Order #{oid} not found.")
            return
        self._active_order = self._orders[oid]
        print(f"  [CLI] Active order switched to Order #{oid}.")

    def _get_active_order(self) -> Order:
        if self._active_order is None:
            print("  [Error] No active order. Use 'order create' first.")
            return None
        return self._active_order

    def cmd_order_add(self, item_id, quantity=1):
        """Add item to active order."""
        order = self._get_active_order()
        if order is None:
            return
        if item_id not in self._menu:
            print(f"  [Error] Item '{item_id}' not found in menu.")
            return
        try:
            order.add_item(self._menu[item_id], int(quantity))
        except (ValueError, InvalidTransitionError) as e:
            print(f"  [Error] {e}")

    def cmd_order_remove(self, item_id):
        """Remove item from active order."""
        order = self._get_active_order()
        if order is None:
            return
        try:
            order.remove_item(item_id)
        except (ValueError, InvalidTransitionError) as e:
            print(f"  [Error] {e}")

    def cmd_order_view(self):
        """View active order."""
        order = self._get_active_order()
        if order:
            order.view_order()

    def cmd_order_add_discount(self, dtype, value, description=None):
        """
        Add a discount to the active order.
        dtype: 'pct' or 'fixed'
        value: float
        """
        order = self._get_active_order()
        if order is None:
            return
        val = float(value)
        try:
            if dtype == "pct":
                d = PercentageDiscount(val, description)
            elif dtype == "fixed":
                d = FixedAmountDiscount(val, description)
            else:
                print(f"  [Error] Unknown discount type '{dtype}'. Use 'pct' or 'fixed'.")
                return
            order.add_discount(d)
        except ValueError as e:
            print(f"  [Error] {e}")

    def cmd_order_set_tip(self, percentage):
        """Set tip percentage on active order."""
        order = self._get_active_order()
        if order is None:
            return
        try:
            order.set_tip(float(percentage))
        except ValueError as e:
            print(f"  [Error] {e}")

    def cmd_order_confirm(self):
        """Confirm active order (validates and decrements stock)."""
        order = self._get_active_order()
        if order is None:
            return
        try:
            order.confirm(inventory=self._inventory)
        except (ValueError, InvalidTransitionError) as e:
            print(f"  [Error] {e}")

    def cmd_order_prepare(self):
        order = self._get_active_order()
        if order:
            try:
                order.prepare()
            except InvalidTransitionError as e:
                print(f"  [Error] {e}")

    def cmd_order_ready(self):
        order = self._get_active_order()
        if order:
            try:
                order.mark_ready()
            except InvalidTransitionError as e:
                print(f"  [Error] {e}")

    def cmd_order_serve(self):
        order = self._get_active_order()
        if order:
            try:
                order.serve()
            except InvalidTransitionError as e:
                print(f"  [Error] {e}")

    def cmd_order_pay(self):
        order = self._get_active_order()
        if order:
            try:
                order.pay()
            except InvalidTransitionError as e:
                print(f"  [Error] {e}")

    def cmd_order_receipt(self):
        """Print receipt for active order."""
        order = self._get_active_order()
        if order:
            order.print_receipt()

    # ─── Interactive Loop ────────────────────────────────────────────────────

    HELP_TEXT = """
╔══════════════════════════════════════════════════════╗
║          RESTAURANT ORDERING SYSTEM - HELP           ║
╠══════════════════════════════════════════════════════╣
║  MENU COMMANDS                                       ║
║  menu list                                           ║
║  menu add food  <id> <name> <price>                  ║
║  menu add drink <id> <name> <price>                  ║
║  menu add combo <id> <name> <id1,id2,...> [discount] ║
║  menu toggle <id>                                    ║
║  menu update <id> <new_price>                        ║
╠══════════════════════════════════════════════════════╣
║  INVENTORY COMMANDS                                  ║
║  inv set <item_id> <quantity>                        ║
║  inv show                                            ║
╠══════════════════════════════════════════════════════╣
║  ORDER COMMANDS                                      ║
║  order create                                        ║
║  order select <order_id>                             ║
║  order add <item_id> [qty]                           ║
║  order remove <item_id>                              ║
║  order view                                          ║
║  order discount pct <value> [description]            ║
║  order discount fixed <value> [description]          ║
║  order tip <percentage>                              ║
║  order confirm                                       ║
║  order prepare                                       ║
║  order ready                                         ║
║  order serve                                         ║
║  order pay                                           ║
║  order receipt                                       ║
╠══════════════════════════════════════════════════════╣
║  OTHER                                               ║
║  help    - Show this menu                            ║
║  quit    - Exit                                      ║
╚══════════════════════════════════════════════════════╝
"""

    def run(self):
        """Start the interactive CLI loop."""
        print("\n╔══════════════════════════════════════╗")
        print("║   RESTAURANT ORDERING SYSTEM v1.0    ║")
        print("╚══════════════════════════════════════╝")
        print("Type 'help' for a list of commands.\n")

        while True:
            try:
                raw = input("restaurant> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                break

            if not raw:
                continue

            parts = raw.split()
            cmd = parts[0].lower()

            try:
                # --- Quit ---
                if cmd in ("quit", "exit", "q"):
                    print("Goodbye!")
                    break

                # --- Help ---
                elif cmd == "help":
                    print(self.HELP_TEXT)

                # --- Menu ---
                elif cmd == "menu":
                    if len(parts) < 2:
                        print("  Usage: menu [list|add|toggle|update]")
                    elif parts[1] == "list":
                        self.cmd_menu_list()
                    elif parts[1] == "add" and len(parts) >= 3:
                        kind = parts[2]
                        if kind == "food" and len(parts) >= 6:
                            self.cmd_menu_add_food(parts[3], parts[4], parts[5])
                        elif kind == "drink" and len(parts) >= 6:
                            self.cmd_menu_add_drink(parts[3], parts[4], parts[5])
                        elif kind == "combo" and len(parts) >= 6:
                            ids = parts[5].split(",")
                            disc = float(parts[6]) if len(parts) >= 7 else 0.10
                            self.cmd_menu_add_combo(parts[3], parts[4], ids, disc)
                        else:
                            print("  Usage: menu add food/drink/combo <id> <name> <price_or_ids> [discount]")
                    elif parts[1] == "toggle" and len(parts) >= 3:
                        self.cmd_menu_toggle(parts[2])
                    elif parts[1] == "update" and len(parts) >= 4:
                        self.cmd_menu_update_price(parts[2], parts[3])
                    else:
                        print("  Unknown menu command.")

                # --- Inventory ---
                elif cmd == "inv":
                    if len(parts) < 2:
                        print("  Usage: inv [set|show]")
                    elif parts[1] == "set" and len(parts) >= 4:
                        self.cmd_inventory_set(parts[2], parts[3])
                    elif parts[1] == "show":
                        self.cmd_inventory_show()
                    else:
                        print("  Usage: inv set <item_id> <qty> | inv show")

                # --- Order ---
                elif cmd == "order":
                    if len(parts) < 2:
                        print("  Usage: order [create|add|remove|view|confirm|prepare|ready|serve|pay|receipt|tip|discount]")
                    elif parts[1] == "create":
                        self.cmd_order_create()
                    elif parts[1] == "select" and len(parts) >= 3:
                        self.cmd_order_select(parts[2])
                    elif parts[1] == "add" and len(parts) >= 3:
                        qty = int(parts[3]) if len(parts) >= 4 else 1
                        self.cmd_order_add(parts[2], qty)
                    elif parts[1] == "remove" and len(parts) >= 3:
                        self.cmd_order_remove(parts[2])
                    elif parts[1] == "view":
                        self.cmd_order_view()
                    elif parts[1] == "discount" and len(parts) >= 4:
                        desc = " ".join(parts[4:]) if len(parts) >= 5 else None
                        self.cmd_order_add_discount(parts[2], parts[3], desc)
                    elif parts[1] == "tip" and len(parts) >= 3:
                        self.cmd_order_set_tip(parts[2])
                    elif parts[1] == "confirm":
                        self.cmd_order_confirm()
                    elif parts[1] == "prepare":
                        self.cmd_order_prepare()
                    elif parts[1] == "ready":
                        self.cmd_order_ready()
                    elif parts[1] == "serve":
                        self.cmd_order_serve()
                    elif parts[1] == "pay":
                        self.cmd_order_pay()
                    elif parts[1] == "receipt":
                        self.cmd_order_receipt()
                    else:
                        print("  Unknown order command.")

                else:
                    print(f"  Unknown command: '{cmd}'. Type 'help' for options.")

            except Exception as e:
                print(f"  [Error] {e}")


# ─── Entry Point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    cli = RestaurantCLI()
    cli.run()
