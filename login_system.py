import tkinter as tk
from tkinter import ttk, messagebox

class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#f0f0f0")
        
        box = tk.Frame(self, bg="white", padx=40, pady=40, relief="raised", bd=2)
        box.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(box, text="Bijuli Tech Login", font=("Helvetica", 20, "bold"), bg="white", fg="#333").pack(pady=(0, 20))
        
        tk.Label(box, text="Username:", bg="white", font=("Helvetica", 10)).pack(anchor="w")
        self.username_entry = ttk.Entry(box, width=30, font=("Helvetica", 11))
        self.username_entry.pack(pady=(0, 10))
        
        tk.Label(box, text="Password:", bg="white", font=("Helvetica", 10)).pack(anchor="w")
        self.password_entry = ttk.Entry(box, show="*", width=30, font=("Helvetica", 11))
        self.password_entry.pack(pady=(0, 20))
        
        tk.Button(box, text="Login", command=self.attempt_login, 
                  bg="#4CAF50", fg="white", font=("Helvetica", 12, "bold"), 
                  width=20, cursor="hand2").pack()

        self.password_entry.bind("<Return>", lambda e: self.attempt_login())

    def attempt_login(self):
        u = self.username_entry.get().strip()
        p = self.password_entry.get().strip()
        user = self.controller.db.login(u, p)
        
        if user:
            self.controller.on_login_success(user)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")
            self.password_entry.delete(0, tk.END)