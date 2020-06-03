import cv2
from mtcnn import MTCNN
from PIL import Image
import numpy as np
import argparse

# n -> fps count
# F -> desired framerate
# i -> counter value for naming filename
n = 0
F = 30
i = 0
captureOnlyThisFrame = [1,10,20]
required_size = (224,224)

# Command Line arguments
parser = argparse.ArgumentParser(description="Tools for gathering training and testing data for halo")
parser.add_argument("person", help="Name of the person who is captured")
parser.add_argument("nickname", help="Nickname of the person, for naming file")
parser.add_argument("--train", action="store_true", help="Use this to save this image as training data")
parser.add_argument("--test", action="store_true", help="Use this to save this image as testing data")
args = parser.parse_args()

if args.train:
    location = 'dataset/train'
elif args.test:
    location = 'dataset/test'
elif args.train and args.test:
    print("Please define one of them train or test!")
else:
    location = 'dataset/train'


detector = MTCNN()

# Using webcam
video = cv2.VideoCapture(0)

if not video.isOpened():
    print('Error opening the camera')

while True:
    # Open the camera
    ret, frame = video.read()
    
    if n == F:
        n = 0

    n += 1
    i += 1
    if n in captureOnlyThisFrame:
        # Resize the frame size and convert it to RGB Color
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = frame[:, :, ::-1]

        # Detect the face from rgb input
        result = detector.detect_faces(rgb_small_frame)

        if result:
            bounding_box = result[0]['box']
            keypoints = result[0]['keypoints']
            x, y, width, height = bounding_box
            
            # Save and resize image 
            face_frame = frame[y:y+height, x:x+width].copy()
            try:
                face_image = Image.fromarray(face_frame)
            except ValueError:
                continue
            face_image = face_image.resize(required_size)
            face_array = np.asarray(face_image)
            filename = location + '/' + args.person + '/' + args.nickname + str(i) + '.jpg'
            try:
                cv2.imwrite(filename, face_array)
            except AssertionError as err:
                print("Cannot write image: " + err)                    
            print("Writing {} into dataset".format(filename))

            cv2.rectangle(frame,
                        (x, y),
                        (x+width, y + height),
                        (0,155,255),
                        2)

            cv2.circle(frame,(keypoints['left_eye']), 2, (0,155,255), 2)
            cv2.circle(frame,(keypoints['right_eye']), 2, (0,155,255), 2)
            cv2.circle(frame,(keypoints['nose']), 2, (0,155,255), 2)
            cv2.circle(frame,(keypoints['mouth_left']), 2, (0,155,255), 2)
            cv2.circle(frame,(keypoints['mouth_right']), 2, (0,155,255), 2)

    cv2.imshow('Video MTCNN', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video.release()
cv2.destroyAllWindows()
