import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import messagebox
import os
import sqlite3   # ← Chỉ cần cái này thôi
from PIL import Image, ImageTk
import requests
from io import BytesIO
import subprocess
import sys
import threading
import time

# Xóa bỏ các import không dùng nữa:
# - import pyodbc
# - from config import DB_CONFIG
# - from dbm import sqlite3  ← sai, không có module dbm.sqlite3

# ────────────────────────────────────────────────
# KẾT NỐI DATABASE (SQLite)
# ────────────────────────────────────────────────
conn = None
cursor = None

def connect_database():
    """Kết nối tới file SQLite database.db"""
    global conn, cursor
    try:
        # Thêm check_same_thread=False để cho phép dùng trong nhiều thread (Tkinter + threading)
        conn = sqlite3.connect("database.db", check_same_thread=False)
        cursor = conn.cursor()
        print("✓ Kết nối SQLite thành công! (database.db)")
        return True
    except Exception as e:
        print(f"✗ LỖI kết nối SQLite: {e}")
        print("→ Kiểm tra file 'database.db' có nằm cùng thư mục với file .py không?")
        return False
# Gọi kết nối ngay đầu chương trình
if not connect_database():
    print("⚠️ Không thể kết nối database. Ứng dụng sẽ chạy nhưng không có dữ liệu.")

# ────────────────────────────────────────────────
# HÀM LẤY THÔNG TIN TRƯỜNG TỪ DATABASE
# ────────────────────────────────────────────────
def get_school_info(school_name):
    """Lấy hình ảnh + mô tả từ database"""
    try:
        print(f"🔍 Tìm trường: '{school_name}'")
        
        query = "SELECT hinh_anh, mo_ta FROM rules WHERE truong = ?"
        cursor.execute(query, (school_name,))
        result = cursor.fetchone()
        
        if result:
            print(f"✓ Tìm thấy!")
            hinh_anh = result[0] if result[0] else None
            mo_ta = result[1] if result[1] else "Không có thông tin"
            return hinh_anh, mo_ta
        else:
            print(f"✗ Không tìm thấy: {school_name}")
            query_like = "SELECT truong, hinh_anh, mo_ta FROM rules WHERE truong LIKE ?"
            cursor.execute(query_like, (f"%{school_name}%",))
            result_like = cursor.fetchone()
            if result_like:
                print(f"✓ Tìm thấy tương tự: {result_like[0]}")
                return result_like[1], result_like[2]
            return None, "Không có thông tin"
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return None, "Không có thông tin"

# ────────────────────────────────────────────────
# HÀM TÌM KIẾM
# ────────────────────────────────────────────────
def tim_kiem():
    global current_photo, current_img_label

    btn_tim.config(state="disabled")
    show_loading(True)

    x = combo_x.get().split()[0]
    e = combo_e.get().split()[0]
    r = combo_r.get().split()[0]
    f = combo_f.get().split()[0]
    t = combo_t.get().split()[0]
    s = combo_s.get().split()[0]

    e_pattern = f"%{e}%"

    query = """
    SELECT truong
    FROM rules
    WHERE X = ?
      AND E LIKE ?
      AND R = ?
      AND F = ?
      AND T = ?
      AND S = ?
    ORDER BY truong
    """

    results = []
    error_msg = None

    try:
        cursor.execute(query, (x, e_pattern, r, f, t, s))
        results = cursor.fetchall()
    except Exception as ex:
        error_msg = str(ex)

    for widget in frame_result_inner.winfo_children():
        widget.destroy()

    if error_msg:
        tk.Label(frame_result_inner, text=f"LỖI TRUY VẤN:\n{error_msg}",
                 fg="red", bg="white", font=("Segoe UI", 11)).pack(pady=20)
    elif not results:
        tk.Label(frame_result_inner, text="Không tìm thấy trường phù hợp.\nThử thay đổi tiêu chí nhé!",
                 fg="#555", bg="white", font=("Segoe UI", 12, "italic")).pack(pady=40)
    else:
        for row in results:
            truong_name = row[0].strip()
            create_school_card(truong_name)

    show_loading(False)
    btn_tim.config(state="normal")

# ... (phần còn lại của code giữ nguyên: create_school_card, loading, back_to_ui, giao diện Tkinter, on_closing, root.mainloop()...)

