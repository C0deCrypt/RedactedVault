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

def animate_text(label, text):
    """Typewriter effect for text animation"""
    label.config(text="")
    for i in range(len(text) + 1):
        label.after(50 * i, lambda s=text[:i]: label.config(text=s))

def add_file_card(parent, filename, icon, idx):
    """Create a file card with hover effects"""
    card = tk.Frame(parent, bg="#252525", bd=0)
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
    chk = tk.Checkbutton(card, variable=var, bg="#252525",
                        activebackground="#252525", selectcolor=BG)
    chk.pack(side="right", padx=10)

    # Hover effect
    card.bind("<Enter>", lambda e, c=card: c.config(bg="#333"))
    card.bind("<Leave>", lambda e, c=card: c.config(bg="#252525"))
    return card

def add_btn_light(button):
    """Add hover effects to buttons"""
    button.bind("<Enter>", lambda e: button.config(fg=HOVER))
    button.bind("<Leave>", lambda e: button.config(fg=TEXT))
    button.config(highlightbackground=BORDER, highlightthickness=1)

def create_vault_ui(root):
    """Main function to create the vault interface"""
    # Window setup
    root.geometry("1280x720")
    root.configure(bg="#000000")
    root.title("NEO VAULT")

    # Main Container with subtle border
    main_frame = tk.Frame(root, bg=BORDER, padx=1, pady=1)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Content Area
    content = tk.Frame(main_frame, bg=BG)
    content.pack(fill="both", expand=True)

    # User Profile Header
    header = tk.Frame(content, bg=BG, bd=0)
    header.pack(fill="x", pady=(20, 10), padx=20)

    # Avatar
    try:
        avatar_img = Image.open("avatar.png").resize((80, 80))
        avatar_photo = ImageTk.PhotoImage(avatar_img)
        avatar_label = tk.Label(header, image=avatar_photo, bg=BG)
        avatar_label.image = avatar_photo  # Keep reference
    except:
        avatar_label = tk.Label(header, text="👤", bg=BG, fg=GOLD,
                              font=("Segoe UI Emoji", 36))
    avatar_label.pack(side="left")

    # User Info
    user_frame = tk.Frame(header, bg=BG)
    user_frame.pack(side="left", padx=15)

    tk.Label(user_frame, text="AGENT PROFILE", bg=BG, fg=CORAL,
            font=("Terminal", 10)).pack(anchor="w")
    user_label = tk.Label(user_frame, text="", bg=BG, fg=TEXT,
                         font=("Terminal", 12))
    user_label.pack(anchor="w")
    animate_text(user_label, "Cyber_Operative_7")

    # File Display Area
    file_container = tk.Frame(content, bg=BORDER, padx=1, pady=1)
    file_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    file_canvas = tk.Canvas(file_container, bg=BG, highlightthickness=0)
    scrollbar = ttk.Scrollbar(file_container, orient="vertical",
                             command=file_canvas.yview)
    scrollable_frame = tk.Frame(file_canvas, bg=BG)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: file_canvas.configure(scrollregion=file_canvas.bbox("all"))
    )

    file_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    file_canvas.configure(yscrollcommand=scrollbar.set)

    file_canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Sample Files
    files = [
        ("secret_plans.txt", "📄"),
        ("bitcoin_keys.pdf", "📄"),
        ("mission_briefing.mp4", "🎥"),
        ("suspicious_cat.jpg", "🖼️"),
        ("backup_codes.txt", "📄")
    ]

    for i, (fname, icon) in enumerate(files):
        add_file_card(scrollable_frame, fname, icon, i)

    # Control Buttons
    controls = tk.Frame(content, bg=BG)
    controls.pack(fill="x", pady=(0, 20), padx=20)

    def add_file():
        print("Add file dialog")

    def view_file():
        print("View file with auth check")

    def delete_file():
        print("Delete confirmation")

    buttons = [
        ("➕ Add", add_file),
        ("👁️ View", view_file),
        ("🗑️ Delete", delete_file),
        ("🔐 Lock", root.quit)
    ]

    for text, cmd in buttons:
        btn = tk.Button(controls, text=text, bg=BG, fg=TEXT,
                       activebackground=HOVER, bd=0, font=("Terminal", 10),
                       command=cmd)
        btn.pack(side="left", padx=10)
        add_btn_light(btn)

    return {
        'root': root,
        'file_canvas': file_canvas,
        'scrollable_frame': scrollable_frame
    }

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    ui = create_vault_ui(root)
    root.mainloop()