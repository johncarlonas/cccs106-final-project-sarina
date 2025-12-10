
import cv2
import numpy as np
import base64
import time
import os
from math import sqrt, radians, sin, cos, asin
from .bearing import bearing_to_target

# --- FIX: Dynamic Path Finding ---
# Current file is in: src/ar_navigation/ar_camera.py
_current_dir = os.path.dirname(os.path.abspath(__file__))

# We need to go up one level (to src) then into assets
# path: src/ar_navigation/../assets/arrow.png
ARROW_PATH = os.path.join(_current_dir, "..", "assets", "arrow.png")

# Resolve exact path to avoid symlink/relative path issues
ARROW_PATH = os.path.abspath(ARROW_PATH)
print(f"DEBUG: Looking for arrow at: {ARROW_PATH}")

# Load image
_arrow_img = cv2.imread(ARROW_PATH, cv2.IMREAD_UNCHANGED)

# Fallback: If image still fails, create a red triangle programmatically so app doesn't crash
if _arrow_img is None:
    print(f"WARNING: Arrow image not found at {ARROW_PATH}. Using fallback shape.")
    # Create a 100x100 transparent image
    _arrow_img = np.zeros((100, 100, 4), dtype=np.uint8)
    # Draw a red triangle
    # Points: Top-Center, Bottom-Left, Bottom-Right
    pts = np.array([[50, 10], [10, 90], [90, 90]], np.int32)
    cv2.fillPoly(_arrow_img, [pts], (0, 0, 255, 255)) # Red color, Full Alpha

def _encode_frame_to_base64(frame):
    _, buf = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
    return base64.b64encode(buf).decode('utf-8')

