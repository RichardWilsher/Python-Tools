import os
import cv2
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from logger import Logger

# Initialize logger
logger = Logger()
logger.start("image_deduplicator", 1)  # 1 = log to file

class ImageDeduplicatorGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Image Deduplicator")
        self.geometry("900x600")

        self.dir_path = ""
        self.duplicates = []
        self.current_index = 0

        self.create_widgets()

    def create_widgets(self):
        top_frame = ttk.Frame(self)
        top_frame.pack(fill="x", pady=10)

        ttk.Button(top_frame, text="Select Folder", command=self.select_folder).grid(row=0, column=0, padx=5)
        ttk.Button(top_frame, text="Scan for Duplicates", command=self.scan_duplicates).grid(row=0, column=1, padx=5)

        self.progress = ttk.Progressbar(top_frame, length=200, mode='determinate')
        self.progress.grid(row=0, column=2, padx=5)

        self.listbox = tk.Listbox(self)
        self.listbox.pack(fill="both", expand=True, padx=10, pady=10)
        self.listbox.bind("<<ListboxSelect>>", self.show_selected_images)

        img_frame = ttk.Frame(self)
        img_frame.pack(fill="x")

        self.left_panel = ttk.Label(img_frame, text="Left Image")
        self.left_panel.pack(side="left", expand=True)

        self.right_panel = ttk.Label(img_frame, text="Right Image")
        self.right_panel.pack(side="right", expand=True)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x")

        self.delete_left_btn = ttk.Button(btn_frame, text="Delete Left", command=self.delete_left, state="disabled")
        self.delete_left_btn.pack(side="left", padx=10, pady=5)

        self.delete_right_btn = ttk.Button(btn_frame, text="Delete Right", command=self.delete_right, state="disabled")
        self.delete_right_btn.pack(side="left", padx=10, pady=5)

        self.skip_btn = ttk.Button(btn_frame, text="Skip", command=self.skip_pair, state="disabled")
        self.skip_btn.pack(side="left", padx=10, pady=5)

    def select_folder(self):
        self.dir_path = filedialog.askdirectory()

    def scan_duplicates(self):
        if not self.dir_path:
            messagebox.showerror("Error", "Please select a folder first.")
            return

        self.delete_left_btn.config(state="disabled")
        self.delete_right_btn.config(state="disabled")
        self.skip_btn.config(state="disabled")
        threading.Thread(target=self._scan_duplicates_thread).start()

    def _scan_duplicates_thread(self):
        image_files = [f for f in os.listdir(self.dir_path)
                       if os.path.isfile(os.path.join(self.dir_path, f)) and f.lower().endswith((".jpg", ".jpeg", ".png"))]
        duplicates = []
        total = len(image_files)
        checked = 0

        for i in range(total):
            path1 = os.path.join(self.dir_path, image_files[i])
            try:
                img1 = cv2.imread(path1, cv2.IMREAD_UNCHANGED)
                if img1 is None or img1.size == 0:
                    logger.log(2, "Read Error", f"Failed to load image: {path1}")
                    continue
            except Exception as e:
                logger.log(3, "Read Exception", f"Error reading image {path1}: {e}")
                continue

            for j in range(i + 1, total):
                path2 = os.path.join(self.dir_path, image_files[j])
                try:
                    img2 = cv2.imread(path2, cv2.IMREAD_UNCHANGED)
                    if img2 is None or img2.size == 0:
                        logger.log(2, "Read Error", f"Failed to load image: {path2}")
                        continue
                except Exception as e:
                    logger.log(3, "Read Exception", f"Error reading image {path2}: {e}")
                    continue

                if img1.shape == img2.shape and not (cv2.bitwise_xor(img1, img2).any()):
                    duplicates.append((path1, path2))

            checked += 1
            self.progress['value'] = (checked / total) * 100

        self.duplicates = duplicates
        self.progress['value'] = 100

        self.listbox.delete(0, tk.END)
        for pair in self.duplicates:
            self.listbox.insert(tk.END, f"{os.path.basename(pair[0])} <-> {os.path.basename(pair[1])}")

        if duplicates:
            self.delete_left_btn.config(state="normal")
            self.delete_right_btn.config(state="normal")
            self.skip_btn.config(state="normal")
            self.listbox.selection_set(0)
            self.show_selected_images(None)
        else:
            messagebox.showinfo("Done", "No duplicates found.")

    def show_selected_images(self, event):
        selection = self.listbox.curselection()
        if not selection:
            return

        index = selection[0]
        self.current_index = index
        path1, path2 = self.duplicates[index]

        self.display_image(path1, self.left_panel)
        self.display_image(path2, self.right_panel)

    def display_image(self, path, panel):
        try:
            image = Image.open(path)
            image.verify()
            image = Image.open(path)
            image.thumbnail((300, 300))
            photo = ImageTk.PhotoImage(image)
            panel.image = photo
            panel.config(image=photo, text="")
        except Exception as e:
            logger.log(3, "Image Load", f"Corrupt or invalid image: {path} - {e}")
            panel.config(text="Invalid or Corrupt Image", image="")
            panel.image = None

    def delete_left(self):
        if self.duplicates:
            path1, path2 = self.duplicates[self.current_index]
            os.remove(path1)
            logger.log(1, "Delete", f"Deleted {path1}")
            self.remove_current_pair()

    def delete_right(self):
        if self.duplicates:
            path1, path2 = self.duplicates[self.current_index]
            os.remove(path2)
            logger.log(1, "Delete", f"Deleted {path2}")
            self.remove_current_pair()

    def skip_pair(self):
        self.remove_current_pair()

    def remove_current_pair(self):
        if self.duplicates:
            self.duplicates.pop(self.current_index)
            self.listbox.delete(self.current_index)

            if self.current_index >= len(self.duplicates):
                self.current_index = len(self.duplicates) - 1

            if self.duplicates:
                self.listbox.selection_clear(0, tk.END)
                self.listbox.selection_set(self.current_index)
                self.listbox.activate(self.current_index)
                self.show_selected_images(None)
            else:
                self.left_panel.config(text="Left Image", image="")
                self.right_panel.config(text="Right Image", image="")
                self.delete_left_btn.config(state="disabled")
                self.delete_right_btn.config(state="disabled")
                self.skip_btn.config(state="disabled")

if __name__ == "__main__":
    try:
        app = ImageDeduplicatorGUI()
        app.mainloop()
    finally:
        logger.stop()
