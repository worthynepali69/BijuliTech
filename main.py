import tkinter as tk
from tkinter import ttk, font, messagebox
import threading
import time

# Import your page modules
from pages.login_page import LoginPage
from pages.store_page import StorePage
from pages.product_detail_page import ProductDetailPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.receipt_page import ReceiptPage
from pages.admin_dashboard import AdminDashboard
from pages.forgot_password import ForgotPasswordPage

# Import database and widgets
from db.database import Database
from widgets.toast import Toast

class BijuliTechApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Bijuli Tech E-commerce")
        self.geometry("1400x900") # Start with a large window
        self.minsize(1200, 800) # Set a minimum size
        self.option_add('*tearOff', False) # Disable tear-off for menus

        self.db = Database()
        self.cart = {} # {product_id: {'name': str, 'price': float, 'quantity': int}}
        self.current_user = None # {'username': str, 'role': str}
        self.current_order_id = None # To store the latest order ID for the receipt

        self.fonts = {
            "title": font.Font(family="Arial", size=24, weight="bold"),
            "header": font.Font(family="Arial", size=18, weight="bold"),
            "subheader": font.Font(family="Arial", size=14, weight="bold"),
            "body_bold": font.Font(family="Arial", size=12, weight="bold"),
            "body": font.Font(family="Arial", size=12),
            "small": font.Font(family="Arial", size=10),
            "small_bold": font.Font(family="Arial", size=10, weight="bold")
        }
        
        self.colors = {
            "primary": "#007bff",   # A friendly blue
            "accent": "#28a745",    # Green for success/add
            "bg": "#ffffff",        # --- NEW: White background ---
            "fg": "#343a40",        # Dark text
            "text_light": "#6c757d", # Lighter grey text
            "white": "#ffffff",
            "border": "#dee2e6",    # Light grey border
            "error": "#dc3545",     # Red for errors
            "warning": "#ffc107",   # Yellow for warnings
            "blue_bg": "#007bff",   # For the new login panel
            "blue_fg": "#ffffff"    # For text on the blue panel
        }

        self.setup_styles()

        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (LoginPage, StorePage, ProductDetailPage, CartPage, CheckoutPage, ReceiptPage, AdminDashboard, ForgotPasswordPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.toast = Toast(self)
        
        self.show_frame("LoginPage")

    def setup_styles(self):
        style = ttk.Style(self)
        style.theme_use('clam') 

        # --- NEW THEME: White and Blue ---
        style.configure("TFrame", background=self.colors["white"])
        style.configure("TLabel", background=self.colors["white"], foreground=self.colors["fg"], font=self.fonts["body"])
        style.configure("Header.TLabel", font=self.fonts["title"], foreground=self.colors["primary"], background=self.colors["white"])
        style.configure("Subheader.TLabel", font=self.fonts["header"], foreground=self.colors["fg"], background=self.colors["white"])
        style.configure("Error.TLabel", font=self.fonts["body"], foreground=self.colors["error"], background=self.colors["white"])
        style.configure("TEntry", fieldbackground=self.colors["white"], bordercolor=self.colors["border"], foreground=self.colors["fg"], font=self.fonts["body"])
        style.configure("TText", fieldbackground=self.colors["white"], bordercolor=self.colors["border"], foreground=self.colors["fg"], font=self.fonts["body"])
        style.configure("TCombobox", fieldbackground=self.colors["white"], bordercolor=self.colors["border"], foreground=self.colors["fg"], font=self.fonts["body"])

        # --- NEW: Styles for Login Page ---
        style.configure("Blue.TFrame", background=self.colors["blue_bg"])
        style.configure("Blue.TLabel", background=self.colors["blue_bg"], foreground=self.colors["blue_fg"], font=self.fonts["body"])
        style.configure("Header.Blue.TLabel", background=self.colors["blue_bg"], foreground=self.colors["blue_fg"], font=self.fonts["title"])
        style.configure("Subheader.Blue.TLabel", background=self.colors["blue_bg"], foreground=self.colors["blue_fg"], font=self.fonts["subheader"])
        style.configure("White.TButton", background=self.colors["white"], foreground=self.colors["primary"], font=self.fonts["body_bold"], padding=10)
        style.map("White.TButton",
                  background=[('active', self.colors["border"]), ('pressed', self.colors["border"])],
                  foreground=[('active', self.colors["primary"])])

        # Buttons
        style.configure("TButton", 
                        font=self.fonts["body_bold"], 
                        foreground=self.colors["fg"], 
                        background=self.colors["white"],
                        bordercolor=self.colors["border"],
                        focusthickness=0,
                        focuscolor='none',
                        padding=10)
        style.map("TButton", 
                  background=[('active', self.colors["bg"]), ('pressed', self.colors["bg"])],
                  foreground=[('active', self.colors["primary"])]) 

        style.configure("Accent.TButton", 
                        background=self.colors["primary"], 
                        foreground=self.colors["white"], 
                        bordercolor=self.colors["primary"],
                        font=self.fonts["body_bold"],
                        padding=10)
        style.map("Accent.TButton", 
                  background=[('active', self.colors["primary"]), ('pressed', self.colors["primary"])],
                  foreground=[('active', self.colors["white"])]) 
        
        style.configure("Warning.TButton", 
                        background=self.colors["error"], 
                        foreground=self.colors["white"], 
                        bordercolor=self.colors["error"],
                        font=self.fonts["body_bold"],
                        padding=10)
        style.map("Warning.TButton", 
                  background=[('active', self.colors["error"]), ('pressed', self.colors["error"])],
                  foreground=[('active', self.colors["white"])])
                  
        style.configure("Link.TButton", 
                        background=self.colors["white"], 
                        foreground=self.colors["text_light"],
                        bordercolor=self.colors["white"],
                        focusthickness=0,
                        focuscolor='none',
                        font=self.fonts["small"],
                        padding=(5,2)) 
        style.map("Link.TButton",
                  foreground=[('active', self.colors["primary"]), ('pressed', self.colors["primary"])],
                  background=[('active', self.colors["white"]), ('pressed', self.colors["white"])])

        # Navbar
        style.configure("Navbar.TFrame", background=self.colors["white"], borderwidth=1, relief="solid", bordercolor=self.colors["border"])
        style.configure("Navbar.Title.TButton", 
                        background=self.colors["white"], 
                        foreground=self.colors["primary"], 
                        font=self.fonts["title"],
                        bordercolor=self.colors["white"],
                        focusthickness=0,
                        focuscolor='none')
        style.map("Navbar.Title.TButton", 
                  background=[('active', self.colors["white"]), ('pressed', self.colors["white"])], 
                  foreground=[('active', self.colors["primary"])])
        
        style.configure("Navbar.TButton", 
                        background=self.colors["white"], 
                        foreground=self.colors["fg"],
                        bordercolor=self.colors["white"], 
                        font=self.fonts["body"],
                        focusthickness=0,
                        focuscolor='none',
                        padding=10)
        style.map("Navbar.TButton", 
                  background=[('active', self.colors["white"]), ('pressed', self.colors["white"])],
                  foreground=[('active', self.colors["primary"])]) 

        # Card frames
        style.configure("Card.TFrame", 
                        background=self.colors["white"], 
                        borderwidth=1, 
                        relief="solid", 
                        bordercolor=self.colors["border"])
        style.configure("Card.TLabel", background=self.colors["white"], foreground=self.colors["fg"], font=self.fonts["body"])
        style.configure("Bold.Card.TLabel", background=self.colors["white"], foreground=self.colors["fg"], font=self.fonts["body_bold"])
        style.configure("Light.Card.TLabel", background=self.colors["white"], foreground=self.colors["text_light"], font=self.fonts["small"])
        style.configure("Header.Card.TLabel", background=self.colors["white"], foreground=self.colors["primary"], font=self.fonts["title"])
        style.configure("Subheader.Light.Card.TLabel", background=self.colors["white"], foreground=self.colors["text_light"], font=self.fonts["subheader"])
        style.configure("Price.Card.TLabel", background=self.colors["white"], foreground=self.colors["fg"], font=self.fonts["header"]) 
        
        style.configure("Stock.TLabel", background=self.colors["white"], font=self.fonts["small_bold"])
        style.configure("InStock.Stock.TLabel", foreground=self.colors["accent"])
        style.configure("OutOfStock.Stock.TLabel", foreground=self.colors["error"])

        # --- NEW: Styles for Discount/Total in Checkout ---
        style.configure("Summary.TLabel", background=self.colors["white"], foreground=self.colors["fg"], font=self.fonts["body"])
        style.configure("Summary.Bold.TLabel", background=self.colors["white"], foreground=self.colors["fg"], font=self.fonts["body_bold"])
        style.configure("Summary.Total.TLabel", background=self.colors["white"], foreground=self.colors["fg"], font=self.fonts["subheader"])
        style.configure("Discount.TLabel", background=self.colors["white"], foreground=self.colors["accent"], font=self.fonts["body_bold"])
        style.configure("InvalidDiscount.TLabel", background=self.colors["white"], foreground=self.colors["error"], font=self.fonts["body_bold"])
        
        # Quantity Spinner
        style.configure("QuantitySpinner.TFrame", background=self.colors["white"], borderwidth=1, relief="solid", bordercolor=self.colors["border"])
        style.configure("QuantitySpinner.TButton", 
                        background=self.colors["bg"], 
                        foreground=self.colors["fg"], 
                        font=self.fonts["small_bold"],
                        padding=5,
                        focusthickness=0,
                        focuscolor='none',
                        borderwidth=0) 
        style.map("QuantitySpinner.TButton", 
                  background=[('active', self.colors["border"]), ('pressed', self.colors["primary"])],
                  foreground=[('active', self.colors["primary"]), ('pressed', self.colors["white"])])
        style.configure("QuantitySpinner.TLabel", background=self.colors["white"], foreground=self.colors["fg"], font=self.fonts["body_bold"])

        # Receipt Page
        style.configure("Receipt.TLabel", background=self.colors["white"], foreground=self.colors["fg"], font=self.fonts["body"])
        style.configure("Receipt.Header.TLabel", background=self.colors["white"], foreground=self.colors["primary"], font=self.fonts["header"])
        style.configure("Receipt.Bold.TLabel", background=self.colors["white"], foreground=self.colors["fg"], font=self.fonts["body_bold"])
        style.configure("Receipt.ItemHeader.TLabel", background=self.colors["bg"], foreground=self.colors["fg"], font=self.fonts["body_bold"], padding=(5,5))
        style.configure("Receipt.Item.TLabel", background=self.colors["white"], foreground=self.colors["fg"], font=self.fonts["body"], padding=(5,2))
        style.configure("Receipt.Total.TLabel", background=self.colors["primary"], foreground=self.colors["white"], font=self.fonts["subheader"], padding=(10,10))
        
        # Admin Dashboard
        style.configure("TNotebook", background=self.colors["white"], borderwidth=0)
        style.configure("TNotebook.Tab", 
                        font=self.fonts["body_bold"], 
                        padding=(10, 5), 
                        background=self.colors["bg"], 
                        foreground=self.colors["text_light"],
                        bordercolor=self.colors["border"])
        style.map("TNotebook.Tab",
                  background=[("selected", self.colors["white"]), ("active", self.colors["border"])],
                  foreground=[("selected", self.colors["primary"])])


    def show_frame(self, page_name, context=None):
        frame = self.frames[page_name]
        frame.tkraise()
        if hasattr(frame, "on_show"):
            frame.on_show(context)
        for name, other_frame in self.frames.items():
            if name != page_name and hasattr(other_frame, "on_hide"):
                other_frame.on_hide()
        
    def show_toast(self, message, style="info"):
        self.toast.show(message, style)

    # --- Cart Management ---
    def add_to_cart(self, product_id, name, price, quantity=1):
        if product_id in self.cart:
            self.cart[product_id]['quantity'] += quantity
        else:
            self.cart[product_id] = {'name': name, 'price': price, 'quantity': quantity}
        self.show_toast(f"Added {quantity} x {name} to cart!", style="success")
        
        # Update cart count on all navbars
        for page in self.frames.values():
            if hasattr(page, 'navbar'):
                page.navbar.update_cart_count()

    def update_cart_item_quantity(self, product_id, quantity):
        if product_id in self.cart:
            if quantity <= 0:
                del self.cart[product_id]
            else:
                self.cart[product_id]['quantity'] = quantity
            self.show_toast("Cart updated!", style="info")
        
    def remove_from_cart(self, product_id):
        if product_id in self.cart:
            del self.cart[product_id]
            self.show_toast("Item removed from cart!", style="info")

    def get_cart_items(self):
        return list(self.cart.values())

    def get_cart_total_quantity(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_cart_total_price(self):
        return sum(item['price'] * item['quantity'] for item in self.cart.values())

    def clear_cart(self):
        self.cart = {}
        self.show_toast("Cart cleared!", style="info")

    # --- User Session Management ---
    def handle_login(self, username, role):
        self.current_user = {'username': username, 'role': role}
        self.show_toast(f"Welcome, {username}!", style="success")
        
        for page in self.frames.values():
            if hasattr(page, 'navbar'):
                page.navbar.update_navbar_for_role(role)
        
        if role == "admin":
            self.show_frame("AdminDashboard")
        else:
            self.show_frame("StorePage")

    def handle_logout(self):
        self.current_user = None
        self.cart = {} 
        self.show_toast("You have been logged out.", style="info")
        
        for page in self.frames.values():
            if hasattr(page, 'navbar'):
                page.navbar.update_navbar_for_role(None)

        self.show_frame("LoginPage")

if __name__ == "__main__":
    app = BijuliTechApp()
    app.mainloop()