def _rotate_image(img, angle):
    h, w = img.shape[:2]
    M = cv2.getRotationMatrix2D((w//2, h//2), -angle, 1.0)
    return cv2.warpAffine(img, M, (w, h), borderMode=cv2.BORDER_TRANSPARENT)

def _overlay_perspective_arrow(frame, arrow_rgba, angle_deg, scale=1.0):
    # Rotate
    arrow_rot = _rotate_image(arrow_rgba, angle_deg)

    # Scale
    h_a, w_a = arrow_rot.shape[:2]
    target_w = int(w_a * scale)
    target_h = int(h_a * scale)
    
    if target_w < 10 or target_h < 10:
        return frame
        
    arrow_resized = cv2.resize(arrow_rot, (target_w, target_h), interpolation=cv2.INTER_AREA)
    fh, fw = frame.shape[:2]

    # Position: Bottom center
    x = fw // 2 - target_w // 2
    y = int(fh * 0.75) - target_h // 2

    # Ensure coordinates are within bounds
    x = max(0, x)
    y = max(0, y)
    x = min(x, fw - 1)
    y = min(y, fh - 1)

    # Compute how much of the arrow actually fits on the frame
    actual_w = min(target_w, fw - x)
    actual_h = min(target_h, fh - y)

    if actual_w <= 0 or actual_h <= 0:
        return frame

    # Crop the arrow to the part that fits
    arrow_to_use = arrow_resized[:actual_h, :actual_w]

    # Extract ROI from frame (guaranteed to be same size)
    roi = frame[y:y+actual_h, x:x+actual_w]

    # Alpha blending
    if arrow_to_use.shape[2] == 4:
        b, g, r, a = cv2.split(arrow_to_use)
        arrow_rgb = cv2.merge((b, g, r))
        mask = a.astype(float) / 255.0
        mask = np.stack([mask, mask, mask], axis=-1)  # Shape: (H, W, 3)
    else:
        arrow_rgb = arrow_to_use.astype(float)
        mask = np.ones_like(arrow_rgb)

    # Ensure types
    roi = roi.astype(float)
    arrow_rgb = arrow_rgb.astype(float)

    # Blend
    blended = (roi * (1 - mask) + arrow_rgb * mask).astype(np.uint8)
    frame[y:y+actual_h, x:x+actual_w] = blended
    return frame

def haversine_m(a_lat, a_lon, b_lat, b_lon):
    R = 6371000
    dlat = radians(b_lat - a_lat)
    dlon = radians(b_lon - a_lon)
    a = sin(dlat/2)**2 + cos(radians(a_lat))*cos(radians(b_lat))*sin(dlon/2)**2
    c = 2*asin(min(1, sqrt(a)))
    return R*c

def generate_frames(route_points, frame_callback, get_user_location_func, get_user_heading_func, stop_flag):
    cap = None
    # Try different camera indices (0 is usually back cam on phones, 1/2 on PC)
    for camera_index in [1, 2]:
        cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap = cv2.VideoCapture(camera_index)
        
        if cap.isOpened():
            ret, _ = cap.read()
            if ret:
                break
            cap.release()
            cap = None
            
    if cap is None:
        print("Error: Could not open any camera.")
        return

    # Optimization: Lower resolution for speed
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # Prepare arrow image
    arrow_rgba = _arrow_img.copy()
    if arrow_rgba.shape[2] == 3:
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

        # --- VISUAL DEBUG: Check if GPS is the issue ---
        if user_lat is None:
            cv2.putText(frame, "Waiting for GPS...", (30, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            b64 = _encode_frame_to_base64(frame)
            frame_callback(b64)
            time.sleep(0.1)
            continue

        if waypoint_index >= len(route_points):
            cv2.putText(frame, "Arrived!", (30, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            b64 = _encode_frame_to_base64(frame)
            frame_callback(b64)
            time.sleep(0.1)
            continue

        # Navigation Logic
        tx, ty = route_points[waypoint_index][0], route_points[waypoint_index][1]
        dist = haversine_m(user_lat, user_lon, tx, ty)

        if dist < 5.0 and waypoint_index < len(route_points)-1:
            waypoint_index += 1
            tx, ty = route_points[waypoint_index][0], route_points[waypoint_index][1]
            dist = haversine_m(user_lat, user_lon, tx, ty)

        bearing = bearing_to_target(user_lat, user_lon, tx, ty)
        angle_to_draw = (bearing - user_heading + 360) % 360

        # Smoother, smaller arrow: 0.3 (far) to 0.8 (very close)
        scale = max(0.3, min(0.8, 0.8 - (dist / 70.0)))
        last_scale = 0.9 * last_scale + 0.1 * scale

        # --- NEW: Elegant Navy Blue Transparent Banner ---
        banner_text = f"Destination: {int(dist)} m"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.65   # Clean, not too big
        thickness = 1       # Thin stroke for elegance

        # Get text size
        (text_w, text_h), baseline = cv2.getTextSize(banner_text, font, font_scale, thickness)
        
        # Add generous padding
        pad_x, pad_y = 25, 15
        banner_w = text_w + 2 * pad_x
        banner_h = text_h + baseline + 2 * pad_y

        # Position: top center
        fh, fw = frame.shape[:2]
        x0 = (fw - banner_w) // 2
        y0 = 25

        # Ensure on-screen
        x0 = max(0, min(x0, fw - banner_w))
        y0 = max(0, min(y0, fh - banner_h))

        # Create overlay with deep navy blue (#002A7A → BGR: 122, 42, 0)
        overlay = frame.copy()
        alpha = 0.7  # 70% opacity — tweak as needed
        cv2.rectangle(overlay, (x0, y0), (x0 + banner_w, y0 + banner_h), (122, 42, 0), -1)  # Navy blue

        # Blend with original frame
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

        # Draw smooth, anti-aliased soft white text
        text_x = x0 + pad_x
        text_y = y0 + pad_y + text_h
        cv2.putText(
            frame,
            banner_text,
            (text_x, text_y),
            font,
            font_scale,
            (240, 240, 240),  # Soft white for contrast
            thickness,
            cv2.LINE_AA  # ← Smooth, no pixelation!
        )

        # Draw Arrow (unchanged)
        frame = _overlay_perspective_arrow(frame, arrow_rgba, angle_to_draw, scale)  # or last_scale

        b64 = _encode_frame_to_base64(frame)
        frame_callback(b64)

        time.sleep(0.03)

    cap.release()