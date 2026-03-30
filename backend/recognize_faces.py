import cv2
import face_recognition
import os
import requests

dataset_dir = "known_faces"
known_encodings = []
known_names = []

# Load all images from known_faces
for file in os.listdir(dataset_dir):
    if file.endswith((".jpg", ".png")):
        image = face_recognition.load_image_file(os.path.join(dataset_dir, file))
        encoding = face_recognition.face_encodings(image)
        if encoding:
            known_encodings.append(encoding[0])
            known_names.append(os.path.splitext(file)[0])

cap = cv2.VideoCapture(0)
print("Press 'q' to quit.")

recognized_names = set()  # avoid sending duplicate requests

while True:
    ret, frame = cap.read()
    if not ret:
        break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_encodings, face_encoding)
        name = "Unknown"

        if True in matches:
            match_index = matches.index(True)
            name = known_names[match_index]

            # Send name to backend if not already sent
            if name not in recognized_names:
                try:
                    requests.post("http://127.0.0.1:5000/mark_attendance", json={"name": name})
                    recognized_names.add(name)
                    print(f"Marked attendance for {name}")
                except:
                    print("Failed to connect to backend")

        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(frame, name, (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    cv2.imshow("Face Recognition", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
