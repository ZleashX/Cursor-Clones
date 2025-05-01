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


def main():
    global lookMonitorIndex
    with mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=False, min_detection_confidence=0.5, min_tracking_confidence=0.5) as face_mesh:
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                continue

            # Mirror image (Optional)
            image = mirrorImage(image)

            # Generate face mesh
            results = face_mesh.process(bgr2rgb(image))

            # Processing Face Landmarks
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:

                    # HEAD TILT ANGLE -----------------------------------
                    yaw = pipelineHeadTiltPose(image, face_landmarks)
                    # Print Mouse Position
                    cv2.putText(image, str(mouse.position), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

            #Hardcode the monitor index based on yaw for now. Change the yaw depend on your monitor setup
            if yaw > 12:
                lookMonitorIndex = 1
            else:
                lookMonitorIndex = 0

            # Show Image
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
    listener = Listener(on_click=on_click)
    listener.start()

    main()
