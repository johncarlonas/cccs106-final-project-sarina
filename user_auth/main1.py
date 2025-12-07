import flet as ft
import sqlite3
import hashlib
import re
import os

# ---------- Colors ----------
PRIMARY_BLUE = "#002A7A"   # Dark blue background
WHITE = "#FFFFFF"
LIGHT_BLUE = "#0A3FA6"
FILL_COLOR = "#19026B"
HINT_COLOR = "#979797"

DB_NAME = "users.db"


# ---------- SQLite Helpers ----------
def create_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(fullname: str, email: str, password: str) -> tuple[bool, str]:
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        hashed = hash_password(password)
        cursor.execute(
            "INSERT INTO users (fullname, email, password) VALUES (?, ?, ?)",
            (fullname, email, hashed),
        )
        conn.commit()
        conn.close()
        return True, "Account created successfully!"
    except sqlite3.IntegrityError:
        return False, "Email already exists."
    except Exception as e:
        return False, f"DB error: {e}"


def login_user(email: str, password: str) -> tuple[bool, str, dict]:
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        hashed = hash_password(password)
        cursor.execute(
            "SELECT id, fullname, email FROM users WHERE email=? AND password=?",
            (email, hashed),
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            user = {"id": row[0], "fullname": row[1], "email": row[2]}
            return True, "Login successful!", user
        else:
            return False, "Invalid email or password.", {}
    except Exception as e:
        return False, f"DB error: {e}", {}


# ---------- Utility ----------
def is_valid_email(email: str) -> bool:
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None


# ---------- Main App ----------
class AuthApp:
    def __init__(self, page: ft.Page):
        self.page = page
        create_database()

        self.page.title = "SARI NA? - Auth"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 20
        self.page.bgcolor = PRIMARY_BLUE
        self.page.window.width = 400
        self.page.window.height = 750
        self.page.window.resizable = False

        # state
        self.mode = "login"
        self.current_user = None

        # build UI
        self.build_ui()

        # Load remember me
        stored_email = self.page.client_storage.get("remember_email")
        if stored_email:
            self.email.value = stored_email
            self.remember.value = True
            self.page.update()

    # ----------------------------------------------------
    #   MAIN UI
    # ----------------------------------------------------
    def build_ui(self):
        self.logo = ft.Image(
            src="logo.png",
            width=220,
            height=70,
            fit=ft.ImageFit.CONTAIN,
        )

        # --- Tabs ---
        self.tab_signup = ft.Container(
            ft.Text("Sign Up", size=14, weight=ft.FontWeight.BOLD),
            alignment=ft.alignment.center,
            padding=10,
            expand=1,
            border_radius=20,
            ink=True,
            on_click=lambda e: self.switch_mode("signup"),
        )

        self.tab_login = ft.Container(
            ft.Text("Login", size=14, weight=ft.FontWeight.BOLD),
            alignment=ft.alignment.center,
            padding=10,
            expand=1,
            border_radius=20,
            ink=True,
            on_click=lambda e: self.switch_mode("login"),
        )

        self.tabs = ft.Row([self.tab_signup, self.tab_login], width=300, spacing=10)

        # --- Inputs ---
        self.fullnametext = ft.Text("Full Name", color=WHITE, size=14, width=300)
        self.fullname = ft.TextField(
            hint_text="Full Name",
            hint_style=ft.TextStyle(color=HINT_COLOR),
            border_radius=30,
            filled=True,
            bgcolor=FILL_COLOR,
            border_color=FILL_COLOR,
            width=300,
            text_style=ft.TextStyle(color=WHITE),
        )

        self.emailtext = ft.Text("Email Address", color=WHITE, size=14, width=300)
        self.email = ft.TextField(
            hint_text="Enter your email address",
            hint_style=ft.TextStyle(color=HINT_COLOR),
            border_radius=30,
            filled=True,
            bgcolor=FILL_COLOR,
            border_color=FILL_COLOR,
            width=300,
            text_style=ft.TextStyle(color=WHITE),
        )

        self.passwordtext = ft.Text("Password", color=WHITE, size=14, width=300)
        self.password = ft.TextField(
            hint_text="Enter your password",
            hint_style=ft.TextStyle(color=HINT_COLOR),
            password=True,
            can_reveal_password=True,
            border_radius=30,
            filled=True,
            bgcolor=FILL_COLOR,
            border_color=FILL_COLOR,
            width=300,
            text_style=ft.TextStyle(color=WHITE),
        )

        self.confirmpasstext = ft.Text("Confirm Password", color=WHITE, size=14, width=300)
        self.confirm = ft.TextField(
            hint_text="Confirm Password",
            hint_style=ft.TextStyle(color=HINT_COLOR),
            password=True,
            can_reveal_password=True,
            border_radius=30,
            filled=True,
            bgcolor=FILL_COLOR,
            border_color=FILL_COLOR,
            width=300,
            text_style=ft.TextStyle(color=WHITE),
        )

        # Remember me / forgot
        self.remember = ft.Checkbox(
            label="Remember Me",
            value=False,
            check_color=ft.Colors.BLUE_500,
            fill_color=ft.Colors.WHITE,
            label_style=ft.TextStyle(color=WHITE)
        )
        self.forgot_btn = ft.TextButton(
            content=ft.Text("Forgot Password?", color=WHITE, size=12),
            on_click=lambda e: self.page.snack_bar.show_message("Forgot password pressed"),
        )
        self.remember_row = ft.Row([self.remember, ft.Container(expand=1), self.forgot_btn], width=300)

        # Main action button
        self.main_button = ft.Container(
            ft.Text("Login", size=16, weight=ft.FontWeight.BOLD, color=PRIMARY_BLUE),
            bgcolor=WHITE,
            height=48,
            width=300,
            alignment=ft.alignment.center,
            border_radius=30,
            ink=True,
            on_click=self.submit,
        )

        self.google_btn = ft.Image(src="google.png", width=60, height=60)
        self.message = ft.Text("", color=ft.Colors.RED_600, visible=False)

        self.main_column = ft.Column(
            [
                ft.Container(height=20),
                self.logo,
                ft.Container(height=20),
                self.tabs,
                ft.Container(height=10),
                self.fullnametext,
                self.fullname,
                self.emailtext,
                self.email,
                self.passwordtext,
                self.password,
                self.confirmpasstext,
                self.confirm,
                self.remember_row,
                ft.Container(height=10),
                self.main_button,
                ft.Container(height=10),
                ft.Text("Or continue with", color=WHITE, size=12),
                self.google_btn,
                self.message,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
        )

        self.page.scroll = ft.ScrollMode.AUTO
        self.page.add(self.main_column)
        self.update_ui()

    # ----------------------------------------------------
    #   SWITCH THEMES
    # ----------------------------------------------------
    def switch_mode(self, mode):
        self.mode = mode
        self.update_ui()
        self.page.update()

    def update_ui(self):
        """Correct highlight for tabs."""
        if self.mode == "login":
            # LOGIN tab highlighted
            self.tab_login.bgcolor = WHITE
            self.tab_login.content.color = PRIMARY_BLUE

            self.tab_signup.bgcolor = PRIMARY_BLUE
            self.tab_signup.content.color = WHITE

            # hide signup fields
            self.fullnametext.visible = False
            self.fullname.visible = False
            self.confirmpasstext.visible = False
            self.confirm.visible = False
            self.remember.visible = True

            self.main_button.content.value = "Login"

        else:
            # SIGNUP tab highlighted
            self.tab_signup.bgcolor = WHITE
            self.tab_signup.content.color = PRIMARY_BLUE

            self.tab_login.bgcolor = PRIMARY_BLUE
            self.tab_login.content.color = WHITE

            # show signup fields
            self.fullnametext.visible = True
            self.fullname.visible = True
            self.confirmpasstext.visible = True
            self.confirm.visible = True
            self.remember.visible = False

            self.main_button.content.value = "Sign Up"

        self.message.visible = False
        self.page.update()

    # ----------------------------------------------------
    #   SUBMIT
    # ----------------------------------------------------
    def submit(self, e):
        email = self.email.value.strip()
        password = self.password.value.strip()

        if not email or not password:
            self.show_snack("Please fill in email and password.", False)
            return

        if not is_valid_email(email):
            self.show_snack("Invalid email format.", False)
            return

        if self.mode == "login":
            success, msg, user = login_user(email, password)
            if success:
                self.current_user = user
                if self.remember.value:
                    self.page.client_storage.set("remember_email", email)
                else:
                    try:
                        self.page.client_storage.remove("remember_email")
                    except:
                        pass

                self.show_snack(msg, True)
                self.show_logged_in_view()
            else:
                self.show_snack(msg, False)

        else:
            fullname = self.fullname.value.strip()
            confirm = self.confirm.value.strip()

            if not fullname:
                self.show_snack("Enter full name.", False)
                return
            if password != confirm:
                self.show_snack("Passwords do not match.", False)
                return
            if len(password) < 6:
                self.show_snack("Password must be at least 6 characters.", False)
                return

            ok, msg = register_user(fullname, email, password)
            if ok:
                self.show_snack(msg, True)
                self.switch_mode("login")
                self.email.value = email
                self.password.value = ""
            else:
                self.show_snack(msg, False)

    # ----------------------------------------------------
    def show_snack(self, message, success):
        color = ft.Colors.GREEN if success else ft.Colors.RED
        self.page.snack_bar = ft.SnackBar(ft.Text(message), bgcolor=color)
        self.page.snack_bar.open = True
        self.page.update()

    # ----------------------------------------------------
    def show_logged_in_view(self):
        name = self.current_user["fullname"]

        self.page.controls.clear()
        card = ft.Container(
            ft.Column(
                [
                    ft.Text(f"Welcome, {name}!", size=26, weight=ft.FontWeight.BOLD),
                    ft.Text("You're logged in. Tap 'Open AR' to continue."),
                    ft.ElevatedButton("Open AR", on_click=lambda e: self.page.snack_bar.show_message("Open AR placeholder")),
                    ft.TextButton("Logout", on_click=self.logout),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            width=340,
            padding=20,
            border_radius=16,
            bgcolor=WHITE,
        )

        self.page.add(ft.Column([ft.Container(height=40), card], horizontal_alignment=ft.CrossAxisAlignment.CENTER))
        self.page.update()

    def logout(self, e):
        self.current_user = None
        self.page.controls.clear()
        self.build_ui()
        self.page.update()


# ---------- Entry ----------
def main(page: ft.Page):
    AuthApp(page)


if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")
