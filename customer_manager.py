import tkinter as tk
from tkinter import ttk, messagebox

class CustomerManager(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.db = controller.db 
        self.configure(bg="#f0f0f0")

        # Header
        header = tk.Frame(self, bg="#FF9800", height=60)
        header.pack(fill="x")

        tk.Button(header, text="← Back to Dashboard", command=lambda: controller.show_frame("AdminMenu"),
                  bg="#F57C00", fg="white", relief="flat", font=("Helvetica", 10)).pack(side="left", padx=10, pady=10)

        tk.Label(header, text="Customer Management", font=("Helvetica", 18, "bold"), 
                 bg="#FF9800", fg="white").pack(side="left", padx=20)

        # Toolbar
        toolbar = tk.Frame(self, bg="#f0f0f0", pady=10)
        toolbar.pack(fill="x", padx=20)

        tk.Button(toolbar, text="+ Add Customer", command=self.open_add_popup, 
                  bg="#4CAF50", fg="white", font=("bold")).pack(side="left", padx=5)
        
        tk.Button(toolbar, text="Edit Selected", command=self.open_edit_popup, 
                  bg="#2196F3", fg="white").pack(side="left", padx=5)
        
        tk.Button(toolbar, text="Delete Selected", command=self.delete_customer, 
                  bg="#f44336", fg="white").pack(side="left", padx=5)
        
        tk.Button(toolbar, text="↻ Refresh List", command=self.load_data,
                  bg="white", fg="#333").pack(side="right", padx=5)

        # Table
        table_frame = tk.Frame(self)
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Added "Points" to columns
        cols = ("ID", "Name", "Phone", "Email", "Type", "Points")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings")
        
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        for col in cols:
            self.tree.heading(col, text=col)
            if col == "Points":
                self.tree.column(col, width=80, anchor="center")
            elif col == "ID":
                self.tree.column(col, width=50, anchor="center")
            else:
                self.tree.column(col, width=120)
        
        self.load_data()

    def refresh(self):
        self.load_data()

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        customers = self.db.get_all_customers()
        for c in customers:
            c_type = c.get('customer_type', 'Standard') 
            points = c.get('loyalty_points', 0)
            # Insert Points into the view
            self.tree.insert("", "end", values=(c['id'], c['name'], c['phone'], c['email'], c_type, points))

    def open_add_popup(self):
        self.popup_form("Add Customer")

    def open_edit_popup(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Please select a customer to edit.")
            return
        
        item = self.tree.item(selected[0])
        data = item['values']
        self.popup_form("Edit Customer", data)

    def popup_form(self, title, data=None):
        popup = tk.Toplevel(self)
        popup.title(title)
        popup.geometry("400x450")
        popup.configure(bg="#ffffff")
        popup.grab_set()

        pad_opts = {'padx': 20, 'pady': (15, 5)}
        entry_opts = {'padx': 20, 'pady': 5}

        tk.Label(popup, text="Full Name:", bg="white", font=("bold")).pack(anchor="w", **pad_opts)
        entry_name = tk.Entry(popup, bg="#f9f9f9", relief="solid", bd=1)
        entry_name.pack(fill="x", **entry_opts)

        tk.Label(popup, text="Phone Number:", bg="white", font=("bold")).pack(anchor="w", **pad_opts)
        entry_phone = tk.Entry(popup, bg="#f9f9f9", relief="solid", bd=1)
        entry_phone.pack(fill="x", **entry_opts)

        tk.Label(popup, text="Email Address:", bg="white", font=("bold")).pack(anchor="w", **pad_opts)
        entry_email = tk.Entry(popup, bg="#f9f9f9", relief="solid", bd=1)
        entry_email.pack(fill="x", **entry_opts)

        tk.Label(popup, text="Customer Type:", bg="white", font=("bold")).pack(anchor="w", **pad_opts)
        entry_type = ttk.Combobox(popup, values=["Standard", "Student", "VIP", "Corporate"], state="readonly")
        entry_type.current(0)
        entry_type.pack(fill="x", **entry_opts)

        if data:
            entry_name.insert(0, data[1])
            entry_phone.insert(0, str(data[2]))
            entry_email.insert(0, data[3])
            if len(data) > 4:
                entry_type.set(data[4])

        def save():
            name = entry_name.get().strip()
            phone = entry_phone.get().strip()
            email = entry_email.get().strip()
            c_type = entry_type.get()
            
            if not name: 
                messagebox.showerror("Error", "Name is required")
                return

            if data:
                self.db.update_customer(data[0], name, phone, email, c_type)
            else:
                self.db.add_customer(name, phone, email, c_type)
            
            popup.destroy()
            self.load_data()
            messagebox.showinfo("Success", "Customer Saved")

        tk.Button(popup, text="Save Customer", command=save, 
                  bg="#4CAF50", fg="white", height=2, width=20, font=("bold")).pack(pady=30)

    def delete_customer(self):
        selected = self.tree.selection()
        if not selected: return
        
        item = self.tree.item(selected[0])
        cid = item['values'][0]
        name = item['values'][1]
        
        if messagebox.askyesno("Confirm", f"Delete customer '{name}'?"):
            self.db.delete_customer(cid)
            self.load_data()