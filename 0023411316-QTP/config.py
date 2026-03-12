# ────────────────────────────────────────────────
# DATABASE CONFIGURATION
# ────────────────────────────────────────────────

DB_CONFIG = {
    "SERVER": "DESKTOP-5V5LP3S",      # Thay bằng server của bạn
    "DATABASE": "tuvan_truong",        # Tên database
    "DRIVER": "ODBC Driver 17 for SQL Server",
    "TRUSTED_CONNECTION": True         # Dùng Windows Authentication
}

# Nếu muốn dùng SQL Authentication (user/password) thì dùng cái này:
# DB_CONFIG = {
#     "SERVER": "localhost",
#     "DATABASE": "tuvan_truong",
#     "USER": "sa",
#     "PASSWORD": "your_password",
#     "DRIVER": "ODBC Driver 17 for SQL Server",
#     "TRUSTED_CONNECTION": False
# }