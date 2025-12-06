import flet as ft
import time
import threading
from src.ui.opening import OpeningView
from src.ui.new_user import NewUserView
from src.ui.user_selection import UserSelectionView
from src.ui.login_signup import LoginSignupView
from src.ui.home import HomeView
from src.ui.settings import SettingsView

def main(page: ft.Page):
    page.title = "SARI NA"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 400 
    page.window.height = 800
    page.window.center()
    page.window_resizable = False
    
    def route_change(route):
        page.views.clear()
        if page.route == "/":
            page.views.append(OpeningView(page))
            
            def delayed_navigate():
                time.sleep(5)
                if page.route == "/":
                    page.go("/new_user")
            
            threading.Thread(target=delayed_navigate, daemon=True).start()
            
        elif page.route == "/new_user":
            page.views.append(NewUserView(page))
        elif page.route == "/user_selection":
            page.views.append(UserSelectionView(page))
        elif page.route == "/login_signup":
            page.views.append(LoginSignupView(page))
        elif page.route == "/home":
            page.views.append(HomeView(page))
        elif page.route == "/settings":
            page.views.append(SettingsView(page))
        page.update()

    def view_pop(view):
        if len(page.views) > 1:
            page.views.pop()
            top_view = page.views[-1]
            page.go(top_view.route)
        else:
            page.window_destroy()

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets", upload_dir="assets")
