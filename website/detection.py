import datetime
from time import strftime
import cv2
from PIL import Image
from Attendence.settings import BASE_DIR
import os
import sqlite3
import numpy as np
from django.contrib import messages
from .models import User, Attendance
from django.db import connection
from datetime import date
from datetime import datetime


detector = cv2.CascadeClassifier(
    'website/trainer/haarcascade_frontalface_default.xml')
recognizer = cv2.face.LBPHFaceRecognizer_create()


class FaceRecognition:
    def faceDetect(self, Entry1):

        cam = cv2.VideoCapture(0)
        cam.set(3, 640)  # set video width
        cam.set(4, 480)  # set video height
        face_detector = cv2.CascadeClassifier(
            'website/trainer/haarcascade_frontalface_default.xml')

        user_id = Entry1

        count = 0

        while (True):
            ret, img = cam.read()
            # img = cv2.flip(img, -1) # flip video image vertically
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_detector.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
                count += 1

                # Save the captured image into the datasets folder
                cv2.imwrite("website/dataset/User_id."+str(user_id) +
                            '.'+str(count) + ".jpg", gray[y:y+h, x:x+w])
                cv2.imshow(
                    ' system is taking images please wait few seconds here', img)

            k = cv2.waitKey(100) & 0xff  # Press 'ESC' for exiting video
            if k == 27:
                break
            elif count >= 50:  # Take 50 face sample and stop video
                break
        print("\n [INFO] Exiting Program and cleanup stuff")
        cam.release()
        cv2.destroyAllWindows()

    def trainFace(self):
        data_dir = ('website/dataset')
        path = [os.path.join(data_dir, file) for file in os.listdir(data_dir)]

        faces = []
        ids = []

        for image in path:
            img = Image.open(image).convert('L')  # conver in gray scale
            imageNp = np.array(img, 'uint8')
            id = int(os.path.split(image)[1].split('.')[1])

            print("image", id)
            faces.append(imageNp)
            ids.append(id)

            cv2.imshow("Training images with data ....", imageNp)
            cv2.waitKey(1) == 13

        ids = np.array(ids)
        # =================Train Classifier and save data=============#
        clf = cv2.face.LBPHFaceRecognizer_create()
        clf.train(faces, ids)
        clf.write("website/trainer/classifier.xml")
        cv2.destroyAllWindows()
        print("Result", "Training Dataset With Image Complated!")

     # mark attendance
    def mark_attendance(self, fname, lname, rollNo, gender, faculty, sem, uname, usertype):
        now = datetime.now()
        status = 'Present'
        # date = now.strftime("%d/%m/%Y")
        connection = sqlite3.connect('db.sqlite3')
        dateNow = date.today()
        timenow = strftime("%H:%M:%S")
        # Create a cursor object
        cursor = connection.cursor()

        if Attendance.objects.filter(date=dateNow, username=uname).count() != 0:
            print(" Your Attendance already recorded.")
        else:
            query = "INSERT INTO website_attendance(first_name, last_name, roll_num, gender, faculty, sem,date,time,ststus,username,usertype) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            values = (fname, lname, rollNo, gender, faculty, sem,
                      dateNow, timenow, status, uname, usertype)
            cursor.execute(query, values)
            connection.commit()
            connection.close()
            # messages.success("Attendance Taken Successfully..")

    def recognizeFace(self):
        def draw_boundray(img, classifier, scaleFactor, minNeighbors, color, text, clf):
            gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            featuers = classifier.detectMultiScale(
                gray_image, scaleFactor, minNeighbors)

            coord = []

            for (x, y, w, h) in featuers:
                cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 3)
                # iniciate id counter
                id, predict = clf.predict(gray_image[y:y+h, x:x+w])
                # print(id)
                confidence = int((100*(1-predict/300)))
                # Create a connection object
                conn = sqlite3.connect('db.sqlite3')

                # Create a cursor object
                cursor = conn.cursor()

                cursor.execute(
                    "SELECT first_name FROM website_user WHERE id =" + str(id))
                fname = cursor.fetchone()
                fname = "+".join(fname) if fname else ""

                cursor.execute(
                    "SELECT last_name FROM website_user WHERE id=" + str(id))
                lname = cursor.fetchone()
                lname = "+".join(lname) if lname else ""

                cursor.execute(
                    "SELECT faculty FROM website_user WHERE id=" + str(id))
                faculty = cursor.fetchone()
                faculty = "+".join(faculty) if faculty else ""

                cursor.execute(
                    "SELECT semester FROM website_user WHERE id  = " + str(id))
                sem = cursor.fetchone()
                sem = "+".join(sem) if sem else ""

                cursor.execute(
                    "SELECT gender FROM website_user WHERE id =" + str(id))
                gender = cursor.fetchone()
                gender = "+".join(gender) if gender else ""

                cursor.execute(
                    "SELECT username FROM website_user WHERE id =" + str(id))
                uname = cursor.fetchone()
                uname = "+".join(uname) if uname else ""

                cursor.execute(
                    "SELECT roll_num FROM website_user WHERE id  = " + str(id))
                rollNo = cursor.fetchone()
                rollNo = "+".join(rollNo) if rollNo else ""

                cursor.execute(
                    "SELECT userType FROM website_user WHERE id  = " + str(id))
                usertype = cursor.fetchone()
                usertype = "+".join(usertype) if usertype else ""

                if confidence > 77:
                    cv2.putText(
                        img, f"You Are:{usertype}", (x, y-120), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 0, 255), 1)
                    cv2.putText(
                        img, f"usrname:{uname}", (x, y-100), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 0, 255), 1)
                    cv2.putText(img, f"Name:{fname} {lname}", (x, y-80),
                                cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 0, 255), 1)
                    cv2.putText(
                        img, f"Faculty:{faculty}", (x, y-60), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 0, 255), 1)
                    cv2.putText(
                        img, f"Semester:{sem}", (x, y-40), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 0, 255), 1)
                    cv2.putText(
                        img, f"Gender:{gender}", (x, y-20), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 0, 255), 1)
                    cv2.putText(
                        img, f"Roll_No:{rollNo}", (x, y-0), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 0, 255), 1)

                    # Call mark_attendance method when face is recognized
                    if self.mark_attendance:
                        self.mark_attendance(
                            fname, lname, rollNo, gender, faculty, sem, uname, usertype)
                        self.mark_attendance = False
                else:
                    cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 3)
                    cv2.putText(img, "Unknown Face", (x, y-5),
                                cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 255, 0), 3)
                coord = [x, y, w, y]
            return coord

        def recognize(img, clf, faceCascade):
            coord = draw_boundray(img, faceCascade, 1.1,
                                  10, (255, 25, 255), "Face", clf)
            return img

        faceCascade = cv2.CascadeClassifier(
            "website/trainer/haarcascade_frontalface_default.xml")
        clf = cv2.face.LBPHFaceRecognizer_create()
        clf.read("website/trainer/classifier.xml")

        videoCap = cv2.VideoCapture(0)

        while True:
            ret, img = videoCap.read()
            img = recognize(img, clf, faceCascade)
            cv2.imshow("Face Recognition", img)

            if cv2.waitKey(1) == 13:
                break
        videoCap.release()
        cv2.destroyAllWindows()
