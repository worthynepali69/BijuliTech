import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from widgets.navbar import Navbar

class ReceiptPage(ttk.Frame):
    """
    Shows a final receipt/invoice for the order.
    - NEW: Added a "Download Receipt" button.
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
        container.columnconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)
        
        header_frame = ttk.Frame(container)
        header_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 20))
        
        header = ttk.Label(header_frame, text="Order Confirmed!", style="Header.TLabel")
        header.pack(side="left")
        
        download_btn = ttk.Button(
            header_frame,
            text="Download Receipt (.txt)",
            style="TButton",
            command=self.download_receipt
        )
        download_btn.pack(side="right")

        # Main receipt area
        self.receipt_frame = ttk.Frame(container, style="Card.TFrame", padding=30)
        self.receipt_frame.grid(row=1, column=0, sticky="nsew")
        
        self.receipt_text_content = "" # Store receipt for download

    def on_show(self, context=None):
        self.navbar.update_cart_count()
        # context is the order_id
        if context:
            self.load_receipt(context)
        else:
            self.controller.show_frame("StorePage")

    def load_receipt(self, order_id):
        # Clear previous receipt
        for widget in self.receipt_frame.winfo_children():
            widget.destroy()
            
        try:
            order, items = self.controller.db.fetch_order_details(order_id)
            if not order:
                ttk.Label(self.receipt_frame, text="Could not load receipt.", style="Error.TLabel").pack()
                return

            # --- Build the receipt string for download ---
            self.receipt_text_content = f"""
BIJULI TECH - OFFICIAL RECEIPT
================================

Order ID: {order['order_id']}
Date: {order['order_date']}
Status: {order['status']}

CUSTOMER & SHIPPING
--------------------
Name: {order['name']}
Email: {order['email']}
Phone: {order['phone']}
Address: {order['shipping_address']}

