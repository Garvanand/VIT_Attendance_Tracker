import tkinter as tk
from tkinter import *
import os, cv2
import tkinter
import shutil
import csv
import numpy as np
from PIL import ImageTk, Image
import pandas as pd
import datetime
import time
import tkinter.font as font
import pyttsx3

haarcasecade_path = "haarcascade_frontalface_default.xml"
trainimagelabel_path = "./TrainingImageLabel/Trainner.yml"
trainimage_path = "TrainingImage"
studentdetail_path = "./StudentDetails/studentdetails.csv"
attendance_path = "Attendance"

class GradientBackground:
    def __init__(self, master, colors=None):
        self.master = master
        self.colors = colors or [
            "#667EEA",
            "#764BA2",
            "#4A90E2", 
        ]
        self.canvas = tk.Canvas(master, highlightthickness=0)
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        self.gradient_rectangles = []
        self.create_gradient_background()
        self.animate_gradient()

    def create_gradient_background(self):
        width = self.master.winfo_screenwidth()
        height = self.master.winfo_screenheight()
        
        import random
        for i in range(20):
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            x2 = x1 + random.randint(50, 200)
            y2 = y1 + random.randint(50, 200)
            color = random.choice(self.colors)
            rect = self.canvas.create_rectangle(
                x1, y1, x2, y2, 
                fill=color, 
                outline='',
                stipple='gray50'
            )
            self.gradient_rectangles.append((rect, x1, y1, x2, y2))

    def animate_gradient(self):
        import random
        def update():
            width = self.master.winfo_screenwidth()
            height = self.master.winfo_screenheight()
            
            for i, (rect, x1, y1, x2, y2) in enumerate(self.gradient_rectangles):
                dx = random.randint(-3, 3)
                dy = random.randint(-3, 3)
                
                new_x1 = (x1 + dx) % width
                new_y1 = (y1 + dy) % height
                new_x2 = new_x1 + (x2 - x1)
                new_y2 = new_y1 + (y2 - y1)
                
                self.canvas.move(rect, dx, dy)
                self.gradient_rectangles[i] = (rect, new_x1, new_y1, new_x2, new_y2)
            
            self.master.after(50, update)
        
        update()

class AnimatedButton(tk.Button):
    def __init__(self, master, **kwargs):
        self.hover_color = kwargs.pop('hover_color', '#4A90E2')
        self.original_bg = kwargs.get('bg', '#667EEA')
        self.original_fg = kwargs.get('fg', 'white')
        
        super().__init__(master, **kwargs)
        
        self.configure(
            relief=tk.FLAT,
            borderwidth=0,
            font=('Segoe UI', 12, 'bold'),
            activebackground=self.hover_color
        )
        
        # Binding hover and click effects
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        self.bind('<Button-1>', self.on_click)
        self.bind('<ButtonRelease-1>', self.on_release)

    def on_enter(self, e):
        self.configure(
            bg=self.hover_color, 
            cursor='hand2'
        )
        self.lift()

    def on_leave(self, e):
        self.configure(
            bg=self.original_bg, 
            cursor='arrow'
        )

    def on_click(self, e):
        self.configure(
            relief=tk.SUNKEN,
            bg=self.hover_color
        )

    def on_release(self, e):
        self.configure(
            relief=tk.FLAT,
            bg=self.original_bg
        )

def text_to_speech(user_text):
    engine = pyttsx3.init()
    engine.say(user_text)
    engine.runAndWait()

