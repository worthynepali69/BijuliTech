import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os

class ProductManager(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.db = controller.db
        self.configure(bg="#f0f0f0")

        header = tk.Frame(self, bg="#2196F3", height=60)
        header.pack(fill="x")

        tk.Button(header, text="← Back to Dashboard", command=lambda: controller.show_frame("AdminMenu"),
                  bg="#1976D2", fg="white", relief="flat", font=("Helvetica", 10)).pack(side="left", padx=10, pady=10)

        tk.Label(header, text="Product Management", font=("Helvetica", 18, "bold"), 
                 bg="#2196F3", fg="white").pack(side="left", padx=20)

        toolbar = tk.Frame(self, bg="#f0f0f0", pady=10)
        toolbar.pack(fill="x", padx=20)

        tk.Button(toolbar, text="+ Add Product", command=self.open_add_popup, 
                  bg="#4CAF50", fg="white", font=("bold")).pack(side="left", padx=5)
        
        tk.Button(toolbar, text="Edit Selected", command=self.open_edit_popup, 
                  bg="#FF9800", fg="white").pack(side="left", padx=5)
        
        tk.Button(toolbar, text="Delete Selected", command=self.delete_product, 
                  bg="#f44336", fg="white").pack(side="left", padx=5)
        
        tk.Button(toolbar, text="↻ Refresh List", command=self.load_data,
                  bg="white", fg="#333").pack(side="right", padx=5)

        table_frame = tk.Frame(self)
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        cols = ("ID", "Name", "Price", "Stock", "Image Path")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings")
        self.tree.tag_configure('low_stock', background='#FFEBEE', foreground='red')
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        for col in cols:
            self.tree.heading(col, text=col)
            width = 300 if col == "Image Path" else 100
            self.tree.column(col, width=width)

        self.load_data()

    def refresh(self):
        self.load_data()

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        products = self.db.get_all_products()
        for p in products:
            stock = int(p['stock_level'])
            tag = 'low_stock' if stock < 5 else ''
            self.tree.insert("", "end", values=(p['id'], p['name'], p['price'], p['stock_level'], p['image_path']), tags=(tag,))

    def open_add_popup(self):
        self.popup_form("Add Product")

    def open_edit_popup(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Please select a product to edit.")
            return
        item = self.tree.item(selected[0])
        data = item['values']
        self.popup_form("Edit Product", data)

    def popup_form(self, title, data=None):
        popup = tk.Toplevel(self)
        popup.title(title)
        popup.geometry("500x500")
        popup.configure(bg="#ffffff")
        popup.grab_set()
        pad_opts = {'padx': 20, 'pady': (15, 5)}
        entry_opts = {'padx': 20, 'pady': 5}
        tk.Label(popup, text="Product Name:", bg="white", font=("bold")).pack(anchor="w", **pad_opts)
        entry_name = tk.Entry(popup, bg="#f9f9f9", relief="solid", bd=1)
        entry_name.pack(fill="x", **entry_opts)
        tk.Label(popup, text="Price ($):", bg="white", font=("bold")).pack(anchor="w", **pad_opts)
        entry_price = tk.Entry(popup, bg="#f9f9f9", relief="solid", bd=1)
        entry_price.pack(fill="x", **entry_opts)
        tk.Label(popup, text="Stock Quantity:", bg="white", font=("bold")).pack(anchor="w", **pad_opts)
        entry_stock = tk.Entry(popup, bg="#f9f9f9", relief="solid", bd=1)
        entry_stock.pack(fill="x", **entry_opts)
        tk.Label(popup, text="Product Image:", bg="white", font=("bold")).pack(anchor="w", **pad_opts)
        img_frame = tk.Frame(popup, bg="white")
        img_frame.pack(fill="x", **entry_opts)
        self.lbl_image_path = tk.Label(img_frame, text="No file selected", bg="#eee", width=40, anchor="w")
        self.lbl_image_path.pack(side="left", fill="x", expand=True)
        def select_image():
            initial_dir = os.path.join(os.getcwd(), "assets")
            if not os.path.exists(initial_dir): initial_dir = os.getcwd()
            filename = filedialog.askopenfilename(title="Select Image", initialdir=initial_dir, filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
            if filename:
                try:
                    rel_path = os.path.relpath(filename, os.getcwd())
                    if not rel_path.startswith(".."): filename = rel_path
                except: pass 
                self.lbl_image_path.config(text=filename)
        tk.Button(img_frame, text="Browse...", command=select_image).pack(side="right", padx=5)
        if data:
            entry_name.insert(0, data[1])
            entry_price.insert(0, data[2])
            entry_stock.insert(0, data[3])
            self.lbl_image_path.config(text=data[4] if data[4] else "No file selected")
        def save():
            try:
                name = entry_name.get().strip()
                price = float(entry_price.get())
                stock = int(entry_stock.get())
                img_path = self.lbl_image_path.cget("text")
                if img_path == "No file selected": img_path = ""
                if not name: raise ValueError("Name required")
                if data: self.db.update_product(data[0], name, price, img_path, stock)
                else: self.db.add_product(name, price, img_path, stock)
                popup.destroy()
                self.load_data()
                messagebox.showinfo("Success", "Product Saved")
            except ValueError:
                messagebox.showerror("Error", "Invalid Input. Check numbers and fields.")
        tk.Button(popup, text="Save Product", command=save, bg="#4CAF50", fg="white", height=2, width=20, font=("bold")).pack(pady=30)

    def delete_product(self):
        selected = self.tree.selection()
        if not selected: return
        item = self.tree.item(selected[0])
        pid = item['values'][0]
        name = item['values'][1]
        if messagebox.askyesno("Confirm", f"Delete '{name}'?"):
            self.db.delete_product(pid)
            self.load_data()