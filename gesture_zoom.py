import cv2
import mediapipe as mp
import numpy as np
import fitz  # PyMuPDF
import sys
import time
import os
from docx2pdf import convert

# Get document path
doc_path = sys.argv[1]
is_pdf = doc_path.lower().endswith('.pdf')

# Convert to PDF if Word doc
if not is_pdf:
    pdf_path = os.path.splitext(doc_path)[0] + '.pdf'
    convert(doc_path, pdf_path)
    doc_path = pdf_path

# Load document
doc = fitz.open(doc_path)
total_pages = len(doc)
current_page = 0
zoom_factor = 1.0

# Mediapipe Hand Detection
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    model_complexity=1,
    min_detection_confidence=0.75,
    min_tracking_confidence=0.75,
    max_num_hands=2
)
draw_utils = mp.solutions.drawing_utils

# Open webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open camera.")
    sys.exit()

prev_swipe_time = time.time()

try:
    while True:
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        landmark_list = []
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                for idx, lm in enumerate(hand_landmarks.landmark):
                    x, y = int(lm.x * w), int(lm.y * h)
                    landmark_list.append([idx, x, y])
                draw_utils.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # Gesture control
        if landmark_list:
            x1, y1 = landmark_list[4][1], landmark_list[4][2]
            x2, y2 = landmark_list[8][1], landmark_list[8][2]
            cv2.circle(frame, (x1, y1), 7, (0, 255, 0), cv2.FILLED)
            cv2.circle(frame, (x2, y2), 7, (0, 255, 0), cv2.FILLED)
            cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)

            distance = np.linalg.norm([x2 - x1, y2 - y1])
            zoom_factor = np.interp(distance, [15, 220], [0.5, 3.0])
            zoom_factor = max(0.5, min(zoom_factor, 3.0))  # safety clamp

            # Swipe for page navigation (debounced)
            now = time.time()
            wrist_x = landmark_list[0][1]
            palm_x = landmark_list[9][1]
            diff = palm_x - wrist_x

            if abs(diff) > 100 and now - prev_swipe_time > 1.0:
                if diff > 0 and current_page > 0:
                    current_page -= 1
                elif diff < 0 and current_page < total_pages - 1:
                    current_page += 1
                prev_swipe_time = now

        # Render document page with zoom
        try:
            page = doc.load_page(current_page)
            matrix = fitz.Matrix(zoom_factor, zoom_factor)
            pix = page.get_pixmap(matrix=matrix, colorspace=fitz.csRGB, alpha=True)
            doc_img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 4)
            doc_img = cv2.cvtColor(doc_img, cv2.COLOR_BGRA2BGR)
        except Exception as e:
            print(f"Rendering error: {e}")
            continue

        # Add page indicator
        cv2.putText(doc_img, f"Page {current_page+1}/{total_pages}", (20, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        # Combine camera + document preview
        h_combined = max(frame.shape[0], doc_img.shape[0])
        combined = np.zeros((h_combined, frame.shape[1] + doc_img.shape[1], 3), dtype=np.uint8)
        combined[:frame.shape[0], :frame.shape[1]] = frame
        combined[:doc_img.shape[0], frame.shape[1]:frame.shape[1] + doc_img.shape[1]] = doc_img

        cv2.imshow("Gesture Zoom Assistant", combined)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
