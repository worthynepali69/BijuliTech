import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
import webbrowser
import os

class CheckoutPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.discount_percent = 0.0
        self.vip_discount = 0.0
        self.final_total = 0.0
        
        tk.Label(self, text="Checkout & Payment", font=("Helvetica", 18, "bold")).pack(pady=20)
        main_frame = tk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=50)
        
        left_col = tk.LabelFrame(main_frame, text="1. Customer Details", font=("bold"), padx=20, pady=20)
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 10))
        tk.Label(left_col, text="Select Existing Customer:").pack(anchor="w")
        self.customer_var = tk.StringVar()
        self.customer_combo = ttk.Combobox(left_col, textvariable=self.customer_var, state="readonly")
        self.customer_combo.pack(fill="x", pady=(5, 20))
        self.customer_combo.bind("<<ComboboxSelected>>", self.on_customer_select)
        self.lbl_loyalty = tk.Label(left_col, text="Points: 0 | Type: Standard", fg="blue", font=("Helvetica", 10))
        self.lbl_loyalty.pack(anchor="w", pady=5)
        tk.Label(left_col, text="-- OR --", fg="#666").pack(pady=5)
        tk.Button(left_col, text="+ Register New Customer", command=self.open_quick_add_customer, bg="#2196F3", fg="white").pack(fill="x", pady=10)

        right_col = tk.LabelFrame(main_frame, text="2. Payment Summary", font=("bold"), padx=20, pady=20)
        right_col.pack(side="right", fill="both", expand=True, padx=(10, 0))
        voucher_frame = tk.Frame(right_col)
        voucher_frame.pack(fill="x", pady=10)
        tk.Label(voucher_frame, text="Voucher Code:").pack(side="left")
        self.voucher_entry = tk.Entry(voucher_frame, width=15)
        self.voucher_entry.pack(side="left", padx=5)
        tk.Button(voucher_frame, text="Apply", command=self.apply_voucher, bg="#FF9800", fg="white", width=8).pack(side="left")

        pay_frame = tk.Frame(right_col)
        pay_frame.pack(fill="x", pady=10)
        tk.Label(pay_frame, text="Pay Method:").pack(side="left")
        self.payment_method_combo = ttk.Combobox(pay_frame, values=["Cash", "Credit Card", "EFTPOS"], state="readonly", width=12)
        self.payment_method_combo.current(2)
        self.payment_method_combo.pack(side="left", padx=5)
        self.payment_method_combo.bind("<<ComboboxSelected>>", self.on_payment_change)
        
        self.cash_frame = tk.Frame(right_col)
        tk.Label(self.cash_frame, text="Cash Given: $").pack(side="left")
        self.cash_entry = tk.Entry(self.cash_frame, width=10)
        self.cash_entry.pack(side="left")
        self.cash_entry.bind("<KeyRelease>", self.calculate_change)
        self.lbl_change = tk.Label(self.cash_frame, text="Change: $0.00", font=("bold"), fg="red")

        self.lbl_subtotal = tk.Label(right_col, text="Subtotal: $0.00", font=("Helvetica", 11), anchor="e")
        self.lbl_subtotal.pack(fill="x", pady=2)
        self.lbl_vip_disc = tk.Label(right_col, text="VIP Discount (5%): -$0.00", font=("Helvetica", 10), fg="blue", anchor="e")
        self.lbl_discount = tk.Label(right_col, text="Voucher: -$0.00 (0%)", font=("Helvetica", 11), fg="green", anchor="e")
        self.lbl_discount.pack(fill="x", pady=2)
        tk.Frame(right_col, height=2, bg="#333").pack(fill="x", pady=10)
        self.lbl_total = tk.Label(right_col, text="Total: $0.00", font=("Helvetica", 16, "bold"), anchor="e")
        self.lbl_total.pack(fill="x", pady=10)
        tk.Button(right_col, text="Confirm & Pay", command=self.process_payment, bg="#4CAF50", fg="white", font=("Helvetica", 12, "bold"), height=2).pack(fill="x", pady=20)
        tk.Button(self, text="Back to Cart", command=lambda: controller.show_frame("CartPage")).pack(pady=10)

    def refresh(self):
        self.discount_percent = 0.0 
        self.vip_discount = 0.0
        self.voucher_entry.delete(0, tk.END)
        self.load_customers()
        self.update_totals()

    def load_customers(self):
        self.customers_data = self.controller.db.get_all_customers()
        self.customer_combo['values'] = [f"{c['id']} - {c['name']}" for c in self.customers_data]
        if self.customer_combo['values']:
            self.customer_combo.current(0)
            self.on_customer_select(None)

    def on_customer_select(self, event):
        idx = self.customer_combo.current()
        if idx >= 0:
            cust = self.customers_data[idx]
            c_type = cust.get('customer_type', 'Standard')
            points = cust.get('loyalty_points', 0)
            self.lbl_loyalty.config(text=f"Points: {points} | Type: {c_type}")
            if c_type == 'VIP':
                self.vip_discount = 0.05
                self.lbl_vip_disc.pack(fill="x", after=self.lbl_subtotal)
            else:
                self.vip_discount = 0.0
                self.lbl_vip_disc.pack_forget()
            self.update_totals()

    def on_payment_change(self, event):
        if self.payment_method_combo.get() == "Cash":
            self.cash_frame.pack(fill="x", pady=5)
        else:
            self.cash_frame.pack_forget()

    def calculate_change(self, event):
        try:
            given = float(self.cash_entry.get())
            change = given - self.final_total
            if change < 0:
                self.lbl_change.config(text="Insufficient", fg="red")
            else:
                self.lbl_change.config(text=f"Change: ${change:.2f}", fg="green")
        except ValueError:
            self.lbl_change.config(text="Invalid", fg="red")

    def update_totals(self):
        products = self.controller.db.get_all_products()
        subtotal = 0.0 
        for pid, qty in self.controller.cart.items():
            prod = next((p for p in products if p['id'] == int(pid)), None)
            if prod: subtotal += float(prod['price']) * qty
        vip_amt = subtotal * self.vip_discount
        temp_total = subtotal - vip_amt
        voucher_amt = temp_total * self.discount_percent
        self.final_total = temp_total - voucher_amt
        self.lbl_subtotal.config(text=f"Subtotal: ${subtotal:.2f}")
        self.lbl_vip_disc.config(text=f"VIP Discount (5%): -${vip_amt:.2f}")
        self.lbl_discount.config(text=f"Voucher: -${voucher_amt:.2f} ({int(self.discount_percent*100)}%)")
        self.lbl_total.config(text=f"Total: ${self.final_total:.2f}")

    def apply_voucher(self):
        code = self.voucher_entry.get().strip()
        if code == "ais10":
            self.discount_percent = 0.10
            messagebox.showinfo("Voucher", "10% Applied!")
        else:
            self.discount_percent = 0.0
            messagebox.showerror("Error", "Invalid Code")
        self.update_totals()

    def open_quick_add_customer(self):
        popup = tk.Toplevel(self)
        popup.title("New Customer")
        popup.geometry("350x350")
        popup.configure(bg="white")
        tk.Label(popup, text="Name:", bg="white").pack(anchor="w", padx=20)
        e_name = tk.Entry(popup)
        e_name.pack(fill="x", padx=20)
        tk.Label(popup, text="Phone:", bg="white").pack(anchor="w", padx=20)
        e_phone = tk.Entry(popup)
        e_phone.pack(fill="x", padx=20)
        tk.Label(popup, text="Email:", bg="white").pack(anchor="w", padx=20)
        e_email = tk.Entry(popup)
        e_email.pack(fill="x", padx=20)
        tk.Label(popup, text="Type:", bg="white").pack(anchor="w", padx=20)
        e_type = ttk.Combobox(popup, values=["Standard", "Student", "VIP"], state="readonly")
        e_type.current(0)
        e_type.pack(fill="x", padx=20)
        def save_quick():
            if not e_name.get(): return
            self.controller.db.add_customer(e_name.get(), e_phone.get(), e_email.get(), e_type.get())
            popup.destroy()
            self.load_customers() 
            messagebox.showinfo("Success", "Customer Created")
        tk.Button(popup, text="Save", command=save_quick, bg="#4CAF50", fg="white").pack(pady=20)

    def process_payment(self):
        if not self.controller.cart:
            messagebox.showerror("Error", "Cart is empty")
            return
        if self.payment_method_combo.get() == "Cash":
            try:
                given = float(self.cash_entry.get())
                if given < self.final_total:
                    messagebox.showerror("Payment Error", "Insufficient Cash")
                    return
            except ValueError:
                messagebox.showerror("Payment Error", "Invalid Cash Amount")
                return
        cust_str = self.customer_var.get()
        if not cust_str:
            messagebox.showerror("Error", "Select customer")
            return
        cust_id = int(cust_str.split(" - ")[0])
        user_id = self.controller.current_user['id'] 
        self.controller.last_payment_method = self.payment_method_combo.get()
        self.controller.last_discount_amt = (self.final_total / (1 - self.discount_percent)) * self.discount_percent
        order_id = self.controller.db.process_transaction(cust_id, user_id, self.controller.cart, self.final_total)
        if order_id:
            self.controller.current_order_id = order_id
            self.controller.cart = {} 
            self.controller.show_frame("ReceiptPage")
        else:
            messagebox.showerror("Error", "Transaction failed.")

class ReceiptPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="white")
        self.html_content = ""
        tk.Label(self, text="Transaction Complete", font=("Helvetica", 24, "bold"), bg="white", fg="#4CAF50").pack(pady=20)
        container = tk.Frame(self, bg="white", bd=2, relief="solid")
        container.pack(pady=10, padx=20)
        scrollbar = ttk.Scrollbar(container)
        scrollbar.pack(side="right", fill="y")
        self.txt_preview = tk.Text(container, font=("Courier", 12), bg="#FAFAFA", width=60, height=20,
                                   yscrollcommand=scrollbar.set, padx=10, pady=10)
        self.txt_preview.pack(side="left", fill="both")
        scrollbar.config(command=self.txt_preview.yview)
        btn_frame = tk.Frame(self, bg="white")
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="🖨 Print / Save as PDF", command=self.save_receipt,
                  bg="#FF9800", fg="white", font=("Helvetica", 12, "bold"), padx=20, pady=5).pack(side="left", padx=20)
        tk.Button(btn_frame, text="New Sale", command=lambda: controller.show_frame("StorePage"),
                  bg="#2196F3", fg="white", font=("Helvetica", 12, "bold"), padx=20, pady=5).pack(side="left", padx=20)

    def refresh(self):
        oid = self.controller.current_order_id
        if not oid: return
        items = self.controller.db.get_order_items(oid)
        cashier = self.controller.current_user['username'].capitalize() if self.controller.current_user else "Unknown"
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pay_method = getattr(self.controller, 'last_payment_method', 'Cash')
        subtotal = sum(float(i['price_at_time']) * i['quantity'] for i in items)
        try:
            conn = self.controller.db.get_connection()
            c = conn.cursor()
            c.execute("SELECT total_amount FROM orders WHERE id=%s", (oid,))
            final_total = float(c.fetchone()[0])
            conn.close()
        except:
            final_total = subtotal
        gst_val = final_total * 3 / 23 
        discount_val = subtotal - final_total
        preview_lines = [
            f"{'BIJULI TECH POS':^58}",
            f"{'123 University Road, Auckland':^58}",
            "-"*58,
            f"Receipt #: {oid:<20} Date: {now}",
            f"Cashier:   {cashier:<20} Method: {pay_method}",
            "-"*58,
            f"{'Item':<30} {'Qty':<5} {'Price':<10} {'Total':<10}",
            "-"*58
        ]
        rows = "" 
        for item in items:
            name = item['name'][:28]
            qty = item['quantity']
            price = float(item['price_at_time'])
            line_total = price * qty
            preview_lines.append(f"{name:<30} {qty:<5} ${price:<9.2f} ${line_total:<9.2f}")
            rows += f"<tr><td>{item['name']}</td><td>{qty}</td><td>${price:.2f}</td><td>${line_total:.2f}</td></tr>"
        preview_lines.append("-" * 58)
        preview_lines.append(f"{'Subtotal:':<45} ${subtotal:>10.2f}")
        if discount_val > 0.01:
            preview_lines.append(f"{'Total Savings:':<45}-${discount_val:>10.2f}")
        preview_lines.append(f"{'TOTAL (Inc. GST):':<45} ${final_total:>10.2f}")
        preview_lines.append(f"{'GST (15%):':<45} ${gst_val:>10.2f}")
        preview_lines.append("-" * 58)
        self.txt_preview.config(state="normal")
        self.txt_preview.delete("1.0", tk.END)
        self.txt_preview.insert("1.0", "\n".join(preview_lines))
        self.txt_preview.config(state="disabled")
        self.html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 20px; }}
                .header {{ text-align: center; margin-bottom: 20px; }}
                .logo {{ font-size: 24px; font-weight: bold; color: #2196F3; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th, td {{ border-bottom: 1px solid #ddd; padding: 10px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .totals {{ margin-top: 20px; text-align: right; }}
                .footer {{ margin-top: 40px; text-align: center; font-size: 12px; color: #777; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="logo">BIJULI TECH</div>
                <div>123 University Road, Auckland, NZ</div>
                <div>GST No: 123-456-789</div>
                <h3>Tax Invoice #{oid}</h3>
                <p>Date: {now} | Served by: {cashier}</p>
            </div>
            <table>
                <tr><th>Item</th><th>Qty</th><th>Price</th><th>Total</th></tr>
                {rows}
            </table>
            <div class="totals">
                <p>Subtotal: ${subtotal:.2f}</p>
                <p style="color: green">Savings: -${discount_val:.2f}</p>
                <h3>Total: ${final_total:.2f}</h3>
                <p style="font-size: 12px">(Includes GST 15%: ${gst_val:.2f})</p>
                <p><strong>Paid via {pay_method}</strong></p>
            </div>
            <div class="footer">
                Thank you for shopping with us!<br>
                Earned Points: {int(final_total/10)}<br>
                Please retain this receipt for warranty purposes.
            </div>
            <script>window.print();</script> 
        </body>
        </html>
        """

    def save_receipt(self):
        try:
            filename = f"Receipt_{self.controller.current_order_id}.html"
            with open(filename, "w") as f:
                f.write(self.html_content)
            webbrowser.open('file://' + os.path.realpath(filename))
        except Exception as e:
            messagebox.showerror("Error", f"Could not open print dialog: {e}")