import os
import sys
import subprocess

try:
    from pypdf import PdfReader, PdfWriter
except ModuleNotFoundError:
    print("pypdf package nahi mila. Auto-installing...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pypdf"])
    except subprocess.CalledProcessError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pypdf", "--break-system-packages"])
    from pypdf import PdfReader, PdfWriter

import tkinter as tk
from tkinter import ttk, filedialog, messagebox


class PDFUtilityApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Merger & Splitter Utility")
        self.root.geometry("600x500")
        self.root.resizable(False, False)

        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.merge_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.merge_tab, text=" Merge PDFs ")
        self.setup_merge_ui()

        self.split_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.split_tab, text=" Split PDF ")
        self.setup_split_ui()

    def setup_merge_ui(self):
        self.merge_files_list = []

        lbl_desc = ttk.Label(
            self.merge_tab,
            text="Select PDF files in order to merge them into one file:",
            font=("Arial", 10)
        )
        lbl_desc.pack(anchor="w", padx=15, pady=(15, 5))

        list_frame = ttk.Frame(self.merge_tab)
        list_frame.pack(fill="both", expand=True, padx=15, pady=5)

        self.file_listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE, font=("Consolas", 9))
        self.file_listbox.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.file_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.file_listbox.config(yscrollcommand=scrollbar.set)

        btn_frame = ttk.Frame(self.merge_tab)
        btn_frame.pack(fill="x", padx=15, pady=10)

        ttk.Button(btn_frame, text="Add PDFs", command=self.add_merge_files).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Remove Selected", command=self.remove_merge_file).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Clear All", command=self.clear_merge_files).pack(side="left", padx=5)

        ttk.Button(self.merge_tab, text="Merge and Save PDF", command=self.merge_pdfs).pack(
            pady=(0, 15), ipadx=10, ipady=5
        )

    def add_merge_files(self):
        files = filedialog.askopenfilenames(filetypes=[("PDF Files", "*.pdf")])
        for f in files:
            if f not in self.merge_files_list:
                self.merge_files_list.append(f)
                self.file_listbox.insert(tk.END, os.path.basename(f))

    def remove_merge_file(self):
        selected_idx = self.file_listbox.curselection()
        if selected_idx:
            idx = selected_idx[0]
            self.file_listbox.delete(idx)
            del self.merge_files_list[idx]

    def clear_merge_files(self):
        self.file_listbox.delete(0, tk.END)
        self.merge_files_list.clear()

    def merge_pdfs(self):
        if not self.merge_files_list:
            messagebox.showwarning("Warning", "Please add at least one PDF file to merge.")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")]
        )
        if not save_path:
            return

        try:
            writer = PdfWriter()
            for pdf_path in self.merge_files_list:
                reader = PdfReader(pdf_path)
                for page in reader.pages:
                    writer.add_page(page)

            with open(save_path, "wb") as f_out:
                writer.write(f_out)

            messagebox.showinfo("Success", f"PDFs merged successfully!\nSaved to: {save_path}")
            self.clear_merge_files()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to merge PDFs:\n{str(e)}")

    def setup_split_ui(self):
        self.selected_split_file = ""

        f_select = ttk.LabelFrame(self.split_tab, text=" Select PDF File ")
        f_select.pack(fill="x", padx=15, pady=15)

        self.lbl_split_file = ttk.Label(f_select, text="No file selected", foreground="gray")
        self.lbl_split_file.pack(side="left", padx=10, pady=10, expand=True, fill="x")

        ttk.Button(f_select, text="Browse...", command=self.browse_split_file).pack(side="right", padx=10, pady=10)

        f_opts = ttk.LabelFrame(self.split_tab, text=" Split Options ")
        f_opts.pack(fill="x", padx=15, pady=10)

        self.split_mode = tk.StringVar(value="all")

        ttk.Radiobutton(
            f_opts,
            text="Extract each page into individual PDF",
            variable=self.split_mode,
            value="all"
        ).pack(anchor="w", padx=10, pady=5)

        ttk.Radiobutton(
            f_opts,
            text="Extract Page Range (e.g. 1-3, 5):",
            variable=self.split_mode,
            value="range"
        ).pack(anchor="w", padx=10, pady=5)

        self.ent_range = ttk.Entry(f_opts, width=25)
        self.ent_range.pack(anchor="w", padx=30, pady=(0, 10))

        ttk.Button(self.split_tab, text="Split PDF", command=self.split_pdf).pack(pady=20, ipadx=10, ipady=5)

    def browse_split_file(self):
        f = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if f:
            self.selected_split_file = f
            self.lbl_split_file.config(text=os.path.basename(f), foreground="black")

    def split_pdf(self):
        if not self.selected_split_file:
            messagebox.showwarning("Warning", "Please select a PDF file to split.")
            return

        out_dir = filedialog.askdirectory(title="Select Output Folder")
        if not out_dir:
            return

        mode = self.split_mode.get()

        try:
            reader = PdfReader(self.selected_split_file)
            total_pages = len(reader.pages)
            base_name = os.path.splitext(os.path.basename(self.selected_split_file))[0]

            if mode == "all":
                for i, page in enumerate(reader.pages):
                    writer = PdfWriter()
                    writer.add_page(page)
                    out_path = os.path.join(out_dir, f"{base_name}_page_{i+1}.pdf")
                    with open(out_path, "wb") as f_out:
                        writer.write(f_out)
                messagebox.showinfo("Success", f"Split {total_pages} pages into individual PDFs successfully!")

            elif mode == "range":
                range_str = self.ent_range.get().strip()
                if not range_str:
                    messagebox.showwarning("Warning", "Please enter a valid page range (e.g. 1-3, 5).")
                    return

                page_numbers = set()
                parts = range_str.split(",")
                for part in parts:
                    part = part.strip()
                    if "-" in part:
                        start, end = part.split("-")
                        for p in range(int(start), int(end) + 1):
                            if 1 <= p <= total_pages:
                                page_numbers.add(p - 1)
                    else:
                        if part.isdigit():
                            p = int(part)
                            if 1 <= p <= total_pages:
                                page_numbers.add(p - 1)

                if not page_numbers:
                    messagebox.showwarning(
                        "Warning",
                        f"No valid page numbers found for this PDF (Total pages: {total_pages})."
                    )
                    return

                writer = PdfWriter()
                for p_idx in sorted(page_numbers):
                    writer.add_page(reader.pages[p_idx])

                out_path = os.path.join(out_dir, f"{base_name}_extracted.pdf")
                with open(out_path, "wb") as f_out:
                    writer.write(f_out)

                messagebox.showinfo("Success", f"Extracted selected pages successfully!\nSaved to: {out_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to split PDF:\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = PDFUtilityApp(root)
    root.mainloop()