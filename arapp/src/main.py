import flet as ft
import time
import threading
from ui.opening import OpeningView
from ui.new_user import NewUserView
from ui.user_selection import UserSelectionView
from ui.login_signup import LoginSignupView

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
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

ft.app(target=main, assets_dir="../assets")
