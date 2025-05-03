import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from services.file_storage import FileStorageSystem
from db.db_manager import get_files_for_user, log_access
import os

# Colors
BG = "#1C1C1C"  # Main background
TEXT = "#F5E8D8"  # Text color
CORAL = "#FF6F61"  # Accent color
GOLD = "#DAA520"  # Highlight color
HOVER = "#FF4500"  # Hover color
BORDER = "#333333"  # Border color


class VaultApp:
    def __init__(self, root):
        self.root = root
        self.user_id = 1  # Replace with actual authenticated user ID
        self.file_storage = FileStorageSystem()
        self.selected_file_id = None
        self.setup_ui()

    def setup_ui(self):
        """Setup the main UI components"""
        self.root.geometry("1280x720")
        self.root.title("Secure Vault")
        self.root.configure(bg="#000000")

        # Main container
        main_frame = tk.Frame(self.root, bg=BORDER, padx=1, pady=1)
        main_frame.pack(fill="both", expand=True)

        # Content area
        content = tk.Frame(main_frame, bg=BG)
        content.pack(fill="both", expand=True)

        # User profile header
        self.create_user_header(content)

        # File display area with scroll
        self.setup_file_display(content)

        # Control buttons
        self.setup_control_buttons(content)

        # Load files from database
        self.load_files()

    def create_user_header(self, parent):
        """Creates the user profile header section"""
        header = tk.Frame(parent, bg=BG, bd=0)
        header.pack(fill="x", pady=(20, 10), padx=20)

        # Avatar image or placeholder
        try:
            avatar_img = Image.open("avatar.png").resize((80, 80))
            avatar_photo = ImageTk.PhotoImage(avatar_img)
            avatar_label = tk.Label(header, image=avatar_photo, bg=BG)
            avatar_label.image = avatar_photo  # Keep reference
        except:
            avatar_label = tk.Label(header, text="👤", bg=BG, fg=GOLD,
                                    font=("Segoe UI Emoji", 36))
        avatar_label.pack(side="left")

        # User info
        user_frame = tk.Frame(header, bg=BG)
        user_frame.pack(side="left", padx=15)

        tk.Label(user_frame, text="USER PROFILE", bg=BG, fg=CORAL,
                 font=("Terminal", 10)).pack(anchor="w")

        user_label = tk.Label(user_frame, text="", bg=BG, fg=TEXT,
                              font=("Terminal", 12))
        user_label.pack(anchor="w")
        self.animate_text(user_label, "Secure_User_01")

    def animate_text(self, label, text):
        """Creates typewriter effect for text"""
        label.config(text="")
        for i in range(len(text) + 1):
            label.after(50 * i, lambda s=text[:i]: label.config(text=s))

    def setup_file_display(self, parent):
        """Setup the file display area with scroll"""
        file_container = tk.Frame(parent, bg=BORDER, padx=1, pady=1)
        file_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.file_canvas = tk.Canvas(file_container, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(file_container, orient="vertical",
                                  command=self.file_canvas.yview)

        self.scrollable_frame = tk.Frame(self.file_canvas, bg=BG)

        def configure_canvas(e):
            """Adjusts scrollable area width"""
            self.file_canvas.itemconfig("frame", width=e.width - scrollbar.winfo_width())
            self.file_canvas.configure(scrollregion=self.file_canvas.bbox("all"))

        self.file_canvas.create_window((0, 0), window=self.scrollable_frame,
                                       anchor="nw", tags=("frame",))
        self.file_canvas.bind("<Configure>", configure_canvas)
        self.file_canvas.configure(yscrollcommand=scrollbar.set)

        self.file_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def load_files(self):
        """Load files from database into the GUI"""
        # Clear existing files
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Get files from database
        files = get_files_for_user(self.user_id)

        for file in files:
            self.create_file_row(
                file['filename'],
                self.get_file_icon(file['filename']),
                file['id']
            )

    def get_file_icon(self, filename):
        """Get appropriate icon based on file extension"""
        ext = os.path.splitext(filename)[1].lower()
        if ext in ['.txt', '.csv', '.json']:
            return "📄"
        elif ext in ['.jpg', '.jpeg', '.png', '.gif']:
            return "🖼️"
        elif ext in ['.mp4', '.avi', '.mov']:
            return "🎥"
        elif ext in ['.pdf']:
            return "📕"
        else:
            return "📁"

    def create_file_row(self, filename, icon, file_id):
        """Creates a single file row with selection checkbox"""
        row = tk.Frame(self.scrollable_frame, bg="#252525", bd=0, highlightthickness=0)
        row.pack(fill="x", pady=1, ipady=5)

        # File icon
        icon_label = tk.Label(row, text=icon, bg="#252525", fg=GOLD,
                              font=("Segoe UI Emoji", 14), padx=10)
        icon_label.pack(side="left")

        # File name
        name_label = tk.Label(row, text=filename, bg="#252525", fg=TEXT,
                              font=("Consolas", 11), anchor="w")
        name_label.pack(side="left", fill="x", expand=True, padx=5)

        # Selection checkbox
        var = tk.IntVar()
        chk = tk.Checkbutton(
            row,
            variable=var,
            bg="#252525",
            activebackground="#252525",
            selectcolor=BG,
            fg=GOLD,
            activeforeground=GOLD,
            bd=0,
            highlightthickness=0,
            padx=10,
            command=lambda: self.update_selection(file_id, var)
        )
        chk.pack(side="right")

        # Hover effect
        def set_hover(color):
            row.config(bg=color)
            for child in row.winfo_children():
                if isinstance(child, (tk.Label, tk.Checkbutton)):
                    child.config(bg=color)

        row.bind("<Enter>", lambda e: set_hover("#333"))
        row.bind("<Leave>", lambda e: set_hover("#252525"))

    def update_selection(self, file_id, checkbox_var):
        """Handles file selection"""
        if checkbox_var.get():
            self.selected_file_id = file_id
        else:
            self.selected_file_id = None
        self.update_button_states()

    def update_button_states(self):
        """Enable/disable buttons based on selection"""
        for btn in [self.view_btn, self.delete_btn]:
            btn.config(state=tk.NORMAL if self.selected_file_id else tk.DISABLED)

    def setup_control_buttons(self, parent):
        """Setup the control buttons at the bottom"""
        controls = tk.Frame(parent, bg=BG)
        controls.pack(fill="x", pady=(0, 20), padx=20)

        # Add button
        self.add_btn = tk.Button(controls, text="➕ Add", bg=BG, fg=TEXT,
                                 activebackground=HOVER, bd=0, font=("Terminal", 10),
                                 command=self.add_file)
        self.add_btn.pack(side="left", padx=10)

        # View button
        self.view_btn = tk.Button(controls, text="👁️ View", bg=BG, fg=TEXT,
                                  activebackground=HOVER, bd=0, font=("Terminal", 10),
                                  command=self.view_file, state=tk.DISABLED)
        self.view_btn.pack(side="left", padx=10)

        # Delete button
        self.delete_btn = tk.Button(controls, text="🗑️ Delete", bg=BG, fg=TEXT,
                                    activebackground=HOVER, bd=0, font=("Terminal", 10),
                                    command=self.delete_file, state=tk.DISABLED)
        self.delete_btn.pack(side="left", padx=10)

        # Lock button
        lock_btn = tk.Button(controls, text="🔐 Lock", bg=BG, fg=TEXT,
                             activebackground=HOVER, bd=0, font=("Terminal", 10),
                             command=self.root.quit)
        lock_btn.pack(side="left", padx=10)

        # Add hover effects
        for btn in [self.add_btn, self.view_btn, self.delete_btn, lock_btn]:
            btn.bind("<Enter>", lambda e: e.widget.config(fg=HOVER))
            btn.bind("<Leave>", lambda e: e.widget.config(fg=TEXT))
            btn.config(highlightbackground=BORDER, highlightthickness=1)

    def add_file(self):
        """Handle file addition"""
        filepath = filedialog.askopenfilename()
        if filepath:
            try:
                file_id = self.file_storage.add_file_to_vault(self.user_id, filepath)
                log_access(self.user_id, "file_add", f"Added file ID: {file_id}")
                self.load_files()  # Refresh file list
                messagebox.showinfo("Success", "File added to vault!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add file: {str(e)}")

    def view_file(self):
        """Handle file viewing"""
        if self.selected_file_id:
            try:
                self.file_storage.open_file_from_vault(self.selected_file_id, self.user_id)
                log_access(self.user_id, "file_view", f"Viewed file ID: {self.selected_file_id}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file: {str(e)}")

    def delete_file(self):
        """Handle file deletion"""
        if self.selected_file_id:
            if messagebox.askyesno("Confirm", "Delete this file permanently?"):
                try:
                    self.file_storage.delete_file_from_vault(self.selected_file_id, self.user_id)
                    log_access(self.user_id, "file_delete", f"Deleted file ID: {self.selected_file_id}")
                    self.selected_file_id = None
                    self.update_button_states()
                    self.load_files()  # Refresh file list
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to delete file: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = VaultApp(root)
    root.mainloop()