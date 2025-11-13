import tkinter as tk
from tkinter import ttk, messagebox
from widgets.navbar import Navbar

class CheckoutPage(ttk.Frame):
    """
    --- FULLY UPDATED ---
    - FIXED: Duplicate order bug (image_74d7f8.png)
    - Added a 'self.processing_order' lock to prevent
      multiple clicks on the "Place Order" button.
      
    - FIXED: SyntaxError "self.navbar..update_cart_count()"
    - FIXED: SyntaxError "pady=5." (missing parenthesis)
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.fonts = controller.fonts
        self.colors = controller.colors
        
        self.processing_order = False # Lock to prevent duplicate orders
        
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.navbar = Navbar(self, controller)
        self.navbar.grid(row=0, column=0, sticky="nsew")

        # Main container
        container = ttk.Frame(self, padding=(40, 40))
        container.grid(row=1, column=0, sticky="nsew")
        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)
        
        header = ttk.Label(container, text="Checkout", style="Header.TLabel")
        header.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 20))
        
        self.form_vars = {
            "name": tk.StringVar(), "email": tk.StringVar(),
            "phone": tk.StringVar(), "address": tk.StringVar(),
            "country": tk.StringVar(value="New Zealand")
        }
        
        # --- Shipping Details Form ---
        shipping_frame = ttk.Labelframe(container, text="Shipping Details", padding=20)
        shipping_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 20))
        
        self.create_form_entry(shipping_frame, "Name:", self.form_vars["name"])
        self.create_form_entry(shipping_frame, "Email:", self.form_vars["email"])
        self.create_form_entry(shipping_frame, "Phone:", self.form_vars["phone"])
        self.create_form_entry(shipping_frame, "Address:", self.form_vars["address"])
        self.create_form_entry(shipping_frame, "Country:", self.form_vars["country"])

        # --- Payment Simulation Form ---
        payment_frame = ttk.Labelframe(container, text="Payment Details", padding=20)
        payment_frame.grid(row=1, column=1, sticky="nsew")
        
        self.card_vars = {
            "number": tk.StringVar(value="1234 5678 9101 1121"),
            "expiry": tk.StringVar(value="12/26"),
            "cvc": tk.StringVar(value="123")
        }
        
        self.create_form_entry(payment_frame, "Card Number:", self.card_vars["number"])
        self.create_form_entry(payment_frame, "Expiry (MM/YY):", self.card_vars["expiry"])
        self.create_form_entry(payment_frame, "CVC:", self.card_vars["cvc"])
        
        # --- Place Order Button ---
        self.place_order_btn = ttk.Button(
            container,
            text="Confirm Transaction & Place Order",
            style="Accent.TButton",
            command=self.process_order
        )
        self.place_order_btn.grid(row=3, column=0, columnspan=2, sticky="w", ipady=5, pady=30)

    def create_form_entry(self, parent, label, string_var):
        """Helper function to create a labeled entry row."""
        row_frame = ttk.Frame(parent, style="Card.TFrame")
        
        # --- SYNTAX ERROR FIX: Added missing parenthesis ---
        row_frame.pack(fill="x", expand=True, pady=5)
        # --- END OF FIX ---
        
        ttk.Label(row_frame, text=label, width=15, style="Card.TLabel").pack(side="left")
        entry = ttk.Entry(row_frame, textvariable=string_var, font=self.fonts["body"])
        entry.pack(fill="x", expand=True, side="left", padx=5)

    def on_show(self, context=None):
        # --- SYNTAX ERROR FIX: Removed extra dot ---
        self.navbar.update_cart_count()
        # --- END OF FIX ---
        
        self.processing_order = False # Reset lock when page is shown
        self.place_order_btn.config(state="normal") # Ensure button is enabled

        # Check if cart is empty, if so, redirect
        if not self.controller.cart:
            self.controller.show_toast("Your cart is empty!", style="error")
            self.controller.show_frame("StorePage")
            return
            
        # Pre-fill form with customer data
        username = self.controller.current_user['username']
        customer = self.controller.db.fetch_customer_by_username(username)
        if customer:
            self.form_vars["name"].set(customer['name'] or "")
            self.form_vars["email"].set(customer['email'] or "")
            self.form_vars["phone"].set(customer['phone'] or "")
            self.form_vars["address"].set(customer['address'] or "")
            self.form_vars["country"].set(customer['country'] or "New Zealand")

    def process_order(self):
        # --- FIX: Prevent duplicate orders ---
        if self.processing_order:
            self.controller.show_toast("Processing... Please wait.", style="warning")
            return # Already processing, do nothing
        self.processing_order = True
        self.place_order_btn.config(state="disabled") # Disable button
        # --- END OF FIX ---
        
        try:
            # 1. Validate form data
            customer_details = {key: var.get() for key, var in self.form_vars.items()}
            for key, value in customer_details.items():
                if not value:
                    self.controller.show_toast(f"'{key}' is a required field", style="error")
                    self.processing_order = False # Reset lock
                    self.place_order_btn.config(state="normal")
                    return
                    
            for key, var in self.card_vars.items():
                if not var.get():
                    self.controller.show_toast(f"'{key}' is a required payment field", style="error")
                    self.processing_order = False # Reset lock
                    self.place_order_btn.config(state="normal")
                    return

            username = self.controller.current_user['username']
            cart = self.controller.cart
            
            # 2. Attempt to create order (this now checks stock)
            order_id = self.controller.db.create_order(username, cart, customer_details)
            
            # 3. Handle success or failure
            if order_id:
                # Success!
                self.controller.show_toast(f"Order #{order_id} placed successfully!")
                self.controller.current_order_id = order_id # Store for receipt page
                self.controller.clear_cart()
                self.controller.show_frame("ReceiptPage", context=order_id)
            else:
                # Failure (likely stock issue)
                self.controller.show_toast("Error placing order. Stock may be low.", style="error")
                self.processing_order = False # Reset lock
                self.place_order_btn.config(state="normal")
                self.controller.show_frame("CartPage") # Show cart so user can fix

        except Exception as e:
            messagebox.showerror("Order Error", f"An unexpected error occurred: {e}")
            self.processing_order = False # Reset lock
            self.place_order_btn.config(state="normal")