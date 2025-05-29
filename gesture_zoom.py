import cv2
import mediapipe as mp
import numpy as np
import fitz  # PyMuPDF
import sys
import time
from flask import Flask, Response, send_file
import os
from docx2pdf import convert
from PIL import Image
import io

app = Flask(__name__)

# Get document path from command-line arguments
doc_path = sys.argv[1]
is_pdf = doc_path.lower().endswith('.pdf')

# Initialize document
if is_pdf:
    doc = fitz.open(doc_path)
    page = doc.load_page(0)
    rect = page.rect
else:
    # Convert Word to PDF first
    pdf_path = os.path.splitext(doc_path)[0] + '.pdf'
    convert(doc_path, pdf_path)
    doc = fitz.open(pdf_path)
    page = doc.load_page(0)
    rect = page.rect

mpHands = mp.solutions.hands
hands = mpHands.Hands(
    static_image_mode=False,
    model_complexity=1,
    min_detection_confidence=0.75,
    min_tracking_confidence=0.75,
    max_num_hands=2)

Draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
zoom_factor = 1.0
current_page = 0

def generate_frames():
    global zoom_factor, current_page
    
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            frame = cv2.flip(frame, 1)
            frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            Process = hands.process(frameRGB)

            landmarkList = []
            if Process.multi_hand_landmarks:
                for handlm in Process.multi_hand_landmarks:
                    for _id, landmarks in enumerate(handlm.landmark):
                        height, width, _ = frame.shape
                        x, y = int(landmarks.x * width), int(landmarks.y * height)
                        landmarkList.append([_id, x, y])
                    Draw.draw_landmarks(frame, handlm, mpHands.HAND_CONNECTIONS)

            if landmarkList:
                # Get thumb (4) and index finger (8) tips
                x_1, y_1 = landmarkList[4][1], landmarkList[4][2]
                x_2, y_2 = landmarkList[8][1], landmarkList[8][2]

                cv2.circle(frame, (x_1, y_1), 7, (0, 255, 0), cv2.FILLED)
                cv2.circle(frame, (x_2, y_2), 7, (0, 255, 0), cv2.FILLED)
                cv2.line(frame, (x_1, y_1), (x_2, y_2), (0, 255, 0), 3)

                # Calculate distance between fingers for zoom
                L = np.linalg.norm([x_2 - x_1, y_2 - y_1])
                zoom_factor = np.interp(L, [15, 220], [0.5, 3.0])

                # Page navigation with palm movement
                wrist_x = landmarkList[0][1]
                palm_base_x = landmarkList[9][1]
                horizontal_movement = palm_base_x - wrist_x

                if abs(horizontal_movement) > 100:  # Threshold for page turn
                    if horizontal_movement > 0 and current_page > 0:  # Swipe right
                        current_page -= 1
                        page = doc.load_page(current_page)
                        time.sleep(0.5)  # Debounce
                    elif horizontal_movement < 0 and current_page < len(doc) - 1:  # Swipe left
                        current_page += 1
                        page = doc.load_page(current_page)
                        time.sleep(0.5)  # Debounce

            # Render document page with zoom
            matrix = fitz.Matrix(zoom_factor, zoom_factor)
            pix = page.get_pixmap(matrix=matrix, colorspace=fitz.csRGB, alpha=True)
            img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 4)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

            # Add page info overlay
            cv2.putText(img, f"Page {current_page + 1}/{len(doc)}", (20, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # Combine camera feed and document preview
            combined = np.zeros((max(frame.shape[0], img.shape[0]), frame.shape[1] + img.shape[1], 3), dtype=np.uint8)
            combined[:frame.shape[0], :frame.shape[1]] = frame
            combined[:img.shape[0], frame.shape[1]:frame.shape[1]+img.shape[1]] = img

            ret, buffer = cv2.imencode('.jpg', combined)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/document')
def get_document():
    if is_pdf:
        return send_file(doc_path, as_attachment=True)
    else:
        return send_file(doc_path, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)