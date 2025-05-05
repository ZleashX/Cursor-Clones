import cv2
import mediapipe as mp
import numpy as np
from pynput.mouse import Controller, Listener, Button
from monitor import MonitorManager

from utils import bgr2rgb, mirrorImage
from head_orientation import pipelineHeadTiltPose

def on_click(x, y, button, pressed):
    global lookMonitorIndex
    # button.x2 is the top side button on the mouse
    if button == Button.x2 and pressed:
        monitorManager.switchMonitor(lookMonitorIndex, mouse)

def on_move(x, y):
    monitorManager.isCursorCrossMonitor(mouse)

def calibrate_monitors(face_mesh, cap, monitorManager):
    num_monitors = monitorManager.total_monitors
    monitor_yaws = []

    for monitor_idx in range(num_monitors):
        print(f"Calibrating monitor {monitor_idx}. Look at it and press 'c' when ready.")
        while True:
            success, image = cap.read()
            if not success:
                continue
            image = mirrorImage(image)
            cv2.putText(image, f"Look at monitor {monitor_idx} and press 'c'", (50, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow('Calibration', image)
            key = cv2.waitKey(1)
            if key == ord('c'):
                cv2.destroyWindow('Calibration')
                break

        samples = []
        for _ in range(30):
            success, image = cap.read()
            if not success:
                continue
            image = mirrorImage(image)
            results = face_mesh.process(bgr2rgb(image))
            if results.multi_face_landmarks:
                face_landmarks = results.multi_face_landmarks[0]
                yaw = pipelineHeadTiltPose(image, face_landmarks)
                samples.append(yaw)
            cv2.waitKey(1)
        
        avg_yaw = np.mean(samples) if samples else 0.0
        monitor_yaws.append(avg_yaw)
        print(f"Monitor {monitor_idx} avg yaw: {avg_yaw:.2f}")

    return monitor_yaws

def compute_thresholds(monitor_yaws):
    thresholds = []
    for i in range(len(monitor_yaws)-1):
        thresholds.append((monitor_yaws[i] + monitor_yaws[i+1]) / 2)
    return thresholds

def main():
    global lookMonitorIndex
    with mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=False, min_detection_confidence=0.5, min_tracking_confidence=0.5) as face_mesh:

        # Calibration
        monitor_yaws = calibrate_monitors(face_mesh, cap, monitorManager)
        thresholds = compute_thresholds(monitor_yaws)

        # Main loop
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                continue

            image = mirrorImage(image)
            results = face_mesh.process(bgr2rgb(image))

            yaw = 0  # Default yaw value
            if results.multi_face_landmarks:
                face_landmarks = results.multi_face_landmarks[0]
                yaw = pipelineHeadTiltPose(image, face_landmarks)

                # Determine monitor based on thresholds
                lookMonitorIndex = 0
                for i, thresh in enumerate(thresholds):
                    if yaw >= thresh:
                        lookMonitorIndex = i + 1
                    else:
                        break

            # Display info
            cv2.putText(image, f"Yaw: {yaw:.2f}, Monitor: {lookMonitorIndex}", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(image, f"Mouse Position: {mouse.position}", (10, 60), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(image, f"Active Monitor: {monitorManager.active_monitor_index}", (10, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            cv2.imshow('Face Mesh', image)
            if cv2.waitKey(1) == ord('q'):
                break
    cap.release()

if __name__ == "__main__":
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    mp_face_mesh = mp.solutions.face_mesh

    cap = cv2.VideoCapture(0)

    mouse = Controller()
    monitorManager = MonitorManager()
    lookMonitorIndex = 0
    listener = Listener(on_click=on_click, on_move=on_move)
    listener.start()

    main()