def subjectChoose(text_to_speech):
    def FillAttendance():
        sub = tx.get()
        now = time.time()
        future = now + 20
        if sub == "":
            t = "Please enter the subject name!!!"
            text_to_speech(t)
            return

        recognizer = cv2.face.LBPHFaceRecognizer_create()
        try:
            recognizer.read(trainimagelabel_path)
        except:
            e = "Model not found, please train the model"
            Notifica.configure(
                text=e,
                bg="#E74C3C",
                fg="white",
                width=33,
                font=("Segoe UI", 15, "bold"),
            )
            Notifica.place(x=20, y=250)
            text_to_speech(e)
            return

        facecasCade = cv2.CascadeClassifier(haarcasecade_path)
        df = pd.read_csv(studentdetail_path)
        cam = cv2.VideoCapture(0)
        font = cv2.FONT_HERSHEY_SIMPLEX
        col_names = ["Enrollment", "Name"]
        attendance = pd.DataFrame(columns=col_names)

        while True:
            _, im = cam.read()
            gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
            faces = facecasCade.detectMultiScale(gray, 1.2, 5)
            for (x, y, w, h) in faces:
                global Id
                Id, conf = recognizer.predict(gray[y:y + h, x:x + w])
                if conf < 70:
                    Subject = tx.get()
                    ts = time.time()
                    date = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
                    timeStamp = datetime.datetime.fromtimestamp(ts).strftime("%H:%M:%S")
                    aa = df.loc[df["Enrollment"] == Id]["Name"].values
                    tt = str(Id) + "-" + aa
                    attendance.loc[len(attendance)] = [Id, aa]
                    cv2.rectangle(im, (x, y), (x + w, y + h), (0, 260, 0), 4)
                    cv2.putText(im, str(tt), (x + h, y), font, 1, (255, 255, 0), 4)
                else:
                    Id = "Unknown"
                    tt = str(Id)
                    cv2.rectangle(im, (x, y), (x + w, y + h), (0, 25, 255), 7)
                    cv2.putText(im, str(tt), (x + h, y), font, 1, (0, 25, 255), 4)

            if time.time() > future:
                break

            attendance = attendance.drop_duplicates(["Enrollment"], keep="first")
            cv2.imshow("Filling Attendance...", im)
            key = cv2.waitKey(30) & 0xFF
            if key == 27:
                break

        ts = time.time()
        attendance[date] = 1
        date = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
        path = os.path.join(attendance_path, Subject)

        if not os.path.exists(path):
            os.makedirs(path)

        fileName = f"{path}/{Subject}_{date}.csv"
        attendance = attendance.drop_duplicates(["Enrollment"], keep="first")
        attendance.to_csv(fileName, index=False)

        m = f"Attendance Filled Successfully for {Subject}"
        Notifica.configure(
            text=m,
            bg="#2ECC71",
            fg="white",
            width=33,
            relief=tk.RIDGE,
            bd=5,
            font=("Segoe UI", 15, "bold"),
        )
        text_to_speech(m)
        Notifica.place(x=20, y=250)

        cam.release()
        cv2.destroyAllWindows()
    subject = Tk()
    subject.title("Take Attendance")
    subject.geometry("580x420")
    subject.resizable(0, 0)
    
    gradient_bg = GradientBackground(subject)

    main_frame = tk.Frame(subject, bg='white')
    main_frame.place(relx=0.1, rely=0.1, relwidth=0.8, relheight=0.8)

    title_label = tk.Label(
        main_frame, 
        text="Take Attendance", 
        font=('Segoe UI', 24, 'bold'),
        fg="#2D3748",
        bg='white'
    )
    title_label.pack(pady=(30, 20))

    Notifica = tk.Label(
        main_frame,
        text="",
        bg="#2ECC71",
        fg="white",
        width=33,
        height=2,
        font=("Segoe UI", 15, "bold"),
    )
    Notifica.pack(pady=10)

    input_frame = tk.Frame(main_frame, bg='white')
    input_frame.pack(padx=50, fill=tk.X)

    sub_label = tk.Label(
        input_frame,
        text="Enter Subject",
        font=('Segoe UI', 12),
        fg="#2D3748",
        bg='white'
    )
    sub_label.pack(pady=(10, 5), anchor='w')

    tx = tk.Entry(
        input_frame,
        width=30,
        font=('Segoe UI', 14),
        relief=tk.FLAT,
        bg="#F4F6F9"
    )
    tx.pack(pady=(0, 10), ipady=5)

    btn_frame = tk.Frame(main_frame, bg='white')
    btn_frame.pack(pady=20)

    def Attf():
        sub = tx.get()
        if sub == "":
            t = "Please enter the subject name!!!"
            text_to_speech(t)
        else:
            subject_path = f"Attendance/{sub}"
            if os.path.exists(subject_path):
                os.startfile(subject_path)
            else:
                t = f"No attendance folder found for {sub}"
                text_to_speech(t)

    fill_a = AnimatedButton(
        btn_frame, 
        text="Fill Attendance",
        command=FillAttendance,
        bg="#667EEA",
        fg='white',
        width=20,
        height=2,
        hover_color="#5A67D8"
    )
    fill_a.pack(side=tk.LEFT, padx=10)

    attf = AnimatedButton(
        btn_frame, 
        text="Check Sheets",
        command=Attf,
        bg="#764BA2",
        fg='white',
        width=20,
        height=2,
        hover_color="#5D3FD3"
    )
    attf.pack(side=tk.LEFT, padx=10)

    subject.mainloop()

if __name__ == "__main__":
    subjectChoose(text_to_speech)