import tkinter as tk
from tkinter import ttk

class Toast:
    """
    FIXED: TypeError: __init__() missing 1 required positional argument: 'message'
    - The 'message' argument was removed from __init__ and is now only required by the show() method.
    """
    def __init__(self, parent):
        self.parent = parent
        self.colors = parent.colors # Get colors from the controller
        self.fonts = parent.fonts   # Get fonts from the controller

        # Create the label widget, but keep it hidden
        self.toast_label = ttk.Label(parent, text="", anchor="center", style="Toast.TLabel", font=self.fonts["body_bold"])
        
        # Style configurations
        self.style = ttk.Style()
        self.style.configure("Toast.TLabel",
                             padding=15,
                             borderwidth=1,
                             relief="solid",
                             foreground=self.colors["white"])
        
        # Style for "info" (blue)
        self.style.configure("info.Toast.TLabel",
                             background=self.colors["primary"],
                             bordercolor=self.colors["primary"])
        
        # Style for "success" (green)
        self.style.configure("success.Toast.TLabel",
                             background=self.colors["accent"],
                             bordercolor=self.colors["accent"])
        
        # Style for "error" (red)
        self.style.configure("error.Toast.TLabel",
                             background=self.colors["error"],
                             bordercolor=self.colors["error"])
        
        # Style for "warning" (yellow)
        self.style.configure("warning.Toast.TLabel",
                             background=self.colors["warning"],
                             bordercolor=self.colors["warning"],
                             foreground=self.colors["fg"]) # Dark text on yellow

    def show(self, message, style="info"):
        """
        Show the toast notification.
        'style' can be 'info', 'success', 'error', or 'warning'.
        """
        try:
            self.toast_label.config(text=message)
            
            # Apply the correct style
            full_style = f"{style}.Toast.TLabel"
            
            # This is a check to make sure the style exists before applying it
            if not full_style in self.style.layout(full_style):
                full_style = "info.Toast.TLabel" # Default fallback
            
            self.toast_label.config(style=full_style)
            
            # Position at top-center
            self.toast_label.place(relx=0.5, y=20, anchor="n")
            
            # Hide after 2.5 seconds
            self.parent.after(2500, self.hide)
        except Exception as e:
            print(f"Error showing toast: {e}")

    def hide(self):
        """Hides the toast label."""
        self.toast_label.place_forget()
