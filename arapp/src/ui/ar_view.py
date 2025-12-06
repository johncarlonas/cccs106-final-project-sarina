
import flet as ft
import threading
from ar_navigation.ar_camera import generate_frames

# NOTE: paupdate na lang ng UI neto tenks

class ARView(ft.View):
    def __init__(self, page):
        super().__init__("/ar")
        self.page = page
        self.img = ft.Image(src="", width=page.window.width, height=page.window.height, fit=ft.ImageFit.COVER)
        self.controls = [self.img, ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: page.go("/"))]

        self.stop_event = threading.Event()

        # get route from session
        route = page.session.get("current_route")
        if not route:
            page.snack_bar = ft.SnackBar(ft.Text("No route found"))
            page.snack_bar.open = True
            page.update()
            return

        # helper functions to get GPS and heading from page
        def get_user_location():
            try:
                loc = page.geolocator.get_geolocation()
                return (loc.latitude, loc.longitude)
            except Exception:
                return (None, None)

        def get_user_heading():
            try:
                return getattr(page, "heading", 0)
            except Exception:
                return 0

        def frame_callback(b64):
            # update Flet image using base64 payload
            self.img.src_base64 = b64
            self.page.update()

        # start camera thread
        threading.Thread(target=generate_frames, args=(route, frame_callback, get_user_location, get_user_heading, self.stop_event), daemon=True).start()

    def did_dispose(self):
        self.stop_event.set()
        super().did_dispose()
