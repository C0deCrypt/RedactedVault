import tkinter as tk
from tkinter import ttk, messagebox

# Colors (same as vault)
BG = "#1C1C1C"  # Main background
TEXT = "#F5E8D8"  # Text color
CORAL = "#FF6F61"  # Accent color
GOLD = "#DAA520"  # Highlight color
HOVER = "#FF4500"  # Hover color
BORDER = "#333333"  # Border color


def validate_code_input(char):
    return char in "0123456789+-/*="


def create_auth_window():
    root = tk.Tk()
    root.title("Agent Authentication")
    root.geometry("500x600")  # Slightly smaller window for login
    root.configure(bg="#000000")

    # Main container
    main_frame = tk.Frame(root, bg=BORDER, padx=1, pady=1)
    main_frame.pack(fill="both", expand=True)

    content = tk.Frame(main_frame, bg=BG)
    content.pack(fill="both", expand=True, padx=20, pady=20)

    # Title
    title = tk.Label(content, text="AUTHENTICATION",
                     bg=BG, fg=CORAL, font=("Terminal", 24))  # Slightly smaller title
    title.pack(pady=(55, 35))

    # Username field
    tk.Label(content, text="Agent Codename:", bg=BG, fg=TEXT,
             font=("Terminal", 12)).pack(anchor="w", padx=20)

    username_entry = tk.Entry(content, bg="#252525", fg=TEXT,
                              font=("Consolas", 11),
                              insertbackground=TEXT, bd=0,
                              highlightthickness=1,
                              highlightcolor=BORDER)
    username_entry.pack(fill="x", padx=20, pady=(5, 15), ipady=5)


    # Biometric selection
    tk.Label(content, text="Biometric Authentication:",
             bg=BG, fg=TEXT, font=("Terminal", 12)).pack(anchor="w", padx=20, pady=(15, 5))

    bio_var = tk.StringVar(value="face")

    frame = tk.Frame(content, bg=BG)
    frame.pack(fill="x", padx=20)

    face_btn = tk.Radiobutton(
        frame, text="Facial Recognition", variable=bio_var, value="face",
        bg=BG, fg=TEXT, selectcolor=BG, activebackground=BG,
        font=("Terminal", 11), highlightthickness=0
    )
    face_btn.pack(side="left", padx=10)

    finger_btn = tk.Radiobutton(
        frame, text="Fingerprint", variable=bio_var, value="finger",
        bg=BG, fg=TEXT, selectcolor=BG, activebackground=BG,
        font=("Terminal", 11), highlightthickness=0
    )
    finger_btn.pack(side="left", padx=10)

    # Authentication button
    def on_auth():
        # TODO: Here you guys will handle authentication, because when user is clicking on Auth btn we are calling this function
        username = username_entry.get()
        method = bio_var.get() #is my type hai k finger use honi yaa face, dekh lena isko
        print("Auth btn is clicked")

    auth_btn = tk.Button(
        content, text="AUTHENTICATE",
        bg=CORAL,
        fg=TEXT,
        activebackground=HOVER,
        font=("Terminal", 12),
        bd=0,
        padx=15,
        pady=6,
        relief="flat",
        command=on_auth
    )
    auth_btn.pack(pady=(95,55), ipady=3)



    # Hover effects
    def on_enter_auth(e):
        e.widget.config(bg=HOVER)

    def on_leave_auth(e):
        e.widget.config(bg=CORAL)

    def on_enter_switch(e):
        e.widget.config(fg=HOVER)

    def on_leave_switch(e):
        e.widget.config(fg=TEXT)

    auth_btn.bind("<Enter>", on_enter_auth)
    auth_btn.bind("<Leave>", on_leave_auth)

    root.mainloop()


if __name__ == "__main__":
    create_auth_window()