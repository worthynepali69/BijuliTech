import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os

class StorePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#f0f0f0")
        self.image_cache = {} 
        
        # Navbar
        navbar = tk.Frame(self, bg="#2196F3", height=60, pady=10)
        navbar.pack(fill="x")
        
        nav_left = tk.Frame(navbar, bg="#2196F3")
        nav_left.pack(side="left", padx=20)

        def go_back():
            if self.controller.current_user['role'] == 'admin':
                controller.show_frame("AdminMenu")

        self.back_btn = tk.Button(nav_left, text="← Admin", command=go_back,
                                  bg="#1565C0", fg="white", relief="flat", font=("Helvetica", 10))

        tk.Label(nav_left, text="Bijuli Tech", font=("Helvetica", 20, "bold"), 
                 bg="#2196F3", fg="white").pack(side="left", padx=(10, 0))
        
        nav_right = tk.Frame(navbar, bg="#2196F3")
        nav_right.pack(side="right", padx=20)
        
        self.cart_btn = tk.Button(nav_right, text="🛒 (0)", 
                                  command=lambda: controller.show_frame("CartPage"),
                                  bg="white", fg="#2196F3", font=("Helvetica", 11, "bold"), width=10)
        self.cart_btn.pack(side="left", padx=10)
        
        tk.Button(nav_right, text="Logout", 
                  command=lambda: controller.logout(self),
                  bg="#FF5252", fg="white", font=("Helvetica", 10, "bold")).pack(side="left", padx=5)

        # Search
        search_panel = tk.Frame(self, bg="white", pady=15, padx=20)
        search_panel.pack(fill="x")
        search_container = tk.Frame(search_panel, bg="white")
        search_container.pack(anchor="center")
        tk.Label(search_container, text="Find Product:", bg="white", font=("Helvetica", 11), fg="#555").pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_container, textvariable=self.search_var, width=40, font=("Helvetica", 12), bd=2, relief="groove")
        search_entry.pack(side="left", padx=10, ipady=3)
        search_entry.bind("<Return>", lambda e: self.refresh(self.search_var.get())) 
        tk.Button(search_container, text="Search", command=lambda: self.refresh(self.search_var.get()),
                  bg="#2196F3", fg="white", font=("Helvetica", 10, "bold"), width=10).pack(side="left", padx=2)
        tk.Button(search_container, text="Clear", command=lambda: self.clear_search(),
                  bg="#E0E0E0", fg="black", font=("Helvetica", 10), width=8).pack(side="left", padx=2)

        # Grid
        grid_container = tk.Frame(self, bg="#f0f0f0")
        grid_container.pack(fill="both", expand=True, padx=20, pady=20)
        self.canvas = tk.Canvas(grid_container, bg="#f0f0f0", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(grid_container, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas, bg="#f0f0f0")
        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        
        def on_canvas_configure(event):
            self.canvas.itemconfig(self.canvas_window, width=event.width)
        self.canvas.bind("<Configure>", on_canvas_configure)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.toast_label = tk.Label(self, text="", bg="#333", fg="white", font=("Helvetica", 10), padx=20, pady=10, relief="flat")

    def clear_search(self):
        self.search_var.set("")
        self.refresh()

    def update_cart_count(self):
        count = sum(self.controller.cart.values())
        self.cart_btn.config(text=f"🛒 ({count})")

    def refresh(self, search_query=""):
        self.update_cart_count()
        if self.controller.current_user and self.controller.current_user['role'] == 'admin':
            self.back_btn.pack(side="left", padx=(0, 10))
        else:
            self.back_btn.pack_forget()

        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        self.image_cache = {}

        try:
            all_products = self.controller.db.get_all_products()
        except Exception as e:
            tk.Label(self.scroll_frame, text=f"Database Error: {e}", fg="red", bg="#f0f0f0").pack(pady=20)
            return

        if search_query:
            products = [p for p in all_products if search_query.lower() in p['name'].lower()]
        else:
            products = all_products

        if not products:
            tk.Label(self.scroll_frame, text="No products found.", font=("Helvetica", 14), bg="#f0f0f0", fg="#666").pack(pady=50)
            return

        columns = 4
        for i in range(columns):
            self.scroll_frame.columnconfigure(i, weight=1)

        for index, prod in enumerate(products):
            row = index // columns
            col = index % columns
            self.create_product_card(prod, row, col)

    def create_product_card(self, product, r, c):
        card_border = tk.Frame(self.scroll_frame, bg="#d9d9d9", padx=1, pady=1)
        card_border.grid(row=r, column=c, padx=15, pady=15, sticky="ew")
        card = tk.Frame(card_border, bg="white", padx=10, pady=10)
        card.pack(fill="both", expand=True)

        img_path = product.get('image_path', '')
        tk_img = None
        try:
            if img_path:
                if not os.path.isabs(img_path):
                    img_path = os.path.join(os.getcwd(), img_path)
                if os.path.exists(img_path):
                    pil_img = Image.open(img_path)
                    pil_img = pil_img.resize((160, 130), Image.Resampling.LANCZOS)
                    tk_img = ImageTk.PhotoImage(pil_img)
            if tk_img is None:
                pil_img = Image.new('RGB', (160, 130), color="#F5F5F5")
                tk_img = ImageTk.PhotoImage(pil_img)
            self.image_cache[product['id']] = tk_img
            tk.Label(card, image=tk_img, bg="white").pack(pady=(0, 10), anchor="center")
        except Exception as e:
            tk.Label(card, text="[No Image]", bg="#eee", height=6, width=20).pack(pady=(0, 10))

        tk.Label(card, text=product['name'], font=("Helvetica", 11, "bold"), bg="white", wraplength=180, justify="center").pack(anchor="center", fill="x")
        tk.Label(card, text=f"${product['price']}", font=("Helvetica", 11, "bold"), fg="#2E7D32", bg="white").pack(anchor="center", pady=2)

        stock = product['stock_level']
        stock_text = f"{stock} in stock" if stock > 0 else "Out of Stock"
        stock_color = "#757575" if stock > 0 else "#D32F2F"
        tk.Label(card, text=stock_text, font=("Helvetica", 9), fg=stock_color, bg="white").pack(anchor="center", pady=(0, 10))

        state = "normal" if stock > 0 else "disabled"
        btn_text = "Add to Cart" if stock > 0 else "Unavailable"
        
        add_btn = tk.Button(card, text=btn_text, state=state,
                            command=lambda: self.add_to_cart(product),
                            bg="#2196F3" if stock > 0 else "#E0E0E0", 
                            fg="white" if stock > 0 else "#9E9E9E", 
                            font=("Helvetica", 10, "bold"), relief="flat", 
                            cursor="hand2" if stock > 0 else "arrow", pady=5)
        add_btn.pack(fill="x", padx=5)

    def add_to_cart(self, product):
        pid = product['id']
        current_stock = product['stock_level']
        in_cart = self.controller.cart.get(pid, 0)
        if in_cart + 1 <= current_stock:
            self.controller.cart[pid] = in_cart + 1
            self.update_cart_count()
            self.show_toast(f"Added 1 {product['name']}")
        else:
            messagebox.showwarning("Stock Limit", "Cannot add more than available stock.")

    def show_toast(self, message):
        self.toast_label.config(text=message, bg="#388E3C")
        self.toast_label.place(relx=0.5, rely=0.9, anchor="center")
        self.after(1500, lambda: self.toast_label.place_forget())