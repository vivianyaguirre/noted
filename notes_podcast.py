# Takes in the notes and turns it into Podcast
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path

from pypdf import PdfReader
from docx import Document as DocxDocument
from PIL import Image
import pytesseract

from config import config


# --- Text extraction helpers ---
def read_pdf(path: Path) -> str:
    try:
        reader = PdfReader(path.as_posix())
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception:
        return ""

def read_docx(path: Path) -> str:
    try:
        doc = DocxDocument(path.as_posix())
        return "\n".join(p.text for p in doc.paragraphs)
    except Exception:
        return ""

def read_image_ocr(path: Path) -> str:
    try:
        img = Image.open(path.as_posix())
        return pytesseract.image_to_string(img)
    except Exception:
        return ""

def extract_text(paths) -> str:
    chunks = []
    for p in paths:
        p = Path(p)
        ext = p.suffix.lower()
        if ext == ".pdf":
            chunks.append(read_pdf(p))
        elif ext == ".docx":
            chunks.append(read_docx(p))
        elif ext in [".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"]:
            chunks.append(read_image_ocr(p))
        else:
            # fallback: try UTF-8 text
            try:
                chunks.append(p.read_text(encoding="utf-8"))
            except Exception:
                pass
    return "\n\n".join(c for c in chunks if c.strip())


class App:
    def __init__(self, root):
        self.root = root  # ← store root; needed later
        root.title("NOTED — Notes → Podcast (Gemini + Python TTS)")

        self.files = []
        self.topic_var = tk.StringVar(value="Untitled Topic")

        frm = ttk.Frame(root, padding=12)
        frm.grid(sticky="nsew")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        # Make both columns expand
        frm.columnconfigure(0, weight=1)   # ← add this
        frm.columnconfigure(1, weight=1)   # you already had column 1 later

        ttk.Label(frm, text="Topic:").grid(row=0, column=0, sticky="w")
        self.topic_entry = ttk.Entry(frm, textvariable=self.topic_var, width=50)
        self.topic_entry.grid(row=0, column=1, sticky="ew", padx=6)

        self.add_btn = ttk.Button(frm, text="Add files (PDF/DOCX/Images)", command=self.add_files)
        self.add_btn.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8,2))

        self.listbox = tk.Listbox(frm, height=6)
        self.listbox.grid(row=2, column=0, columnspan=2, sticky="nsew")
        frm.rowconfigure(2, weight=1)

        # --- Buttons row (centered, equal widths) ---
        buttons = ttk.Frame(frm)
        buttons.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(8, 2))
        buttons.columnconfigure(0, weight=1, uniform="btns")
        buttons.columnconfigure(1, weight=1, uniform="btns")

        self.gen_btn = ttk.Button(buttons, text="Generate Podcast", command=self.generate)
        self.gen_btn.grid(row=0, column=0, sticky="ew", padx=(0, 4))

        self.restart_btn = ttk.Button(buttons, text="Restart (keep script)", command=self.restart)
        self.restart_btn.grid(row=0, column=1, sticky="ew", padx=(4, 0))

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
        if not self.files:
            messagebox.showinfo("NOTED", "Add at least one file first.")
            return
        self.status.set("Extracting text…")
        self.script_txt.delete("1.0", tk.END)
        self.save_btn.config(state="disabled")
        self.generated_script = ""

        raw = extract_text(self.files)
        if not raw.strip():
            messagebox.showerror("NOTED", "No text found. Check OCR (Tesseract) for images.")
            return

        # We will add Gemini summarization + script next
        self.script_txt.insert(tk.END, raw[:1200] + ("\n...\n" if len(raw) > 1200 else ""))
        self.status.set("Notes extracted. Next: Gemini summarization (coming up).")

    def save_mp3(self):
        messagebox.showinfo("NOTED", "We’ll add MP3 synthesis next.")
        
    def restart(self):
        """
        Reset the UI (files, list, topic, preview, status) but KEEP the generated script
        so the user can still save the already generated content.
        """
        # Reset file selections
        self.files.clear()
        self.listbox.delete(0, tk.END)

        # Reset topic and preview area
        self.topic_var.set("Untitled Topic")
        self.script_txt.delete("1.0", tk.END)

        # Re-enable controls
        self.add_btn.config(state="normal")
        self.gen_btn.config(state="normal")

        # If a script already exists, keep Save enabled so it can still be saved
        if self.generated_script.strip():
            self.save_btn.config(state="normal")
            self.status.set("Reset. Prior script preserved in memory — you can still click 'Save MP3'.")
        else:
            self.save_btn.config(state="disabled")
            self.status.set("Reset. No prior script found.")


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


