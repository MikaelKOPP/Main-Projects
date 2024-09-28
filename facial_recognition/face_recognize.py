'''
VIKTIG: create_data.py må først kjøres, for å opprette bilder som kan brukes for å smamnelikne med haar cascade filen.
'''

import cv2
import sys
import numpy as np
import os

# configuration
size = 4
haar_file = 'haarcascade_frontalface_default.xml'
datasets = 'datasets'

# part 1: create and train the recognizer
print('Leter etter fjeset ditt..')

# prepare data structures
images, labels, names, id = [], [], {}, 0

# load training data
for (subdirs, dirs, files) in os.walk(datasets):
    for subdir in dirs:
        names[id] = subdir
        subjectpath = os.path.join(datasets, subdir)
        for filename in os.listdir(subjectpath):
            path = os.path.join(subjectpath, filename)
            label = id
            images.append(cv2.imread(path, 0))
            labels.append(int(label))
        id += 1

# set image dimensions
width, height = 130, 100

# convert lists to numpy arrays
images, labels = [np.array(lis) for lis in [images, labels]]

# create and train the modle
model = cv2.face.LBPHFaceRecognizer_create()
model.train(images, labels)

# part 2: use the trained recognizer on camera stream
face_cascade = cv2.CascadeClassifier(haar_file)
webcam = cv2.VideoCapture(0)

while True:
    # read frame from webcam
    _, frame = webcam.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # detect faces
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    
    for (x, y, w, h) in faces:
        # draw rectangle around the face
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        
        # extract and resize face region
        face = gray[y:y + h, x:x + w]
        face_resize = cv2.resize(face, (width, height))
        
        # try to recognize the face
        prediction = model.predict(face_resize)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
        
        if prediction[1] < 500:
            # recognized face
            cv2.putText(frame, f'{names[prediction[0]]} - {prediction[1]:.0f}', 
                        (x-10, y-10), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0)) # custom font
        else:
            # unrecognized face
            cv2.putText(frame, 'not recognized', 
                        (x-10, y-10), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0)) 
    
    # display the resulting frame
    cv2.imshow('Trykk ESC for å gå ut...', frame)
    
    # break loop on 'Esc' kye press
    if cv2.waitKey(10) == 27:
        break

# clean up
webcam.release()
cv2.destroyAllWindows()