ITEMS PURCHASED
--------------------
"""
            # --- END of header ---

            # Create UI
            receipt_header = ttk.Label(self.receipt_frame, text=f"Receipt for Order #{order['order_id']}", style="Receipt.Header.TLabel")
            receipt_header.pack(anchor="w", pady=(0, 20))
            
            # --- Customer Details ---
            cust_frame = ttk.Frame(self.receipt_frame, style="Card.TFrame")
            cust_frame.pack(fill="x", expand=True, pady=10)
            cust_frame.columnconfigure(1, weight=1)
            cust_frame.columnconfigure(3, weight=1)
            
            ttk.Label(cust_frame, text="Customer:", style="Receipt.Bold.TLabel").grid(row=0, column=0, sticky="w", padx=10, pady=5)
            ttk.Label(cust_frame, text=order['name'], style="Receipt.TLabel").grid(row=0, column=1, sticky="w", padx=10, pady=5)
            
            ttk.Label(cust_frame, text="Date:", style="Receipt.Bold.TLabel").grid(row=0, column=2, sticky="w", padx=10, pady=5)
            ttk.Label(cust_frame, text=order['order_date'], style="Receipt.TLabel").grid(row=0, column=3, sticky="w", padx=10, pady=5)

            ttk.Label(cust_frame, text="Address:", style="Receipt.Bold.TLabel").grid(row=1, column=0, sticky="w", padx=10, pady=5)
            ttk.Label(cust_frame, text=order['shipping_address'], style="Receipt.TLabel", wraplength=400).grid(row=1, column=1, sticky="w", padx=10, pady=5)
            
            ttk.Label(cust_frame, text="Status:", style="Receipt.Bold.TLabel").grid(row=1, column=2, sticky="w", padx=10, pady=5)
            ttk.Label(cust_frame, text=order['status'], style="Receipt.Bold.TLabel").grid(row=1, column=3, sticky="w", padx=10, pady=5)
            
            # --- Items Header ---
            items_header_frame = ttk.Frame(self.receipt_frame, style="Receipt.ItemHeader.TLabel") # Use style for bg
            items_header_frame.pack(fill="x", expand=True, pady=(20, 0))
            items_header_frame.columnconfigure(0, weight=4)
            items_header_frame.columnconfigure(1, weight=1)
            items_header_frame.columnconfigure(2, weight=1)
            items_header_frame.columnconfigure(3, weight=1)
            
            ttk.Label(items_header_frame, text="Item", style="Receipt.ItemHeader.TLabel").grid(row=0, column=0, sticky="w", padx=5)
            ttk.Label(items_header_frame, text="Price", style="Receipt.ItemHeader.TLabel").grid(row=0, column=1, sticky="e", padx=5)
            ttk.Label(items_header_frame, text="Quantity", style="Receipt.ItemHeader.TLabel").grid(row=0, column=2, sticky="e", padx=5)
            ttk.Label(items_header_frame, text="Total", style="Receipt.ItemHeader.TLabel").grid(row=0, column=3, sticky="e", padx=5)
            
            self.receipt_text_content += "{:<40} {:>10} {:>10} {:>10}\n".format("Item", "Price", "Qty", "Total")
            self.receipt_text_content += "-" * 70 + "\n"

            # --- Items Loop ---
            for item in items:
                item_frame = ttk.Frame(self.receipt_frame, style="Card.TFrame", padding=(0, 5))
                item_frame.pack(fill="x", expand=True)
                item_frame.columnconfigure(0, weight=4)
                item_frame.columnconfigure(1, weight=1)
                item_frame.columnconfigure(2, weight=1)
                item_frame.columnconfigure(3, weight=1)
                
                item_total = item['price_per_unit'] * item['quantity']
                
                ttk.Label(item_frame, text=item['name'], style="Receipt.Item.TLabel").grid(row=0, column=0, sticky="w", padx=5)
                ttk.Label(item_frame, text=f"${item['price_per_unit']:.2f}", style="Receipt.Item.TLabel").grid(row=0, column=1, sticky="e", padx=5)
                ttk.Label(item_frame, text=f"{item['quantity']}", style="Receipt.Item.TLabel").grid(row=0, column=2, sticky="e", padx=5)
                ttk.Label(item_frame, text=f"${item_total:.2f}", style="Receipt.Item.TLabel").grid(row=0, column=3, sticky="e", padx=5)
                
                self.receipt_text_content += "{:<40} {:>10.2f} {:>10} {:>10.2f}\n".format(
                    item['name'][:38], item['price_per_unit'], item['quantity'], item_total
                )

            # --- Total ---
            self.receipt_text_content += "\n" + "=" * 70 + "\n"
            self.receipt_text_content += f"{'GRAND TOTAL:':>61} ${order['total_amount']:.2f}\n"
            self.receipt_text_content += "\nThank you for shopping at Bijuli Tech!"
            
            total_frame = ttk.Frame(self.receipt_frame, style="Receipt.Total.TLabel")
            total_frame.pack(fill="x", expand=True, pady=(20, 0))
            total_frame.columnconfigure(0, weight=1)
            
            ttk.Label(
                total_frame, 
                text=f"GRAND TOTAL: NZ${order['total_amount']:.2f}",
                style="Receipt.Total.TLabel",
                font=self.fonts["header"]
            ).grid(row=0, column=0, sticky="e", padx=10, pady=10)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load receipt: {e}")
            print(f"Failed to load receipt: {e}")

    def download_receipt(self):
        """Saves the receipt as a .txt file."""
        if not self.receipt_text_content:
            self.controller.show_toast("No receipt content to save.", style="error")
            return
            
        order_id = self.controller.current_order_id
        filename = f"BijuliTech_Receipt_{order_id}.txt"
        
        try:
            filepath = filedialog.asksaveasfilename(
                initialfile=filename,
                defaultextension=".txt",
                filetypes=[("Text Documents", "*.txt"), ("All Files", "*.*")]
            )
            
            if not filepath:
                # User cancelled the dialog
                return
                
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(self.receipt_text_content)
                
            self.controller.show_toast(f"Receipt saved to {filepath}", style="success")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")