def create_school_card(name):
    """Card kết quả full chiều ngang, ảnh lớn và mô tả dễ đọc. (Đã xoá bảng thông tin cơ bản)"""
    card = tk.Frame(
        frame_result_inner,
        bg="#ffffff",
        bd=1,
        relief="solid",
        highlightbackground="#cfe0ff",
        highlightthickness=1
    )
    card.pack(fill="x", pady=10, padx=10)

    tk.Label(
        card,
        text=name,
        font=("Segoe UI", 22, "bold"),
        fg="#1e40af",
        bg="#ffffff",
        anchor="w"
    ).pack(fill="x", padx=18, pady=(12, 8))

    hinh_anh, mo_ta = get_school_info(name)

    if hinh_anh:
        try:
            response = requests.get(hinh_anh, timeout=6)
            response.raise_for_status()
            img_data = BytesIO(response.content)
            img = Image.open(img_data).convert("RGB")

            # Ảnh tự co giãn theo vùng kết quả để hạn chế khoảng trống.
            available_width = frame_result_inner.winfo_width() - 64
            target_width = max(1000, min(available_width, 1600))
            aspect_ratio = img.width / img.height if img.height else 2
            target_height = int(target_width / aspect_ratio)
            target_height = max(420, min(target_height, 620))
            resized_img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)

            photo = ImageTk.PhotoImage(resized_img)
            lbl_img = tk.Label(card, image=photo, bg="#ffffff", bd=0)
            lbl_img.image = photo
            lbl_img.pack(fill="x", padx=18, pady=(4, 12))
        except Exception:
            tk.Label(
                card,
                text="Không tải được ảnh",
                fg="#7a7a7a",
                bg="#ffffff",
                font=("Segoe UI", 11, "italic")
            ).pack(pady=(6, 14))
    else:
        tk.Label(
            card,
            text="(Chưa có ảnh khuôn viên)",
            fg="#7a7a7a",
            bg="#ffffff",
            font=("Segoe UI", 12, "italic")
        ).pack(pady=(6, 14))

    # ✅ CHỈ GIỮ LẠI MỤC MÔ TẢ TRƯỜNG (XOÁ BẢNG THÔNG TIN CƠ BẢN)
    tk.Label(
        card,
        text="Mô tả trường",
        font=("Segoe UI", 13, "bold"),
        fg="#1f2937",
        bg="#ffffff",
        anchor="w"
    ).pack(fill="x", padx=18, pady=(0, 6))

    desc_label = tk.Label(
        card,
        text=mo_ta,
        font=("Segoe UI", 13),
        fg="#374151",
        bg="#ffffff",
        justify="left",
        anchor="nw",
        wraplength=900
    )
    desc_label.pack(fill="both", expand=True, padx=18, pady=(0, 14))
    
    card.bind(
        "<Configure>",
        lambda e, lbl=desc_label: lbl.config(wraplength=max(e.width - 52, 420))
    )


# ────────────────────────────────────────────────
# LOADING ANIMATION
# ────────────────────────────────────────────────
loading_label = None
loading_dots = 0

def update_loading():
    global loading_dots
    if loading_label and loading_label.winfo_exists():
        dots = "." * (loading_dots % 4)
        loading_label.config(text=f"Đang tìm kiếm{dots}")
        loading_dots += 1
        root.after(400, update_loading)

def show_loading(show):
    global loading_label
    if show:
        if not loading_label or not loading_label.winfo_exists():
            loading_label = tk.Label(root, text="Đang tìm kiếm...", font=("Segoe UI", 12),
                                     fg="#3b82f6", bg="#f0f5f9")
            loading_label.place(relx=0.5, rely=0.88, anchor="center")
        update_loading()
    else:
        if loading_label and loading_label.winfo_exists():
            loading_label.destroy()
            loading_label = None


def launch_script(script_path):
    if os.name == "nt":
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
        subprocess.Popen(
            [sys.executable, script_path],
            cwd=os.path.dirname(script_path),
            creationflags=creationflags,
            close_fds=True,
        )
        return

    subprocess.Popen([sys.executable, script_path], cwd=os.path.dirname(script_path), close_fds=True)


def back_to_ui():
    if os.environ.get("EDM_PARENT_UI") == "1":
        on_closing()
        return

    ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui.py")
    if not os.path.exists(ui_path):
        messagebox.showerror("Không tìm thấy file", "Không thấy file ui.py")
        return

    try:
        launch_script(ui_path)
        on_closing()
    except Exception as exc:
        messagebox.showerror("Lỗi quay lại", f"Không mở được ui.py\n{exc}")


# ────────────────────────────────────────────────
# GIAO DIỆN CHÍNH
# ────────────────────────────────────────────────
root = tk.Tk()
root.title("Tư vấn chọn trường ĐH 2025-2026")

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

root.geometry(f"{screen_width}x{screen_height}+0+0")
root.configure(bg="#f1f5f9")
root.resizable(True, True)

style = ttk.Style()
style.theme_use("clam")
style.configure("TCombobox", font=("Segoe UI", 10))
style.map("TCombobox", fieldbackground=[("readonly", "#ffffff")])

