import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import math

class ImageViewer(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Image Viewer")
        self.geometry("1000x600")

        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.listbox_frame = tk.Frame(self.main_frame)
        self.listbox_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.canvas_frame = tk.Frame(self.main_frame)
        self.canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.listbox = tk.Listbox(self.listbox_frame)
        self.listbox.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        self.listbox.bind('<<ListboxSelect>>', self.on_image_select)

        self.listbox_scrollbar = tk.Scrollbar(self.listbox_frame, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=self.listbox_scrollbar.set)

        self.canvas = tk.Canvas(self.canvas_frame, bg="gray")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.save_button = tk.Button(self, text="Save Circles", command=self.save_circle)
        self.save_button.pack(pady=10)

        self.img = None
        self.img_obj = None
        self.scale = 1.0
        self.image_size=0,0

        self.bind("<MouseWheel>", self.zoom)

        # 拖动相关参数
        self.bind("<Button-2>", self.start_move)
        self.bind("<B2-Motion>", self.move)

        self.offset_x = 0
        self.offset_y = 0
        self.start_x = 0
        self.start_y = 0

        self.images = []
        self.image_files = []
        self.points = []
        self.circles = []  # 保存所有圆的信息
        self.current_image_name = ""

        self.load_images()

    def load_images(self):
        folder = filedialog.askdirectory()
        if not folder:
            return

        self.images = []
        self.image_files = []

        for file in os.listdir(folder):
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                image_path = os.path.join(folder, file)
                self.image_files.append(image_path)
                self.listbox.insert(tk.END, file)

        self.listbox.select_set(0)
        self.show_image()

    def on_image_select(self, event):
        selected_index = self.listbox.curselection()
        if not selected_index:
            return

        selected_file = self.listbox.get(selected_index[0])
        self.current_image_name = selected_file
        file_path = self.image_files[selected_index[0]]
        img = Image.open(file_path)
        self.image_size=img.size

        self.images = [img]

        self.clear_canvas()  # 清空画布和圆的信息

        self.show_image()

        txt_file_path = self.get_txt_file_path()
        if os.path.exists(txt_file_path):
            self.load_circles_from_txt(txt_file_path)

    def clear_canvas(self):
        """清空画布和相关信息"""
        self.canvas.delete("all")
        self.circles = []
        self.points = []

    def show_image(self, event=None):
        if not self.images:
            return

        img = self.images[0]
        self.img = img.resize((int(img.width * self.scale), int(img.height * self.scale)), Image.Resampling.LANCZOS)
        self.img_obj = ImageTk.PhotoImage(self.img)

        self.canvas.delete("all")
        self.canvas.create_image(self.offset_x, self.offset_y, image=self.img_obj, anchor=tk.NW)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

        # 重新绘制圆
        self.draw_all_circles()

    def zoom(self, event):
        if event.delta > 0:
            self.scale *= 1.1
        else:
            self.scale /= 1.1
        self.show_image()

    def start_move(self, event):
        self.start_x = event.x
        self.start_y = event.y

    def move(self, event):
        dx = event.x - self.start_x
        dy = event.y - self.start_y

        self.offset_x += dx
        self.offset_y += dy

        self.start_x = event.x
        self.start_y = event.y

        self.show_image()  # 确保移动后圆的位置被正确调整

    def on_canvas_click(self, event):
        canvas_x, canvas_y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        img_x = (canvas_x - self.offset_x) / self.scale
        img_y = (canvas_y - self.offset_y) / self.scale

        if len(self.points) < 3:
            self.points.append((img_x, img_y))
            self.canvas.create_oval(canvas_x-2, canvas_y-2, canvas_x+2, canvas_y+2, fill='red', outline='red')
            if len(self.points) == 3:
                self.draw_circle()

    def draw_circle(self):
        if len(self.points) != 3:
            return

        p1, p2, p3 = self.points
        center, radius = self.calculate_circle(p1, p2, p3)
        if center and radius:
            cx, cy = center
            self.circles.append((cx, cy, radius))  # 保存圆的信息
            self.draw_single_circle(cx, cy, radius)
            self.points = []  # 清空点以便绘制下一个圆

    def draw_single_circle(self, cx, cy, radius):
        """在画布上绘制单个圆"""
        canvas_center_x = cx * self.scale + self.offset_x
        canvas_center_y = cy * self.scale + self.offset_y
        canvas_radius = radius * self.scale
        self.canvas.create_oval(canvas_center_x - canvas_radius, canvas_center_y - canvas_radius,
                                canvas_center_x + canvas_radius, canvas_center_y + canvas_radius,
                                outline='blue', width=2, tags="circle")

    def draw_all_circles(self):
        """绘制所有存储的圆"""
        for circle in self.circles:
            cx, cy, radius = circle
            self.draw_single_circle(cx, cy, radius)

    def calculate_circle(self, p1, p2, p3):
        def dist(p, q):
            return math.sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)

        def circle_from_three_points(p1, p2, p3):
            ax, ay = p1
            bx, by = p2
            cx, cy = p3

            d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
            if d == 0:
                return None, None

            ux = ((ax**2 + ay**2) * (by - cy) + (bx**2 + by**2) * (cy - ay) + (cx**2 + cy**2) * (ay - by)) / d
            uy = ((ax**2 + ay**2) * (cx - bx) + (bx**2 + by**2) * (ax - cx) + (cx**2 + cy**2) * (bx - ax)) / d

            center = (ux, uy)
            radius = dist(center, p1)

            return center, radius

        return circle_from_three_points(p1, p2, p3)

    def save_circle(self):
        if not self.circles:
            messagebox.showwarning("No Circles", "No circles to save. Please draw circles first.")
            return

        txt_file_path = self.get_txt_file_path()
        with open(txt_file_path, 'w') as file:
            for circle in self.circles:
                cx, cy, radius = circle
                width,height=self.image_size
                file.write(f"{cx},{cy},{radius},{width},{height}\n")
        messagebox.showinfo("Saved", f"Circle information saved to {txt_file_path}")

    def get_txt_file_path(self):
        base_name, _ = os.path.splitext(self.current_image_name)
        return os.path.join(os.path.dirname(self.image_files[0]),'labels_circle', f"{base_name}.txt")

    def load_circles_from_txt(self, txt_file_path):
        self.clear_canvas()  # 清空画布上的圆
        with open(txt_file_path, 'r') as file:
            for line in file:
                cx, cy, radius ,width,height= map(float, line.strip().split(','))
                self.circles.append((cx, cy, radius))  # 读取圆的信息并保存
        self.draw_all_circles()

if __name__ == "__main__":
    app = ImageViewer()
    app.canvas.bind("<Button-1>", app.on_canvas_click)
    app.mainloop()
