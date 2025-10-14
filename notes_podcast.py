# Takes in the notes and turns it into Podcast
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path

from config import config

class App:
    def __init__(self, root):
        root.title("NOTED — Notes → Podcast (Gemini + Python TTS)")

        self.files = []
        self.topic_var = tk.StringVar(value="Untitled Topic")

        frm = ttk.Frame(root, padding=12)
        frm.grid(sticky="nsew")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        ttk.Label(frm, text="Topic:").grid(row=0, column=0, sticky="w")
        self.topic_entry = ttk.Entry(frm, textvariable=self.topic_var, width=50)
        self.topic_entry.grid(row=0, column=1, sticky="ew", padx=6)

        self.add_btn = ttk.Button(frm, text="Add files (PDF/DOCX/Images)", command=self.add_files)
        self.add_btn.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8,2))

        self.listbox = tk.Listbox(frm, height=6)
        self.listbox.grid(row=2, column=0, columnspan=2, sticky="nsew")
        frm.rowconfigure(2, weight=1)
        frm.columnconfigure(1, weight=1)

        self.gen_btn = ttk.Button(frm, text="Generate Podcast", command=self.generate)
        self.gen_btn.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(8,2))

        ttk.Label(frm, text="Script preview:").grid(row=4, column=0, columnspan=2, sticky="w", pady=(8,0))
        self.script_txt = tk.Text(frm, height=18, wrap="word")
        self.script_txt.grid(row=5, column=0, columnspan=2, sticky="nsew")
        frm.rowconfigure(5, weight=2)

        self.save_btn = ttk.Button(frm, text="Save MP3", command=self.save_mp3, state="disabled")
        self.save_btn.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(8,2))

        self.status = tk.StringVar(value="Ready.")
        ttk.Label(frm, textvariable=self.status).grid(row=7, column=0, columnspan=2, sticky="w", pady=(6,0))

        self.output_dir = Path("data/outputs")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.generated_script = ""

    def add_files(self):
        paths = filedialog.askopenfilenames(
            title="Select notes files",
            filetypes=[
                ("Supported", "*.pdf *.docx *.png *.jpg *.jpeg *.bmp *.tif *.tiff *.txt"),
                ("PDF", "*.pdf"), ("Word", "*.docx"), ("Images", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff"),
                ("Text", "*.txt"), ("All", "*.*"),
            ]
        )
        if not paths: return
        for p in paths:
            self.files.append(p)
            self.listbox.insert(tk.END, p)

    def generate(self):
        messagebox.showinfo("NOTED", "We’ll add the generation logic next.")

    def save_mp3(self):
        messagebox.showinfo("NOTED", "We’ll add MP3 synthesis next.")

def main():
    if not config.gemini_api_key or config.gemini_api_key.startswith("PUT_"):
        messagebox.showerror("NOTED", "Add your Google AI Studio key to config.toml")
        return
    root = tk.Tk()
    App(root)
    root.geometry("880x700")
    root.mainloop()

if __name__ == "__main__":
    main()


