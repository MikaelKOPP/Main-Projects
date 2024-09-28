import cv2
import os
import numpy as np

# configuration
haar_file = 'haarcascade_frontalface_default.xml'
datasets = 'datasets'
sub_data = 'your_face'
path = os.path.join(datasets, sub_data)

# create directory if it doesn't exist
if not os.path.isdir(path):
    os.makedirs(path)

# define image size
width, height = 130, 100

# initialize face detector and webcam
face_cascade = cv2.CascadeClassifier(haar_file)
webcam = cv2.VideoCapture(0)

# capture 30 images
count = 1
while count < 30:
    _, frame = webcam.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 4)
    
    for (x, y, w, h) in faces:
        # draw rectangle around face
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        
        # extract and resize face region
        face = gray[y:y + h, x:x + w]
        face_resize = cv2.resize(face, (width, height))
        
        # save the captured face
        cv2.imwrite(f'{path}/{count}.png', face_resize)
        count += 1
    
    cv2.imshow('Face Capture', frame)
    
    # break loop on 'Esc' key press
    if cv2.waitKey(10) == 27:
        break

# clean up
webcam.release()
cv2.destroyAllWindows()