# Tiêu đề
header_frame = tk.Frame(root, bg="#3b82f6", pady=18)
header_frame.pack(fill="x")

tk.Button(
    header_frame,
    text="← Về UI chính",
    bg="#1e40af",
    fg="white",
    activebackground="#1d4ed8",
    activeforeground="white",
    font=("Segoe UI", 10, "bold"),
    relief="flat",
    bd=0,
    padx=12,
    pady=6,
    cursor="hand2",
    command=back_to_ui,
).place(x=16, y=14)

tk.Label(header_frame, text="TƯ VẤN CHỌN TRƯỜNG ĐẠI HỌC 2025-2026",
         font=("Segoe UI", 20, "bold"), bg="#3b82f6", fg="white").pack()

# Frame filter
frame_filter = tk.Frame(root, bg="#f1f5f9", padx=20, pady=20)
frame_filter.pack(fill="x")

labels = ["Khối ngành", "Phương thức XT", "Điểm thi", "Học phí/năm", "Khu vực", "Loại trường"]
values_list = [
    ["X1 - Y tế - sức khỏe", "X2 - Giáo dục - sư phạm", "X3 - Kỹ thuật Kỹ sư",
     "X4 - Công nghệ thông tin – AI", "X5 - Kinh doanh – quản trị", "X6 - Marketing – truyền thông",
     "X7 - Tài chính – kế toán", "X8 - Luật – pháp lý", "X9 - Nông – Lâm – Ngư",
     "X10 - Du lịch – khách sạn", "X11 - Ngoại giao – Ngôn ngữ", "X12 - Quân đội – công an"],

    ["E0 - Học bạ", "E1 - Điểm THPT", "E2 - Đánh giá năng lực",
     "E3 - Xét tuyển riêng", "E4 - Cả 4 phương thức"],

    ["R0 - dưới 15", "R1 - 16-20", "R2 - 21-25", "R3 - trên 25"],

    ["F0 - dưới 15 triệu", "F1 - 16-25 triệu", "F2 - 26-35 triệu", "F3 - trên 36 triệu"],

    ["T0 - Miền Nam", "T1 - Miền Bắc", "T2 - Miền Trung"],

    ["S0 - Công lập", "S1 - Dân lập", "S2 - Quốc tế"]
]

combos = []
for i, (lbl_text, opts) in enumerate(zip(labels, values_list)):
    tk.Label(frame_filter, text=lbl_text, bg="#f1f5f9", fg="#1e40af",
             font=("Segoe UI", 11, "bold")).grid(row=0, column=i, padx=6, pady=(0, 8), sticky="ew")

    combo = ttk.Combobox(frame_filter, values=opts, width=28, state="readonly",
                         font=("Segoe UI", 10), justify="center")
    combo.grid(row=1, column=i, padx=6, pady=6, sticky="ew")
    combo.set("--Tất Cả--")
    combos.append(combo)

for i in range(6):
    frame_filter.columnconfigure(i, weight=1)

combo_x, combo_e, combo_r, combo_f, combo_t, combo_s = combos

# Nút tìm kiếm
def on_enter(e):
    btn_tim["background"] = "#2563eb"

def on_leave(e):
    btn_tim["background"] = "#3b82f6"

btn_tim = tk.Button(root, text="TÌM KIẾM NGAY", bg="#3b82f6", fg="white",
                    font=("Segoe UI", 12, "bold"), width=20, height=2,
                    relief="flat", bd=0, command=lambda: threading.Thread(target=tim_kiem, daemon=True).start())
btn_tim.pack(pady=15)
btn_tim.bind("<Enter>", on_enter)
btn_tim.bind("<Leave>", on_leave)

# Khu vực kết quả (cải tiến)
frame_result = tk.LabelFrame(root, text=" KẾT QUẢ ", bg="#ffffff", fg="#1e40af",
                             font=("Segoe UI", 12, "bold"), padx=5, pady=5, bd=1, relief="solid")
frame_result.pack(padx=15, pady=(0, 15), fill="both", expand=True)

canvas = tk.Canvas(frame_result, bg="#ffffff", highlightthickness=0)
scrollbar = ttk.Scrollbar(frame_result, orient="vertical", command=canvas.yview)
frame_result_inner = tk.Frame(canvas, bg="#ffffff")

frame_result_inner.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas_window = canvas.create_window((0, 0), window=frame_result_inner, anchor="nw")
canvas.bind(
    "<Configure>",
    lambda e: canvas.itemconfig(canvas_window, width=e.width)
)
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Đóng kết nối
def on_closing():
    if cursor: cursor.close()
    if conn: conn.close()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()