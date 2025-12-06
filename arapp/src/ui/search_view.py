
import flet as ft
from ar_navigation.routing import get_route
from ar_navigation.places import PLACES

# NOTE: paupdate na lang ng UI neto tenks

class SearchView(ft.View):
    def __init__(self, page):
        super().__init__("/search")
        self.page = page

        self.search = ft.TextField(label="Search building", width=320, on_change=self.on_change)
        self.list_view = ft.ListView(expand=True, spacing=5)
        self.start_nav_btn = ft.ElevatedButton("Start Navigation", on_click=self.start_navigation)

        # simple user location placeholder (in final app we use page.geolocator)
        self.user_lat = None
        self.user_lon = None

        content = ft.Column(
            [
                ft.Text("SARI NA Campus Navigator", size=28),
                self.search,
                self.list_view,
                self.start_nav_btn
            ],
            spacing=10,
        )

        self.controls = [content]

        # pre-fill list
        self.update_suggestions("")

    def on_change(self, e):
        q = e.control.value.strip().lower()
        self.update_suggestions(q)

    def update_suggestions(self, q):
        self.list_view.controls.clear()
        names = list(PLACES.keys())
        if q:
            names = [n for n in names if q in n.lower()]
        for n in names[:30]:
            b = ft.ListTile(title=ft.Text(n), on_click=lambda e, name=n: self.select_name(name))
            self.list_view.controls.append(b)
        self.page.update()

    def select_name(self, name):
        self.search.value = name
        self.update_suggestions(name)
        self.page.update()

    def start_navigation(self, e):
        dest_name = self.search.value
        if not dest_name or dest_name not in PLACES:
            self.page.snack_bar = ft.SnackBar(ft.Text("Please choose a valid building"))
            self.page.snack_bar.open = True
            self.page.update()
            return

        dest_coords = PLACES[dest_name]
        # get user's location using page.geolocator (mobile)
        try:
            loc = self.page.geolocator.get_geolocation()
            user_lat = loc.latitude
            user_lon = loc.longitude
        except Exception:
            # fallback: ask user to input or use a fake location while in production
            user_lat, user_lon = 13.6235, 123.1941

        # compute route (synchronous; could be moved to background)
        route = get_route((user_lat, user_lon), dest_coords)
        # push AR view with route in query state
        self.page.session.set("current_route", route)
        self.page.go("/ar")