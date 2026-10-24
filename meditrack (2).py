import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from decimal import Decimal
import ctypes
import random

from database import connect_database


# ============================================================
# DPI SETTINGS
# ============================================================

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


# ============================================================
# MEDI TRACK APPLICATION
# ============================================================

class MediTrackApp:

    # ---------------- COLORS ----------------

    BG = "#F3F6FB"
    NAVY = "#172D50"
    NAVY_DARK = "#102442"
    BLUE = "#2F70E8"
    TEXT = "#20334F"
    MUTED = "#71819A"
    BORDER = "#E1E8F2"
    GREEN = "#159B72"
    ORANGE = "#D99016"
    RED = "#D94B5B"
    PURPLE = "#7657D8"
    WHITE = "#FFFFFF"

    LOW_STOCK_LIMIT = 10
    EXPIRY_WARNING_DAYS = 30

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(self, root):

        self.root = root

        self.root.title(
            "MediTrack | Medical Store Management System"
        )

        self.root.geometry("1500x900")
        self.root.minsize(1150, 720)
        self.root.configure(bg=self.BG)

        self.username = ""
        self.role = ""

        self.medicines = []
        self.patients = []
        self.cart = []

        self.current_page = ""

        self.tree = None
        self.bill_tree = None

        self.setup_styles()

        self.show_login()

    # ========================================================
    # DATABASE CONNECTION
    # ========================================================

    def db(self):

        conn = connect_database()

        if conn is None:

            messagebox.showerror(
                "Database Error",
                "Could not connect to MySQL.\n\n"
                "Please check database.py and MySQL."
            )

        return conn

    # ========================================================
    # LOAD MEDICINES
    # ========================================================

    def load_medicines(self):

        conn = self.db()

        if not conn:
            return

        try:

            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT
                    product_id,
                    product_name,
                    product_category,
                    batch_number,
                    quantity,
                    manufacturing_date,
                    expiry_date,
                    supplier,
                    price,
                    stock_entry_date,
                    status,
                    purchase_price,
                    selling_price,
                    minimum_stock
                FROM products
                ORDER BY product_name
            """)

            self.medicines = cursor.fetchall()

            cursor.close()
            conn.close()

        except Exception as e:

            messagebox.showerror(
                "Database Error",
                f"Could not load medicines.\n\n{e}"
            )

            try:
                conn.close()
            except:
                pass

    # ========================================================
    # LOAD PATIENTS
    # ========================================================

    def load_patients(self):

        conn = self.db()

        if not conn:
            return

        try:

            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT
                    patient_id,
                    patient_name,
                    age,
                    gender,
                    phone,
                    address
                FROM patients
                ORDER BY patient_name
            """)

            self.patients = cursor.fetchall()

            cursor.close()
            conn.close()

        except Exception:
            self.patients = []

            try:
                conn.close()
            except:
                pass

    # ========================================================
    # STATUS CALCULATION
    # ========================================================

    def product_status(self, medicine):

        quantity = int(
            medicine.get("quantity") or 0
        )

        expiry = medicine.get("expiry_date")

        if hasattr(expiry, "date"):
            expiry = expiry.date()

        elif isinstance(expiry, str):

            expiry = datetime.strptime(
                expiry[:10],
                "%Y-%m-%d"
            ).date()

        minimum = int(
            medicine.get("minimum_stock")
            or self.LOW_STOCK_LIMIT
        )

        days_left = (
            expiry - date.today()
        ).days

        if quantity == 0:
            return "Out of Stock"

        if days_left < 0:
            return "Expired"

        if days_left <= self.EXPIRY_WARNING_DAYS:
            return "Expiring Soon"

        if quantity <= minimum:
            return "Low Stock"

        return "Safe"

    # ========================================================
    # SETUP STYLE
    # ========================================================

    def setup_styles(self):

        style = ttk.Style()

        style.theme_use("clam")

        style.configure(
            "Treeview",
            background=self.WHITE,
            fieldbackground=self.WHITE,
            foreground=self.TEXT,
            rowheight=40,
            borderwidth=0,
            font=("Segoe UI", 10)
        )

        style.configure(
            "Treeview.Heading",
            background="#EDF2F9",
            foreground=self.TEXT,
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padding=(8, 10)
        )

        style.map(
            "Treeview",
            background=[
                ("selected", "#DCE9FF")
            ],
            foreground=[
                ("selected", self.TEXT)
            ]
        )

    # ========================================================
    # LOGIN SCREEN
    # ========================================================

    def show_login(self):

        for widget in self.root.winfo_children():
            widget.destroy()

        background = tk.Frame(
            self.root,
            bg=self.NAVY
        )

        background.pack(
            fill="both",
            expand=True
        )

        # ---------------- LEFT ----------------

        left = tk.Frame(
            background,
            bg=self.NAVY
        )

        left.place(
            relx=0,
            rely=0,
            relwidth=.53,
            relheight=1
        )

        tk.Label(
            left,
            text="✚",
            bg=self.BLUE,
            fg="white",
            font=("Segoe UI", 44, "bold"),
            width=3
        ).pack(pady=(150, 20))

        tk.Label(
            left,
            text="MediTrack",
            bg=self.NAVY,
            fg="white",
            font=("Segoe UI", 34, "bold")
        ).pack()

        tk.Label(
            left,
            text="MEDICAL STORE MANAGEMENT SYSTEM",
            bg=self.NAVY,
            fg="#B8C8E0",
            font=("Segoe UI", 12, "bold")
        ).pack(pady=8)

        tk.Label(
            left,
            text="Inventory  •  Billing  •  Patients  •  Reports",
            bg=self.NAVY,
            fg="#D3DFF0",
            font=("Segoe UI", 11)
        ).pack()

        # ---------------- RIGHT ----------------

        right = tk.Frame(
            background,
            bg=self.WHITE
        )

        right.place(
            relx=.53,
            rely=0,
            relwidth=.47,
            relheight=1
        )

        card = tk.Frame(
            right,
            bg=self.WHITE,
            highlightbackground=self.BORDER,
            highlightthickness=1
        )

        card.place(
            relx=.5,
            rely=.5,
            anchor="center",
            width=430,
            height=470
        )

        tk.Label(
            card,
            text="Welcome Back",
            bg=self.WHITE,
            fg=self.TEXT,
            font=("Segoe UI", 23, "bold")
        ).pack(pady=(45, 6))

        tk.Label(
            card,
            text="Login to continue to MediTrack",
            bg=self.WHITE,
            fg=self.MUTED,
            font=("Segoe UI", 10)
        ).pack(pady=(0, 28))

        # USERNAME

        tk.Label(
            card,
            text="Username",
            bg=self.WHITE,
            fg=self.TEXT,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", padx=45)

        self.login_user = tk.Entry(
            card,
            bg="#F8FAFD",
            fg=self.TEXT,
            relief="flat",
            highlightbackground=self.BORDER,
            highlightthickness=1,
            font=("Segoe UI", 11)
        )

        self.login_user.pack(
            fill="x",
            padx=45,
            ipady=10,
            pady=(7, 18)
        )

        # PASSWORD

        tk.Label(
            card,
            text="Password",
            bg=self.WHITE,
            fg=self.TEXT,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", padx=45)

        self.login_pass = tk.Entry(
            card,
            show="*",
            bg="#F8FAFD",
            fg=self.TEXT,
            relief="flat",
            highlightbackground=self.BORDER,
            highlightthickness=1,
            font=("Segoe UI", 11)
        )

        self.login_pass.pack(
            fill="x",
            padx=45,
            ipady=10,
            pady=(7, 25)
        )

        self.login_pass.bind(
            "<Return>",
            lambda event: self.login()
        )

        # LOGIN BUTTON

        tk.Button(
            card,
            text="LOGIN  →",
            command=self.login,
            bg=self.BLUE,
            fg="white",
            activebackground=self.NAVY,
            activeforeground="white",
            bd=0,
            cursor="hand2",
            font=("Segoe UI", 11, "bold"),
            pady=12
        ).pack(
            fill="x",
            padx=45
        )

        tk.Label(
            card,
            text="Default: admin / admin123",
            bg=self.WHITE,
            fg=self.MUTED,
            font=("Segoe UI", 9)
        ).pack(pady=22)

        self.login_user.focus_set()

    # ========================================================
    # LOGIN
    # ========================================================

    def login(self):

        username = self.login_user.get().strip()
        password = self.login_pass.get()

        if not username or not password:

            messagebox.showwarning(
                "Login",
                "Enter username and password."
            )

            return

        conn = self.db()

        if not conn:
            return

        try:

            cursor = conn.cursor(
                dictionary=True
            )

            cursor.execute(
                """
                SELECT username, role
                FROM users
                WHERE username=%s
                AND password=%s
                """,
                (username, password)
            )

            user = cursor.fetchone()

            cursor.close()
            conn.close()

            if not user:

                messagebox.showerror(
                    "Login Failed",
                    "Invalid username or password."
                )

                return

            self.username = user["username"]
            self.role = user["role"]

            self.build_application()

        except Exception as e:

            messagebox.showerror(
                "Login Error",
                str(e)
            )

    # ========================================================
    # MAIN APPLICATION
    # ========================================================

    def build_application(self):

        for widget in self.root.winfo_children():
            widget.destroy()

        self.load_medicines()
        self.load_patients()

        self.shell = tk.Frame(
            self.root,
            bg=self.BG
        )

        self.shell.pack(
            fill="both",
            expand=True
        )

        # SIDEBAR

        self.sidebar = tk.Frame(
            self.shell,
            bg=self.NAVY,
            width=245
        )

        self.sidebar.pack(
            side="left",
            fill="y"
        )

        self.sidebar.pack_propagate(False)

        # MAIN

        self.main = tk.Frame(
            self.shell,
            bg=self.BG
        )

        self.main.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.build_sidebar()
        self.build_topbar()

        self.content = tk.Frame(
            self.main,
            bg=self.BG
        )

        self.content.pack(
            fill="both",
            expand=True,
            padx=28,
            pady=24
        )

        self.show_page("Dashboard")

    # ========================================================
    # SIDEBAR
    # ========================================================

    def build_sidebar(self):

        brand = tk.Frame(
            self.sidebar,
            bg=self.NAVY
        )

        brand.pack(
            fill="x",
            padx=20,
            pady=(25, 28)
        )

        tk.Label(
            brand,
            text="✚",
            bg=self.BLUE,
            fg="white",
            font=("Segoe UI", 21, "bold"),
            width=2
        ).pack(
            side="left",
            padx=(0, 11)
        )

        brand_text = tk.Frame(
            brand,
            bg=self.NAVY
        )

        brand_text.pack(
            side="left"
        )

        tk.Label(
            brand_text,
            text="MediTrack",
            bg=self.NAVY,
            fg="white",
            font=("Segoe UI", 17, "bold")
        ).pack(anchor="w")

        tk.Label(
            brand_text,
            text="MEDICAL MANAGEMENT",
            bg=self.NAVY,
            fg="#AFC0D9",
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w")

        tk.Label(
            self.sidebar,
            text="WORKSPACE",
            bg=self.NAVY,
            fg="#A9BBD5",
            font=("Segoe UI", 9, "bold")
        ).pack(
            anchor="w",
            padx=24,
            pady=(0, 8)
        )

        menu = [
            ("Dashboard", "▦"),
            ("Medicine Inventory", "💊"),
            ("Add Medicine", "+"),
            ("Billing", "▣"),
            ("Patients", "♙"),
            ("Restock", "📦"),
            ("Stock Alerts", "!"),
            ("Expiry Alerts", "⚠"),
            ("Sales Reports", "▥"),
            ("Bill History", "▤")
        ]

        self.nav_buttons = {}

        for name, icon in menu:

            button = tk.Button(
                self.sidebar,
                text=f"  {icon}   {name}",
                command=lambda p=name:
                self.show_page(p),
                anchor="w",
                bd=0,
                relief="flat",
                cursor="hand2",
                bg=self.NAVY,
                fg="#D3DFF0",
                activebackground=self.BLUE,
                activeforeground="white",
                font=("Segoe UI", 10),
                padx=12,
                pady=11
            )

            button.pack(
                fill="x",
                padx=10,
                pady=2
            )

            self.nav_buttons[name] = button

        bottom = tk.Frame(
            self.sidebar,
            bg=self.NAVY
        )

        bottom.pack(
            side="bottom",
            fill="x",
            padx=18,
            pady=18
        )

        tk.Label(
            bottom,
            text=f"Logged in: {self.username}",
            bg=self.NAVY,
            fg="#B8C8E0",
            font=("Segoe UI", 9)
        ).pack(anchor="w")

        tk.Label(
            bottom,
            text=self.role,
            bg=self.NAVY,
            fg="#8198B8",
            font=("Segoe UI", 8)
        ).pack(anchor="w")

        tk.Button(
            bottom,
            text="↪  Logout",
            command=self.logout,
            bg="#233D63",
            fg="white",
            activebackground=self.RED,
            bd=0,
            cursor="hand2",
            font=("Segoe UI", 9, "bold"),
            pady=8
        ).pack(
            fill="x",
            pady=(10, 0)
        )

    # ========================================================
    # TOP BAR
    # ========================================================

    def build_topbar(self):

        self.topbar = tk.Frame(
            self.main,
            bg=self.WHITE,
            height=68
        )

        self.topbar.pack(fill="x")
        self.topbar.pack_propagate(False)

        self.page_title = tk.Label(
            self.topbar,
            text="Dashboard",
            bg=self.WHITE,
            fg=self.TEXT,
            font=("Segoe UI", 18, "bold")
        )

        self.page_title.pack(
            side="left",
            padx=30
        )

        tk.Label(
            self.topbar,
            text="●  DATABASE CONNECTED",
            bg=self.WHITE,
            fg=self.GREEN,
            font=("Segoe UI", 9, "bold")
        ).pack(
            side="right",
            padx=30
        )

    # ========================================================
    # LOGOUT
    # ========================================================

    def logout(self):

        if messagebox.askyesno(
            "Logout",
            "Do you want to logout?"
        ):

            self.username = ""
            self.role = ""
            self.cart = []

            self.show_login()

    # ========================================================
    # PAGE NAVIGATION
    # ========================================================

    def clear_content(self):

        for widget in self.content.winfo_children():
            widget.destroy()

    def show_page(self, page):

        self.current_page = page

        self.page_title.config(
            text=page
        )

        for name, button in self.nav_buttons.items():

            active = name == page

            button.config(
                bg=self.BLUE if active else self.NAVY,
                fg="white"
                if active
                else "#D3DFF0",
                font=(
                    "Segoe UI",
                    10,
                    "bold" if active else "normal"
                )
            )

        self.clear_content()

        self.tree = None

        if page == "Dashboard":
            self.build_dashboard()

        elif page == "Medicine Inventory":
            self.build_inventory_page()

        elif page == "Add Medicine":
            self.open_medicine_form()

        elif page == "Billing":
            self.build_billing_page()

        elif page == "Patients":
            self.build_patients_page()

        elif page == "Restock":
            self.build_restock_page()

        elif page == "Stock Alerts":
            self.build_alert_page("stock")

        elif page == "Expiry Alerts":
            self.build_alert_page("expiry")

        elif page == "Sales Reports":
            self.build_sales_report()

        elif page == "Bill History":
            self.build_bill_history()

    # ========================================================
    # DASHBOARD COUNT
    # ========================================================

    def get_counts(self):

        statuses = [
            self.product_status(p)
            for p in self.medicines
        ]

        return {

            "total":
                len(self.medicines),

            "stock":
                sum(
                    int(p["quantity"] or 0)
                    for p in self.medicines
                ),

            "low":
                statuses.count("Low Stock"),

            "out":
                statuses.count("Out of Stock"),

            "soon":
                statuses.count("Expiring Soon"),

            "expired":
                statuses.count("Expired")
        }

    # ========================================================
    # TODAY SALES
    # ========================================================

    def today_sales(self):

        conn = self.db()

        if not conn:
            return Decimal("0"), 0

        try:

            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    COALESCE(SUM(grand_total),0),
                    COUNT(*)
                FROM bills
                WHERE DATE(bill_date)=CURDATE()
            """)

            total, count = cursor.fetchone()

            cursor.close()
            conn.close()

            return (
                Decimal(str(total or 0)),
                int(count or 0)
            )

        except Exception:

            try:
                conn.close()
            except:
                pass

            return Decimal("0"), 0

    # ========================================================
    # DASHBOARD CARD
    # ========================================================

    def make_card(
        self,
        parent,
        title,
        value,
        subtitle,
        color,
        icon,
        command
    ):

        card = tk.Frame(
            parent,
            bg=self.WHITE,
            highlightbackground=self.BORDER,
            highlightthickness=1,
            cursor="hand2"
        )

        def click(event=None):
            command()

        card.bind(
            "<Button-1>",
            click
        )

        title_label = tk.Label(
            card,
            text=title,
            bg=self.WHITE,
            fg=self.MUTED,
            font=("Segoe UI", 9, "bold")
        )

        title_label.pack(
            anchor="w",
            padx=17,
            pady=(15, 4)
        )

        title_label.bind(
            "<Button-1>",
            click
        )

        icon_label = tk.Label(
            card,
            text=icon,
            bg=color,
            fg="white",
            font=("Segoe UI", 14, "bold"),
            width=3
        )

        icon_label.pack(
            anchor="e",
            padx=16
        )

        icon_label.bind(
            "<Button-1>",
            click
        )

        value_label = tk.Label(
            card,
            text=str(value),
            bg=self.WHITE,
            fg=self.TEXT,
            font=("Segoe UI", 24, "bold")
        )

        value_label.pack(
            anchor="w",
            padx=17
        )

        value_label.bind(
            "<Button-1>",
            click
        )

        subtitle_label = tk.Label(
            card,
            text=subtitle,
            bg=self.WHITE,
            fg=self.MUTED,
            font=("Segoe UI", 8)
        )

        subtitle_label.pack(
            anchor="w",
            padx=17,
            pady=(0, 15)
        )

        subtitle_label.bind(
            "<Button-1>",
            click
        )

        return card

    # ========================================================
    # DASHBOARD
    # ========================================================

    def build_dashboard(self):

        counts = self.get_counts()

        sales, bills = self.today_sales()

        heading = tk.Frame(
            self.content,
            bg=self.BG
        )

        heading.pack(
            fill="x",
            pady=(0, 17)
        )

        tk.Label(
            heading,
            text=f"Good day, {self.username} 👋",
            bg=self.BG,
            fg=self.TEXT,
            font=("Segoe UI", 15, "bold")
        ).pack(anchor="w")

        tk.Label(
            heading,
            text="Manage medicines, billing, patients and stock.",
            bg=self.BG,
            fg=self.MUTED,
            font=("Segoe UI", 9)
        ).pack(
            anchor="w",
            pady=(4, 0)
        )

        # ---------------- CARDS ----------------

        cards = tk.Frame(
            self.content,
            bg=self.BG
        )

        cards.pack(
            fill="x",
            pady=(0, 20)
        )

        data = [

            (
                "Total Medicines",
                counts["total"],
                "Products",
                self.BLUE,
                "💊",
                lambda:
                self.show_page(
                    "Medicine Inventory"
                )
            ),

            (
                "Total Stock",
                counts["stock"],
                "Units available",
                self.GREEN,
                "📦",
                lambda:
                self.show_page(
                    "Medicine Inventory"
                )
            ),

            (
                "Low Stock",
                counts["low"],
                "Need restocking",
                self.ORANGE,
                "!",
                lambda:
                self.show_page(
                    "Stock Alerts"
                )
            ),

            (
                "Expiring Soon",
                counts["soon"],
                "Within 30 days",
                self.RED,
                "⚠",
                lambda:
                self.show_page(
                    "Expiry Alerts"
                )
            ),

            (
                "Today's Bills",
                bills,
                "Bills generated",
                self.PURPLE,
                "▣",
                lambda:
                self.show_page(
                    "Bill History"
                )
            ),

            (
                "Today's Sales",
                f"₹{sales:.2f}",
                "Revenue",
                self.GREEN,
                "₹",
                lambda:
                self.show_page(
                    "Sales Reports"
                )
            )
        ]

        for i, item in enumerate(data):

            cards.columnconfigure(
                i,
                weight=1
            )

            self.make_card(
                cards,
                *item
            ).grid(
                row=0,
                column=i,
                sticky="nsew",
                padx=4
            )

        # ---------------- QUICK ACTIONS ----------------

        quick = tk.Frame(
            self.content,
            bg=self.WHITE,
            highlightbackground=self.BORDER,
            highlightthickness=1
        )

        quick.pack(
            fill="x",
            pady=(0, 18)
        )

        tk.Label(
            quick,
            text="Quick Actions",
            bg=self.WHITE,
            fg=self.TEXT,
            font=("Segoe UI", 12, "bold")
        ).pack(
            anchor="w",
            padx=20,
            pady=(15, 10)
        )

        actions = [

            (
                "＋  Add Medicine",
                self.BLUE,
                lambda:
                self.show_page(
                    "Add Medicine"
                )
            ),

            (
                "🧾  New Bill",
                self.GREEN,
                lambda:
                self.show_page(
                    "Billing"
                )
            ),

            (
                "👤  Add Patient",
                self.PURPLE,
                lambda:
                self.show_page(
                    "Patients"
                )
            ),

            (
                "📦  Restock",
                self.ORANGE,
                lambda:
                self.show_page(
                    "Restock"
                )
            )
        ]

        buttons_frame = tk.Frame(
            quick,
            bg=self.WHITE
        )

        buttons_frame.pack(
            fill="x",
            padx=20,
            pady=(0, 16)
        )

        for text, color, command in actions:

            tk.Button(
                buttons_frame,
                text=text,
                command=command,
                bg=color,
                fg="white",
                activebackground=self.NAVY,
                bd=0,
                cursor="hand2",
                font=("Segoe UI", 9, "bold"),
                padx=18,
                pady=10
            ).pack(
                side="left",
                padx=(0, 10)
            )

        # ---------------- NOTIFICATIONS ----------------

        notification = tk.Frame(
            self.content,
            bg=self.WHITE,
            highlightbackground=self.BORDER,
            highlightthickness=1
        )

        notification.pack(
            fill="both",
            expand=True
        )

        tk.Label(
            notification,
            text="🔔 Live Stock Notifications",
            bg=self.WHITE,
            fg=self.TEXT,
            font=("Segoe UI", 12, "bold")
        ).pack(
            anchor="w",
            padx=20,
            pady=(15, 10)
        )

        low_items = [

            p for p in self.medicines

            if self.product_status(p)
            in (
                "Low Stock",
                "Out of Stock"
            )
        ]

        if not low_items:

            tk.Label(
                notification,
                text="✓ All medicines have sufficient stock.",
                bg=self.WHITE,
                fg=self.GREEN,
                font=("Segoe UI", 10, "bold")
            ).pack(
                anchor="w",
                padx=20,
                pady=10
            )

        else:

            for p in low_items[:8]:

                status = self.product_status(p)

                if status == "Out of Stock":

                    text = (
                        f"🔴 {p['product_name']} "
                        f"— OUT OF STOCK"
                    )

                else:

                    text = (
                        f"⚠ {p['product_name']} "
                        f"— {p['quantity']} units remaining "
                        f"(minimum "
                        f"{p.get('minimum_stock') or 10})"
                    )

                tk.Label(
                    notification,
                    text=text,
                    bg="#FFECEF"
                    if status == "Out of Stock"
                    else "#FFF8E9",
                    fg=self.RED
                    if status == "Out of Stock"
                    else self.ORANGE,
                    font=("Segoe UI", 9, "bold"),
                    anchor="w"
                ).pack(
                    fill="x",
                    padx=20,
                    pady=3,
                    ipady=5
                )

    # ========================================================
    # INVENTORY PAGE
    # ========================================================

    def build_inventory_page(self):

        header = tk.Frame(
            self.content,
            bg=self.BG
        )

        header.pack(
            fill="x",
            pady=(0, 14)
        )

        tk.Label(
            header,
            text="Medicine Inventory",
            bg=self.BG,
            fg=self.TEXT,
            font=("Segoe UI", 14, "bold")
        ).pack(side="left")

        tk.Button(
            header,
            text="+  Add Medicine",
            command=lambda:
            self.show_page(
                "Add Medicine"
            ),
            bg=self.BLUE,
            fg="white",
            activebackground=self.NAVY,
            bd=0,
            cursor="hand2",
            font=("Segoe UI", 9, "bold"),
            padx=18,
            pady=9
        ).pack(side="right")

        # SEARCH

        search = tk.Frame(
            self.content,
            bg=self.WHITE,
            highlightbackground=self.BORDER,
            highlightthickness=1
        )

        search.pack(
            fill="x",
            pady=(0, 12)
        )

        tk.Label(
            search,
            text="🔍",
            bg=self.WHITE,
            fg=self.MUTED
        ).pack(
            side="left",
            padx=15
        )

        self.inv_search = tk.StringVar()

        entry = tk.Entry(
            search,
            textvariable=self.inv_search,
            bg=self.WHITE,
            fg=self.TEXT,
            bd=0,
            font=("Segoe UI", 10)
        )

        entry.pack(
            side="left",
            fill="x",
            expand=True,
            ipady=10
        )

        self.inv_search.trace_add(
            "write",
            lambda *_:
            self.refresh_inventory_table()
        )

        # TABLE

        frame = tk.Frame(
            self.content,
            bg=self.WHITE,
            highlightbackground=self.BORDER,
            highlightthickness=1
        )

        frame.pack(
            fill="both",
            expand=True
        )

        columns = (
            "id",
            "name",
            "category",
            "batch",
            "supplier",
            "purchase",
            "selling",
            "stock",
            "expiry",
            "status"
        )

        self.tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        headings = {

            "id": "ID",
            "name": "Medicine",
            "category": "Category",
            "batch": "Batch",
            "supplier": "Supplier",
            "purchase": "Purchase",
            "selling": "Selling",
            "stock": "Stock",
            "expiry": "Expiry",
            "status": "Status"
        }

        widths = {

            "id": 45,
            "name": 170,
            "category": 120,
            "batch": 100,
            "supplier": 130,
            "purchase": 80,
            "selling": 80,
            "stock": 70,
            "expiry": 100,
            "status": 115
        }

        for column in columns:

            self.tree.heading(
                column,
                text=headings[column]
            )

            self.tree.column(
                column,
                width=widths[column]
            )

        scrollbar = ttk.Scrollbar(
            frame,
            orient="vertical",
            command=self.tree.yview
        )

        self.tree.configure(
            yscrollcommand=scrollbar.set
        )

        self.tree.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(8, 0),
            pady=8
        )

        scrollbar.pack(
            side="right",
            fill="y",
            pady=8
        )

        # ACTIONS

        actions = tk.Frame(
            self.content,
            bg=self.BG
        )

        actions.pack(
            fill="x",
            pady=(12, 0)
        )

        tk.Button(
            actions,
            text="✎ Edit",
            command=self.edit_selected,
            bg=self.BLUE,
            fg="white",
            bd=0,
            cursor="hand2",
            font=("Segoe UI", 9, "bold"),
            padx=18,
            pady=9
        ).pack(
            side="left",
            padx=(0, 8)
        )

        tk.Button(
            actions,
            text="🗑 Delete",
            command=self.delete_selected,
            bg=self.RED,
            fg="white",
            bd=0,
            cursor="hand2",
            font=("Segoe UI", 9, "bold"),
            padx=18,
            pady=9
        ).pack(
            side="left",
            padx=(0, 8)
        )

        tk.Button(
            actions,
            text="↻ Refresh",
            command=self.refresh_inventory,
            bg=self.WHITE,
            fg=self.TEXT,
            bd=0,
            cursor="hand2",
            font=("Segoe UI", 9, "bold"),
            padx=18,
            pady=9
        ).pack(
            side="left"
        )

        self.refresh_inventory_table()

    # ========================================================
    # REFRESH INVENTORY
    # ========================================================

    def refresh_inventory(self):

        self.load_medicines()

        self.refresh_inventory_table()

    def refresh_inventory_table(self):

        if not self.tree:
            return

        for item in self.tree.get_children():

            self.tree.delete(item)

        term = (
            self.inv_search.get()
            .lower()
            .strip()
        )

        for medicine in self.medicines:

            searchable = " ".join(
                [
                    str(
                        medicine.get(
                            "product_name",
                            ""
                        )
                    ),
                    str(
                        medicine.get(
                            "product_category",
                            ""
                        )
                    ),
                    str(
                        medicine.get(
                            "batch_number",
                            ""
                        )
                    ),
                    str(
                        medicine.get(
                            "supplier",
                            ""
                        )
                    )
                ]
            ).lower()

            if term and term not in searchable:
                continue

            purchase = Decimal(
                str(
                    medicine.get(
                        "purchase_price"
                    ) or 0
                )
            )

            selling = Decimal(
                str(
                    medicine.get(
                        "selling_price"
                    )
                    or
                    medicine.get(
                        "price"
                    )
                    or 0
                )
            )

            self.tree.insert(
                "",
                "end",
                values=(
                    medicine["product_id"],
                    medicine["product_name"],
                    medicine["product_category"],
                    medicine["batch_number"],
                    medicine["supplier"] or "-",
                    f"₹{purchase:.2f}",
                    f"₹{selling:.2f}",
                    medicine["quantity"],
                    str(
                        medicine["expiry_date"]
                    )[:10],
                    self.product_status(
                        medicine
                    )
                )
            )

    # ========================================================
    # SELECT PRODUCT
    # ========================================================

    def selected_product(self):

        if not self.tree:
            return None

        selection = self.tree.selection()

        if not selection:
            return None

        values = self.tree.item(
            selection[0],
            "values"
        )

        product_id = int(values[0])

        for medicine in self.medicines:

            if int(
                medicine["product_id"]
            ) == product_id:

                return medicine

        return None

    # ========================================================
    # DELETE MEDICINE
    # ========================================================

    def delete_selected(self):

        medicine = self.selected_product()

        if not medicine:

            messagebox.showwarning(
                "Selection",
                "Select a medicine first."
            )

            return

        if not messagebox.askyesno(
            "Delete",
            f"Delete {medicine['product_name']}?"
        ):
            return

        conn = self.db()

        if not conn:
            return

        try:

            cursor = conn.cursor()

            cursor.execute(
                """
                DELETE FROM products
                WHERE product_id=%s
                """,
                (
                    medicine["product_id"],
                )
            )

            conn.commit()

            cursor.close()
            conn.close()

            self.load_medicines()

            self.refresh_inventory_table()

            messagebox.showinfo(
                "Deleted",
                "Medicine deleted successfully."
            )

        except Exception as e:

            try:
                conn.rollback()
                conn.close()
            except:
                pass

            messagebox.showerror(
                "Delete Error",
                str(e)
            )

    # ========================================================
    # EDIT MEDICINE
    # ========================================================

    def edit_selected(self):

        medicine = self.selected_product()

        if not medicine:

            messagebox.showwarning(
                "Selection",
                "Select a medicine first."
            )

            return

        self.open_medicine_form(
            medicine
        )

    # ========================================================
    # MEDICINE FORM
    # ========================================================

    def open_medicine_form(
        self,
        medicine=None
    ):

        editing = medicine is not None

        title = (
            "Edit Medicine"
            if editing
            else
            "Add New Medicine"
        )

        tk.Label(
            self.content,
            text=title,
            bg=self.BG,
            fg=self.TEXT,
            font=("Segoe UI", 15, "bold")
        ).pack(
            anchor="w",
            pady=(0, 4)
        )

        tk.Label(
            self.content,
            text=(
                "Enter complete medicine, supplier, "
                "cost and stock information."
            ),
            bg=self.BG,
            fg=self.MUTED,
            font=("Segoe UI", 9)
        ).pack(
            anchor="w",
            pady=(0, 15)
        )

        variables = {

            "name": tk.StringVar(),

            "category": tk.StringVar(),

            "batch": tk.StringVar(),

            "supplier": tk.StringVar(),

            "quantity": tk.StringVar(),

            "minimum": tk.StringVar(
                value="10"
            ),

            "purchase": tk.StringVar(),

            "selling": tk.StringVar(),

            "manufacturing": tk.StringVar(),

            "expiry": tk.StringVar()
        }

        if editing:

            variables["name"].set(
                medicine["product_name"]
            )

            variables["category"].set(
                medicine["product_category"]
            )

            variables["batch"].set(
                medicine["batch_number"]
            )

            variables["supplier"].set(
                medicine["supplier"] or ""
            )

            variables["quantity"].set(
                medicine["quantity"]
            )

            variables["minimum"].set(
                medicine.get(
                    "minimum_stock"
                ) or 10
            )

            variables["purchase"].set(
                medicine.get(
                    "purchase_price"
                ) or 0
            )

            variables["selling"].set(
                medicine.get(
                    "selling_price"
                )
                or
                medicine.get(
                    "price"
                )
                or 0
            )

            variables["manufacturing"].set(
                str(
                    medicine.get(
                        "manufacturing_date"
                    )
                    or ""
                )[:10]
            )

            variables["expiry"].set(
                str(
                    medicine["expiry_date"]
                )[:10]
            )

        form = tk.Frame(
            self.content,
            bg=self.WHITE,
            highlightbackground=self.BORDER,
            highlightthickness=1
        )

        form.pack(
            fill="x"
        )

        form.grid_columnconfigure(
            1,
            weight=1
        )

        form.grid_columnconfigure(
            3,
            weight=1
        )

        fields = [

            (
                "Medicine Name",
                "name",
                0,
                0
            ),

            (
                "Category",
                "category",
                0,
                2
            ),

            (
                "Batch Number",
                "batch",
                1,
                0
            ),

            (
                "Supplier",
                "supplier",
                1,
                2
            ),

            (
                "Quantity",
                "quantity",
                2,
                0
            ),

            (
                "Minimum Stock",
                "minimum",
                2,
                2
            ),

            (
                "Purchase Cost (₹)",
                "purchase",
                3,
                0
            ),

            (
                "Selling Price (₹)",
                "selling",
                3,
                2
            ),

            (
                "Manufacturing Date",
                "manufacturing",
                4,
                0
            ),

            (
                "Expiry Date",
                "expiry",
                4,
                2
            )
        ]

        for label, key, row, column in fields:

            tk.Label(
                form,
                text=label,
                bg=self.WHITE,
                fg=self.TEXT,
                font=("Segoe UI", 9, "bold")
            ).grid(
                row=row,
                column=column,
                sticky="w",
                padx=(22, 8),
                pady=(13, 4)
            )

            tk.Entry(
                form,
                textvariable=variables[key],
                bg="#F8FAFD",
                fg=self.TEXT,
                relief="flat",
                highlightbackground=self.BORDER,
                highlightthickness=1,
                font=("Segoe UI", 10)
            ).grid(
                row=row,
                column=column + 1,
                sticky="ew",
                padx=(0, 22),
                pady=(13, 4),
                ipady=8
            )

        tk.Label(
            form,
            text="Date format: YYYY-MM-DD",
            bg=self.WHITE,
            fg=self.MUTED,
            font=("Segoe UI", 8)
        ).grid(
            row=5,
            column=0,
            columnspan=4,
            sticky="w",
            padx=22,
            pady=(3, 15)
        )

        buttons = tk.Frame(
            self.content,
            bg=self.BG
        )

        buttons.pack(
            fill="x",
            pady=15
        )

        tk.Button(
            buttons,
            text=(
                "✓  Update Medicine"
                if editing
                else
                "✓  Save Medicine"
            ),
            command=lambda:
            self.save_product(
                variables,
                medicine["product_id"]
                if editing
                else None
            ),
            bg=self.BLUE,
            fg="white",
            activebackground=self.NAVY,
            bd=0,
            cursor="hand2",
            font=("Segoe UI", 10, "bold"),
            padx=22,
            pady=10
        ).pack(
            side="left"
        )

        tk.Button(
            buttons,
            text="Cancel",
            command=lambda:
            self.show_page(
                "Medicine Inventory"
            ),
            bg=self.WHITE,
            fg=self.TEXT,
            bd=0,
            cursor="hand2",
            font=("Segoe UI", 10, "bold"),
            padx=22,
            pady=10
        ).pack(
            side="left",
            padx=8
        )

    # ========================================================
    # SAVE MEDICINE
    # ========================================================

    def save_product(
        self,
        variables,
        product_id=None
    ):

        required = [
            "name",
            "category",
            "batch",
            "quantity",
            "expiry",
            "supplier",
            "purchase",
            "selling",
            "minimum"
        ]

        for field in required:

            if not variables[field].get().strip():

                messagebox.showwarning(
                    "Missing Data",
                    "Please fill all required fields."
                )

                return

        try:

            quantity = int(
                variables[
                    "quantity"
                ].get()
            )

            minimum = int(
                variables[
                    "minimum"
                ].get()
            )

            purchase = Decimal(
                variables[
                    "purchase"
                ].get()
            )

            selling = Decimal(
                variables[
                    "selling"
                ].get()
            )

            if (
                quantity < 0
                or minimum < 0
                or purchase < 0
                or selling < 0
            ):
                raise ValueError

            manufacturing = None

            if variables[
                "manufacturing"
            ].get().strip():

                manufacturing = datetime.strptime(
                    variables[
                        "manufacturing"
                    ].get(),
                    "%Y-%m-%d"
                ).date()

            expiry = datetime.strptime(
                variables[
                    "expiry"
                ].get(),
                "%Y-%m-%d"
            ).date()

        except Exception:

            messagebox.showerror(
                "Invalid Data",
                "Check quantity, prices and dates.\n\n"
                "Date format: YYYY-MM-DD"
            )

            return

        days = (
            expiry - date.today()
        ).days

        if quantity == 0:
            status = "Out of Stock"

        elif days < 0:
            status = "Expired"

        elif days <= self.EXPIRY_WARNING_DAYS:
            status = "Expiring Soon"

        elif quantity <= minimum:
            status = "Low Stock"

        else:
            status = "Safe"

        conn = self.db()

        if not conn:
            return

        try:

            cursor = conn.cursor()

            if product_id is None:

                cursor.execute(
                    """
                    INSERT INTO products
                    (
                        product_name,
                        product_category,
                        batch_number,
                        quantity,
                        manufacturing_date,
                        expiry_date,
                        supplier,
                        price,
                        stock_entry_date,
                        status,
                        purchase_price,
                        selling_price,
                        minimum_stock
                    )
                    VALUES
                    (
                        %s,%s,%s,%s,%s,%s,%s,%s,
                        CURDATE(),%s,%s,%s,%s
                    )
                    """,
                    (
                        variables["name"].get(),
                        variables["category"].get(),
                        variables["batch"].get(),
                        quantity,
                        manufacturing,
                        expiry,
                        variables["supplier"].get(),
                        selling,
                        status,
                        purchase,
                        selling,
                        minimum
                    )
                )

                message = (
                    "Medicine added successfully."
                )

            else:

                cursor.execute(
                    """
                    UPDATE products SET

                        product_name=%s,

                        product_category=%s,

                        batch_number=%s,

                        quantity=%s,

                        manufacturing_date=%s,

                        expiry_date=%s,

                        supplier=%s,

                        price=%s,

                        status=%s,

                        purchase_price=%s,

                        selling_price=%s,

                        minimum_stock=%s

                    WHERE product_id=%s
                    """,
                    (
                        variables["name"].get(),
                        variables["category"].get(),
                        variables["batch"].get(),
                        quantity,
                        manufacturing,
                        expiry,
                        variables["supplier"].get(),
                        selling,
                        status,
                        purchase,
                        selling,
                        minimum,
                        product_id
                    )
                )

                message = (
                    "Medicine updated successfully."
                )

            conn.commit()

            cursor.close()
            conn.close()

            self.load_medicines()

            messagebox.showinfo(
                "Success",
                message
            )

            self.show_page(
                "Medicine Inventory"
            )

        except Exception as e:

            try:
                conn.rollback()
                conn.close()
            except:
                pass

            messagebox.showerror(
                "Database Error",
                str(e)
            )

    # ========================================================
    # PATIENT PAGE
    # ========================================================

    def build_patients_page(self):

        header = tk.Frame(
            self.content,
            bg=self.BG
        )

        header.pack(
            fill="x",
            pady=(0, 12)
        )

        tk.Label(
            header,
            text="Patients",
            bg=self.BG,
            fg=self.TEXT,
            font=("Segoe UI", 15, "bold")
        ).pack(
            side="left"
        )

        tk.Button(
            header,
            text="+ Add Patient",
            command=self.add_patient_dialog,
            bg=self.PURPLE,
            fg="white",
            bd=0,
            cursor="hand2",
            font=("Segoe UI", 9, "bold"),
            padx=18,
            pady=9
        ).pack(
            side="right"
        )

        frame = tk.Frame(
            self.content,
            bg=self.WHITE,
            highlightbackground=self.BORDER,
            highlightthickness=1
        )

        frame.pack(
            fill="both",
            expand=True
        )

        columns = (
            "id",
            "name",
            "age",
            "gender",
            "phone",
            "address"
        )

        tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings"
        )

        headings = {

            "id": "ID",
            "name": "Patient Name",
            "age": "Age",
            "gender": "Gender",
            "phone": "Phone",
            "address": "Address"
        }

        for column in columns:

            tree.heading(
                column,
                text=headings[column]
            )

        tree.column(
            "id",
            width=60
        )

        tree.column(
            "name",
            width=200
        )

        tree.column(
            "age",
            width=70
        )

        tree.column(
            "gender",
            width=90
        )

        tree.column(
            "phone",
            width=150
        )

        tree.column(
            "address",
            width=350
        )

        tree.pack(
            fill="both",
            expand=True,
            padx=8,
            pady=8
        )

        for patient in self.patients:

            tree.insert(
                "",
                "end",
                values=(
                    patient["patient_id"],
                    patient["patient_name"],
                    patient["age"] or "-",
                    patient["gender"] or "-",
                    patient["phone"] or "-",
                    patient["address"] or "-"
                )
            )

    # ========================================================
    # ADD PATIENT
    # ========================================================

    def add_patient_dialog(self, return_to_billing=False):

        window = tk.Toplevel(
            self.root
        )

        window.title(
            "Add Patient"
        )

        # Give the patient form enough vertical space so the save button is visible.
        window.geometry(
            "600x620" if return_to_billing else "460x600"
        )

        window.configure(
            bg=self.WHITE
        )

        window.transient(
            self.root
        )

        window.grab_set()

        fields = {}

        field_data = [

            (
                "Patient Name",
                "name"
            ),

            (
                "Age",
                "age"
            ),

            (
                "Gender",
                "gender"
            ),

            (
                "Phone",
                "phone"
            ),

            (
                "Address",
                "address"
            )
        ]

        for label, key in field_data:

            tk.Label(
                window,
                text=label,
                bg=self.WHITE,
                fg=self.TEXT,
                font=("Segoe UI", 9, "bold")
            ).pack(
                anchor="w",
                padx=35,
                pady=(15, 4)
            )

            entry = tk.Entry(
                window,
                bg="#F8FAFD",
                fg=self.TEXT,
                relief="flat",
                highlightbackground=self.BORDER,
                highlightthickness=1
            )

            entry.pack(
                fill="x",
                padx=35,
                ipady=8
            )

            fields[key] = entry

        def save_patient():

            if not fields[
                "name"
            ].get().strip():

                messagebox.showwarning(
                    "Patient",
                    "Enter patient name.",
                    parent=window
                )

                return

            age_text = fields["age"].get().strip()
            if age_text and not age_text.isdigit():
                messagebox.showwarning(
                    "Patient", "Age must be a whole number.", parent=window
                )
                return

            conn = self.db()

            if not conn:
                return

            try:

                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT INTO patients
                    (
                        patient_name,
                        age,
                        gender,
                        phone,
                        address
                    )
                    VALUES(%s,%s,%s,%s,%s)
                    """,
                    (
                        fields[
                            "name"
                        ].get(),

                        int(
                            fields[
                                "age"
                            ].get()
                        )
                        if fields[
                            "age"
                        ].get().strip()
                        else None,

                        fields[
                            "gender"
                        ].get(),

                        fields[
                            "phone"
                        ].get(),

                        fields[
                            "address"
                        ].get()
                    )
                )

                new_patient_id = cursor.lastrowid

                conn.commit()

                cursor.close()
                conn.close()

                self.load_patients()

                window.destroy()

                if return_to_billing:
                    self.show_page("Billing")
                    self.bill_patient.set(
                        next(
                            (
                                f"{p['patient_id']} - "
                                f"{p['patient_name']} - "
                                f"{p['phone'] or ''}"
                                for p in self.patients
                                if int(p["patient_id"]) == int(new_patient_id)
                            ),
                            "Walk-in Customer"
                        )
                    )
                else:
                    self.show_page("Patients")

                messagebox.showinfo(
                    "Success",
                    "Patient added successfully."
                )

            except Exception as e:

                try:
                    conn.close()
                except:
                    pass

                messagebox.showerror(
                    "Error",
                    str(e),
                    parent=window
                )

        tk.Button(
            window,
            text=("SAVE PATIENT & CONTINUE TO BILLING"
                  if return_to_billing else "SAVE PATIENT DETAILS"),
            command=save_patient,
            bg=self.PURPLE,
            fg="white",
            bd=0,
            cursor="hand2",
            font=("Segoe UI", 10, "bold"),
            pady=10
        ).pack(
            fill="x",
            padx=35,
            pady=25
        )

    # ========================================================
    # BILLING PAGE
    # ========================================================

    def build_billing_page(self):
        self.cart = []
        self.bill_tree = None

        heading = tk.Frame(self.content, bg=self.BG)
        heading.pack(fill="x", pady=(0, 12))
        tk.Label(
            heading, text="Create New Bill", bg=self.BG, fg=self.TEXT,
            font=("Segoe UI", 18, "bold")
        ).pack(side="left")
        tk.Label(
            heading, text="Patient  →  Medicines  →  Payment  →  Confirm",
            bg=self.BG, fg=self.MUTED, font=("Segoe UI", 9)
        ).pack(side="left", padx=18, pady=(5, 0))

        def section(parent, title, subtitle=None):
            card = tk.Frame(
                parent, bg=self.WHITE,
                highlightbackground=self.BORDER, highlightthickness=1
            )
            tk.Label(
                card, text=title, bg=self.WHITE, fg=self.TEXT,
                font=("Segoe UI", 11, "bold")
            ).pack(anchor="w", padx=16, pady=(12, 2))
            if subtitle:
                tk.Label(
                    card, text=subtitle, bg=self.WHITE, fg=self.MUTED,
                    font=("Segoe UI", 8)
                ).pack(anchor="w", padx=16, pady=(0, 8))
            return card

        # 1. Patient and payment details
        patient_card = section(
            self.content, "1. Patient Details",
            "Choose an existing patient or add a new patient before billing."
        )
        patient_card.pack(fill="x", pady=(0, 10))
        patient_row = tk.Frame(patient_card, bg=self.WHITE)
        patient_row.pack(fill="x", padx=16, pady=(2, 14))
        patient_row.grid_columnconfigure(1, weight=1)
        patient_row.grid_columnconfigure(4, weight=1)

        tk.Label(
            patient_row, text="Patient", bg=self.WHITE, fg=self.TEXT,
            font=("Segoe UI", 9, "bold")
        ).grid(row=0, column=0, padx=(0, 8), sticky="w")

        patient_values = ["Walk-in Customer"] + [
            f"{p['patient_id']} - {p['patient_name']} - {p.get('phone') or ''}"
            for p in self.patients
        ]
        self.bill_patient = tk.StringVar(value=patient_values[0])
        self.bill_patient_combo = ttk.Combobox(
            patient_row, textvariable=self.bill_patient,
            values=patient_values, state="readonly", width=34
        )
        self.bill_patient_combo.grid(
            row=0, column=1, sticky="ew", padx=(0, 8), ipady=3
        )

        tk.Button(
            patient_row, text="+ Add Patient",
            command=lambda: self.add_patient_dialog(return_to_billing=True),
            bg=self.PURPLE, fg="white", activebackground=self.NAVY,
            activeforeground="white", bd=0, cursor="hand2",
            font=("Segoe UI", 9, "bold"), padx=14, pady=8
        ).grid(row=0, column=2, padx=(0, 24))

        tk.Label(
            patient_row, text="Payment Method", bg=self.WHITE, fg=self.TEXT,
            font=("Segoe UI", 9, "bold")
        ).grid(row=0, column=3, padx=(0, 8), sticky="w")

        self.payment = tk.StringVar(value="Cash")
        ttk.Combobox(
            patient_row, textvariable=self.payment,
            values=["Cash", "UPI", "Card", "Other"],
            state="readonly", width=15
        ).grid(row=0, column=4, sticky="ew", ipady=3)

        # 2. Medicine selection
        medicine_card = section(
            self.content, "2. Medicine Details",
            "Select an in-stock, non-expired medicine and enter the quantity."
        )
        medicine_card.pack(fill="x", pady=(0, 10))
        medicine_row = tk.Frame(medicine_card, bg=self.WHITE)
        medicine_row.pack(fill="x", padx=16, pady=(2, 14))
        medicine_row.grid_columnconfigure(1, weight=1)

        tk.Label(
            medicine_row, text="Medicine", bg=self.WHITE, fg=self.TEXT,
            font=("Segoe UI", 9, "bold")
        ).grid(row=0, column=0, padx=(0, 8), sticky="w")

        self.bill_product = tk.StringVar()
        names = [
            f"{p['product_id']} - {p['product_name']} (Stock: {p['quantity']})"
            for p in self.medicines
            if int(p.get("quantity") or 0) > 0
            and self.product_status(p) != "Expired"
        ]
        self.bill_product_combo = ttk.Combobox(
            medicine_row, textvariable=self.bill_product,
            values=names, state="readonly"
        )
        self.bill_product_combo.grid(
            row=0, column=1, sticky="ew", padx=(0, 12), ipady=3
        )

        tk.Label(
            medicine_row, text="Quantity", bg=self.WHITE, fg=self.TEXT,
            font=("Segoe UI", 9, "bold")
        ).grid(row=0, column=2, padx=(0, 8), sticky="w")
        self.bill_qty = tk.StringVar(value="1")
        tk.Spinbox(
            medicine_row, from_=1, to=999, textvariable=self.bill_qty,
            width=7, relief="solid", bd=1
        ).grid(row=0, column=3, padx=(0, 12), ipady=4)

        tk.Button(
            medicine_row, text="＋ Add to Bill", command=self.add_to_cart,
            bg=self.GREEN, fg="white", activebackground="#0E805D",
            bd=0, cursor="hand2", font=("Segoe UI", 9, "bold"),
            padx=16, pady=9
        ).grid(row=0, column=4)

        # 3. Bill items and totals
        body = tk.Frame(self.content, bg=self.BG)
        body.pack(fill="both", expand=True)

        left = section(
            body, "3. Bill Items",
            "Review medicine, batch, quantity, unit price and line amount."
        )
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        columns = ("medicine", "batch", "qty", "rate", "amount")
        self.bill_tree = ttk.Treeview(left, columns=columns, show="headings", height=9)
        headings = {
            "medicine": "Medicine", "batch": "Batch No.",
            "qty": "Qty", "rate": "Unit Price", "amount": "Amount"
        }
        widths = {"medicine": 220, "batch": 95, "qty": 55, "rate": 95, "amount": 105}
        for column in columns:
            self.bill_tree.heading(column, text=headings[column])
            self.bill_tree.column(
                column, width=widths[column],
                anchor="w" if column == "medicine" else "center"
            )
        self.bill_tree.pack(fill="both", expand=True, padx=12, pady=(4, 12))

        right = section(body, "4. Bill Summary")
        right.configure(width=315)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        # Footer is packed first at the bottom, keeping both actions visible.
        bill_actions = tk.Frame(right, bg=self.WHITE)
        bill_actions.pack(side="bottom", fill="x", padx=16, pady=(8, 14))

        tk.Button(
            bill_actions, text="SAVE BILL",
            command=self.confirm_bill, bg=self.BLUE, fg="white",
            activebackground=self.NAVY, activeforeground="white",
            bd=0, cursor="hand2", font=("Segoe UI", 10, "bold"), pady=12
        ).pack(fill="x", pady=(0, 8))

        tk.Button(
            bill_actions, text="CLEAR BILL", command=self.clear_cart,
            bg="#EDF2F9", fg=self.TEXT, activebackground="#DCE6F3",
            bd=0, cursor="hand2", font=("Segoe UI", 9, "bold"), pady=9
        ).pack(fill="x")

        self.subtotal_label = self.summary_row(right, "Subtotal", "₹0.00")
        self.discount_var = tk.StringVar(value="0")
        tk.Label(
            right, text="Discount (₹)", bg=self.WHITE, fg=self.MUTED,
            font=("Segoe UI", 9)
        ).pack(anchor="w", padx=16, pady=(10, 3))
        discount_entry = tk.Entry(
            right, textvariable=self.discount_var, bg="#F8FAFD",
            fg=self.TEXT, relief="flat", highlightbackground=self.BORDER,
            highlightthickness=1
        )
        discount_entry.pack(fill="x", padx=16, ipady=7)
        discount_entry.bind("<KeyRelease>", lambda event: self.update_bill_summary())

        tk.Label(
            right, text="GST Rate (%)", bg=self.WHITE, fg=self.MUTED,
            font=("Segoe UI", 9)
        ).pack(anchor="w", padx=16, pady=(10, 3))
        self.gst_var = tk.StringVar(value="5")
        gst_entry = tk.Entry(
            right, textvariable=self.gst_var, bg="#F8FAFD",
            fg=self.TEXT, relief="flat", highlightbackground=self.BORDER,
            highlightthickness=1
        )
        gst_entry.pack(fill="x", padx=16, ipady=7)
        gst_entry.bind("<KeyRelease>", lambda event: self.update_bill_summary())

        self.taxable_label = self.summary_row(right, "Taxable Amount", "₹0.00")
        self.cgst_label = self.summary_row(right, "CGST", "₹0.00")
        self.sgst_label = self.summary_row(right, "SGST", "₹0.00")
        self.gst_label = self.summary_row(right, "Total GST", "₹0.00")
        self.grand_label = self.summary_row(right, "Amount to Pay", "₹0.00", True)


    def summary_row(
        self,
        parent,
        title,
        value,
        bold=False
    ):

        frame = tk.Frame(
            parent,
            bg=self.WHITE
        )

        frame.pack(
            fill="x",
            padx=20,
            pady=5
        )

        tk.Label(
            frame,
            text=title,
            bg=self.WHITE,
            fg=self.MUTED,
            font=(
                "Segoe UI",
                9,
                "bold" if bold else "normal"
            )
        ).pack(
            side="left"
        )

        label = tk.Label(
            frame,
            text=value,
            bg=self.WHITE,
            fg=self.TEXT,
            font=(
                "Segoe UI",
                11,
                "bold" if bold else "normal"
            )
        )

        label.pack(
            side="right"
        )

        return label

    # ========================================================
    # ADD TO BILL
    # ========================================================

    def add_to_cart(self):

        if not self.bill_product.get():

            messagebox.showwarning(
                "Billing",
                "Select a medicine."
            )

            return

        try:

            quantity = int(
                self.bill_qty.get()
            )

            if quantity <= 0:
                raise ValueError

        except:

            messagebox.showwarning(
                "Billing",
                "Enter a valid quantity."
            )

            return

        product_id = int(
            self.bill_product
            .get()
            .split(" - ")[0]
        )

        medicine = next(
            (
                p
                for p in self.medicines
                if int(
                    p["product_id"]
                ) == product_id
            ),
            None
        )

        if not medicine:
            return

        already_added = sum(
            item["quantity"]
            for item in self.cart
            if item["product_id"]
            == product_id
        )

        available = int(
            medicine["quantity"] or 0
        )

        if (
            already_added
            + quantity
            > available
        ):

            messagebox.showerror(
                "Insufficient Stock",
                f"{medicine['product_name']}\n\n"
                f"Available: {available}\n"
                f"Already in bill: {already_added}\n"
                f"Requested: {quantity}"
            )

            return

        selling_price = Decimal(
            str(
                medicine.get(
                    "selling_price"
                )
                or
                medicine.get(
                    "price"
                )
                or 0
            )
        )

        purchase_price = Decimal(
            str(
                medicine.get(
                    "purchase_price"
                )
                or 0
            )
        )

        for item in self.cart:

            if (
                item["product_id"]
                == product_id
            ):

                item["quantity"] += quantity

                item["amount"] = (
                    item["quantity"]
                    * selling_price
                )

                self.refresh_cart()

                return

        self.cart.append(

            {
                "product_id":
                    product_id,

                "name":
                    medicine["product_name"],

                "batch":
                    medicine["batch_number"],

                "quantity":
                    quantity,

                "selling_price":
                    selling_price,

                "purchase_price":
                    purchase_price,

                "amount":
                    quantity
                    * selling_price
            }
        )

        self.refresh_cart()

    # ========================================================
    # REFRESH CART
    # ========================================================

    def refresh_cart(self):

        if not self.bill_tree:
            return

        for item in self.bill_tree.get_children():

            self.bill_tree.delete(item)

        for item in self.cart:

            self.bill_tree.insert(
                "",
                "end",
                values=(
                    item["name"],
                    item["batch"],
                    item["quantity"],
                    f"₹{item['selling_price']:.2f}",
                    f"₹{item['amount']:.2f}"
                )
            )

        self.update_bill_summary()

    # ========================================================
    # BILL CALCULATION
    # ========================================================

    def update_bill_summary(self):

        subtotal = sum(
            (
                item["amount"]
                for item in self.cart
            ),
            Decimal("0")
        )

        try:

            discount = Decimal(
                self.discount_var.get()
                or "0"
            )

        except:

            discount = Decimal("0")

        try:

            gst_rate = Decimal(
                self.gst_var.get()
                or "0"
            )

        except:

            gst_rate = Decimal("0")

        taxable = max(
            subtotal - discount,
            Decimal("0")
        )

        gst = (
            taxable
            * gst_rate
            / Decimal("100")
        )

        grand_total = (
            taxable + gst
        )

        self.subtotal_label.config(
            text=f"₹{subtotal:.2f}"
        )

        if hasattr(self, "taxable_label"):
            self.taxable_label.config(text=f"₹{taxable:.2f}")
        if hasattr(self, "cgst_label"):
            self.cgst_label.config(text=f"₹{(gst / Decimal('2')):.2f}")
        if hasattr(self, "sgst_label"):
            self.sgst_label.config(text=f"₹{(gst / Decimal('2')):.2f}")
        self.gst_label.config(text=f"₹{gst:.2f}")
        self.grand_label.config(text=f"₹{grand_total:.2f}")

        return (
            subtotal,
            discount,
            gst,
            grand_total
        )

    # ========================================================
    # CLEAR CART
    # ========================================================

    def clear_cart(self):

        self.cart = []

        self.discount_var.set("0")

        self.refresh_cart()

    # ========================================================
    # CONFIRM BILL
    # ========================================================

    def confirm_bill(self):

        if not self.cart:

            messagebox.showwarning(
                "Billing",
                "Add at least one medicine."
            )

            return

        (
            subtotal,
            discount,
            gst,
            total
        ) = self.update_bill_summary()

        if discount < 0:
            messagebox.showerror("Billing", "Discount cannot be negative.")
            return

        if discount > subtotal:
            messagebox.showerror("Billing", "Discount cannot exceed the subtotal.")
            return

        try:
            gst_rate = Decimal(self.gst_var.get() or "0")
        except Exception:
            messagebox.showerror("Billing", "Enter a valid GST percentage.")
            return

        if gst_rate < 0 or gst_rate > 100:
            messagebox.showerror("Billing", "GST rate must be between 0 and 100.")
            return

        # PATIENT

        patient_id = None
        customer_name = "Walk-in Customer"
        phone = ""
        selected_patient_details = None

        selected_patient = (
            self.bill_patient.get()
        )

        if (
            selected_patient
            != "Walk-in Customer"
        ):

            patient_id = int(
                selected_patient
                .split(" - ")[0]
            )

            patient = next(
                (
                    p
                    for p in self.patients
                    if int(
                        p["patient_id"]
                    ) == patient_id
                ),
                None
            )

            if patient:

                selected_patient_details = patient

                customer_name = (
                    patient["patient_name"]
                )

                phone = (
                    patient["phone"]
                    or ""
                )

        bill_number = (
            "MT-"
            + datetime.now().strftime(
                "%Y%m%d%H%M%S"
            )
            + str(
                random.randint(
                    10,
                    99
                )
            )
        )

        conn = self.db()

        if not conn:
            return

        try:

            cursor = conn.cursor()

            # CHECK STOCK

            for item in self.cart:

                cursor.execute(
                    """
                    SELECT quantity
                    FROM products
                    WHERE product_id=%s
                    FOR UPDATE
                    """,
                    (
                        item["product_id"],
                    )
                )

                row = cursor.fetchone()

                available = (
                    int(row[0])
                    if row
                    else 0
                )

                if (
                    item["quantity"]
                    > available
                ):

                    raise Exception(
                        f"Insufficient stock for "
                        f"{item['name']}.\n\n"
                        f"Available: {available}\n"
                        f"Requested: "
                        f"{item['quantity']}"
                    )

            # BILL

            cursor.execute(
                """
                INSERT INTO bills
                (
                    bill_number,
                    patient_id,
                    customer_name,
                    customer_phone,
                    subtotal,
                    discount,
                    gst,
                    grand_total,
                    payment_method,
                    created_by
                )
                VALUES
                (
                    %s,%s,%s,%s,%s,
                    %s,%s,%s,%s,%s
                )
                """,
                (
                    bill_number,
                    patient_id,
                    customer_name,
                    phone,
                    subtotal,
                    discount,
                    gst,
                    total,
                    self.payment.get(),
                    self.username
                )
            )

            bill_id = cursor.lastrowid

            # BILL ITEMS + STOCK UPDATE

            for item in self.cart:

                cursor.execute(
                    """
                    INSERT INTO bill_items
                    (
                        bill_id,
                        product_id,
                        medicine_name,
                        batch_number,
                        quantity,
                        selling_price,
                        purchase_price,
                        amount
                    )
                    VALUES
                    (
                        %s,%s,%s,%s,%s,
                        %s,%s,%s
                    )
                    """,
                    (
                        bill_id,
                        item["product_id"],
                        item["name"],
                        item["batch"],
                        item["quantity"],
                        item["selling_price"],
                        item["purchase_price"],
                        item["amount"]
                    )
                )

                cursor.execute(
                    """
                    UPDATE products
                    SET quantity =
                    quantity - %s
                    WHERE product_id=%s
                    """,
                    (
                        item["quantity"],
                        item["product_id"]
                    )
                )

            conn.commit()

            cursor.close()
            conn.close()

            self.load_medicines()

            self.cart = []

            self.show_bill_success(
                bill_number,
                customer_name,
                phone,
                subtotal,
                discount,
                gst,
                total,
                selected_patient_details
            )

        except Exception as e:

            try:
                conn.rollback()
                conn.close()
            except:
                pass

            messagebox.showerror(
                "Billing Error",
                str(e)
            )

    # ========================================================
    # BILL SUCCESS WINDOW
    # ========================================================

    def show_bill_success(
        self,
        bill_number,
        customer_name,
        phone,
        subtotal,
        discount,
        gst,
        total,
        patient_details=None
    ):

        window = tk.Toplevel(
            self.root
        )

        window.title(
            "Bill Generated"
        )

        window.geometry(
            "520x620"
        )

        window.configure(
            bg=self.WHITE
        )

        window.transient(
            self.root
        )

        tk.Label(
            window,
            text="✓",
            bg=self.GREEN,
            fg="white",
            font=("Segoe UI", 28, "bold"),
            width=2
        ).pack(
            pady=(30, 10)
        )

        tk.Label(
            window,
            text="Bill Generated Successfully",
            bg=self.WHITE,
            fg=self.GREEN,
            font=("Segoe UI", 16, "bold")
        ).pack()

        tk.Label(
            window,
            text=f"Bill No: {bill_number}",
            bg=self.WHITE,
            fg=self.MUTED,
            font=("Segoe UI", 10)
        ).pack(pady=5)

        box = tk.Frame(
            window,
            bg="#F8FAFD",
            highlightbackground=self.BORDER,
            highlightthickness=1
        )

        box.pack(
            fill="x",
            padx=30,
            pady=20
        )

        rows = [

            (
                "Customer",
                customer_name
            ),

            (
                "Phone",
                phone or "-"
            ),

            (
                "Subtotal",
                f"₹{subtotal:.2f}"
            ),

            (
                "Discount",
                f"₹{discount:.2f}"
            ),

            (
                "GST",
                f"₹{gst:.2f}"
            ),

            (
                "Grand Total",
                f"₹{total:.2f}"
            )
        ]

        if patient_details:
            rows[2:2] = [
                ("Age", patient_details.get("age") or "-"),
                ("Gender", patient_details.get("gender") or "-"),
                ("Address", patient_details.get("address") or "-"),
            ]

        for label, value in rows:

            frame = tk.Frame(
                box,
                bg="#F8FAFD"
            )

            frame.pack(
                fill="x",
                padx=18,
                pady=7
            )

            tk.Label(
                frame,
                text=label,
                bg="#F8FAFD",
                fg=self.MUTED,
                font=("Segoe UI", 9)
            ).pack(
                side="left"
            )

            tk.Label(
                frame,
                text=value,
                bg="#F8FAFD",
                fg=self.TEXT,
                font=("Segoe UI", 9, "bold")
            ).pack(
                side="right"
            )

        tk.Label(
            window,
            text="✓ Stock automatically updated in MySQL.",
            bg=self.WHITE,
            fg=self.GREEN,
            font=("Segoe UI", 9, "bold")
        ).pack(pady=10)

        tk.Button(
            window,
            text="Close",
            command=lambda: (
                window.destroy(),
                self.show_page("Billing")
            ),
            bg=self.BLUE,
            fg="white",
            bd=0,
            cursor="hand2",
            font=("Segoe UI", 10, "bold"),
            padx=30,
            pady=10
        ).pack(pady=20)

    # ========================================================
    # RESTOCK PAGE
    # ========================================================

    def build_restock_page(self):

        tk.Label(
            self.content,
            text="Restock Management",
            bg=self.BG,
            fg=self.TEXT,
            font=("Segoe UI", 15, "bold")
        ).pack(
            anchor="w"
        )

        tk.Label(
            self.content,
            text="Medicines requiring replenishment with supplier and cost details.",
            bg=self.BG,
            fg=self.MUTED,
            font=("Segoe UI", 9)
        ).pack(
            anchor="w",
            pady=(4, 15)
        )

        frame = tk.Frame(
            self.content,
            bg=self.WHITE,
            highlightbackground=self.BORDER,
            highlightthickness=1
        )

        frame.pack(
            fill="both",
            expand=True
        )

        columns = (
            "medicine",
            "supplier",
            "stock",
            "minimum",
            "needed",
            "purchase",
            "estimated"
        )

        tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings"
        )

        headings = {

            "medicine": "Medicine",
            "supplier": "Supplier",
            "stock": "Current",
            "minimum": "Minimum",
            "needed": "Suggested Restock",
            "purchase": "Purchase Cost",
            "estimated": "Estimated Cost"
        }

        for column in columns:

            tree.heading(
                column,
                text=headings[column]
            )

        for medicine in self.medicines:

            quantity = int(
                medicine["quantity"] or 0
            )

            minimum = int(
                medicine.get(
                    "minimum_stock"
                )
                or self.LOW_STOCK_LIMIT
            )

            if quantity <= minimum:

                target = max(
                    minimum * 5,
                    50
                )

                needed = max(
                    target - quantity,
                    0
                )

                purchase = Decimal(
                    str(
                        medicine.get(
                            "purchase_price"
                        )
                        or 0
                    )
                )

                tree.insert(
                    "",
                    "end",
                    values=(
                        medicine[
                            "product_name"
                        ],

                        medicine[
                            "supplier"
                        ]
                        or "-",

                        quantity,

                        minimum,

                        needed,

                        f"₹{purchase:.2f}",

                        f"₹{purchase * needed:.2f}"
                    )
                )

        tree.pack(
            fill="both",
            expand=True,
            padx=8,
            pady=8
        )

    # ========================================================
    # ALERT PAGE
    # ========================================================

    def build_alert_page(
        self,
        alert_type
    ):

        if alert_type == "stock":

            title = "Stock Alerts"

            description = (
                "Low-stock and out-of-stock medicines."
            )

        else:

            title = "Expiry Alerts"

            description = (
                "Expired and soon-to-expire medicines."
            )

        tk.Label(
            self.content,
            text=title,
            bg=self.BG,
            fg=self.TEXT,
            font=("Segoe UI", 15, "bold")
        ).pack(
            anchor="w"
        )

        tk.Label(
            self.content,
            text=description,
            bg=self.BG,
            fg=self.MUTED,
            font=("Segoe UI", 9)
        ).pack(
            anchor="w",
            pady=(4, 15)
        )

        frame = tk.Frame(
            self.content,
            bg=self.WHITE,
            highlightbackground=self.BORDER,
            highlightthickness=1
        )

        frame.pack(
            fill="both",
            expand=True
        )

        columns = (
            "name",
            "batch",
            "supplier",
            "stock",
            "expiry",
            "status",
            "cost"
        )

        tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings"
        )

        headings = {

            "name": "Medicine",
            "batch": "Batch",
            "supplier": "Supplier",
            "stock": "Stock",
            "expiry": "Expiry",
            "status": "Status",
            "cost": "Purchase Cost"
        }

        for column in columns:

            tree.heading(
                column,
                text=headings[column]
            )

        for medicine in self.medicines:

            status = self.product_status(
                medicine
            )

            if alert_type == "stock":

                show = status in (
                    "Low Stock",
                    "Out of Stock"
                )

            else:

                show = status in (
                    "Expired",
                    "Expiring Soon"
                )

            if show:

                tree.insert(
                    "",
                    "end",
                    values=(
                        medicine[
                            "product_name"
                        ],

                        medicine[
                            "batch_number"
                        ],

                        medicine[
                            "supplier"
                        ] or "-",

                        medicine[
                            "quantity"
                        ],

                        str(
                            medicine[
                                "expiry_date"
                            ]
                        )[:10],

                        status,

                        f"₹{Decimal(str(medicine.get('purchase_price') or 0)):.2f}"
                    )
                )

        tree.pack(
            fill="both",
            expand=True,
            padx=8,
            pady=8
        )

    # ========================================================
    # SALES REPORT
    # ========================================================

    def build_sales_report(self):

        tk.Label(
            self.content,
            text="Sales & Profit Reports",
            bg=self.BG,
            fg=self.TEXT,
            font=("Segoe UI", 15, "bold")
        ).pack(
            anchor="w"
        )

        tk.Label(
            self.content,
            text="Today's sales, bills, units sold and estimated profit.",
            bg=self.BG,
            fg=self.MUTED,
            font=("Segoe UI", 9)
        ).pack(
            anchor="w",
            pady=(4, 15)
        )

        total = Decimal("0")
        profit = Decimal("0")
        units = 0
        bills = 0

        conn = self.db()

        if conn:

            try:

                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT
                        COALESCE(
                            SUM(grand_total),
                            0
                        ),
                        COUNT(*)
                    FROM bills
                    WHERE DATE(bill_date)
                    = CURDATE()
                    """
                )

                total, bills = (
                    cursor.fetchone()
                )

                cursor.execute(
                    """
                    SELECT
                        COALESCE(
                            SUM(quantity),
                            0
                        ),

                        COALESCE(
                            SUM(
                                (
                                    selling_price
                                    -
                                    purchase_price
                                )
                                * quantity
                            ),
                            0
                        )

                    FROM bill_items bi

                    JOIN bills b
                    ON b.bill_id =
                    bi.bill_id

                    WHERE DATE(
                        b.bill_date
                    )
                    = CURDATE()
                    """
                )

                units, profit = (
                    cursor.fetchone()
                )

                cursor.close()
                conn.close()

                total = Decimal(
                    str(total or 0)
                )

                profit = Decimal(
                    str(profit or 0)
                )

            except Exception:

                try:
                    conn.close()
                except:
                    pass

        cards = tk.Frame(
            self.content,
            bg=self.BG
        )

        cards.pack(
            fill="x"
        )

        data = [

            (
                "Today's Revenue",
                f"₹{total:.2f}",
                self.BLUE
            ),

            (
                "Today's Bills",
                bills,
                self.PURPLE
            ),

            (
                "Units Sold",
                units,
                self.GREEN
            ),

            (
                "Estimated Profit",
                f"₹{profit:.2f}",
                self.ORANGE
            )
        ]

        for title, value, color in data:

            frame = tk.Frame(
                cards,
                bg=self.WHITE,
                highlightbackground=self.BORDER,
                highlightthickness=1
            )

            frame.pack(
                side="left",
                fill="x",
                expand=True,
                padx=4
            )

            tk.Label(
                frame,
                text=title,
                bg=self.WHITE,
                fg=self.MUTED,
                font=("Segoe UI", 9, "bold")
            ).pack(
                anchor="w",
                padx=18,
                pady=(16, 5)
            )

            tk.Label(
                frame,
                text=str(value),
                bg=self.WHITE,
                fg=color,
                font=("Segoe UI", 21, "bold")
            ).pack(
                anchor="w",
                padx=18,
                pady=(0, 16)
            )

        tk.Label(
            self.content,
            text=(
                "Profit = "
                "(Selling Price − Purchase Price) "
                "× Quantity Sold"
            ),
            bg=self.BG,
            fg=self.MUTED,
            font=("Segoe UI", 9)
        ).pack(
            anchor="w",
            pady=20
        )

    # ========================================================
    # BILL HISTORY
    # ========================================================

    def build_bill_history(self):

        tk.Label(
            self.content,
            text="Bill History",
            bg=self.BG,
            fg=self.TEXT,
            font=("Segoe UI", 15, "bold")
        ).pack(
            anchor="w"
        )

        tk.Label(
            self.content,
            text="Previously generated medical bills.",
            bg=self.BG,
            fg=self.MUTED,
            font=("Segoe UI", 9)
        ).pack(
            anchor="w",
            pady=(4, 15)
        )

        frame = tk.Frame(
            self.content,
            bg=self.WHITE,
            highlightbackground=self.BORDER,
            highlightthickness=1
        )

        frame.pack(
            fill="both",
            expand=True
        )

        columns = (
            "bill",
            "customer",
            "date",
            "subtotal",
            "discount",
            "gst",
            "total",
            "payment",
            "staff"
        )

        tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings"
        )

        headings = {

            "bill": "Bill No",
            "customer": "Customer",
            "date": "Date",
            "subtotal": "Subtotal",
            "discount": "Discount",
            "gst": "GST",
            "total": "Total",
            "payment": "Payment",
            "staff": "Staff"
        }

        for column in columns:

            tree.heading(
                column,
                text=headings[column]
            )

            tree.column(
                column,
                width=110,
                anchor="center"
            )

        tree.column(
            "customer",
            width=170
        )

        tree.pack(
            fill="both",
            expand=True,
            padx=8,
            pady=8
        )

        conn = self.db()

        if not conn:
            return

        try:

            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT
                    bill_number,
                    customer_name,
                    bill_date,
                    subtotal,
                    discount,
                    gst,
                    grand_total,
                    payment_method,
                    created_by

                FROM bills

                ORDER BY bill_id DESC

                LIMIT 200
                """
            )

            rows = cursor.fetchall()

            for row in rows:

                tree.insert(
                    "",
                    "end",
                    values=(

                        row[0],

                        row[1],

                        str(
                            row[2]
                        )[:19],

                        f"₹{Decimal(str(row[3] or 0)):.2f}",

                        f"₹{Decimal(str(row[4] or 0)):.2f}",

                        f"₹{Decimal(str(row[5] or 0)):.2f}",

                        f"₹{Decimal(str(row[6] or 0)):.2f}",

                        row[7],

                        row[8]
                    )
                )

            cursor.close()
            conn.close()

        except Exception as e:

            try:
                conn.close()
            except:
                pass

            messagebox.showerror(
                "History Error",
                str(e)
            )


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = MediTrackApp(
        root
    )

    root.mainloop()