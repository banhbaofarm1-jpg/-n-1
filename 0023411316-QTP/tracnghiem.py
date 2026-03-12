import customtkinter as ctk
import os
import sqlite3
import json
import subprocess
import sys
from datetime import datetime
from tkinter import messagebox

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# Kết nối DB
conn = sqlite3.connect("holland_riasec.db")
c = conn.cursor()
c.execute(
    """CREATE TABLE IF NOT EXISTS results
             (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, date TEXT, code TEXT, scores TEXT)"""
)
conn.commit()


class HollandQuizApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Trắc nghiệm Holland RIASEC")
        self.geometry("1240x860")
        self.minsize(980, 700)
        self.resizable(True, True)

        self.ui = {
            "bg": "#EDF2FF",
            "surface": "#FFFFFF",
            "soft_surface": "#F8FAFC",
            "text": "#0F172A",
            "subtext": "#475569",
            "line": "#E2E8F0",
            "primary": "#2563EB",
            "primary_hover": "#1D4ED8",
            "success": "#059669",
            "muted_btn": "#64748B",
            "muted_btn_hover": "#475569",
        }

        self.category_styles = {
            "R": {"name": "Kỹ thuật", "accent": "#F97316", "soft": "#FFF7ED"},
            "I": {"name": "Nghiên cứu", "accent": "#0284C7", "soft": "#E0F2FE"},
            "A": {"name": "Nghệ thuật", "accent": "#D946EF", "soft": "#FDF4FF"},
            "S": {"name": "Xã hội", "accent": "#16A34A", "soft": "#F0FDF4"},
            "E": {"name": "Quản lý", "accent": "#EF4444", "soft": "#FEF2F2"},
            "C": {"name": "Nghiệp vụ", "accent": "#0F766E", "soft": "#F0FDFA"},
        }

        self.jobs = {
            "R": "Kỹ sư cơ khí, kỹ thuật viên điện - điện tử, vận hành thiết bị",
            "I": "Lập trình viên, chuyên viên dữ liệu, nghiên cứu khoa học",
            "A": "Thiết kế đồ họa, content sáng tạo, truyền thông nghệ thuật",
            "S": "Giáo viên, tư vấn tâm lý, công tác xã hội, điều dưỡng",
            "E": "Quản lý kinh doanh, sales, marketing, khởi nghiệp",
            "C": "Kế toán, hành chính nhân sự, kiểm toán, vận hành",
        }

        self.user_name = ""
        self.scores = {"R": 0, "I": 0, "A": 0, "S": 0, "E": 0, "C": 0}
        self.check_vars = []
        self.option_cards = []

        self.sections = [
            {
                "title": "KỸ THUẬT",
                "icon": "🔧",
                "subtitle": "Bạn có nhiều sở thích liên quan đến nhóm kỹ thuật không?",
                "category": "R",
                "options": [
                    "Tôi thích sửa chữa máy móc, xe cộ hoặc đồ điện tử.",
                    "Tôi thích làm việc với cây cối, trồng trọt hoặc chăm sóc động vật.",
                    "Tôi thích xây dựng, lắp ráp hoặc làm thủ công bằng tay.",
                    "Tôi thích hoạt động ngoài trời như câu cá, cắm trại.",
                    "Tôi thích sử dụng dụng cụ, máy móc để tạo sản phẩm.",
                    "Tôi thích lái xe tải hoặc máy móc nặng.",
                    "Tôi thích làm thợ mộc hoặc thợ cơ khí.",
                    "Tôi thích làm vườn hoặc nông nghiệp.",
                    "Tôi thích sửa ống nước hoặc điện trong nhà.",
                    "Tôi thích làm việc với động vật hoặc thú cưng.",
                ],
            },
            {
                "title": "NGHIÊN CỨU",
                "icon": "🔬",
                "subtitle": "Bạn có niềm đam mê nghiên cứu mọi thứ không?",
                "category": "I",
                "options": [
                    "Tôi thích đọc sách khoa học, nghiên cứu hoặc thí nghiệm.",
                    "Tôi thích giải toán phức tạp hoặc vấn đề logic.",
                    "Tôi thích phân tích dữ liệu hoặc điều tra sự thật.",
                    "Tôi thích làm việc trong phòng thí nghiệm.",
                    "Tôi thích khám phá kiến thức mới về vũ trụ hoặc sinh học.",
                    "Tôi thích lập trình máy tính hoặc công nghệ.",
                    "Tôi thích đọc báo khoa học hoặc tài liệu chuyên môn.",
                    "Tôi thích quan sát và phân tích hành vi.",
                    "Tôi thích giải quyết vấn đề khoa học.",
                    "Tôi thích nghiên cứu lịch sử hoặc khảo cổ.",
                ],
            },
            {
                "title": "NGHỆ THUẬT",
                "icon": "🎨",
                "subtitle": "Con người nghệ thuật thường bay bổng, bạn có thấy giống mình không?",
                "category": "A",
                "options": [
                    "Tôi thích vẽ tranh, thiết kế hoặc sáng tác nhạc.",
                    "Tôi thích viết truyện, thơ hoặc kịch bản.",
                    "Tôi thích diễn xuất, nhảy múa hoặc chụp ảnh.",
                    "Tôi thích trang trí nội thất hoặc thời trang.",
                    "Tôi thích làm việc tự do theo cảm hứng.",
                    "Tôi thích chơi nhạc cụ hoặc hát.",
                    "Tôi thích thiết kế đồ họa hoặc web.",
                    "Tôi thích sáng tạo ý tưởng mới lạ.",
                    "Tôi thích đọc sách văn học hoặc tiểu thuyết.",
                    "Tôi thích làm phim hoặc quay video.",
                ],
            },
            {
                "title": "XÃ HỘI",
                "icon": "👥",
                "subtitle": "Bạn có dễ kết nối và hỗ trợ người khác trong cuộc sống?",
                "category": "S",
                "options": [
                    "Tôi thích dạy học hoặc hướng dẫn người khác.",
                    "Tôi thích tư vấn, lắng nghe và giúp đỡ bạn bè.",
                    "Tôi thích làm việc chăm sóc sức khỏe như y tá.",
                    "Tôi thích tổ chức hoạt động nhóm hoặc sự kiện.",
                    "Tôi thích giao tiếp nhiều với mọi người.",
                    "Tôi thích làm việc từ thiện hoặc xã hội.",
                    "Tôi thích huấn luyện thể thao hoặc kỹ năng.",
                    "Tôi thích làm MC hoặc thuyết trình.",
                    "Tôi thích chăm sóc trẻ em hoặc người già.",
                    "Tôi thích làm việc nhóm để giải quyết vấn đề.",
                ],
            },
            {
                "title": "QUẢN LÝ",
                "icon": "💼",
                "subtitle": "Bạn có tố chất lãnh đạo và định hướng kết quả không?",
                "category": "E",
                "options": [
                    "Tôi thích lãnh đạo nhóm hoặc quản lý dự án.",
                    "Tôi thích thuyết phục người khác mua hàng.",
                    "Tôi thích kinh doanh hoặc khởi nghiệp.",
                    "Tôi thích tranh luận hoặc đàm phán.",
                    "Tôi thích làm việc cạnh tranh đạt doanh số.",
                    "Tôi thích bán hàng hoặc marketing.",
                    "Tôi thích làm chính trị hoặc lãnh đạo.",
                    "Tôi thích tổ chức sự kiện lớn.",
                    "Tôi thích quản lý tài chính hoặc kinh doanh.",
                    "Tôi thích thuyết trình trước đám đông.",
                ],
            },
            {
                "title": "NGHIỆP VỤ",
                "icon": "📋",
                "subtitle": "Bạn có xu hướng làm việc cẩn thận, nề nếp và quy củ?",
                "category": "C",
                "options": [
                    "Tôi thích sắp xếp tài liệu, hồ sơ gọn gàng.",
                    "Tôi thích làm việc với số liệu, tính toán chính xác.",
                    "Tôi thích tuân thủ quy tắc và lịch trình.",
                    "Tôi thích nhập liệu hoặc quản lý dữ liệu.",
                    "Tôi thích công việc chi tiết, cẩn thận.",
                    "Tôi thích làm kế toán hoặc ngân hàng.",
                    "Tôi thích sắp xếp lịch làm việc.",
                    "Tôi thích kiểm tra lỗi hoặc kiểm toán.",
                    "Tôi thích làm thư ký hoặc hành chính.",
                    "Tôi thích công việc có quy trình rõ ràng.",
                ],
            },
        ]

        self.section_answers = [[False] * len(s["options"]) for s in self.sections]
        self.current_section_index = 0

        self.configure(fg_color=self.ui["bg"])
        self.show_intro()

    def _launch_script(self, script_path: str) -> None:
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

    def back_to_home(self):
        if os.environ.get("EDM_PARENT_UI") == "1":
            self.destroy()
            return

        ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui.py")
        if not os.path.exists(ui_path):
            messagebox.showerror("Không tìm thấy file", "Không thấy file ui.py")
            return

        try:
            self._launch_script(ui_path)
            self.destroy()
        except Exception as exc:
            messagebox.showerror("Lỗi quay lại", f"Không mở được ui.py\n{exc}")

    def reset_quiz_state(self):
        self.scores = {"R": 0, "I": 0, "A": 0, "S": 0, "E": 0, "C": 0}
        self.section_answers = [[False] * len(s["options"]) for s in self.sections]
        self.check_vars = []
        self.option_cards = []
        self.current_section_index = 0

    def swap_frame(self):
        if hasattr(self, "current_frame"):
            self.current_frame.destroy()

        main = ctk.CTkFrame(self, fg_color=self.ui["bg"])
        main.pack(fill="both", expand=True)
        self.current_frame = main
        return main

    def show_intro(self):
        main = self.swap_frame()

        hero = ctk.CTkFrame(
            main,
            fg_color=self.ui["surface"],
            corner_radius=20,
            border_width=1,
            border_color=self.ui["line"],
        )
        hero.pack(fill="both", expand=True, padx=70, pady=50)

        ctk.CTkButton(
            hero,
            text="← Quay lại UI",
            command=self.back_to_home,
            height=38,
            width=140,
            font=("Segoe UI", 12, "bold"),
            fg_color=self.ui["muted_btn"],
            hover_color=self.ui["muted_btn_hover"],
            corner_radius=10,
        ).pack(anchor="w", padx=22, pady=(18, 4))

        accent_bar = ctk.CTkFrame(hero, fg_color=self.ui["primary"], height=12, corner_radius=20)
        accent_bar.pack(fill="x", padx=0, pady=(0, 20))

        ctk.CTkLabel(
            hero,
            text="HOLLAND RIASEC",
            font=("Segoe UI", 15, "bold"),
            text_color=self.ui["primary"],
        ).pack(pady=(15, 0))

        ctk.CTkLabel(
            hero,
            text="Trắc Nghiệm Định Hướng Nghề Nghiệp",
            font=("Segoe UI", 36, "bold"),
            text_color=self.ui["text"],
        ).pack(pady=(8, 20))

        ctk.CTkLabel(
            hero,
            text=(
                "KHÁM PHÁ NHÓM NGHỀ PHÙ HỢP DỰA TRÊN SÁU DANH MỤC\n"
              
            ),
            font=("Segoe UI", 15),
            text_color=self.ui["subtext"],
            justify="center",
        ).pack(pady=(0, 32))

        form = ctk.CTkFrame(hero, fg_color=self.ui["soft_surface"], corner_radius=16)
        form.pack(fill="x", padx=140, pady=(0, 25))

        ctk.CTkLabel(
            form,
            text="Tên của bạn (tùy chọn)",
            font=("Segoe UI", 14, "bold"),
            text_color=self.ui["text"],
        ).pack(anchor="w", padx=22, pady=(18, 8))

        self.name_entry = ctk.CTkEntry(
            form,
            height=46,
            font=("Segoe UI", 14),
            placeholder_text="Nhập tên hoặc để trống...",
            border_color=self.ui["line"],
            fg_color="white",
            text_color=self.ui["text"],
        )
        self.name_entry.pack(fill="x", padx=22, pady=(0, 18))

        ctk.CTkButton(
            hero,
            text="Bắt đầu làm bài",
            command=self.start_quiz,
            height=50,
            width=230,
            font=("Segoe UI", 16, "bold"),
            fg_color=self.ui["primary"],
            hover_color=self.ui["primary_hover"],
            corner_radius=14,
        ).pack(pady=(0, 20))

        ctk.CTkLabel(
            hero,
            text="Mỗi câu có thể chọn nhiều đáp án phù hợp với bản thân.",
            font=("Segoe UI", 12),
            text_color="#64748B",
        ).pack(pady=(0, 14))

    def start_quiz(self):
        self.user_name = self.name_entry.get().strip() or "Người dùng"
        self.reset_quiz_state()
        self.show_section(0)

    def show_section(self, index):
        self.current_section_index = index
        main = self.swap_frame()

        section = self.sections[index]
        style = self.category_styles[section["category"]]
        accent = style["accent"]
        soft = style["soft"]

        header = ctk.CTkFrame(
            main,
            fg_color=self.ui["surface"],
            corner_radius=18,
            border_width=1,
            border_color=self.ui["line"],
        )
        header.pack(fill="x", padx=35, pady=(25, 15))

        top_meta = ctk.CTkFrame(header, fg_color=self.ui["surface"])
        top_meta.pack(fill="x", padx=24, pady=(20, 0))

        ctk.CTkLabel(
            top_meta,
            text=f"PHẦN {index + 1}/{len(self.sections)}",
            font=("Segoe UI", 12, "bold"),
            text_color="#64748B",
        ).pack(side="left")

        tag = ctk.CTkFrame(top_meta, fg_color=soft, corner_radius=30, border_width=1, border_color=accent)
        tag.pack(side="right")
        ctk.CTkLabel(
            tag,
            text=f"{section['icon']} {style['name']}",
            font=("Segoe UI", 12, "bold"),
            text_color=accent,
        ).pack(padx=12, pady=5)

        ctk.CTkLabel(
            header,
            text=f"{section['icon']} {section['title']}",
            font=("Segoe UI", 30, "bold"),
            text_color=self.ui["text"],
        ).pack(anchor="w", padx=24, pady=(12, 6))

        ctk.CTkLabel(
            header,
            text=section["subtitle"],
            font=("Segoe UI", 14),
            text_color=self.ui["subtext"],
            wraplength=960,
            justify="left",
        ).pack(anchor="w", padx=24, pady=(0, 16))

        progress = ctk.CTkProgressBar(
            header,
            height=10,
            fg_color="#E2E8F0",
            progress_color=accent,
            corner_radius=999,
        )
        progress.pack(fill="x", padx=24, pady=(0, 22))
        progress.set((index + 1) / len(self.sections))

        card = ctk.CTkFrame(
            main,
            fg_color=self.ui["surface"],
            corner_radius=18,
            border_width=1,
            border_color=self.ui["line"],
        )
        card.pack(fill="both", expand=True, padx=35, pady=(0, 12))

        ctk.CTkLabel(
            card,
            text="Chọn một hoặc nhiều đáp án gần với bạn nhất",
            font=("Segoe UI", 16, "bold"),
            text_color=self.ui["text"],
        ).pack(anchor="w", padx=24, pady=(18, 8))

        ctk.CTkLabel(
            card,
            text="Màu câu hỏi đã được đồng bộ theo nhóm để dễ tập trung.",
            font=("Segoe UI", 12),
            text_color="#64748B",
        ).pack(anchor="w", padx=24, pady=(0, 12))

        scroll = ctk.CTkScrollableFrame(card, fg_color=self.ui["surface"])
        scroll.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        self.check_vars = []
        self.option_cards = []
        for opt_index, opt in enumerate(section["options"]):
            initial_state = self.section_answers[index][opt_index]
            var = ctk.BooleanVar(value=initial_state)
            self.check_vars.append(var)

            item = ctk.CTkFrame(
                scroll,
                fg_color=soft,
                corner_radius=12,
                border_width=1,
                border_color=self.blend_color(accent, "#FFFFFF", 0.48),
            )
            item.pack(fill="x", pady=7, padx=6)

            item.bind("<Enter>", lambda _e, i=opt_index: self.set_option_hover(i, True))
            item.bind("<Leave>", lambda _e, i=opt_index: self.set_option_hover(i, False))

            cb = ctk.CTkCheckBox(
                item,
                text=opt,
                variable=var,
                command=lambda i=opt_index: self.update_option_style(i),
                font=("Segoe UI", 13),
                text_color=self.ui["text"],
                fg_color=accent,
                hover_color=self.shift_color(accent, -18),
                border_color=accent,
                checkmark_color="white",
                width=30,
            )
            cb.pack(anchor="w", padx=14, pady=10, fill="x")

            self.option_cards.append({"frame": item, "soft": soft, "accent": accent, "hover": False})
            self.update_option_style(opt_index)

        nav = ctk.CTkFrame(main, fg_color=self.ui["bg"])
        nav.pack(fill="x", padx=35, pady=(4, 20))

        ctk.CTkButton(
            nav,
            text="Về UI chính",
            command=self.back_to_home,
            height=45,
            width=140,
            font=("Segoe UI", 13, "bold"),
            fg_color=self.ui["muted_btn"],
            hover_color=self.ui["muted_btn_hover"],
            corner_radius=12,
        ).pack(side="left", padx=6)

        if index > 0:
            ctk.CTkButton(
                nav,
                text="Quay lại",
                command=lambda: self.previous_section(index),
                height=45,
                width=140,
                font=("Segoe UI", 13, "bold"),
                fg_color=self.ui["muted_btn"],
                hover_color=self.ui["muted_btn_hover"],
                corner_radius=12,
            ).pack(side="left", padx=6)

        next_text = "Hoàn thành" if index == len(self.sections) - 1 else "Tiếp theo"
        ctk.CTkButton(
            nav,
            text=next_text,
            command=lambda: self.next_section(index),
            height=45,
            width=160,
            font=("Segoe UI", 13, "bold"),
            fg_color=accent,
            hover_color=self.shift_color(accent, -20),
            corner_radius=12,
        ).pack(side="right", padx=6)

    def set_option_hover(self, option_index, is_hovering):
        if option_index < len(self.option_cards):
            self.option_cards[option_index]["hover"] = is_hovering
            self.update_option_style(option_index)

    def update_option_style(self, option_index):
        if option_index >= len(self.option_cards):
            return

        card = self.option_cards[option_index]
        accent = card["accent"]
        selected = self.check_vars[option_index].get()
        hovering = card["hover"]

        if selected:
            bg = self.blend_color(accent, "#FFFFFF", 0.82)
            border = accent
        elif hovering:
            bg = self.blend_color(accent, "#FFFFFF", 0.92)
            border = self.blend_color(accent, "#FFFFFF", 0.42)
        else:
            bg = card["soft"]
            border = self.blend_color(accent, "#FFFFFF", 0.52)

        card["frame"].configure(fg_color=bg, border_color=border)

    def persist_section_answers(self, index):
        section = self.sections[index]
        cat = section["category"]

        new_answers = [v.get() for v in self.check_vars]
        old_answers = self.section_answers[index]

        self.scores[cat] += sum(new_answers) - sum(old_answers)
        self.section_answers[index] = new_answers

    def previous_section(self, index):
        self.persist_section_answers(index)
        self.show_section(index - 1)

    def next_section(self, index):
        self.persist_section_answers(index)

        if index == len(self.sections) - 1:
            self.show_result()
        else:
            self.show_section(index + 1)

    def show_result(self):
        main = self.swap_frame()

        order = {cat: idx for idx, cat in enumerate(self.scores.keys())}
        sorted_scores = sorted(self.scores.items(), key=lambda x: (-x[1], order[x[0]]))
        top3 = sorted_scores[:3]
        code = "".join([cat for cat, _score in top3])

        header = ctk.CTkFrame(
            main,
            fg_color=self.ui["surface"],
            corner_radius=20,
            border_width=1,
            border_color=self.ui["line"],
        )
        header.pack(fill="x", padx=35, pady=(25, 14))

        ctk.CTkLabel(
            header,
            text=f"Kết quả của {self.user_name}",
            font=("Segoe UI", 15, "bold"),
            text_color=self.ui["subtext"],
        ).pack(anchor="w", padx=24, pady=(20, 6))

        ctk.CTkLabel(
            header,
            text="Mã Holland của bạn",
            font=("Segoe UI", 28, "bold"),
            text_color=self.ui["text"],
        ).pack(anchor="w", padx=24, pady=(0, 8))

        code_box = ctk.CTkFrame(
            header,
            fg_color="#ECFDF5",
            corner_radius=14,
            border_width=1,
            border_color="#A7F3D0",
        )
        code_box.pack(anchor="w", padx=24, pady=(0, 18))
        ctk.CTkLabel(
            code_box,
            text=f"{' - '.join(code)}",
            font=("Segoe UI", 28, "bold"),
            text_color=self.ui["success"],
        ).pack(padx=18, pady=8)

        ctk.CTkLabel(
            header,
            text="Top 3 nhóm nổi trội được xếp theo điểm cao nhất.",
            font=("Segoe UI", 12),
            text_color="#64748B",
        ).pack(anchor="w", padx=24, pady=(0, 20))

        body = ctk.CTkScrollableFrame(
            main,
            fg_color=self.ui["surface"],
            corner_radius=20,
            border_width=1,
            border_color=self.ui["line"],
        )
        body.pack(fill="both", expand=True, padx=35, pady=(0, 12))

        ctk.CTkLabel(
            body,
            text="Top 3 điểm mạnh",
            font=("Segoe UI", 18, "bold"),
            text_color=self.ui["text"],
        ).pack(anchor="w", padx=20, pady=(18, 8))

        max_per_category = {s["category"]: len(s["options"]) for s in self.sections}
        for rank, (cat, score) in enumerate(top3, 1):
            style = self.category_styles[cat]
            rank_card = ctk.CTkFrame(
                body,
                fg_color=style["soft"],
                corner_radius=14,
                border_width=1,
                border_color=style["accent"],
            )
            rank_card.pack(fill="x", padx=20, pady=7)

            ctk.CTkLabel(
                rank_card,
                text=f"Hạng {rank}  •  {cat} - {style['name']}",
                font=("Segoe UI", 15, "bold"),
                text_color=style["accent"],
            ).pack(anchor="w", padx=16, pady=(12, 4))

            ctk.CTkLabel(
                rank_card,
                text=f"Điểm: {score}/{max_per_category[cat]}",
                font=("Segoe UI", 13),
                text_color=self.ui["text"],
            ).pack(anchor="w", padx=16, pady=(0, 12))

        ctk.CTkLabel(
            body,
            text="Phân bố điểm 6 nhóm",
            font=("Segoe UI", 18, "bold"),
            text_color=self.ui["text"],
        ).pack(anchor="w", padx=20, pady=(18, 8))

        for cat, score in sorted_scores:
            style = self.category_styles[cat]
            row = ctk.CTkFrame(body, fg_color=self.ui["surface"])
            row.pack(fill="x", padx=20, pady=6)

            ctk.CTkLabel(
                row,
                text=f"{cat} - {style['name']}",
                width=210,
                anchor="w",
                font=("Segoe UI", 13, "bold"),
                text_color=self.ui["text"],
            ).pack(side="left")

            bar = ctk.CTkProgressBar(
                row,
                width=520,
                height=12,
                fg_color="#E2E8F0",
                progress_color=style["accent"],
                corner_radius=999,
            )
            bar.pack(side="left", padx=10)
            max_score = max_per_category[cat]
            bar.set(score / max_score if max_score else 0)

            ctk.CTkLabel(
                row,
                text=f"{score}/{max_score}",
                width=74,
                anchor="e",
                font=("Segoe UI", 12, "bold"),
                text_color="#334155",
            ).pack(side="left")

        ctk.CTkLabel(
            body,
            text="Gợi ý nghề nghiệp theo mã của bạn",
            font=("Segoe UI", 18, "bold"),
            text_color=self.ui["text"],
        ).pack(anchor="w", padx=20, pady=(20, 8))

        for cat in code:
            style = self.category_styles[cat]
            job_card = ctk.CTkFrame(
                body,
                fg_color=self.ui["soft_surface"],
                corner_radius=12,
                border_width=1,
                border_color=self.ui["line"],
            )
            job_card.pack(fill="x", padx=20, pady=5)

            ctk.CTkLabel(
                job_card,
                text=f"{cat} - {style['name']}",
                font=("Segoe UI", 13, "bold"),
                text_color=style["accent"],
            ).pack(anchor="w", padx=14, pady=(10, 2))

            ctk.CTkLabel(
                job_card,
                text=self.jobs.get(cat, ""),
                font=("Segoe UI", 12),
                text_color=self.ui["subtext"],
                wraplength=860,
                justify="left",
            ).pack(anchor="w", padx=14, pady=(0, 10))

        nav = ctk.CTkFrame(main, fg_color=self.ui["bg"])
        nav.pack(fill="x", padx=35, pady=(6, 20))

        ctk.CTkButton(
            nav,
            text="Về UI chính",
            command=self.back_to_home,
            height=45,
            width=130,
            font=("Segoe UI", 13, "bold"),
            fg_color=self.ui["muted_btn"],
            hover_color=self.ui["muted_btn_hover"],
            corner_radius=12,
        ).pack(side="left", padx=6)

        ctk.CTkButton(
            nav,
            text="Làm lại",
            command=self.restart,
            height=45,
            width=130,
            font=("Segoe UI", 13, "bold"),
            fg_color=self.ui["primary"],
            hover_color=self.ui["primary_hover"],
            corner_radius=12,
        ).pack(side="left", padx=6)

        ctk.CTkButton(
            nav,
            text="Thoát",
            command=self.quit,
            height=45,
            width=130,
            font=("Segoe UI", 13, "bold"),
            fg_color=self.ui["muted_btn"],
            hover_color=self.ui["muted_btn_hover"],
            corner_radius=12,
        ).pack(side="left", padx=6)

        date_str = datetime.now().strftime("%d/%m/%Y %H:%M")
        c.execute(
            "INSERT INTO results (name, date, code, scores) VALUES (?, ?, ?, ?)",
            (self.user_name, date_str, code, json.dumps(self.scores)),
        )
        conn.commit()

    def blend_color(self, color_a, color_b, ratio):
        ratio = max(0.0, min(1.0, ratio))
        a = color_a.lstrip("#")
        b = color_b.lstrip("#")
        ar, ag, ab = int(a[0:2], 16), int(a[2:4], 16), int(a[4:6], 16)
        br, bg, bb = int(b[0:2], 16), int(b[2:4], 16), int(b[4:6], 16)
        r = int(ar * (1 - ratio) + br * ratio)
        g = int(ag * (1 - ratio) + bg * ratio)
        b = int(ab * (1 - ratio) + bb * ratio)
        return f"#{r:02x}{g:02x}{b:02x}"

    def shift_color(self, hex_color, delta):
        code = hex_color.lstrip("#")
        r = min(255, max(0, int(code[0:2], 16) + delta))
        g = min(255, max(0, int(code[2:4], 16) + delta))
        b = min(255, max(0, int(code[4:6], 16) + delta))
        return f"#{r:02x}{g:02x}{b:02x}"

    def restart(self):
        self.reset_quiz_state()
        self.show_intro()


if __name__ == "__main__":
    app = HollandQuizApp()
    app.mainloop()
