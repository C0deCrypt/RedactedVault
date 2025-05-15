import os
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
from db.db_manager import get_files_for_user, get_current_user, set_current_user, get_current_user_id
import shutil
import uuid
import tempfile
from cryptography.fernet import Fernet
import threading
import time
from db.db_manager import (
    get_current_user_id,
    get_connection,
    insert_file_record,
    delete_file_record,
    get_file_record_by_id
)

# Colors
BG = "#1C1C1C"  # Main background
TEXT = "#F5E8D8"  # Text color
CORAL = "#FF6F61"  # Accent color
GOLD = "#DAA520"  # Highlight color
HOVER = "#FF4500"  # Hover color
BORDER = "#333333"  # Border color

def get_file_icon(filename):
    extension = filename.split('.')[-1].lower()
    icon_map = {
        'txt': '📄',  'pdf': '📄',  'doc': '📄', 'docx': '📄',
        'jpg': '🖼️', 'png': '🖼️', 'gif': '🖼️',
        'mp4': '🎥', 'mov': '🎥', 'avi': '🎥',
        'zip': '🗄️', 'rar': '🗄️',
        'exe': '⚙️', 'py': '🐍'
    }
    return icon_map.get(extension, '📁')  # Default icon

# Global variable to track selected file
selected_file_id = None
checkbox_vars = {} # {file_id: tk.IntVar()}


def animate_text(label, text):
    """Creates typewriter effect for text"""
    label.config(text="")
    for i in range(len(text) + 1):
        label.after(200 * i, lambda s=text[:i]: label.config(text=s))


def create_file_row(parent, filename, icon, file_id):
    """Creates a single file row with selection checkbox"""
    global selected_file_id, checkbox_vars

    row = tk.Frame(parent, bg="#252525", bd=0, highlightthickness=0)
    row.pack(fill="x", pady=1, ipady=5)

    # File icon
    icon_label = tk.Label(row, text=icon, bg="#252525", fg=GOLD,
                          font=("Segoe UI Emoji", 14), padx=10)
    icon_label.pack(side="left")

    # File name
    name_label = tk.Label(row, text=filename, bg="#252525", fg=TEXT,
                          font=("Consolas", 11), anchor="w")
    name_label.pack(side="left", fill="x", expand=True, padx=5)

    # Selection checkbox (only one file can be selected)
    var = tk.IntVar()
    checkbox_vars[file_id] = var  # Store the variable
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
        command=lambda: update_selection(file_id)
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

    return row


# Simplify the update_selection function
def update_selection(file_id):
    """Handles file selection (only one file at a time)"""
    global selected_file_id, checkbox_vars

    # If this checkbox is being checked
    if checkbox_vars[file_id].get():
        # Uncheck all other checkboxes
        for fid, var in checkbox_vars.items():
            if fid != file_id:
                var.set(0)

        selected_file_id = file_id
    else:
        selected_file_id = None

    update_button_states()


def update_button_states():
    """Enable/disable buttons based on selection"""
    for btn in [view_btn, delete_btn]:
        btn.config(state=tk.NORMAL if selected_file_id else tk.DISABLED)


