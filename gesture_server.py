import cv2
import numpy as np
import mediapipe as mp
import websockets
import asyncio
import json
from collections import deque

# MediaPipe setup
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5)

# State variables
zoom_active = False
drag_active = False
start_point = None
last_command_time = 0
command_cooldown = 1.0  # seconds
trail_points = deque(maxlen=50)

# Gesture thresholds
ZOOM_THRESHOLD = 0.05
SWIPE_THRESHOLD = 50
PINCH_THRESHOLD = 30
SPREAD_THRESHOLD = 80

async def handle_gesture(websocket):
    global zoom_active, drag_active, start_point, last_command_time
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process hand landmarks
            results = hands.process(rgb_frame)
            current_time = asyncio.get_event_loop().time()
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Get key landmarks
                    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                    middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
                    wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
                    
                    # Convert to pixel coordinates
                    tx, ty = int(thumb_tip.x * w), int(thumb_tip.y * h)
                    ix, iy = int(index_tip.x * w), int(index_tip.y * h)
                    mx, my = int(middle_tip.x * w), int(middle_tip.y * h)
                    wx, wy = int(wrist.x * w), int(wrist.y * h)
                    
                    # Calculate distances
                    pinch_distance = np.hypot(ix - tx, iy - ty)
                    spread_distance = np.hypot(ix - mx, iy - my)
                    
                    # Detect pinch (zoom in)
                    if pinch_distance < PINCH_THRESHOLD and current_time - last_command_time > command_cooldown:
                        await websocket.send("zoom_in")
                        last_command_time = current_time
                        cv2.putText(frame, "ZOOM IN", (50, 100), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
                    
                    # Detect spread (zoom out)
                    elif spread_distance > SPREAD_THRESHOLD and current_time - last_command_time > command_cooldown:
                        await websocket.send("zoom_out")
                        last_command_time = current_time
                        cv2.putText(frame, "ZOOM OUT", (50, 100), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
                    
                    # Detect swipe (page navigation)
                    if not drag_active and spread_distance < PINCH_THRESHOLD:
                        drag_active = True
                        start_point = (wx, wy)
                        trail_points.clear()
                    
                    if drag_active:
                        current_point = (wx, wy)
                        trail_points.append(current_point)
                        
                        # Check for swipe release
                        if spread_distance > PINCH_THRESHOLD:
                            drag_active = False
                            if start_point and len(trail_points) > 1:
                                end_point = trail_points[-1]
                                dx = end_point[0] - start_point[0]
                                
                                if dx > SWIPE_THRESHOLD and current_time - last_command_time > command_cooldown:
                                    await websocket.send("next_page")
                                    last_command_time = current_time
                                    cv2.putText(frame, "NEXT PAGE", (50, 100), 
                                               cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
                                elif dx < -SWIPE_THRESHOLD and current_time - last_command_time > command_cooldown:
                                    await websocket.send("prev_page")
                                    last_command_time = current_time
                                    cv2.putText(frame, "PREV PAGE", (50, 100), 
                                               cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
                    
                    # Draw hand skeleton
                    mp_drawing.draw_landmarks(
                        frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                        mp_drawing.DrawingSpec(color=(121, 22, 76), thickness=2, circle_radius=4),
                        mp_drawing.DrawingSpec(color=(250, 44, 250), thickness=2, circle_radius=2))
            
            cv2.imshow('Gesture Controls', frame)
            
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break
            
            await asyncio.sleep(0.01)
            
    finally:
        cap.release()
        cv2.destroyAllWindows()

async def websocket_handler(websocket, path=None):  # Made path optional
    print(f"New connection from {websocket.remote_address}")
    try:
        await handle_gesture(websocket)
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")
    except Exception as e:
        print(f"Error: {e}")

async def main():
    try:
        async with websockets.serve(websocket_handler, "localhost", 8765):
            print("Gesture server started on ws://localhost:8765")
            await asyncio.Future()  # run forever
    except Exception as e:
        print(f"Server error: {e}")

if __name__ == "__main__":
    asyncio.run(main())