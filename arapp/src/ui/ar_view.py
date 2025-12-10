
import flet as ft
import threading
from src.ar_navigation.ar_camera import generate_frames

class ARView(ft.View):
    def __init__(self, page):
        super().__init__("/ar")
        self.page = page
        self.img = ft.Image(src="", width=page.window.width, height=page.window.height, fit=ft.ImageFit.COVER)
        
        self.stop_event = threading.Event()
        
        def on_back_click(e):
            self.stop_event.set()
            page.go("/home")
        
        back_button = ft.Container(
            content=ft.IconButton(ft.Icons.ARROW_BACK, icon_color="white", icon_size=30, on_click=on_back_click),
            bgcolor="#80000000", border_radius=25, padding=5, top=40, left=20
        )
        
        self.controls = [ft.Stack([self.img, back_button], expand=True)]

        route = page.session.get("current_route")
        if not route:
            # Dummy route for testing
            route = [(13.621775, 123.194824), (13.622, 123.195)]

        def get_user_location():
            try:
                # 1. Try Real GPS
                if hasattr(page, "geolocator"):
                    loc = page.geolocator.get_geolocation()
                    if loc:
                        return (loc.latitude, loc.longitude)
                
                # 2. Fallback for testing/desktop (Returns start of route)
                # Without this, the arrow will never show if GPS is flaky
                if route:
                    return route[0]
                return (None, None)
            except Exception:
                if route: return route[0]
                return (None, None)

        def get_user_heading():
            try:
                return getattr(page, "heading", 0)
            except:
                return 0

        def frame_callback(b64):
            if self.stop_event.is_set(): return
            try:
                self.img.src_base64 = b64
                self.page.update()
            except:
                self.stop_event.set()

        threading.Thread(
            target=generate_frames, 
            args=(route, frame_callback, get_user_location, get_user_heading, self.stop_event), 
            daemon=True
        ).start()

    def did_dispose(self):
        self.stop_event.set()
        super().did_dispose()