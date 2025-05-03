import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import random

# Colors
BG = "#1C1C1C"
TEXT = "#F5E8D8"
CORAL = "#FF6F61"
GOLD = "#DAA520"
HOVER = "#FF4500"
BORDER = "#333333"


class VaultUI:
    def __init__(self, master):
        self.master = master
        master.geometry("1280x720")
        master.configure(bg=BG)

        # Main Container with subtle border
        self.main_frame = tk.Frame(master, bg=BORDER, padx=1, pady=1)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Content Area
        self.content = tk.Frame(self.main_frame, bg=BG)
        self.content.pack(fill="both", expand=True)

        # User Profile Header
        self.header = tk.Frame(self.content, bg=BG, bd=0)
        self.header.pack(fill="x", pady=(20, 10), padx=20)

        # Anime Avatar (Replaced circle)
        try:
            self.avatar_img = Image.open("avatar.png").resize((80, 80))
            self.avatar_photo = ImageTk.PhotoImage(self.avatar_img)
            self.avatar_label = tk.Label(self.header, image=self.avatar_photo, bg=BG)
        except:
            # Fallback if image not found
            self.avatar_label = tk.Label(self.header, text="👤", bg=BG, fg=GOLD,
                                         font=("Segoe UI Emoji", 36))
        self.avatar_label.pack(side="left")

        # User Info
        self.user_frame = tk.Frame(self.header, bg=BG)
        self.user_frame.pack(side="left", padx=15)

        tk.Label(self.user_frame, text="AGENT PROFILE", bg=BG, fg=CORAL,
                 font=("Terminal", 10)).pack(anchor="w")
        self.user_label = tk.Label(self.user_frame, text="", bg=BG, fg=TEXT,
                                   font=("Terminal", 12))
        self.user_label.pack(anchor="w")
        self.animate_text("Cyber_Operative_7", self.user_label)

        # File Display Area with border
        self.file_container = tk.Frame(self.content, bg=BORDER, padx=1, pady=1)
        self.file_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.file_canvas = tk.Canvas(self.file_container, bg=BG, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.file_container, orient="vertical",
                                       command=self.file_canvas.yview)
        self.scrollable_frame = tk.Frame(self.file_canvas, bg=BG)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.file_canvas.configure(
                scrollregion=self.file_canvas.bbox("all")
            )
        )

        self.file_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.file_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.file_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Sample Files
        files = [
            ("secret_plans.txt", "📄"),
            ("bitcoin_keys.pdf", "📄"),
            ("mission_briefing.mp4", "🎥"),
            ("suspicious_cat.jpg", "🖼️"),
            ("backup_codes.txt", "📄")
        ]

        for i, (fname, icon) in enumerate(files):
            self.add_file_card(fname, icon, i)

        # Control Buttons with subtle lighting
        self.controls = tk.Frame(self.content, bg=BG)
        self.controls.pack(fill="x", pady=(0, 20), padx=20)

        buttons = [
            ("➕ Add", self.add_file),
            ("👁️ View", self.view_file),
            ("🗑️ Delete", self.delete_file),
            ("🔐 Lock", lambda: master.quit())
        ]

        for text, cmd in buttons:
            btn = tk.Button(self.controls, text=text, bg=BG, fg=TEXT,
                            activebackground=HOVER, bd=0, font=("Terminal", 10),
                            command=cmd)
            btn.pack(side="left", padx=10)
            self.add_btn_light(btn)

    def animate_text(self, text, label):
        label.config(text="")
        for i in range(len(text) + 1):
            label.after(50 * i, lambda s=text[:i]: label.config(text=s))

    def add_file_card(self, filename, icon, idx):
        card = tk.Frame(self.scrollable_frame, bg="#252525", bd=0)
        card.pack(fill="x", pady=2, padx=2)

        # File Icon
        tk.Label(card, text=icon, bg="#252525", fg=GOLD,
                 font=("Segoe UI Emoji", 14)).pack(side="left", padx=10)

        # Filename
        name_label = tk.Label(card, text=filename, bg="#252525", fg=TEXT,
                              font=("Consolas", 10), anchor="w")
        name_label.pack(side="left", fill="x", expand=True)

        # Selection Checkbox
        var = tk.IntVar()
        chk = tk.Checkbutton(card, variable=var, bg="#252525", activebackground="#252525",
                             selectcolor=BG)
        chk.pack(side="right", padx=10)

        # Hover effect
        card.bind("<Enter>", lambda e, c=card: c.config(bg="#333"))
        card.bind("<Leave>", lambda e, c=card: c.config(bg="#252525"))

    def add_btn_light(self, widget):
        # Subtle border lighting effect
        widget.bind("<Enter>", lambda e: widget.config(fg=HOVER))
        widget.bind("<Leave>", lambda e: widget.config(fg=TEXT))

        # Add permanent thin border
        widget.config(highlightbackground=BORDER, highlightthickness=1)

    def add_file(self):
        print("Add file dialog")

    def view_file(self):
        print("View file with auth check")

    def delete_file(self):
        print("Delete confirmation")


# Run
root = tk.Tk()
root.title("NEO VAULT")
root.configure(bg="#000000")
VaultUI(root)
root.mainloop()