import tkinter as tk
from tkinter import messagebox

from db.db_manager import get_username_by_unlock_code
from gui.authenticate_window import create_auth_window
from gui.register_window import create_registration_window  # Import registration window

# Secret code trigger + auth code
SECRET_TRIGGER = "0000+-"
auth_code = ""
# Colors
BG = "#1C1C1C"
TEXT = "#F5E8D8"
CORAL = "#FF6F61"
GOLD = "#DAA520"
HOVER = "#FF4500"
BORDER = "#333333"
BTN_BG = "#252525"
EQUAL_BTN = "#FF6F00"
EQUAL_HOVER = "#FF8C00"

expression = ""

def create_calculator():
    def append(char):
        global expression
        expression += char
        display_var.set(expression)

        if expression.endswith(SECRET_TRIGGER):
            root.withdraw()
            create_registration_window(root)
            expression = ""
            display_var.set("")

        elif len(expression) >= 6:  # Or whatever length your unlock code uses
            username = get_username_by_unlock_code(expression)
            if username:
                root.destroy()
                create_auth_window(username)  # Pass the username to auth window
            else:
                messagebox.showerror("Error", "Invalid unlock code.")
            expression = ""
            display_var.set("")

    def clear():
        global expression
        expression = ""
        display_var.set("")

    def backspace():
        global expression
        expression = expression[:-1]
        display_var.set(expression)

    def calculate():
        global expression
        try:
            result = str(eval(expression))
            display_var.set(result)
            expression = result
        except:
            messagebox.showerror("Error", "Invalid Expression")
            expression = ""

    root = tk.Tk()
    root.title("Smart Calculator")
    root.configure(bg=BG)
    root.resizable(False, False)

    # Display
    display_var = tk.StringVar()
    display = tk.Entry(root, textvariable=display_var, font=("Consolas", 20),
                       bg=BTN_BG, fg=TEXT, bd=0, insertbackground=TEXT,
                       justify="right", highlightthickness=0)
    display.grid(row=0, column=0, columnspan=4, sticky="nsew", padx=10, pady=10, ipady=10)

    # Buttons
    buttons = [
        ("AC", clear), ("CE", backspace), ("÷", lambda: append("/")), ("×", lambda: append("*")),
        ("7", lambda: append("7")), ("8", lambda: append("8")), ("9", lambda: append("9")), ("-", lambda: append("-")),
        ("4", lambda: append("4")), ("5", lambda: append("5")), ("6", lambda: append("6")), ("+", lambda: append("+")),
        ("1", lambda: append("1")), ("2", lambda: append("2")), ("3", lambda: append("3")), ("%", lambda: append("%")),
        ("0", lambda: append("0")), (".", lambda: append(".")), ("=", calculate)
    ]

    row = 1
    col = 0
    for (text, command) in buttons:
        btn = tk.Button(root, text=text, command=command,
                        font=("Consolas", 18), bg=BTN_BG, fg=TEXT,
                        bd=0, activebackground=HOVER, padx=10, pady=10)

        if text == "=":
            btn.config(bg=EQUAL_BTN, activebackground=EQUAL_HOVER)
            btn.grid(row=row, column=col, columnspan=2, sticky="nsew", padx=2, pady=2, ipadx=10, ipady=10)
            col += 1
        else:
            btn.grid(row=row, column=col, sticky="nsew", padx=2, pady=2, ipadx=10, ipady=10)

        col += 1
        if col > 3:
            col = 0
            row += 1

    # Grid scaling
    for i in range(6):
        root.grid_rowconfigure(i, weight=1)
    for i in range(4):
        root.grid_columnconfigure(i, weight=1)

    root.mainloop()


if __name__ == "__main__":
    create_calculator()

