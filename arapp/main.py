import flet as ft
import time
import threading
import os
import sys

# Add src directory to path for both development and production
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from ui.opening import OpeningView
from ui.new_user import NewUserView
from ui.user_selection import UserSelectionView
from ui.login_signup import LoginSignupView
from ui.email_verification import EmailVerificationView
from ui.forgot_password import ForgotPasswordView
from ui.home import HomeView
from ui.settings import SettingsView
from ui.ar_view import ARView
from admin_ui.dashboard import DashboardView
from utils.auth_middleware import check_route_access

def main(page: ft.Page):
    page.title = "SARI NA"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 400 
    page.window.height = 800
    page.window.center()
    page.window_resizable = False
    
    # TEMPORARY: Reset client storage for testing - REMOVE THIS AFTER TESTING
    page.client_storage.clear()
    
    # Check app state
    def check_first_launch():
        """Check if this is the first launch of the app"""
        # Use client storage to track first launch
        first_launch = page.client_storage.get("first_launch")
        return first_launch is None or first_launch == True
    
    def check_logged_in():
        """Check if a user is logged in"""
        logged_in_email = page.client_storage.get("logged_in_user")
        return logged_in_email is not None
    
    def route_change(route):
        page.views.clear()
        
        # Protected routes - check access before rendering
        protected_routes = ["/home", "/dashboard", "/settings", "/ar"]
        
        if page.route in protected_routes:
            if not check_route_access(page, page.route):
                # User doesn't have access - redirect to appropriate page
                user_email = page.client_storage.get("logged_in_user")
                
                if not user_email:
                    # Not logged in - go to login
                    page.go("/login_signup")
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text("Please login to access this page"),
                        bgcolor="red"
                    )
                    page.snack_bar.open = True
                else:
                    # Logged in but wrong role - show error
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text("You don't have permission to access this page"),
                        bgcolor="red"
                    )
                    page.snack_bar.open = True
                
                page.update()
                return
        
        if page.route == "/":
            page.views.append(OpeningView(page))
            page.views.append(OpeningView(page))
            
            def delayed_navigate():
                time.sleep(3)
                if page.route == "/":
                    # Determine where to navigate based on app state
                    if check_logged_in():
                        # User is logged in, go to home
                        page.go("/home")
                    elif check_first_launch():
                        # First launch, show new_user
                        page.go("/new_user")
                    else:
                        # Not first launch but no user logged in
                        page.go("/user_selection")
            
            threading.Thread(target=delayed_navigate, daemon=True).start()
            
        elif page.route == "/new_user":
            page.views.append(NewUserView(page))
        elif page.route == "/user_selection":
            page.views.append(UserSelectionView(page))
        elif page.route == "/login_signup":
            page.views.append(LoginSignupView(page))
        elif page.route == "/email_verification":
            page.views.append(EmailVerificationView(page))
        elif page.route == "/forgot_password":
            page.views.append(ForgotPasswordView(page))
        elif page.route == "/home":
            page.views.append(HomeView(page))
        elif page.route == "/dashboard":
            page.views.append(DashboardView(page))
        elif page.route == "/settings":
            page.views.append(SettingsView(page))
        elif page.route == "/ar":
            page.views.append(ARView(page))
        page.update()

    def view_pop(view):
        if len(page.views) > 1:
            page.views.pop()
            top_view = page.views[-1]
            page.go(top_view.route)
        # Don't destroy window, just stay on current view

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets", upload_dir="assets")
