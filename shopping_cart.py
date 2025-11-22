import tkinter as tk
from tkinter import ttk, messagebox

class CartPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        tk.Label(self, text="Shopping Cart", font=("Helvetica", 18, "bold")).pack(pady=20)
        self.list_frame = tk.Frame(self)
        self.list_frame.pack(fill="both", expand=True, padx=50)
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="← Back to Store", command=lambda: controller.show_frame("StorePage"), font=("Helvetica", 10)).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Proceed to Checkout →", command=lambda: controller.show_frame("CheckoutPage"), bg="#4CAF50", fg="white", font=("Helvetica", 11, "bold")).pack(side="left", padx=10)

    def refresh(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        if not self.controller.cart:
            tk.Label(self.list_frame, text="Your cart is empty.", font=("Helvetica", 14), fg="#666").pack(pady=50)
            return
        products = self.controller.db.get_all_products()
        total_val = 0.0
        headers = ["Product", "Price", "Quantity", "Subtotal", "Action"]
        for i in range(5):
            self.list_frame.columnconfigure(i, weight=1)
        for i, h in enumerate(headers):
            tk.Label(self.list_frame, text=h, font=("Helvetica", 10, "bold"), bg="#ddd", padx=10, pady=5).grid(row=0, column=i, sticky="ew")
        row_idx = 1
        for pid, qty in self.controller.cart.items():
            prod = next((p for p in products if p['id'] == int(pid)), None)
            if prod:
                price = float(prod['price'])
                subtotal = price * qty
                total_val += subtotal
                tk.Label(self.list_frame, text=prod['name'], font=("Helvetica", 11)).grid(row=row_idx, column=0, pady=10)
                tk.Label(self.list_frame, text=f"${price:.2f}").grid(row=row_idx, column=1, pady=10)
                qty_frame = tk.Frame(self.list_frame)
                qty_frame.grid(row=row_idx, column=2, pady=10)
                tk.Button(qty_frame, text="-", width=2, command=lambda p=pid: self.update_qty(p, -1)).pack(side="left")
                tk.Label(qty_frame, text=str(qty), width=4).pack(side="left", padx=5)
                tk.Button(qty_frame, text="+", width=2, command=lambda p=pid, s=prod['stock_level']: self.update_qty(p, 1, s)).pack(side="left")
                tk.Label(self.list_frame, text=f"${subtotal:.2f}", font=("bold")).grid(row=row_idx, column=3, pady=10)
                tk.Button(self.list_frame, text="Remove", fg="white", bg="#ff4444", font=("Helvetica", 9), command=lambda p=pid: self.update_qty(p, -999)).grid(row=row_idx, column=4, pady=10)
                row_idx += 1
        tk.Label(self.list_frame, text="", bg="#333").grid(row=row_idx, column=0, columnspan=5, sticky="ew", pady=(20,0)) 
        row_idx += 1
        tk.Label(self.list_frame, text=f"Grand Total: ${total_val:.2f}", font=("Helvetica", 16, "bold"), fg="#2196F3").grid(row=row_idx, column=3, columnspan=2, pady=20)

    def update_qty(self, pid, change, max_stock=1000):
        current_qty = self.controller.cart.get(pid, 0)
        new_qty = current_qty + change
        if change == -999 or new_qty <= 0:
            del self.controller.cart[pid]
        elif new_qty > max_stock:
            messagebox.showwarning("Stock Limit", "Maximum stock reached.")
            return
        else:
            self.controller.cart[pid] = new_qty
        self.refresh()