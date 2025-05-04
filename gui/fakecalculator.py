'''
import tkinter as tk
from tkinter import messagebox
import pickle

# Secret codes
REGISTER_CODE = "0000+"
AUTH_CODE = "1234+"

# Colors
BG = "#1C1C1C"        # Background
TEXT = "#F5E8D8"      # Primary text
CORAL = "#FF6F61"     # Accent 1
GOLD = "#DAA520"      # Accent 2
HOVER = "#FF4500"     # Hover effects
BORDER = "#333333"    # Borders
BTN_BG = "#252525"    # Button background
EQUAL_BTN = "#FF6F00" # Orange for equal
EQUAL_HOVER = "#FF8C00"

class SmartCalcVault(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Smart Calculator")
        self.geometry("350x500")
        self.configure(bg=BG)
        self.resizable(False, False)

        self.equation = ""

        container = tk.Frame(self, bg=BG)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        self.display = tk.Entry(container, font=("Consolas", 28), bg=BTN_BG, fg=TEXT,
                                insertbackground=TEXT, justify='right', bd=0, relief='flat',
                                highlightthickness=1, highlightbackground=BORDER)
        self.display.pack(fill="x", pady=(0, 10), ipady=10)

        button_frame = tk.Frame(container, bg=BG)
        button_frame.pack(fill="both", expand=True)

        layout = {
            (0, 0): 'AC', (0, 1): 'CE', (0, 2): '/',  (0, 3): '*',
            (1, 0): '7',  (1, 1): '8',  (1, 2): '9',  (1, 3): '-',
            (2, 0): '4',  (2, 1): '5',  (2, 2): '6',  (2, 3): '+',
            (3, 0): '1',  (3, 1): '2',  (3, 2): '3',
            (4, 0): '%',  (4, 1): '0',  (4, 2): '.',
        }

        for r in range(5):
            button_frame.grid_rowconfigure(r, weight=1, uniform="row")
        for c in range(4):
            button_frame.grid_columnconfigure(c, weight=1, uniform="col")

        for (r, c), val in layout.items():
            btn = tk.Label(button_frame, text=val, font=("Terminal", 18),
                           bg=BTN_BG, fg=CORAL if val in ['AC', 'CE'] else TEXT,
                           bd=0, padx=10, pady=10)

            btn.grid(row=r, column=c, sticky="nsew", padx=2, pady=2)
            self.add_btn_animations(btn, val)
            btn.bind("<Button-1>", lambda e, char=val: self.on_button_click(char))

        # Equal button spans two rows
        equal_btn = tk.Label(button_frame, text='=', font=("Terminal", 18),
                             bg=EQUAL_BTN, fg=TEXT, bd=0, padx=10, pady=10)
        equal_btn.grid(row=3, column=3, rowspan=2, sticky="nsew", padx=2, pady=2)
        self.add_equal_hover(equal_btn)
        equal_btn.bind("<Button-1>", lambda e: self.on_button_click('='))

    def on_button_click(self, char):
        if char == 'AC':
            self.equation = ""
        elif char == 'CE':
            self.equation = self.equation[:-1] if self.equation else ""
        elif char == '=':
            self.evaluate_code_or_calc()
            return
        elif char == '%':
            try:
                self.equation = str(eval(self.equation + "/100"))
            except:
                messagebox.showerror("Error", "Invalid Expression")
        else:
            self.equation += str(char)

        self.update_display()

    def update_display(self):
        self.display.delete(0, tk.END)
        self.display.insert(0, self.equation)

    def evaluate_code_or_calc(self):
        code = self.equation
        self.equation = ""

        if code == REGISTER_CODE:
            self.popup_input("Register", "Enter a username to register:", self.register_face)
        elif code == AUTH_CODE:
            self.popup_input("Authenticate", "Enter your username:", self.authenticate_user)
        else:
            try:
                result = str(eval(code))
                self.equation = result
            except:
                messagebox.showerror("Error", "Invalid Expression")

        self.update_display()

    def add_btn_animations(self, widget, val):
        widget.bind("<Enter>", lambda e: widget.config(fg=HOVER))
        widget.bind("<Leave>", lambda e: widget.config(fg=CORAL if val in ['AC', 'CE'] else TEXT))

    def add_equal_hover(self, widget):
        widget.bind("<Enter>", lambda e: widget.config(bg=EQUAL_HOVER, font=("Terminal", 20, "bold")))
        widget.bind("<Leave>", lambda e: widget.config(bg=EQUAL_BTN, font=("Terminal", 18)))

    # Placeholder methods
    def popup_input(self, title, prompt, callback):
        messagebox.showinfo(title, prompt + " (Simulated)")

    def register_face(self, username):
        print(f"Registering face for: {username}")

    def authenticate_user(self, username):
        print(f"Authenticating user: {username}")

if __name__ == "__main__":
    app = SmartCalcVault()
    app.mainloop()
'''
import tkinter as tk
from tkinter import messagebox
from gui.register_window import create_registration_window  # Import registration window

# Secret code trigger
SECRET_TRIGGER = "0000+-"

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
            create_registration_window()
            expression = ""  # Reset to prevent repeat triggers
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
