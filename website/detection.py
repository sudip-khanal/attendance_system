import datetime
from time import strftime
import cv2
from PIL import Image
from Attendence.settings import BASE_DIR
import os
import sqlite3
import numpy as np
from django.contrib import messages
from .models import User, StudentRecord,Attendance
from django.db import connection
from datetime import date
from datetime import datetime



detector = cv2.CascadeClassifier('website/trainer/haarcascade_frontalface_default.xml')
recognizer = cv2.face.LBPHFaceRecognizer_create()


class FaceRecognition: 
    def faceDetect(self, Entry1):
        
        cam = cv2.VideoCapture(0)
        cam.set(3, 640) # set video width
        cam.set(4, 480) # set video height
        face_detector=cv2.CascadeClassifier('website/trainer/haarcascade_frontalface_default.xml')

        user_id = Entry1

        count = 0

        while(True):
            ret, img = cam.read()
            #img = cv2.flip(img, -1) # flip video image vertically
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_detector.detectMultiScale(gray, 1.3, 5)

            for (x,y,w,h) in faces:
                cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)     
                count += 1

                # Save the captured image into the datasets folder
                cv2.imwrite("website/dataset/User_id." + str(user_id) + '.' + str(count) + ".jpg", gray[y:y+h,x:x+w])
                cv2.imshow('image', img)

            k = cv2.waitKey(100) & 0xff # Press 'ESC' for exiting video
            if k == 27:
                break
            elif count >= 50: # Take 50 face sample and stop video
                break
        print("\n [INFO] Exiting Program and cleanup stuff")
        cam.release()
        cv2.destroyAllWindows()
    


    def trainFace(self):
        data_dir=('website/dataset')
        path=[os.path.join(data_dir,file) for file in os.listdir(data_dir)]
        
        faces=[]
        ids=[]

        for image in path:
            img=Image.open(image).convert('L') # conver in gray scale 
            imageNp = np.array(img,'uint8')
            id =int(os.path.split(image)[1].split('.')[1])
            print("image",id)
            faces.append(imageNp)
            ids.append(id)

            cv2.imshow("Training images with data ....",imageNp)
            cv2.waitKey(1)==13
        
        ids=np.array(ids)
           #=================Train Classifier and save data=============#
        clf= cv2.face.LBPHFaceRecognizer_create()
        clf.train(faces,ids)
        clf.write("website/trainer/classifier.xml")
        cv2.destroyAllWindows()
        print("Result","Training Dataset With Image Complated!")

     ##mark attendance
    def mark_attendance(self,fname,lname,faculty,sem,gender,s_uid,rollNo):
        now = datetime.now()
        status = 'Present'
        # date = now.strftime("%d/%m/%Y")
        connection = sqlite3.connect('db.sqlite3')
        dateNow = date.today()
        timenow = strftime("%H:%M:%S")
        # Create a cursor object
        cursor = connection.cursor()
    
        if Attendance.objects.filter(date=dateNow , user_id=s_uid).count() != 0:
            print("Attendance already recorded.")
        else:
            query = "INSERT INTO website_attendance(user_id, first_name, last_name, roll_num, gender, faculty, sem, ststus, date,time) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?,?)"
            values = (s_uid, fname, lname, rollNo, gender, faculty, sem, status, dateNow,timenow)
            cursor.execute(query, values)
            connection.commit()
            connection.close()
            print("Attendance Taken Successfully..")

         

    def recognizeFace(self):
        def draw_boundray(img,classifier,scaleFactor,minNeighbors,color,text,clf):
            gray_image=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            featuers=classifier.detectMultiScale(gray_image,scaleFactor,minNeighbors)

            coord=[]
            
            for (x,y,w,h) in featuers:
                cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),3)
                #iniciate id counter
                id,predict=clf.predict(gray_image[y:y+h,x:x+w])
                #print(id)
                confidence=int((100*(1-predict/300)))
                # Create a connection object
                conn = sqlite3.connect('db.sqlite3')

                # Create a cursor object
                cursor = conn.cursor() 
                
                cursor.execute("SELECT first_name FROM website_studentrecord WHERE user_id =" + str(id))
                fname=cursor.fetchone()
                fname = "+".join(fname)                    

                cursor.execute("SELECT last_name FROM website_studentrecord WHERE user_id=" + str(id))
                lname =cursor.fetchone()
                lname = "+".join(lname) 

                cursor.execute("SELECT my_faculty FROM website_studentrecord WHERE user_id="+ str(id))
                faculty=cursor.fetchone()
                faculty = "+".join(faculty) 

                cursor.execute("SELECT sem FROM website_studentrecord WHERE user_id  = "+ str(id))
                sem=cursor.fetchone()
                sem = "+".join(sem) 

                cursor.execute("SELECT gender FROM website_studentrecord WHERE user_id ="+ str(id))
                gender=cursor.fetchone()
                gender = "+".join(gender)

                cursor.execute("SELECT user_id FROM website_studentrecord WHERE user_id  = "+ str(id))
                s_uid=cursor.fetchone()
                s_uid = "+".join(s_uid)

                cursor.execute("SELECT roll_num FROM website_studentrecord WHERE user_id  = "+ str(id))
                rollNo=cursor.fetchone()
                rollNo = "+".join(rollNo)
                
                if confidence > 77:
                    
                    cv2.putText(img,f"User Id:{s_uid}",(x,y-120),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,0,255),1)
                    cv2.putText(img,f"Name:{fname} {lname}",(x,y-100),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,0,255),1)
                    cv2.putText(img,f"Faculty:{faculty}",(x,y-80),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,0,255),1)
                    cv2.putText(img,f"Semester:{sem}",(x,y-60),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,0,255),1)
                    cv2.putText(img,f"Gender:{gender}",(x,y-40),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,0,255),1)
                    cv2.putText(img,f"Roll_No:{rollNo}",(x,y-20),cv2.FONT_HERSHEY_COMPLEX,0.8,(0,0,255),1)
                    
                      # Call mark_attendance method when face is recognized
                    if self.mark_attendance:
                        self.mark_attendance(fname, lname, faculty, sem, gender, s_uid, rollNo)
                        self.mark_attendance = False
                else:
                    cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),3)
                    cv2.putText(img,"Unknown Face",(x,y-5),cv2.FONT_HERSHEY_COMPLEX,0.8,(255,255,0),3)    
                coord=[x,y,w,y]
            return coord 
        
        def recognize(img,clf,faceCascade):
            coord = draw_boundray(img,faceCascade,1.1,10,(255,25,255),"Face",clf)
            return img
        
        faceCascade=cv2.CascadeClassifier("website/trainer/haarcascade_frontalface_default.xml")
        clf=cv2.face.LBPHFaceRecognizer_create()
        clf.read("website/trainer/classifier.xml")

        videoCap=cv2.VideoCapture(0)

        while True:
            ret,img=videoCap.read()
            img=recognize(img,clf,faceCascade)
            cv2.imshow("Face Recognition",img)

            if cv2.waitKey(1) == 13:
                break
        videoCap.release()
        cv2.destroyAllWindows()



        
          

   





