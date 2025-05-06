import tkinter as tk
from tkinter import messagebox
from db.db_manager import get_username_by_unlock_code
from gui.authenticate_window import create_auth_window
from gui.register_window import create_registration_window

# Constants
SECRET_TRIGGER = "0000+-"
expression = ""

# Colors
BG = "#1C1C1C"
TEXT = "#F5E8D8"
CORAL = "#FF6F61"
GOLD = "#DAA520"
HOVER = "#FF4500"
BORDER = "#333333"
BTN_BG = "#252525"
EQUAL_BTN = "#FF6F61"
EQUAL_HOVER = "#FF4500"

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

        # Equal button
        equal_btn = tk.Label(button_frame, text='=', font=("Terminal", 18),
                             bg=EQUAL_BTN, fg=TEXT, bd=0, padx=10, pady=10)
        equal_btn.grid(row=3, column=3, rowspan=2, sticky="nsew", padx=2, pady=2)
        self.add_equal_hover(equal_btn)
        equal_btn.bind("<Button-1>", lambda e: self.on_button_click('='))

    def on_button_click(self, char):
        if char == 'AC':
            self.equation = ""
        elif char == 'CE':
            self.equation = self.equation[:-1]
        elif char == '=':
            self.evaluate_expression()
            return
        elif char == '%':
            try:
                self.equation = str(eval(self.equation + "/100"))
            except:
                messagebox.showerror("Error", "Invalid Expression")
        else:
            self.equation += str(char)

        self.update_display()

        # Logic for registration/authentication
        if self.equation.endswith(SECRET_TRIGGER):
            self.withdraw()
            create_registration_window(self)
            self.equation = ""
            self.update_display()
        elif len(self.equation) >= 6:
            username = get_username_by_unlock_code(self.equation)
            if username:
                self.destroy()
                create_auth_window(username)
            else:
                messagebox.showerror("Error", "Invalid unlock code.")
            self.equation = ""
            self.update_display()

    def update_display(self):
        self.display.delete(0, tk.END)
        self.display.insert(0, self.equation)

    def evaluate_expression(self):
        try:
            result = str(eval(self.equation))
            self.equation = result
        except:
            messagebox.showerror("Error", "Invalid Expression")
            self.equation = ""
        self.update_display()

    def add_btn_animations(self, widget, val):
        widget.bind("<Enter>", lambda e: widget.config(fg=HOVER, font=("Terminal", 20, "bold")))
        widget.bind("<Leave>", lambda e: widget.config(fg=CORAL if val in ['AC', 'CE'] else TEXT,  font=("Terminal", 18)))

    def add_equal_hover(self, widget):
        widget.bind("<Enter>", lambda e: widget.config(bg=EQUAL_HOVER, font=("Terminal", 20, "bold")))
        widget.bind("<Leave>", lambda e: widget.config(bg=EQUAL_BTN, font=("Terminal", 18)))


if __name__ == "__main__":
    app = SmartCalcVault()
    app.mainloop()
