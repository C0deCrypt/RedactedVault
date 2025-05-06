import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os

from db.db_manager import get_user_id, set_current_user
from gui.vault import create_vault_ui

BG = "#1C1C1C"
TEXT = "#F5E8D8"
CORAL = "#FF6F61"
HOVER = "#FF4500"
BORDER = "#333333"

def create_auth_window(passed_username):
    root = tk.Tk()
    root.title("Agent Authentication")
    root.geometry("500x600")
    root.configure(bg="#000000")

    main_frame = tk.Frame(root, bg=BORDER, padx=1, pady=1)
    main_frame.pack(fill="both", expand=True)

    content = tk.Frame(main_frame, bg=BG)
    content.pack(fill="both", expand=True, padx=20, pady=20)

    title = tk.Label(content, text="AUTHENTICATION", bg=BG, fg=CORAL, font=("Terminal", 24))
    title.pack(pady=(55, 35))

    tk.Label(content, text="Agent Codename:", bg=BG, fg=TEXT, font=("Terminal", 12)).pack(anchor="w", padx=20)
    username_entry = tk.Entry(content, bg="#252525", fg=TEXT, font=("Consolas", 11),
                              insertbackground=TEXT, bd=0, highlightthickness=1, highlightcolor=BORDER)
    username_entry.pack(fill="x", padx=20, pady=(5, 15), ipady=5)

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

    def on_auth():
        entered_username = username_entry.get().strip()
        method = bio_var.get()

        if entered_username != passed_username:
            messagebox.showerror("Error", "Username mismatch.")
            return

        if method == "face":
            try:
                from face_authentication.face_auth import authenticate_face
                success = authenticate_face(entered_username)
                if success:
                    user_id = get_user_id(entered_username)
                    if user_id:
                        set_current_user(entered_username, user_id)
                        messagebox.showinfo("Success", f"Welcome back, {entered_username}!")
                        root.destroy()
                        vault_root = tk.Tk()
                        create_vault_ui(vault_root)
                        vault_root.mainloop()
                else:
                    messagebox.showerror("Failed", "Face authentication failed.")
            except Exception as e:
                messagebox.showerror("Error", f"Face auth error: {e}")
        else:
            try:
                # Fingerprint capture
                capture_exe = os.path.abspath("../fingerprint/capture/CaptureFingerprint/x64/Debug/CaptureFingerprint.exe")
                subprocess.run([capture_exe, entered_username + "_live"], check=True)

                # Fingerprint matching
                match_script = os.path.abspath("../fingerprint/match_template.py")
                result = subprocess.run(
                    [sys.executable, match_script, entered_username],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                output = result.stdout.decode(errors="ignore").strip()
                print("[MATCH OUTPUT]:", output)

                if "AUTH_SUCCESS" in output:
                    user_id = get_user_id(entered_username)
                    if user_id:
                        set_current_user(entered_username, user_id)
                        messagebox.showinfo("Success", f"Welcome back, {entered_username}!")
                        root.destroy()
                        vault_root = tk.Tk()
                        create_vault_ui(vault_root)
                        vault_root.mainloop()
                else:
                    messagebox.showerror("Failed", "Fingerprint mismatch.")
            except Exception as e:
                messagebox.showerror("Error", f"Fingerprint error: {e}")

    auth_btn = tk.Button(content, text="AUTHENTICATE", bg=CORAL, fg=TEXT,
                         activebackground=HOVER, font=("Terminal", 12), bd=0,
                         padx=15, pady=6, relief="flat", command=on_auth)
    auth_btn.pack(pady=(95, 55), ipady=3)
    auth_btn.bind("<Enter>", lambda e: e.widget.config(bg=HOVER))
    auth_btn.bind("<Leave>", lambda e: e.widget.config(bg=CORAL))

    root.mainloop()

if __name__ == "__main__":
    create_auth_window("sample_user")
