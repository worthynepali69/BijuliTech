import tkinter as tk
from tkinter import ttk

class ForgotPasswordPage(ttk.Frame):
    """
    FIXED: "unknown option -background" crash.
    - Changed style of 'Back' button to 'LinkOnCard.TButton'
    - Removed the .config(background=...) line that was causing the crash.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.fonts = controller.fonts
        self.colors = controller.colors
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        main_frame = ttk.Frame(self, style="Login.TFrame", padding=40)
        main_frame.grid(row=0, column=0, sticky="ns")
        main_frame.columnconfigure(0, weight=1)

        header = ttk.Label(
            main_frame,
            text="Forgot Your Password?",
            style="Header.Card.TLabel"
        )
        header.grid(row=0, column=0, pady=(0, 10))
        
        sub_header = ttk.Label(
            main_frame,
            text="Enter your username to reset your password.\n(This is a simulation, no email will be sent.)",
            style="Light.Card.TLabel",
            justify="center"
        )
        sub_header.grid(row=1, column=0, pady=(0, 25))

        self.username_var = tk.StringVar()
        
        username_frame = ttk.Frame(main_frame, style="Card.TFrame")
        username_frame.grid(row=2, column=0, pady=5, sticky="ew")
        ttk.Label(username_frame, text="Username:", style="Card.TLabel").pack(side="left", padx=10)
        ttk.Entry(username_frame, textvariable=self.username_var, font=self.fonts["body"]).pack(side="left", fill="x", expand=True, padx=10, ipady=5)

        self.error_label = ttk.Label(main_frame, text="", style="Error.TLabel")
        # --- FIX: Configure the style, not the widget ---
        style = ttk.Style()
        style.configure("Error.TLabel", background=self.colors["white"])
        # --- END FIX ---
        self.error_label.grid(row=3, column=0, pady=(10, 0))

        # --- Button Frame ---
        button_frame = ttk.Frame(main_frame, style="Card.TFrame")
        button_frame.grid(row=4, column=0, pady=20, sticky="ew")
        button_frame.columnconfigure(0, weight=1)

        reset_button = ttk.Button(
            button_frame,
            text="Send Reset Link",
            style="Accent.TButton",
            command=self.send_reset_link
        )
        reset_button.grid(row=0, column=0, sticky="ew", ipady=5)
        
        # --- THE FIX IS HERE ---
        back_button = ttk.Button(
            main_frame,
            text="← Back to Login",
            style="LinkOnCard.TButton", # Use the new style from main.py
            command=lambda: self.controller.show_frame("LoginPage")
        )
        # REMOVED the crashing .config() line
        back_button.grid(row=5, column=0, pady=(10, 0))
        # --- END OF FIX ---

    def on_show(self, context=None):
        self.username_var.set("")
        self.error_label.config(text="")

    def send_reset_link(self):
        username = self.username_var.get()
        if not username:
            self.error_label.config(text="Please enter a username.")
            return

        # Simulate success
        self.error_label.config(text=f"Reset link sent to {username}'s (simulated) email!", style="TLabel")
        self.controller.show_toast("Password reset link sent (simulation)")