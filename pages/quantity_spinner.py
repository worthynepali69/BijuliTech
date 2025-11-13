import tkinter as tk
from tkinter import ttk

class QuantitySpinner(ttk.Frame):
    """
    FIXED: "bad pad value '-1'" crash.
    - Rebuilt layout using .grid() instead of .pack()
    - Removed all negative padding.
    - This one change fixes the crash on the product page AND
      allows the cart page to load correctly.
    """
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Use the style from main.py that already has a border
        self.config(style="QuantitySpinner.TFrame") 
        
        self.controller = controller
        self.quantity_var = tk.IntVar(value=1)
        
        # --- NEW GRID LAYOUT ---
        # Configure columns to be of equal weight and rows to fill
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.dec_btn = ttk.Button(
            self,
            text="−",
            style="QuantitySpinner.TButton",
            width=3, # Width in characters
            command=self.decrease
        )
        self.dec_btn.grid(row=0, column=0, sticky="nsew")

        self.qty_label = ttk.Label(
            self,
            textvariable=self.quantity_var,
            style="QuantitySpinner.TLabel",
            width=4, # Width in characters
            anchor="center"
        )
        # Use grid, not pack. This was the source of the crash.
        self.qty_label.grid(row=0, column=1, sticky="nsew")

        self.inc_btn = ttk.Button(
            self,
            text="+",
            style="QuantitySpinner.TButton",
            width=3, # Width in characters
            command=self.increase
        )
        self.inc_btn.grid(row=0, column=2, sticky="nsew")

    def increase(self):
        val = self.quantity_var.get()
        if val < 99: # Cap at 99
            self.quantity_var.set(val + 1)

    def decrease(self):
        val = self.quantity_var.get()
        if val > 1: # Minimum of 1
            self.quantity_var.set(val - 1)
            
    def get(self):
        return self.quantity_var.get()

    def set(self, value):
        self.quantity_var.set(value)