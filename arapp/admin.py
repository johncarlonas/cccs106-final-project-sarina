import flet as ft
from src.admin_ui.dashboard import DashboardView
import traceback

def main(page: ft.Page):
    try:
        page.title = "SARI NA - Admin Dashboard"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.window.width = 400
        page.window.height = 800
        page.window.center()
        
        def route_change(route):
            page.views.clear()
            if page.route == "/" or page.route == "/dashboard":
                page.views.append(DashboardView(page))
            page.update()

        def view_pop(view):
            if len(page.views) > 1:
                page.views.pop()
                top_view = page.views[-1]
                page.go(top_view.route)

        page.on_route_change = route_change
        page.on_view_pop = view_pop
        page.go("/dashboard")
    except Exception as e:
        print(f"Error in main: {e}")
        traceback.print_exc()
        page.add(ft.Text(f"Error: {e}", color="red"))

if __name__ == "__main__":
    try:
        ft.app(target=main, assets_dir="assets", upload_dir="assets")
    except Exception as e:
        print(f"Fatal error: {e}")
        traceback.print_exc()
        input("Press Enter to exit...")
