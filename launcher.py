import tkinter as tk
from tkinter import messagebox
import subprocess
import sys

CONTROLS_OBJECT = """=== CONTROLS: OBJECT ANNOTATOR ===

RMB - Draw bbox
W,S - Change object class
D   - Save and Next image
A   - Save and Previous image
Z   - Undo last bbox
C   - Clear current image annotations
Q   - Quit/Back to menu"""

CONTROLS_ROOM = """=== CONTROLS: ROOM ANNOTATOR ===

RMB       - Add point
SPACE/MMB - Close/Finish current polygon
W,S       - Change room class
Z         - Undo last point
D         - Save and Next image
A         - Save and Previous image
C         - Clear current image annotations
Q         - Quit/Back to menu"""

class AnnotatorLauncher(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Floorplan Annotator Hub")
        self.geometry("500x480") 
        self.configure(bg="#2b2b2b") 
        self.resizable(False, False)

        self.withdraw()
        messagebox.showwarning(
            "AHTUNG!!!", 
            "Before starting, please, open your config.yaml file and update all directory paths to match your local setup."
            "\nEnsure that your *images* folder contains the floorplan pages you intend to annotate."
        )
        self.deiconify()

        self.create_main_menu()

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

    def create_main_menu(self):
        self.clear_window()

        title_label = tk.Label(self, text="Please, choose annotation mode", 
                               font=("Arial", 16, "bold"), bg="#2b2b2b", fg="white")
        title_label.pack(pady=40)

        btn_style = {"font": ("Arial", 12, "bold"), "width": 25, "height": 2, "cursor": "hand2"}

        btn_obj = tk.Button(self, text="1. Object Annotator (Bboxes)", 
                            bg="#4CAF50", fg="white", activebackground="#45a049",
                            command=lambda: self.show_instructions("object", CONTROLS_OBJECT), **btn_style)
        btn_obj.pack(pady=10)

        btn_room = tk.Button(self, text="2. Room Annotator (Polygons)", 
                             bg="#008CBA", fg="white", activebackground="#007B9E",
                             command=lambda: self.show_instructions("room", CONTROLS_ROOM), **btn_style)
        btn_room.pack(pady=10)

        btn_quit = tk.Button(self, text="Quit", 
                             bg="#f44336", fg="white", activebackground="#da190b",
                             command=self.destroy, **btn_style)
        btn_quit.pack(pady=30)

    def show_instructions(self, app_type, text_controls):
        self.clear_window()

        title_label = tk.Label(self, text="INSTRUCTIONS", 
                               font=("Arial", 14, "bold"), bg="#2b2b2b", fg="#FFD700")
        title_label.pack(pady=20)

        text_box = tk.Label(self, text=text_controls, font=("Consolas", 11, "bold"), 
                            bg="#1e1e1e", fg="#00FF00", justify=tk.LEFT, padx=20, pady=20,
                            relief=tk.RIDGE, borderwidth=2)
        text_box.pack(pady=10)

        btn_frame = tk.Frame(self, bg="#2b2b2b")
        btn_frame.pack(pady=10)

        self.btn_back = tk.Button(btn_frame, text="BACK", font=("Arial", 10, "bold"), width=15,
                             bg="#555555", fg="white", command=self.create_main_menu)
        self.btn_back.pack(side=tk.LEFT, padx=10)

        self.btn_start = tk.Button(btn_frame, text="CONTINUE", font=("Arial", 10, "bold"), width=15,
                              bg="#4CAF50", fg="white", command=lambda: self.launch_script(app_type))
        self.btn_start.pack(side=tk.LEFT, padx=10)

        help_note = tk.Label(self, text="Tip: Keep this window visible to see controls while annotating.",
                             font=("Arial", 8, "italic"), bg="#2b2b2b", fg="#888888")
        help_note.pack(pady=5)

    def launch_script(self, app_type):
        script_name = "annotator.py" if app_type == "object" else "room_annotator.py"
        
        self.btn_start.config(state=tk.DISABLED, text="RUNNING...", bg="#777777")
        self.btn_back.config(state=tk.DISABLED)
        self.update() 
        
        try:
            subprocess.run([sys.executable, script_name])
        except Exception as e:
            messagebox.showerror("Running failed:(", f"{script_name}.\nError: {e}")
        
        self.create_main_menu()

if __name__ == "__main__":
    app = AnnotatorLauncher()
    app.mainloop()