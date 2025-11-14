import tkinter as tk
from tkinter import ttk

class Navbar(ttk.Frame):
    """
    --- UPDATED ---
    - Changed cart button style to 'Accent.TButton' to make it more prominent.
    - Removed emoji from cart button text for a cleaner look.
    - This is the main navigation bar for the application.
    - Uses 'Navbar.Title.TButton' style to make the logo clickable.
    - Removes the redundant 'Store' button.
    - Correctly shows/hides buttons based on user role (None, 'customer', 'admin').
    """
    def __init__(self, parent, controller):
        super().__init__(parent, style="Navbar.TFrame")
        self.controller = controller
        
        self.grid_columnconfigure(0, weight=1) # Left-aligned (Logo)
        self.grid_columnconfigure(1, weight=1) # Right-aligned (Buttons)

        # Clickable Logo Button
        self.app_name_btn = ttk.Button(
            self,
            text="Bijuli Tech",
            style="Navbar.Title.TButton", # Styled in main.py
            command=lambda: self.go_to_store()
        )
        self.app_name_btn.grid(row=0, column=0, sticky="w", padx=20, pady=10)
        
        # Right-aligned frame for user buttons
        self.right_frame = ttk.Frame(self, style="Navbar.TFrame")
        self.right_frame.grid(row=0, column=1, sticky="e", padx=20, pady=10)
        
        # --- Create all potential buttons ---
        # We will .pack() and .pack_forget() them as needed.
        
        # Customer: Cart Button
        self.cart_button = ttk.Button(
            self.right_frame,
            text="Cart (0)",               # --- UPDATED: Cleaner text
            style="Accent.TButton",      # --- UPDATED: More prominent style
            command=self.view_cart 
        )
        
        # Customer & Admin: Logout Button
        self.logout_button = ttk.Button(
            self.right_frame,
            text="Logout ⇥",
            style="Navbar.TButton",
            command=self.controller.handle_logout
        )
        
        # Logged Out: Login Button
        self.login_button = ttk.Button(
            self.right_frame,
            text="Login",
            style="Navbar.TButton",
            command=lambda: self.controller.show_frame("LoginPage")
        )
        
        # Admin: Dashboard Button
        self.admin_dashboard_button = ttk.Button(
            self.right_frame,
            text="Admin Dashboard",
            style="Navbar.TButton",
            command=lambda: self.controller.show_frame("AdminDashboard")
        )

        # Initial update based on current user (which is None at startup)
        self.update_navbar_for_role(None)

    def update_navbar_for_role(self, role):
        """
        Shows and hides navbar buttons based on the user's role.
        This is called by main.py during login/logout.
        """
        # Clear all existing buttons
        for widget in self.right_frame.winfo_children():
            widget.pack_forget()

        if role == "customer":
            self.cart_button.pack(side="left", padx=5)
            self.logout_button.pack(side="left", padx=5)
            self.update_cart_count() # Update count when logging in
        elif role == "admin":
            self.admin_dashboard_button.pack(side="left", padx=5)
            self.logout_button.pack(side="left", padx=5)
        else: # No user logged in
            self.login_button.pack(side="right", padx=5)
            self.update_cart_count(0) # Clear cart count
            
    def go_to_store(self):
        """Called when the logo is clicked."""
        # Only go to store if a user is logged in
        if self.controller.current_user:
            self.controller.show_frame("StorePage")

    def update_cart_count(self, count=None):
        """Updates the text of the cart button."""
        if count is None:
            # If no count is provided, get it from the controller
            count = self.controller.get_cart_total_quantity()
        self.cart_button.config(text=f"Cart ({count})") # --- UPDATED: Cleaner text
        
    def view_cart(self):
        """Called when the cart button is clicked."""
        self.controller.show_frame("CartPage")