def create_vault_ui(root):
    """Main function to create the vault interface"""
    global view_btn, delete_btn  # Make buttons accessible for state updates
    curr_user = get_current_user()
    curr_user_id = get_current_user_id()

    # Window setup
    root.geometry("1280x720")
    root.title("Secure Vault")
    root.configure(bg="#000000")

    # Main container
    main_frame = tk.Frame(root, bg=BORDER, padx=1, pady=1)
    main_frame.pack(fill="both", expand=True)

    # Content area
    content = tk.Frame(main_frame, bg=BG)
    content.pack(fill="both", expand=True)

    # User profile header
    header = create_user_header(content, curr_user)

    # File display area with scroll
    file_container = tk.Frame(content, bg=BORDER, padx=1, pady=1)
    file_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    file_canvas = tk.Canvas(file_container, bg=BG, highlightthickness=0)
    scrollbar = ttk.Scrollbar(file_container, orient="vertical",
                              command=file_canvas.yview)

    scrollable_frame = tk.Frame(file_canvas, bg=BG)

    def configure_canvas(e):
        """Adjusts scrollable area width"""
        file_canvas.itemconfig("frame", width=e.width - scrollbar.winfo_width())
        file_canvas.configure(scrollregion=file_canvas.bbox("all"))

    file_canvas.create_window((0, 0), window=scrollable_frame,
                              anchor="nw", tags=("frame",))
    file_canvas.bind("<Configure>", configure_canvas)
    file_canvas.configure(yscrollcommand=scrollbar.set)

    file_canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    try:
        files = get_files_for_user()  # Returns list of dictionaries
        for file_record in files:
            # Extract fields from the database record
            filename = file_record['filename']
            file_id = file_record['id']

            # Get the appropriate icon based on filename
            icon = get_file_icon(filename)

            # Create the file row in the scrollable frame
            create_file_row(scrollable_frame, filename, icon, file_id)

    except Exception as e:
        print(f"Unexpected error loading files: {e}")
        # Generic error display
        error_label = tk.Label(scrollable_frame,
                               text="Failed to load files",
                               fg=CORAL, bg=BG)
        error_label.pack(pady=20)

    # Control buttons
    controls = tk.Frame(content, bg=BG)
    controls.pack(fill="x", pady=(0, 20), padx=20)


    # Load encryption key (already encrypted and saved securely)
    with open("secret.key", "rb") as key_file:
        fernet = Fernet(key_file.read())

    HIDDEN_FOLDER = ".vault_hidden"
    os.makedirs(HIDDEN_FOLDER, exist_ok=True)

    def encrypt_and_save_file(original_path):
        user_id = get_current_user_id()
        if not user_id:
            raise ValueError("User not authenticated")

        with open(original_path, "rb") as f:
            original_data = f.read()

        encrypted_data = fernet.encrypt(original_data)
        random_filename = str(uuid.uuid4())  # Random name for security
        hidden_path = os.path.join(HIDDEN_FOLDER, random_filename)

        with open(hidden_path, "wb") as f:
            f.write(encrypted_data)

        # Save original name and path to DB
        insert_file_record(
            user_id=user_id,
            original_name=os.path.basename(original_path),
            hidden_path=hidden_path
        )

    def add_file():


        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename()

        if file_path:
            encrypt_and_save_file(file_path)
            print("File added successfully.")
            for widget in scrollable_frame.winfo_children():
                widget.destroy()

            files = get_files_for_user()  # Fetch updated files list
            for file_record in files:
                filename = file_record['filename']
                file_id = file_record['id']
                icon = get_file_icon(filename)
                create_file_row(scrollable_frame, filename, icon, file_id)

    def delete_file(file_id):
        record = get_file_record_by_id(file_id)

        if not record:
            print("File not found.")
            return

        try:
            if os.path.exists(record['filepath']):
                os.remove(record['filepath'])
            delete_file_record(file_id)
            print("File deleted.")
            for widget in scrollable_frame.winfo_children():
                widget.destroy()

            files = get_files_for_user()  # Fetch updated files list
            for file_record in files:
                filename = file_record['filename']
                file_id = file_record['id']
                icon = get_file_icon(filename)
                create_file_row(scrollable_frame, filename, icon, file_id)
        except Exception as e:
            print(f"Error deleting file: {e}")

    def view_file(file_id):
        record = get_file_record_by_id(file_id)
        if not record:
            print("File not found.")
            return

        try:
            with open(record['filepath'], "rb") as f:
                encrypted_data = f.read()

            decrypted_data = fernet.decrypt(encrypted_data)

            temp_dir = tempfile.mkdtemp()
            temp_path = os.path.join(temp_dir, record['filename'])

            with open(temp_path, "wb") as f:
                f.write(decrypted_data)

                # Open file using default program
                os.startfile(temp_path)

                # Run cleanup in background after delay
                def delayed_cleanup():
                    time.sleep(30)  # give user 30 seconds to view it
                    try:
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                        if os.path.exists(temp_dir):
                            shutil.rmtree(temp_dir)
                        print("Temporary file cleaned up.")
                    except Exception as e:
                        print(f"Error during cleanup: {e}")

                threading.Thread(target=delayed_cleanup).start()

        except Exception as e:
            print(f"Error viewing file: {e}")

    # Create buttons
    add_btn = tk.Button(controls, text="➕ Add", bg=BG, fg=TEXT,
                        activebackground=HOVER, bd=0, font=("Terminal", 10),
                        command=add_file)
    add_btn.pack(side="left", padx=10)

    view_btn = tk.Button(controls, text="👁️ View", bg=BG, fg=TEXT,
                         activebackground=HOVER, bd=0, font=("Terminal", 10),
                         command=lambda: view_file(selected_file_id), state=tk.DISABLED)
    view_btn.pack(side="left", padx=10)

    delete_btn = tk.Button(controls, text="🗑️ Delete", bg=BG, fg=TEXT,
                           activebackground=HOVER, bd=0, font=("Terminal", 10),
                           command=lambda: delete_file(selected_file_id), state=tk.DISABLED)
    delete_btn.pack(side="left", padx=10)

    lock_btn = tk.Button(controls, text="🔐 Lock", bg=BG, fg=TEXT,
                         activebackground=HOVER, bd=0, font=("Terminal", 10),
                         command=lambda: root.destroy())
    lock_btn.pack(side="left", padx=10)

    # Add hover effects to all buttons
    for btn in [add_btn, view_btn, delete_btn, lock_btn]:
        btn.bind("<Enter>", lambda e: e.widget.config(fg=HOVER))
        btn.bind("<Leave>", lambda e: e.widget.config(fg=TEXT))
        btn.config(highlightbackground=BORDER, highlightthickness=1)


def create_user_header(parent, curr_user):
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
    animate_text(user_label, curr_user)

    return header


if __name__ == "__main__":
    root = tk.Tk()
    create_vault_ui(root)
    root.mainloop()