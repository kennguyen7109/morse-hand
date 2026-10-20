import cv2
import numpy as np
import pygame
import math
import time
import mediapipe as mp
import os
# Khai báo chuẩn MediaPipe
mp_hands = mp.solutions.hands
# ==========================================
# 1. CẤU HÌNH BẢNG MÃ MORSE & THƯ VIỆN
# ==========================================
MORSE_CODE_DICT = {
    '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
    '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
    '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
    '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
    '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
    '--..': 'Z', '-----': '0', '.----': '1', '..---': '2', '...--': '3',
    '....-': '4', '.....': '5', '-....': '6', '--...': '7', '---..': '8',
    '----.': '9'
}

# Khởi tạo MediaPipe Hand Tracking
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# Khởi tạo Pygame Display
pygame.init()
pygame.font.init()
os.environ['SDL_VIDEO_CENTERED'] = '1'  # Căn giữa cửa sổ trên màn hình
WIDTH, HEIGHT = 1300, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Morse Hand")
clock = pygame.time.Clock()

# Phông chữ
font_title = pygame.font.SysFont("Arial", 22, bold=True)
font_body = pygame.font.SysFont("Arial", 16)
font_small = pygame.font.SysFont("Arial", 14)
font_msg = pygame.font.SysFont("Arial", 28, bold=True)

# Màu sắc giao diện (RGB)
COLOR_INDEX = (0, 220, 255)     # Ngón trỏ: Cyan (dot)
COLOR_MIDDLE = (180, 100, 255)  # Ngón giữa: Purple (dash)
COLOR_RING = (255, 180, 0)      # Ngón áp út: Yellow (end/space)
COLOR_PINKY = (255, 80, 120)    # Ngón út: Pink (delete/clear)
COLOR_THUMB = (255, 255, 255)   # Ngón cái: White

# ==========================================
# 2. HÀM VẼ GIAO DIỆN GLASSMORPHISM
# ==========================================
def draw_glass_panel(surface, rect, radius=12, bg_color=(20, 26, 38, 200), border_color=(255, 255, 255, 40)):
    """Vẽ bo góc trong suốt hiệu ứng kính mờ"""
    x, y, w, h = rect
    panel = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(panel, bg_color, (0, 0, w, h), border_radius=radius)
    pygame.draw.rect(panel, border_color, (0, 0, w, h), width=1, border_radius=radius)
    surface.blit(panel, (x, y))

def draw_morse_chart(surface, x, y, w, h):
    """Vẽ bảng tra cứu mã Morse góc phải"""
    draw_glass_panel(surface, (x, y, w, h))
    title = font_small.render("MORSE CHART", True, (160, 175, 195))
    surface.blit(title, (x + 15, y + 12))

    items = list(MORSE_CODE_DICT.items())
    col1 = items[:13]
    col2 = items[13:26]
    col3 = items[26:36]

    def render_column(col_data, start_x, start_y):
        for i, (code, char) in enumerate(col_data):
            lbl_char = font_small.render(f"{char}", True, (255, 255, 255))
            lbl_code = font_small.render(f"{code}", True, (0, 220, 255))
            cy = start_y + i * 20
            surface.blit(lbl_char, (start_x, cy))
            surface.blit(lbl_code, (start_x + 25, cy))

    render_column(col1, x + 15, y + 38)
    render_column(col2, x + 105, y + 38)
    render_column(col3, x + 195, y + 38)

# ==========================================
# 3. VÒNG LẶP CHÍNH (MAIN LOOP)
# ==========================================
# 1. Khởi tạo kết nối V4L2 tới /dev/video0
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

# 2. BẮT BUỘC: Ép nén MJPG trước khi đọc khung hình để tránh nghẽn truyền tải qua USBIP
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)

current_morse = ""
message = ""
last_touch_time = 0
TOUCH_COOLDOWN = 0.35  # Thời gian chống bấm lặp (giây)
pinky_hold_start = 0

