# import tkinter as tk
# from tkinter import messagebox
# import pickle
#
# # Secret codes
# REGISTER_CODE = "0000+"
# AUTH_CODE = "1234+"
#
# # Colors
# BG = "#1C1C1C"
# TEXT = "#F5E8D8"
# CORAL = "#FF6F61"
# GOLD = "#DAA520"
# HOVER = "#FF4500"
# BORDER = "#333333"
#
# class SmartCalcVault(tk.Tk):
#     def __init__(self):
#         super().__init__()
#
#         self.title("Smart Calculator")
#         self.geometry("350x500")
#         self.configure(bg=BG)
#         self.resizable(False, False)
#
#         self.equation = ""
#
#         # Display
#         self.display = tk.Entry(self, font=("Consolas", 26), bg="#252525", fg=TEXT,
#                                 insertbackground=TEXT, justify='right', bd=0, relief='flat')
#         self.display.pack(padx=20, pady=20, fill="x", ipady=10)
#
#         # Buttons
#         buttons = [
#             ['7', '8', '9', '+'],
#             ['4', '5', '6', '-'],
#             ['1', '2', '3', '*'],
#             ['C', '0', '.', '/'],
#             ['=']
#         ]
#
#         for row_values in buttons:
#             row = tk.Frame(self, bg=BG)
#             row.pack(padx=10, pady=5, fill="x")
#             for val in row_values:
#                 btn = tk.Button(row, text=val, font=("Terminal", 14), bg=BG, fg=TEXT,
#                                 activebackground=HOVER, activeforeground=TEXT,
#                                 bd=0, width=5, height=2,
#                                 command=lambda char=val: self.on_button_click(char))
#                 btn.pack(side="left", expand=True, fill="both", padx=2, pady=2)
#                 self.add_btn_light(btn)
#
#     def on_button_click(self, char):
#         if char == 'C':
#             self.equation = ""
#         elif char == '=':
#             self.evaluate_code_or_calc()
#         else:
#             self.equation += str(char)
#         self.display.delete(0, tk.END)
#         self.display.insert(0, self.equation)
#
#     def evaluate_code_or_calc(self):
#         code = self.equation
#         self.equation = ""
#         self.display.delete(0, tk.END)
#
#         if code == REGISTER_CODE:
#             self.popup_input("Register", "Enter a username to register:", register_face)
#         elif code == AUTH_CODE:
#             self.popup_input("Authenticate", "Enter your username:", self.authenticate_user)
#         else:
#             try:
#                 result = str(eval(code))
#                 self.equation = result
#             except:
#                 self.equation = ""
#                 messagebox.showerror("Error", "Invalid Expression")
#         self.display.insert(0, self.equation)
#
#     def authenticate_user(self, username):
#         # Check if the username exists and matches the stored data
#         try:
#             with open("users.pkl", "rb") as f:
#                 users = pickle.load(f)
#             if username in users:
#                 # Authentication passed
#                 self.open_vault()
#             else:
#                 messagebox.showerror("Authentication Error", "Username not registered.")
#         except FileNotFoundError:
#             messagebox.showerror("Authentication Error", "No registered users.")
#
#     def popup_input(self, title, prompt, action_callback):
#         popup = tk.Toplevel(self)
#         popup.title(title)
#         popup.configure(bg=BG)
#         popup.geometry("300x120")
#         popup.resizable(False, False)
#
#         tk.Label(popup, text=prompt, font=("Consolas", 11), bg=BG, fg=CORAL).pack(pady=(15, 5))
#         entry = tk.Entry(popup, font=("Consolas", 12), bg="#252525", fg=TEXT,
#                          insertbackground=TEXT, relief="flat")
#         entry.pack(pady=5, padx=20, fill="x")
#
#         def submit():
#             username = entry.get().strip()
#             if username:
#                 popup.destroy()
#                 action_callback(username)
#
#         btn = tk.Button(popup, text="OK", bg=BORDER, fg=TEXT, activebackground=HOVER,
#                         font=("Terminal", 10), command=submit)
#         btn.pack(pady=10)
#         self.add_btn_light(btn)
#
#     def add_btn_light(self, widget):
#         widget.bind("<Enter>", lambda e: widget.config(fg=HOVER))
#         widget.bind("<Leave>", lambda e: widget.config(fg=TEXT))
#         widget.config(highlightbackground=BORDER, highlightthickness=1)
#
#     def open_vault(self):
#         # Open the actual vault application (vault.py)
#         import vault
#         vault.launch_vault()
#
# if __name__ == "__main__":
#     app = SmartCalcVault()
#     app.mainloop()
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