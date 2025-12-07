
import cv2
import numpy as np
import base64
import time
from .bearing import bearing_to_target

# path to arrow PNG
ARROW_PATH = "arapp/assets/arrow_up.png"

# if arrow not found error
_arrow_img = cv2.imread(ARROW_PATH, cv2.IMREAD_UNCHANGED)
if _arrow_img is None:
    raise FileNotFoundError(f"Arrow image not found at {ARROW_PATH}")

# convert frame to text format
def _encode_frame_to_base64(frame):
    _, buf = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
    return base64.b64encode(buf).decode('utf-8')

# rotate image based on direction
def _rotate_image(img, angle):
    h, w = img.shape[:2]
    M = cv2.getRotationMatrix2D((w//2, h//2), -angle, 1.0)
    return cv2.warpAffine(img, M, (w, h), borderMode=cv2.BORDER_TRANSPARENT)

def _overlay_perspective_arrow(frame, arrow_rgba, angle_deg, scale=1.0):
    # get frame height/width first
    fh, fw = frame.shape[:2]

    # rotate arrow
    arrow_rot = _rotate_image(arrow_rgba, angle_deg)

    # calculate target size
    h_a, w_a = arrow_rot.shape[:2]
    target_w = int(w_a * scale)
    target_h = int(h_a * scale)

    # don't draw if too small
    if target_w < 10 or target_h < 10:
        return frame

    # shrink if it exceeds frame dimensions
    if target_h > fh:
        ratio = fh / target_h
        target_h = fh
        target_w = int(target_w * ratio)
    
    if target_w > fw:
        ratio = fw / target_w
        target_w = fw
        target_h = int(target_h * ratio)

    arrow_resized = cv2.resize(arrow_rot, (target_w, target_h), interpolation=cv2.INTER_AREA)

    # position: bottom-center with small offset forward
    x = fw//2 - target_w//2
    y = int(fh * 0.65) - target_h//2 

    # clamp coordinates to ensure they stay inside frame
    x = max(0, min(x, fw - target_w))
    y = max(0, min(y, fh - target_h))

    # split channels
    b,g,r,a = cv2.split(arrow_resized)
    arrow_rgb = cv2.merge((b,g,r))
    mask = a.astype(float)/255.0
    mask = cv2.merge([mask, mask, mask])

    roi = frame[y:y+target_h, x:x+target_w].astype(float)
    arrow_rgb = arrow_rgb.astype(float)

    # final sanity check to avoid crash if rounding errors occur
    if roi.shape[:2] != mask.shape[:2]:
        return frame

    blended = (roi * (1 - mask) + arrow_rgb * mask).astype(np.uint8)
    frame[y:y+target_h, x:x+target_w] = blended
    return frame

def generate_frames(route_points, frame_callback, get_user_location_func, get_user_heading_func, stop_flag):
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    if not cap.isOpened():
        raise RuntimeError("Camera not available")

    # convert loaded arrow to BGRA if needed
    arrow_rgba = _arrow_img.copy()
    if arrow_rgba.shape[2] == 3:
        # add alpha channel if missing
        b,g,r = cv2.split(arrow_rgba)
        alpha = np.full(b.shape, 255, dtype=np.uint8)
        arrow_rgba = cv2.merge([b,g,r,alpha])

    waypoint_index = 0
    last_scale = 1.0

    while not stop_flag.is_set():
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.02)
            continue

        user_lat, user_lon = get_user_location_func()
        user_heading = get_user_heading_func() or 0.0

        # ensure we have route and user location
        if user_lat is None or waypoint_index >= len(route_points):
            b64 = _encode_frame_to_base64(frame)
            frame_callback(b64)
            time.sleep(0.03)
            continue

        # find current target waypoint
        tx, ty = route_points[waypoint_index][0], route_points[waypoint_index][1]  # lat, lon
        bearing = bearing_to_target(user_lat, user_lon, tx, ty)

        # compute simple distance using Haversine approx
        def haversine_m(a_lat,a_lon,b_lat,b_lon):
            from math import radians, sin, cos, sqrt, asin
            R = 6371000
            dlat = radians(b_lat - a_lat); dlon = radians(b_lon - a_lon)
            a = sin(dlat/2)**2 + cos(radians(a_lat))*cos(radians(b_lat))*sin(dlon/2)**2
            c = 2*asin(min(1,sqrt(a)))
            return R*c

        dist = haversine_m(user_lat, user_lon, tx, ty)

        # advance waypoint if within 4 meters
        if dist < 4.0 and waypoint_index < len(route_points)-1:
            waypoint_index += 1
            tx, ty = route_points[waypoint_index][0], route_points[waypoint_index][1]
            bearing = bearing_to_target(user_lat, user_lon, tx, ty)
            dist = haversine_m(user_lat, user_lon, tx, ty)

        # arrow should point in direction user should walk relative to device heading
        angle_to_draw = (bearing - user_heading + 360) % 360

        # scale arrow with approximate distance: closer => larger
        # clamp between 0.4 and 1.4
        scale = max(0.4, min(1.4, 1.2 - (dist / 50.0)))
        last_scale = 0.92*last_scale + 0.08*scale

        # overlay arrow and send frame
        frame_overlay = _overlay_perspective_arrow(frame, arrow_rgba, angle_to_draw, last_scale)
        b64 = _encode_frame_to_base64(frame_overlay)
        frame_callback(b64)

        time.sleep(0.03)

    cap.release()