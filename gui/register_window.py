import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import sys

from db.db_manager import set_current_user
from face_registeration.face_registeration import register_face  # Ensure this is implemented

# Colors
BG = "#1C1C1C"
TEXT = "#F5E8D8"
CORAL = "#FF6F61"
HOVER = "#FF4500"
BORDER = "#333333"

def validate_code_input(char):
    return char in "0123456789+-/*="

def create_registration_window(parent):
    root = tk.Tk()
    root.title("Agent Registration")
    root.geometry("500x600")
    root.configure(bg="#000000")

    main_frame = tk.Frame(root, bg=BORDER, padx=1, pady=1)
    main_frame.pack(fill="both", expand=True)

    content = tk.Frame(main_frame, bg=BG)
    content.pack(fill="both", expand=True, padx=20, pady=20)

    title = tk.Label(content, text="REGISTRATION", bg=BG, fg=CORAL, font=("Terminal", 24))
    title.pack(pady=(55, 35))

    # Username
    tk.Label(content, text="Agent Codename:", bg=BG, fg=TEXT, font=("Terminal", 12)).pack(anchor="w", padx=20)
    username_entry = tk.Entry(content, bg="#252525", fg=TEXT, font=("Consolas", 11),
                              insertbackground=TEXT, bd=0, highlightthickness=1, highlightcolor=BORDER)
    username_entry.pack(fill="x", padx=20, pady=(5, 15), ipady=5)

    # Unlock code
    tk.Label(content, text="Calculator Code", bg=BG, fg=TEXT, font=("Terminal", 12)).pack(anchor="w", padx=20)
    vcmd = (root.register(validate_code_input), '%S')
    code_entry = tk.Entry(content, bg="#252525", fg=TEXT, font=("Consolas", 11),
                          validate="key", validatecommand=vcmd,
                          insertbackground=TEXT, bd=0, highlightthickness=1,
                          highlightcolor=BORDER, show="•")
    code_entry.pack(fill="x", padx=20, pady=(5, 15), ipady=5)

    # Biometric method
    tk.Label(content, text="Biometric Authentication:", bg=BG, fg=TEXT, font=("Terminal", 12)).pack(anchor="w", padx=20, pady=(15, 5))

    bio_var = tk.StringVar(value="face")
    frame = tk.Frame(content, bg=BG)
    frame.pack(fill="x", padx=20)

    face_btn = tk.Radiobutton(frame, text="Facial Recognition", variable=bio_var, value="face",
                              bg=BG, fg=TEXT, selectcolor=BG, activebackground=BG,
                              font=("Terminal", 11), highlightthickness=0)
    face_btn.pack(side="left", padx=10)

    finger_btn = tk.Radiobutton(frame, text="Fingerprint", variable=bio_var, value="finger",
                                bg=BG, fg=TEXT, selectcolor=BG, activebackground=BG,
                                font=("Terminal", 11), highlightthickness=0)
    finger_btn.pack(side="left", padx=10)

    def on_register():
        username = username_entry.get().strip()
        code = code_entry.get().strip()
        method = bio_var.get()

        if not username or not code:
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        set_current_user(username, 1)  # Dummy ID for now

        if method == "face":
            success = register_face(username, code)
            if success:
                messagebox.showinfo("Success", "Face registered successfully!")
                root.destroy()
                if parent: parent.deiconify()
            else:
                messagebox.showerror("Failed", "Face registration failed.")
        else:
            try:
                capture_exe = os.path.abspath("../fingerprint/capture/CaptureFingerprint/x64/Debug/CaptureFingerprint.exe")
                subprocess.run([capture_exe, username], check=True)

                store_script = os.path.abspath("../fingerprint/store_template.py")
                subprocess.run([sys.executable, store_script, username, code], check=True)

                messagebox.showinfo("Success", "Fingerprint registered successfully!")
                root.destroy()
                if parent: parent.deiconify()

            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Fingerprint process failed: {e}")
            except Exception as e:
                messagebox.showerror("Error", f"Unexpected error: {e}")

    register_btn = tk.Button(content, text="REGISTRATION", bg=CORAL, fg=TEXT,
                             activebackground=HOVER, font=("Terminal", 12), bd=0,
                             padx=15, pady=6, relief="flat", command=on_register)
    register_btn.pack(pady=55, ipady=3)
    register_btn.bind("<Enter>", lambda e: e.widget.config(bg=HOVER))
    register_btn.bind("<Leave>", lambda e: e.widget.config(bg=CORAL))

    root.mainloop()

if __name__ == "__main__":
    create_registration_window(None)
