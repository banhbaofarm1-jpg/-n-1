import os
import subprocess
import sys
import tkinter as tk
from datetime import datetime
from tkinter import messagebox

try:
    from PIL import Image, ImageTk  # type: ignore

    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False


class CareerAdvisingUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("HỆ THỐNG TƯ VẤN NGHỀ NGHIỆP")
        self.root.geometry("1200x760")
        self.root.minsize(980, 640)
        self.root.configure(bg="#F3F6FF")

        self.card_images: dict[str, tk.PhotoImage] = {}
        self.cards: dict[str, dict[str, tk.Widget]] = {}
        self.assets_dir = os.path.dirname(os.path.abspath(__file__))
        self.default_images = {
            "card_1": "hinh1.png",
            "card_2": "hinh2.png",
        }
        self.card_titles = {
            "card_1": "Khám Phá Bản Thân",
            "card_2": "Tư Vấn Nghề Nghiệp",
        }
        self.card_scripts = {
            "card_1": "tracnghiem.py",
            "card_2": "tuvannghenhiep.py",
        }

        self._build_layout()
        self._load_default_images()

    def _launch_script(self, script_path: str) -> subprocess.Popen:
        child_env = os.environ.copy()
        child_env["EDM_PARENT_UI"] = "1"

        if os.name == "nt":
            flags = subprocess.CREATE_NEW_PROCESS_GROUP
            if hasattr(subprocess, "CREATE_BREAKAWAY_FROM_JOB"):
                flags |= subprocess.CREATE_BREAKAWAY_FROM_JOB

            return subprocess.Popen(
                [sys.executable, script_path],
                cwd=self.assets_dir,
                creationflags=flags,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=child_env,
            )

        return subprocess.Popen(
            [sys.executable, script_path],
            cwd=self.assets_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=child_env,
        )

    def _finish_launch(self, process: subprocess.Popen, script_name: str) -> None:
        if process.poll() is None:
            self._watch_child_process(process, script_name)
            return

        detail = self._read_process_error(process)
        self._append_launch_log(script_name, process.returncode, detail)
        messagebox.showerror("Lỗi chạy file", f"Không mở được {script_name}\n{detail}")

    def _read_process_error(self, process: subprocess.Popen) -> str:
        stderr_text = ""
        if process.stderr is not None:
            try:
                _stdout, stderr_text = process.communicate(timeout=0.2)
            except Exception:
                pass
        return stderr_text.strip() or f"Tiến trình thoát với mã {process.returncode}"

    def _watch_child_process(self, process: subprocess.Popen, script_name: str) -> None:
        if process.poll() is None:
            self.root.after(500, lambda: self._watch_child_process(process, script_name))
            return

        if process.returncode not in (0, None):
            detail = self._read_process_error(process)
            self._append_launch_log(script_name, process.returncode, detail)
            messagebox.showerror("Lỗi chạy file", f"{script_name} đã đóng bất thường\n{detail}")
        else:
            self._append_launch_log(script_name, process.returncode, "Đóng bình thường")

    def _append_launch_log(self, script_name: str, return_code: int | None, detail: str) -> None:
        log_path = os.path.join(self.assets_dir, "launcher.log")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        content = (
            f"[{timestamp}] script={script_name} returncode={return_code}\n"
            f"{detail}\n"
            f"{'-' * 60}\n"
        )
        try:
            with open(log_path, "a", encoding="utf-8") as log_file:
                log_file.write(content)
        except Exception:
            pass

    def _build_layout(self) -> None:
        wrapper = tk.Frame(self.root, bg="#F3F6FF")
        wrapper.pack(fill="both", expand=True)

        self.banner = tk.Canvas(wrapper, height=185, highlightthickness=0, bg="#1E3A8A")
        self.banner.pack(fill="x", padx=22, pady=(22, 16))
        self.banner.bind("<Configure>", self._render_banner)

        cards_area = tk.Frame(wrapper, bg="#F3F6FF")
        cards_area.pack(fill="both", expand=True, padx=22, pady=(0, 22))
        cards_area.grid_columnconfigure(0, weight=1)
        cards_area.grid_columnconfigure(1, weight=1)
        cards_area.grid_rowconfigure(0, weight=1)

        self.cards["card_1"] = self._create_flash_card(
            card_key="card_1",
            parent=cards_area,
            column=0,
            heading="Khám Phá Bản Thân",
            text="Gợi ý nhóm ngành phù hợp dựa trên sở thích, năng lực và giá trị nghề nghiệp của bạn dựa trên trắc nghiệm tính cách.",
            default_image="hinh1.png",
            start_button_color="#2563EB",
        )
        self.cards["card_2"] = self._create_flash_card(
            card_key="card_2",
            parent=cards_area,
            column=1,
            heading="Tư Vấn Nghề Nghiệp",
            text="Xây dựng kế hoạch học tập, điểm chuẩn và định hướng phát triển nghề nghiệp rõ ràng theo từng giai đoạn.",
            default_image="hinh2.png",
            start_button_color="#0F766E",
        )

    def _render_banner(self, event: tk.Event) -> None:
        width = max(event.width, 1)
        height = max(event.height, 1)
        self.banner.delete("all")

        start = (30, 58, 138)   # #1E3A8A
        end = (14, 116, 144)    # #0E7490

        for i in range(height):
            ratio = i / max(height - 1, 1)
            r = int(start[0] + (end[0] - start[0]) * ratio)
            g = int(start[1] + (end[1] - start[1]) * ratio)
            b = int(start[2] + (end[2] - start[2]) * ratio)
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.banner.create_line(0, i, width, i, fill=color)

        self.banner.create_text(
            48,
            68,
            text="HỆ THỐNG TƯ VẤN NGHỀ NGHIỆP",
            anchor="w",
            font=("Segoe UI", 30, "bold"),
            fill="white",
        )
        self.banner.create_text(
            48,
            118,
            text="Định hướng tương lai nghề nghiệp một cách trực quan, hiện đại và cá nhân hóa",
            anchor="w",
            font=("Segoe UI", 13),
            fill="#DBEAFE",
        )

    def _create_flash_card(
        self,
        card_key: str,
        parent: tk.Frame,
        column: int,
        heading: str,
        text: str,
        default_image: str,
        start_button_color: str,
    ) -> dict[str, tk.Widget]:
        outer = tk.Frame(
            parent,
            bg="#FFFFFF",
            highlightthickness=1,
            highlightbackground="#D7E2FF",
            padx=18,
            pady=18,
        )
        outer.grid(row=0, column=column, sticky="nsew", padx=10, pady=6)

        heading_label = tk.Label(
            outer,
            text=heading,
            bg="#FFFFFF",
            fg="#1D4ED8",
            font=("Segoe UI", 18, "bold"),
        )
        heading_label.pack(anchor="w")

        body_label = tk.Label(
            outer,
            text=text,
            bg="#FFFFFF",
            fg="#334155",
            font=("Segoe UI", 11),
            justify="left",
            wraplength=510,
        )
        body_label.pack(anchor="w", pady=(8, 14))

        image_box = tk.Frame(
            outer,
            bg="#FFFFFF",
            width=520,
            height=265,
            highlightthickness=0,
            bd=0,
        )
        image_box.pack(fill="x", expand=False)
        image_box.pack_propagate(False)

        image_label = tk.Label(
            image_box,
            bg="#FFFFFF",
            fg="#64748B",
            text=f"Đang chờ ảnh {default_image}",
            font=("Segoe UI", 11, "italic"),
        )
        image_label.pack(fill="both", expand=True)

        actions = tk.Frame(outer, bg="#FFFFFF")
        actions.pack(fill="x", pady=(14, 4))
        actions.grid_columnconfigure(0, weight=1)

        start_button = tk.Button(
            actions,
            text="Bắt đầu",
            bg=start_button_color,
            fg="white",
            activebackground=start_button_color,
            activeforeground="white",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            padx=16,
            pady=8,
            cursor="hand2",
            command=lambda key=card_key: self._start_feature(key),
        )
        start_button.grid(row=0, column=0)

        self._bind_card_hover(outer, image_box, image_label, heading_label, body_label)
        self._bind_card_click(outer, image_box, image_label, heading_label, body_label, card_key)

        return {
            "card": outer,
            "image_label": image_label,
            "image_box": image_box,
        }

    def _load_default_images(self) -> None:
        for card_key, image_name in self.default_images.items():
            file_path = os.path.join(self.assets_dir, image_name)
            if not os.path.exists(file_path):
                continue

            if self._set_card_image(card_key, file_path):
                continue

    def _set_card_image(self, card_key: str, file_path: str) -> bool:
        image_label = self.cards[card_key]["image_label"]

        try:
            if PIL_AVAILABLE:
                image = Image.open(file_path)
                image = self._resize_cover(image, 520, 265)
                photo = ImageTk.PhotoImage(image)
            else:
                photo = tk.PhotoImage(file=file_path)
        except Exception:
            return False

        image_label.configure(image=photo, text="")
        image_label.image = photo
        self.card_images[card_key] = photo
        return True

    def _resize_cover(self, image: "Image.Image", target_w: int, target_h: int) -> "Image.Image":
        src_w, src_h = image.size
        if src_w <= 0 or src_h <= 0:
            return image

        scale = max(target_w / src_w, target_h / src_h)
        new_w = max(1, int(src_w * scale))
        new_h = max(1, int(src_h * scale))

        if hasattr(Image, "Resampling"):
            resized = image.resize((new_w, new_h), Image.Resampling.LANCZOS)
        else:
            resized = image.resize((new_w, new_h), Image.LANCZOS)

        left = max(0, (new_w - target_w) // 2)
        top = max(0, (new_h - target_h) // 2)
        right = left + target_w
        bottom = top + target_h
        return resized.crop((left, top, right, bottom))

    def _start_feature(self, card_key: str) -> None:
        script_name = self.card_scripts.get(card_key)
        if not script_name:
            title = self.card_titles.get(card_key, "Tính năng")
            messagebox.showerror("Lỗi", f"Chưa cấu hình cho: {title}")
            return

        script_path = os.path.join(self.assets_dir, script_name)
        if not os.path.exists(script_path):
            messagebox.showerror("Không tìm thấy file", f"Không thấy: {script_name}")
            return

        try:
            process = self._launch_script(script_path)
            self.root.after(350, lambda: self._finish_launch(process, script_name))
        except Exception as exc:
            messagebox.showerror("Lỗi chạy file", f"Không mở được {script_name}\n{exc}")

    def _bind_card_hover(
        self,
        card: tk.Frame,
        image_box: tk.Frame,
        image_label: tk.Label,
        heading_label: tk.Label,
        body_label: tk.Label,
    ) -> None:
        def on_enter(_: tk.Event) -> None:
            card.configure(highlightbackground="#8BB1FF")
            heading_label.configure(fg="#1E40AF")
            body_label.configure(fg="#1F2937")

        def on_leave(_: tk.Event) -> None:
            card.configure(highlightbackground="#D7E2FF")
            heading_label.configure(fg="#1D4ED8")
            body_label.configure(fg="#334155")

        for widget in (card, image_box, image_label, heading_label, body_label):
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)

    def _bind_card_click(
        self,
        card: tk.Frame,
        image_box: tk.Frame,
        image_label: tk.Label,
        heading_label: tk.Label,
        body_label: tk.Label,
        card_key: str,
    ) -> None:
        clickable_widgets: tuple[tk.Widget, ...] = (card, image_box, image_label, heading_label, body_label)

        def on_click(_: tk.Event) -> None:
            self._start_feature(card_key)

        for widget in clickable_widgets:
            widget.configure(cursor="hand2")
            widget.bind("<Button-1>", on_click)


if __name__ == "__main__":
    app_root = tk.Tk()
    CareerAdvisingUI(app_root)
    app_root.mainloop()
