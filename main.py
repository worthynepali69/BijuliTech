import tkinter as tk
from tkinter import ttk, messagebox
from database import Database

try:
    from login_system import LoginPage
    from sales_portal import StorePage
    from shopping_cart import CartPage
    from checkout_process import CheckoutPage, ReceiptPage
    from product_manager import ProductManager
    from customer_manager import CustomerManager
    from order_manager import OrderManager 
except ImportError as e:
    print(f"Warning: {e}. Ensure all application files are present.")

class POSApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Bijuli Tech POS System (SOFT605)")
        self.geometry("1024x768")
        
        self.db = Database()
        self.current_user = None 
        self.cart = {} 
        self.current_order_id = None 

        self.configure_styles()
        
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self.show_login()

    def configure_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TLabel", font=("Helvetica", 12), padding=5)
        style.configure("TButton", font=("Helvetica", 11), padding=5)
        style.configure("Header.TLabel", font=("Helvetica", 18, "bold"), foreground="#333")
        style.configure("Error.TLabel", foreground="red")

    def show_login(self):
        self.frames = {}
        for widget in self.container.winfo_children():
            widget.destroy()
        frame = LoginPage(parent=self.container, controller=self)
        self.frames['LoginPage'] = frame
        frame.grid(row=0, column=0, sticky="nsew")
        frame.tkraise()

    def on_login_success(self, user):
        self.current_user = user
        self.load_app_frames()
        if user['role'] == 'staff':
            self.show_frame("StorePage")
        elif user['role'] == 'admin':
            self.show_frame("AdminMenu")

    def load_app_frames(self):
        try:
            pages = (StorePage, CartPage, CheckoutPage, ReceiptPage, 
                     AdminMenu, ProductManager, CustomerManager, OrderManager)
            for F in pages:
                page_name = F.__name__
                frame = F(parent=self.container, controller=self)
                self.frames[page_name] = frame
                frame.grid(row=0, column=0, sticky="nsew")
        except NameError as e:
            print(f"Error loading frames: {e}")

    def show_frame(self, page_name):
        if page_name in self.frames:
            frame = self.frames[page_name]
            frame.tkraise()
            if hasattr(frame, 'refresh'):
                frame.refresh()
        else:
            messagebox.showerror("Error", f"Page {page_name} not found.")

    def logout(self, current_frame=None):
        self.current_user = None
        self.cart = {}
        self.show_login()

class AdminMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#f0f0f0")
        center_frame = tk.Frame(self, bg="white", padx=40, pady=40, relief="raised", bd=1)
        center_frame.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(center_frame, text="Admin Dashboard", font=("Helvetica", 22, "bold"), 
                 bg="white", fg="#333").pack(pady=(0, 30))
        btn_style = {"font": ("Helvetica", 12), "width": 25, "pady": 10}
        tk.Button(center_frame, text="Enter Store (POS Mode)", bg="#4CAF50", fg="white", **btn_style,
                  command=lambda: controller.show_frame("StorePage")).pack(pady=10)
        tk.Button(center_frame, text="Manage Products", bg="#2196F3", fg="white", **btn_style,
                  command=lambda: controller.show_frame("ProductManager")).pack(pady=10)
        tk.Button(center_frame, text="Manage Customers", bg="#FF9800", fg="white", **btn_style,
                  command=lambda: controller.show_frame("CustomerManager")).pack(pady=10)
        tk.Button(center_frame, text="Order History Log", bg="#607D8B", fg="white", **btn_style,
                  command=lambda: controller.show_frame("OrderManager")).pack(pady=10)
        tk.Button(center_frame, text="Logout", bg="#F44336", fg="white", **btn_style,
                  command=lambda: controller.logout(self)).pack(pady=(30, 0))
        
    def refresh(self):
        pass

if __name__ == "__main__":
    app = POSApp()
    app.mainloop()