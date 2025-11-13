import tkinter as tk
from tkinter import ttk
from widgets.navbar import Navbar
from widgets.quantity_spinner import QuantitySpinner

class CartPage(ttk.Frame):
    """
    --- MAJOR UPDATE ---
    - FIXED: The layout for item rows. "Quantity" and "Total" columns
      will now display correctly, resolving the bug from image_74d075.png.
    - FIXED: The crash from the quantity spinner is resolved by the new
      widgets/quantity_spinner.py file.
    - FIXED: Bound <MouseWheel> to the canvas for touchpad scrolling.
    - FIXED: KeyError: 'card' (replaced with 'white').
    - NEW: Added stock check when increasing quantity.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.fonts = controller.fonts
        self.colors = controller.colors
        
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.navbar = Navbar(self, controller)
        self.navbar.grid(row=0, column=0, sticky="nsew")
        
        container = ttk.Frame(self, padding=(40, 40))
        container.grid(row=1, column=0, sticky="nsew")
        container.columnconfigure(0, weight=3) # Cart items list
        container.columnconfigure(1, weight=1) # Order summary
        container.rowconfigure(1, weight=1)

        header = ttk.Label(container, text="Your Shopping Cart", style="Header.TLabel")
        header.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 20))

        # --- Items List ---
        items_frame_container = ttk.Frame(container, style="Card.TFrame")
        items_frame_container.grid(row=1, column=0, sticky="nsew", padx=(0, 20))
        items_frame_container.rowconfigure(0, weight=1)
        items_frame_container.columnconfigure(0, weight=1)
        
        # --- FIX: Replaced self.colors["card"] with self.colors["white"] ---
        self.canvas = tk.Canvas(items_frame_container, bg=self.colors["white"], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(items_frame_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas, style="Card.TFrame")
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        def _on_canvas_configure(event):
            self.canvas.itemconfig(self.frame_id, width=event.width)
        self.canvas.bind("<Configure>", _on_canvas_configure)

        self.frame_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        
        # This frame holds the actual item rows
        self.items_frame = ttk.Frame(self.scrollable_frame, padding=20, style="Card.TFrame")
        self.items_frame.pack(fill="x", expand=True)

        # --- Summary Frame ---
        summary_frame = ttk.Frame(container, style="Card.TFrame", padding=20)
        summary_frame.grid(row=1, column=1, sticky="nsew")
        summary_frame.rowconfigure(2, weight=1) # Push buttons to bottom
        
        summary_header = ttk.Label(summary_frame, text="Order Summary", style="Subheader.TLabel") 
        summary_header.config(background=self.colors["white"], foreground=self.colors["fg"]) 
        summary_header.pack(anchor="w", pady=(0, 20))

        self.total_label = ttk.Label(summary_frame, text="Total: $0.00", style="Subheader.TLabel")
        self.total_label.config(background=self.colors["white"], foreground=self.colors["fg"])
        self.total_label.pack(anchor="w", pady=10)
        
        # Frame to hold buttons at the bottom
        button_frame = ttk.Frame(summary_frame, style="Card.TFrame")
        button_frame.pack(side="bottom", fill="x")

        checkout_button = ttk.Button(
            button_frame,
            text="Proceed to Checkout",
            style="Accent.TButton",
            command=self.go_to_checkout
        )
        checkout_button.pack(fill="x", ipady=5, pady=(20, 10))
        
        clear_cart_button = ttk.Button(
            button_frame,
            text="Clear Cart",
            style="TButton",
            command=self.clear_cart
        )
        clear_cart_button.pack(fill="x")
        
    def _on_mousewheel(self, event):
        """Enables touchpad/mousewheel scrolling."""
        # Check if scroll region is larger than canvas height
        _ , y1, _ , y2 = self.canvas.bbox("all")
        if (y2 - y1) > self.canvas.winfo_height():
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def on_show(self, context=None):
        self.navbar.update_cart_count()
        self.load_cart_items()
        # Bind mousewheel to canvas for scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def on_hide(self):
        # Unbind mousewheel when page is hidden
        self.canvas.unbind_all("<MouseWheel>")

    def load_cart_items(self):
        # Clear old items
        for widget in self.items_frame.winfo_children():
            widget.destroy()

        cart = self.controller.cart
        if not cart:
            ttk.Label(self.items_frame, text="Your cart is empty.", style="Card.TLabel").pack(pady=20)
            self.total_label.config(text="Total: $0.00")
            return
            
        # --- FIXED: Column layout for headers ---
        header_frame = ttk.Frame(self.items_frame, style="Card.TFrame", padding=(0, 10))
        header_frame.pack(fill="x", expand=True)
        header_frame.columnconfigure(0, weight=3) # Product
        header_frame.columnconfigure(1, weight=1) # Price
        header_frame.columnconfigure(2, weight=1) # Quantity
        header_frame.columnconfigure(3, weight=1) # Total
        header_frame.columnconfigure(4, minsize=30) # Remove btn
        
        ttk.Label(header_frame, text="Product", style="Bold.Card.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(header_frame, text="Price", style="Bold.Card.TLabel").grid(row=0, column=1, sticky="w")
        ttk.Label(header_frame, text="Quantity", style="Bold.Card.TLabel").grid(row=0, column=2, sticky="w")
        ttk.Label(header_frame, text="Total", style="Bold.Card.TLabel").grid(row=0, column=3, sticky="w")
        
        ttk.Separator(self.items_frame, orient="horizontal").pack(fill="x", expand=True, pady=(5, 15))

        for product_id, item in cart.items():
            self.create_item_row(product_id, item)
            
        self.update_total()
        
    def create_item_row(self, product_id, item):
        item_frame = ttk.Frame(self.items_frame, padding=(0, 10), style="Card.TFrame")
        item_frame.pack(fill="x", expand=True)
        
        # --- FIXED: Column layout for items ---
        item_frame.columnconfigure(0, weight=3) # Product
        item_frame.columnconfigure(1, weight=1) # Price
        item_frame.columnconfigure(2, weight=1) # Quantity
        item_frame.columnconfigure(3, weight=1) # Total
        item_frame.columnconfigure(4, minsize=30) # Remove btn
        
        ttk.Label(
            item_frame, text=item['name'], wraplength=300,
            style="Bold.Card.TLabel"
        ).grid(row=0, column=0, sticky="w")

        ttk.Label(
            item_frame, text=f"${item['price']:.2f}",
            style="Card.TLabel"
        ).grid(row=0, column=1, sticky="w")

        # Create the new, fixed quantity spinner
        qty_spinner = QuantitySpinner(item_frame, self.controller)
        qty_spinner.set(item['quantity'])
        # Bind the commands *after* creating it
        qty_spinner.inc_btn.config(command=lambda pid=product_id: self.update_quantity(pid, 1))
        qty_spinner.dec_btn.config(command=lambda pid=product_id: self.update_quantity(pid, -1))
        qty_spinner.grid(row=0, column=2, sticky="w")
        
        item_total = item['price'] * item['quantity']
        ttk.Label(
            item_frame, text=f"${item_total:.2f}",
            style="Bold.Card.TLabel"
        ).grid(row=0, column=3, sticky="w")
        
        remove_btn = ttk.Button(
            item_frame, text="X", style="Link.TButton",
            command=lambda pid=product_id: self.remove_item(pid)
        )
        remove_btn.grid(row=0, column=4, sticky="e", padx=(10, 0))
        
        ttk.Separator(self.items_frame, orient="horizontal").pack(fill="x", expand=True, pady=(15, 15))

    def update_quantity(self, product_id, change):
        current_qty = self.controller.cart[product_id]['quantity']
        new_qty = current_qty + change
        
        # --- NEW: Check stock ---
        stock = self.controller.db.get_product_stock(product_id)
        if new_qty > stock:
            self.controller.show_toast(f"Only {stock} units available", style="error")
            return
        
        self.controller.update_cart_item_quantity(product_id, new_qty)
        self.load_cart_items() # Reload all items to reflect changes
        self.navbar.update_cart_count() # Update navbar count

    def remove_item(self, product_id):
        self.controller.remove_from_cart(product_id)
        self.load_cart_items()
        self.navbar.update_cart_count()

    def update_total(self):
        total = self.controller.get_cart_total_price()
        self.total_label.config(text=f"Total: NZ${total:.2f}")
        
    def clear_cart(self):
        self.controller.clear_cart()
        self.load_cart_items()
        self.navbar.update_cart_count()

    def go_to_checkout(self):
        if not self.controller.cart:
            self.controller.show_toast("Your cart is empty!", style="error")
            return

        # --- NEW: Check stock before checkout ---
        for product_id, item in self.controller.cart.items():
            stock = self.controller.db.get_product_stock(product_id)
            if item['quantity'] > stock:
                self.controller.show_toast(f"Error: Not enough stock for {item['name']}. Only {stock} left.", style="error")
                return # Stop checkout
                
        self.controller.show_frame("CheckoutPage")