running = True
while running:
    dt = clock.tick(60)
    fps = int(clock.get_fps())

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False

    ret, frame = cap.read()
    if not ret or frame is None:
    # Tạo khung hình đen giả lập (1280x720) để giao diện không bị treo
        frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        cv2.putText(frame, "KHONG TIM THAY WEBCAM (WSL)", (400, 360),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    # Xử lý hình ảnh Webcam
    frame = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    # Chuyển Webcam OpenCV sang Surface Pygame
    frame_surface = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
    screen.blit(frame_surface, (0, 0))

    hand_label = "No hand tracked"
    current_time = time.time()

    if results.multi_hand_landmarks and results.multi_handedness:
        hand_landmarks = results.multi_hand_landmarks[0]
        handedness = results.multi_handedness[0].classification[0].label
        hand_label = f"{handedness} hand tracked"

        # Tọa độ các khớp tay (pixel)
        h, w, _ = frame.shape
        pts = [(int(lm.x * w), int(lm.y * h)) for lm in hand_landmarks.landmark]

        # Lấy tọa độ 5 đầu ngón tay
        thumb, index, middle, ring, pinky = pts[4], pts[8], pts[12], pts[16], pts[20]

        # 1. Vẽ bộ khung nối các khớp tay
        connections = mp_hands.HAND_CONNECTIONS
        for connection in connections:
            start_idx, end_idx = connection
            pygame.draw.line(screen, (200, 200, 200), pts[start_idx], pts[end_idx], 2)

        # 2. Vẽ điểm phát sáng cho các đầu ngón tay
        pygame.draw.circle(screen, COLOR_THUMB, thumb, 9)
        pygame.draw.circle(screen, COLOR_INDEX, index, 9)
        pygame.draw.circle(screen, COLOR_MIDDLE, middle, 9)
        pygame.draw.circle(screen, COLOR_RING, ring, 9)
        pygame.draw.circle(screen, COLOR_PINKY, pinky, 9)

        # 3. Tính khoảng cách giữa ngón cái và các ngón khác
        dist_index = math.hypot(thumb[0] - index[0], thumb[1] - index[1])
        dist_middle = math.hypot(thumb[0] - middle[0], thumb[1] - middle[1])
        dist_ring = math.hypot(thumb[0] - ring[0], thumb[1] - ring[1])
        dist_pinky = math.hypot(thumb[0] - pinky[0], thumb[1] - pinky[1])

        THRESHOLD = 32 # Ngưỡng nhận diện chạm (pixel)

        if current_time - last_touch_time > TOUCH_COOLDOWN:
            # Ngón cái + Ngón trỏ -> Dot (.)
            if dist_index < THRESHOLD:
                current_morse += "."
                last_touch_time = current_time

            # Ngón cái + Ngón giữa -> Dash (-)
            elif dist_middle < THRESHOLD:
                current_morse += "-"
                last_touch_time = current_time

            # Ngón cái + Ngón áp út -> Chốt ký tự / Dấu cách
            elif dist_ring < THRESHOLD:
                if current_morse in MORSE_CODE_DICT:
                    message += MORSE_CODE_DICT[current_morse]
                elif current_morse == "":
                    message += " "
                current_morse = ""
                last_touch_time = current_time

            # Ngón cái + Ngón út -> Xóa 1 ký tự / Giữ để xóa hết
            elif dist_pinky < THRESHOLD:
                if pinky_hold_start == 0:
                    pinky_hold_start = current_time

                if current_time - pinky_hold_start > 1.2: # Giữ 1.2s để Xóa tất cả
                    message = ""
                    current_morse = ""
                    pinky_hold_start = 0
                    last_touch_time = current_time
                else:
                    if current_morse:
                        current_morse = current_morse[:-1]
                    elif message:
                        message = message[:-1]
                    last_touch_time = current_time
            else:
                pinky_hold_start = 0

    # ==========================================
    # 4. HỂNH THỊ CÁC PANEL CỦA GIAO DIỆN
    # ==========================================
    # Box Top-Left: Tên App & Trạng thái tay
    draw_glass_panel(screen, (30, 30, 260, 80))
    title_txt = font_title.render("Morse Hand", True, (255, 255, 255))
    status_color = (0, 220, 120) if "tracked" in hand_label and "No" not in hand_label else (255, 100, 100)
    pygame.draw.circle(screen, status_color, (45, 78), 5)
    status_txt = font_small.render(hand_label, True, (180, 195, 210))
    screen.blit(title_txt, (45, 42))
    screen.blit(status_txt, (58, 70))

    # Box Top-Right: Bộ đếm FPS
    draw_glass_panel(screen, (WIDTH - 140, 30, 110, 36))
    pygame.draw.circle(screen, (0, 220, 120), (WIDTH - 125, 48), 4)
    fps_txt = font_body.render(f"{fps} FPS", True, (255, 255, 255))
    screen.blit(fps_txt, (WIDTH - 110, 38))

    # Box Legend: Hướng dẫn chức năng từng ngón tay
    draw_glass_panel(screen, (30, 125, 260, 150))
    legend_items = [
        (COLOR_INDEX, "Index", "dot"),
        (COLOR_MIDDLE, "Middle", "dash"),
        (COLOR_RING, "Ring", "end · ×2 space"),
        (COLOR_PINKY, "Pinky", "delete · hold clear")
    ]
    for i, (color, finger, action) in enumerate(legend_items):
        py = 140 + i * 32
        pygame.draw.circle(screen, color, (48, py + 8), 6)
        f_txt = font_body.render(finger, True, (220, 230, 240))
        a_txt = font_small.render(action, True, (150, 165, 185))
        screen.blit(f_txt, (65, py))
        screen.blit(a_txt, (160, py + 2))

    # Bảng Morse Chart bên phải
    draw_morse_chart(screen, WIDTH - 300, 80, 270, 275)

    # Box Bottom-Left: CURRENT LETTER (Trạng thái nhập Morse)
    draw_glass_panel(screen, (30, HEIGHT - 200, WIDTH - 60, 75))
    lbl_curr = font_small.render("CURRENT LETTER", True, (140, 155, 175))
    screen.blit(lbl_curr, (48, HEIGHT - 190))
    
    morse_display = current_morse if current_morse else "Touch your thumb to a finger to start a letter"
    morse_color = (0, 220, 255) if current_morse else (120, 135, 155)
    txt_curr = font_body.render(morse_display, True, morse_color)
    screen.blit(txt_curr, (48, HEIGHT - 165))

    # Box Bottom-Right: MESSAGE (Ký tự đã tạo)
    draw_glass_panel(screen, (30, HEIGHT - 110, WIDTH - 60, 80))
    lbl_msg = font_small.render("MESSAGE", True, (140, 155, 175))
    lbl_chars = font_small.render(f"{len(message)} chars", True, (140, 155, 175))
    screen.blit(lbl_msg, (48, HEIGHT - 100))
    screen.blit(lbl_chars, (WIDTH - 120, HEIGHT - 100))

    # Con trỏ nhấp nháy cho khung văn bản
    cursor = "|" if int(time.time() * 2) % 2 == 0 else ""
    txt_msg = font_msg.render(f"{message}{cursor}", True, (255, 255, 255))
    screen.blit(txt_msg, (48, HEIGHT - 75))

    pygame.display.flip()

cap.release()
pygame.quit()