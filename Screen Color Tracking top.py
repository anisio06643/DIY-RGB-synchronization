import cv2
import numpy as np
import mss
import serial
import time

# --- CONFIGURATION ---
SERIAL_PORT = 'COM3'
BAUD_RATE = 115200
FPS_TARGET = 60

TOP_START = 0.04         # Skip very top edge (title bars, menu bars)
TOP_END   = 0.25         # Sample down to 25% of screen height
SMOOTHING = 0.2
SAT_THRESHOLD = 80
SAT_BOOST_VIVID = 1.3
MIN_BRIGHTNESS = 8

# Magic prefix bytes to synchronize frame starts with ESP32
MAGIC_HEADER = b'MGK' 

REGIONS = [
    (0.00, 0.33),
    (0.33, 0.67),
    (0.67, 1.00),
]

def get_average_color(img_bgr, x_start_frac, x_end_frac):
    """Expects a standard 3-channel OpenCV BGR image"""
    h, w = img_bgr.shape[:2]
    y1 = max(1, int(h * TOP_START))
    y2 = max(2, int(h * TOP_END))
    x1 = int(w * x_start_frac)
    x2 = int(w * x_end_frac)
    
    strip = img_bgr[y1:y2, x1:x2]
    # Direct mean calculation is significantly faster than resizing down first
    avg_bgr = cv2.mean(strip)[:3] 
    
    # Return directly as standard R, G, B ints
    return int(avg_bgr[2]), int(avg_bgr[1]), int(avg_bgr[0])

def process_color(r, g, b):
    # White/pastel passthrough — no processing
    ch_max = max(r, g, b)
    ch_min = min(r, g, b)
    if ch_max > 180 and (ch_max - ch_min) < 40:
        return r, g, b

    # Saturation boost using standard OpenCV operations
    bgr_pixel = np.uint8([[[b, g, r]]])
    hsv = cv2.cvtColor(bgr_pixel, cv2.COLOR_BGR2HSV)
    h, s, v = hsv[0, 0]

    if s > SAT_THRESHOLD:
        hsv[0, 0, 1] = min(255, int(s * SAT_BOOST_VIVID))
        boosted = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        b, g, r = boosted[0, 0]

    if max(r, g, b) < MIN_BRIGHTNESS:
        return 0, 0, 0

    return int(r), int(g), int(b)

try:
    esp = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.05)
    time.sleep(2)
    print(f"Connected to ESP32 on {SERIAL_PORT}")
except Exception as e:
    print(f"Error opening serial port: {e}")
    exit()

sct = mss.MSS()
monitor = sct.monitors[1]
prev_colors = [(0, 0, 0)] * 3

print(f"Sampling {int(TOP_START*100)}% to {int(TOP_END*100)}% of screen height | Ctrl+C to stop")

try:
    while True:
        start_time = time.time()

        screenshot = sct.grab(monitor)
        # Convert screenshot to predictable OpenCV BGR format immediately
        img_bgra = np.array(screenshot, dtype=np.uint8)
        img_bgr = cv2.cvtColor(img_bgra, cv2.COLOR_BGRA2BGR)

        current_colors = []
        for x_start, x_end in REGIONS:
            r, g, b = get_average_color(img_bgr, x_start, x_end)
            r, g, b = process_color(r, g, b)
            current_colors.append((r, g, b))

        smoothed = []
        for (pr, pg, pb), (cr, cg, cb) in zip(prev_colors, current_colors):
            smoothed.append((
                int(pr * SMOOTHING + cr * (1 - SMOOTHING)),
                int(pg * SMOOTHING + cg * (1 - SMOOTHING)),
                int(pb * SMOOTHING + cb * (1 - SMOOTHING)),
            ))

        prev_colors = smoothed

        # Build raw binary stream: Header (3 bytes) + Color Channel Data (9 bytes)
        payload = bytearray(MAGIC_HEADER)
        for r, g, b in smoothed:
            payload.append(r)
            payload.append(g)
            payload.append(b)
        
        esp.write(payload)

        elapsed = time.time() - start_time
        sleep_time = (1.0 / FPS_TARGET) - elapsed
        if sleep_time > 0:
            time.sleep(sleep_time)

except KeyboardInterrupt:
    print("\nStopping — turning off LEDs...")
    # Send header + 9 zeros to clear out strip
    esp.write(MAGIC_HEADER + bytearray([0] * 9))
    time.sleep(0.1)
    esp.close()
