#  Copyright (c) 2023 Harikeshav R
#  All rights reserved.

import os
import random
import string
import time

import cv2
import face_recognition
from PIL import Image


class Biometrics:
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def register_new_face(self):
        webcam = cv2.VideoCapture(0)

        ret, frame = webcam.read()

        while True:
            try:
                ret, frame = webcam.read()
                cv2.imshow("Registering face", frame)

                key = cv2.waitKey(1)

                if key == 32:
                    webcam.release()
                    cv2.destroyAllWindows()

                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    image = Image.fromarray(frame)

                    path = os.path.join(self.data_dir,
                                        ''.join(random.choices(string.ascii_letters + string.digits, k=16)) + '.png')

                    image.save(path)
                    break

            except KeyboardInterrupt:
                break

        return path

    def recognise(self, known_image_path: str):
        known_face = face_recognition.load_image_file(known_image_path)

        for i in range(5):
            webcam = cv2.VideoCapture(0)
            time.sleep(0.5)
            ret, frame = webcam.read()
            webcam.release()

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame)

            unknown_image_path = os.path.join(self.data_dir,
                                              ''.join(
                                                  random.choices(string.ascii_letters + string.digits, k=16)) + '.png')

            image.save(unknown_image_path)

            unknown_face = face_recognition.load_image_file(unknown_image_path)
            os.remove(unknown_image_path)

            try:
                known_face_encoding = face_recognition.face_encodings(known_face)[0]
                unknown_face_encoding = face_recognition.face_encodings(unknown_face)[0]


            except IndexError:
                continue

            known_faces = [known_face_encoding, ]

            results = face_recognition.compare_faces(known_faces, unknown_face_encoding)

            return results[0]

        return False
