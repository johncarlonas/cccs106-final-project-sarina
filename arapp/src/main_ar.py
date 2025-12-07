
import flet as ft
from ui.search_view import SearchView
from ui.ar_view import ARView

# paayos na lang UI neto kapag iintegrate na thanks

def main(page: ft.Page):
    page.title = "SARI NA"
    page.window_width = 400
    page.window_height = 800
    page.window_resizable = False

    def route_change(route):
        page.views.clear()
        if page.route == "/":
            page.views.append(SearchView(page))
        elif page.route == "/ar":
            page.views.append(ARView(page))
        page.update()

    page.on_route_change = route_change
    page.go("/")

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")
