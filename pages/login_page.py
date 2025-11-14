import tkinter as tk
from tkinter import ttk

class LoginPage(ttk.Frame):
    """
    FIXED: "unknown option -background" crash.
    - Changed style of 'Forgot' button to 'LinkOnCard.TButton'
    - Removed the .config(background=...) line that was causing the crash.
    - Removed auto-filled username/password.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.fonts = controller.fonts
        self.colors = controller.colors
        
        # Center the login box
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        main_frame = ttk.Frame(self, style="Login.TFrame", padding=40)
        main_frame.grid(row=0, column=0, sticky="ns")
        main_frame.columnconfigure(0, weight=1)

        header = ttk.Label(
            main_frame,
            text="Bijuli Tech",
            style="Header.Card.TLabel"
        )
        header.grid(row=0, column=0, pady=(0, 10))
        
        sub_header = ttk.Label(
            main_frame,
            text="Please sign in to continue",
            style="Subheader.Light.Card.TLabel"
        )
        sub_header.grid(row=1, column=0, pady=(0, 25))

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        
        username_frame = ttk.Frame(main_frame, style="Card.TFrame")
        username_frame.grid(row=2, column=0, pady=5, sticky="ew")
        ttk.Label(username_frame, text="Username:", style="Card.TLabel").pack(side="left", padx=10)
        self.username_entry = ttk.Entry(username_frame, textvariable=self.username_var, font=self.fonts["body"])
        self.username_entry.pack(side="left", fill="x", expand=True, padx=10, ipady=5)

        password_frame = ttk.Frame(main_frame, style="Card.TFrame")
        password_frame.grid(row=3, column=0, pady=5, sticky="ew")
        ttk.Label(password_frame, text="Password:", style="Card.TLabel").pack(side="left", padx=10)
        self.password_entry = ttk.Entry(password_frame, textvariable=self.password_var, show="*", font=self.fonts["body"])
        self.password_entry.pack(side="left", fill="x", expand=True, padx=10, ipady=5)
        
        self.error_label = ttk.Label(main_frame, text="", style="Error.TLabel")
        # --- FIX: Configure the style, not the widget ---
        style = ttk.Style()
        style.configure("Error.TLabel", background=self.colors["white"])
        # --- END FIX ---
        self.error_label.grid(row=4, column=0, pady=(10, 0))

        # Bind the <Return> key (Enter) to the login function
        self.username_entry.bind("<Return>", lambda event: self.password_entry.focus())
        self.password_entry.bind("<Return>", lambda event: self.attempt_login())

        # --- Button Frame ---
        button_frame = ttk.Frame(main_frame, style="Card.TFrame")
        button_frame.grid(row=5, column=0, pady=20, sticky="ew")
        button_frame.columnconfigure(0, weight=1)

        login_button = ttk.Button(
            button_frame,
            text="Login",
            style="Accent.TButton",
            command=self.attempt_login
        )
        login_button.grid(row=0, column=0, sticky="ew", ipady=5)
        
        # --- THE FIX IS HERE ---
        forgot_button = ttk.Button(
            main_frame,
            text="Forgot Password?",
            style="LinkOnCard.TButton", # Use the new style from main.py
            command=lambda: self.controller.show_frame("ForgotPasswordPage")
        )
        # REMOVED the crashing .config() line
        forgot_button.grid(row=6, column=0, pady=(10, 0))
        # --- END OF FIX ---

    def on_show(self, context=None):
        # Clear fields when page is shown
        self.username_var.set("")
        self.password_var.set("")
        self.error_label.config(text="")
        # Set focus to the username entry
        self.username_entry.focus_set()

    def attempt_login(self):
        username = self.username_var.get()
        password = self.password_var.get()
        
        if not username or not password:
            self.error_label.config(text="Username and Password are required.")
            return
            
        role = self.controller.db.validate_user(username, password)
        
        if role:
            self.error_label.config(text="")
            self.controller.handle_login(username, role)
        else:
            self.error_label.config(text="Invalid username or password.")
            self.controller.show_toast("Invalid username or password", style="error")