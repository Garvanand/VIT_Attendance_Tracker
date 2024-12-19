import tkinter as tk
from tkinter import ttk, Toplevel, messagebox, Canvas
import os
import cv2
import shutil
import csv
import numpy as np
from PIL import ImageTk, Image
import pandas as pd
import datetime
import time
import pyttsx3
import threading
import random
from tkinter import Canvas, PhotoImage
from PIL import Image, ImageTk
import show_attendance
import takeImage
import trainImage
import automaticAttedance

class GradientBackground:
    def __init__(self, master, colors=None):
        self.master = master
        self.colors = colors or [
            "#667EEA",
            "#764BA2",
            "#4A90E2",
        ]
        self.canvas = Canvas(master, highlightthickness=0)
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        self.gradient_rectangles = []
        self.create_gradient_background()
        self.animate_gradient()

    def create_gradient_background(self):
        width = self.master.winfo_screenwidth()
        height = self.master.winfo_screenheight()
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
        # Extract custom parameters
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

class ModernAttendanceSystem:
    def __init__(self, master):
        self.master = master
        master.title("VIT ATTENDANCE TRACKER")
        master.geometry("1600x900")
        
        self.COLORS = {
            "background": "#F4F6F9",
            "primary": "#667EEA",
            "secondary": "#764BA2",
            "accent": "#4A90E2",
            "text_dark": "#2D3748",
            "text_light": "#FFFFFF",
            "hover": "#5A67D8"
        }
        
        self.gradient_bg = GradientBackground(master)
        
        self.create_blur_overlay()
        self.engine = pyttsx3.init()
        self.create_header()
        self.create_navigation_panel()
        
        self.animate_welcome()
    
    def create_blur_overlay(self):
        self.blur_frame = tk.Frame(
            self.master, 
            bg='white', 
            bd=0
        )
        self.blur_frame.place(
            relx=0.1, 
            rely=0.1, 
            relwidth=0.8, 
            relheight=0.8
        )
        self.blur_frame.lower()
    
    def create_header(self):
        header_frame = tk.Frame(
            self.master, 
            bg=self.COLORS["text_light"], 
            relief=tk.RAISED,
            bd=0
        )
        header_frame.place(
            relx=0.1, 
            rely=0.05, 
            relwidth=0.8, 
            relheight=0.1
        )
        header_frame.lift()
        
        logo_canvas = Canvas(
    header_frame,
    bg=self.COLORS["text_light"],
    highlightthickness=0
)


        logo_canvas = Canvas(
            header_frame,
            bg=self.COLORS["text_light"],
            highlightthickness=0
        )
        logo_canvas.place(relx=0.02, rely=0.1, relwidth=0.08, relheight=0.8)

        def resize_image(event):
            canvas_width = event.width
            canvas_height = event.height

            pil_image = Image.open("logo.png")
            resized_image = pil_image.resize((canvas_width, canvas_height), Image.Resampling.LANCZOS)
            logo_image = ImageTk.PhotoImage(resized_image)

            logo_canvas.create_image(0, 0, anchor="nw", image=logo_image)
            logo_canvas.image = logo_image

        logo_canvas.bind("<Configure>", resize_image)

        title_label = tk.Label(
            header_frame, 
            text="VIT ATTENDANCE TRACKER", 
            font=('Segoe UI', 18, 'bold'),
            fg=self.COLORS["text_dark"],
            bg=self.COLORS["text_light"]
        )
        title_label.place(relx=0.15, rely=0.2)
        
        self.time_label = tk.Label(
            header_frame, 
            font=('Segoe UI', 12),
            fg=self.COLORS["text_dark"],
            bg=self.COLORS["text_light"]
        )
        self.time_label.place(relx=0.8, rely=0.3)
        self.update_time()
    
    def update_time(self):
        current_time = datetime.datetime.now().strftime("%I:%M %p\n%B %d, %Y")
        self.time_label.config(text=current_time)
        self.master.after(1000, self.update_time)
    
    def create_navigation_panel(self):
        nav_frame = tk.Frame(
            self.master, 
            bg='white'
        )
        nav_frame.place(
            relx=0.1, 
            rely=0.2, 
            relwidth=0.8, 
            relheight=0.7
        )
        
        button_configs = [
            {
                "text": "Register Student", 
                "command": self.take_image_ui,
                "bg": self.COLORS["primary"],
                "hover_color": self.COLORS["hover"],
                "icon": "👥"
            },
            {
                "text": "Take Attendance", 
                "command": self.automatic_attendance,
                "bg": self.COLORS["secondary"],
                "hover_color": "#5D3FD3",
                "icon": "📋"
            },
            {
                "text": "View Attendance", 
                "command": self.view_attendance,
                "bg": self.COLORS["accent"],
                "hover_color": "#3A7CA5",
                "icon": "📊"
            },
            {
                "text": "Exit", 
                "command": self.master.quit,
                "bg": "#E74C3C",
                "hover_color": "#C0392B",
                "icon": "❌"
            }
        ]
        
        for i, config in enumerate(button_configs):
            row = i // 2
            col = i % 2
            
            card_frame = tk.Frame(
                nav_frame, 
                bg='white', 
                relief=tk.RAISED,
                bd=1
            )
            card_frame.grid(
                row=row, 
                column=col, 
                padx=20, 
                pady=20, 
                sticky='nsew'
            )
            
            icon_label = tk.Label(
                card_frame, 
                text=config['icon'], 
                font=('Segoe UI', 40),
                bg='white'
            )
            icon_label.pack(pady=(20, 10))
            
            btn = AnimatedButton(
                card_frame, 
                text=config['text'], 
                command=config['command'],
                bg=config['bg'],
                fg='white',
                width=20,
                height=2,
                hover_color=config['hover_color']
            )
            btn.pack(pady=(0, 20))
        
        nav_frame.grid_columnconfigure((0,1), weight=1)
        nav_frame.grid_rowconfigure((0,1), weight=1)
    
    def animate_welcome(self):
        welcome_frame = tk.Frame(
            self.master, 
            bg='#000000'
        )
        welcome_frame.place(
            relx=0.3, 
            rely=0.4, 
            relwidth=0.4, 
            relheight=0.2
        )
        
        welcome_label = tk.Label(
            welcome_frame, 
            text="Welcome to\nVIT Attendance Tracker", 
            font=('Segoe UI', 24, 'bold'),
            fg=self.COLORS["primary"],
            bg='#000000'
        )
        welcome_label.pack(expand=True)
        welcome_frame.config(bg='#000000')
        welcome_label.config(bg='black')
        
        def fade_in(opacity=0):
            if opacity < 100:
                r, g, b = [int(self.hex_to_rgb(self.COLORS["text_light"])[i] * (opacity/100) + 
                               self.hex_to_rgb('#FFFFFF')[i] * ((100-opacity)/100)) 
                           for i in range(3)]
                color = f'#{r:02x}{g:02x}{b:02x}'
                welcome_frame.config(bg=color)
                welcome_label.config(bg=color)
                self.master.after(20, lambda: fade_in(opacity + 10))
            else:
                self.master.after(2000, welcome_frame.destroy)
        
        def fade_out():
            welcome_frame.destroy()
        
        fade_in()
    
    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def take_image_ui(self):
        ImageUI = Toplevel(self.master) 
        ImageUI.title("Register Student")
        ImageUI.geometry("1000x600")
        ImageUI.configure(background=self.COLORS["background"])
        ImageUI.resizable(0, 0)

        main_frame = tk.Frame(
            ImageUI, 
            bg='white', 
            relief=tk.RAISED,
            bd=1
        )
        main_frame.place(
            relx=0.1, 
            rely=0.1, 
            relwidth=0.8, 
            relheight=0.8
        )

        title_label = tk.Label(
            main_frame, 
            text="Student Registration", 
            font=('Segoe UI', 24, 'bold'),
            fg=self.COLORS["text_dark"],
            bg='white'
        )
        title_label.pack(pady=(30, 20))
        form_frame = tk.Frame(main_frame, bg='white')
        form_frame.pack(padx=100, fill=tk.X)

        lbl1 = tk.Label(
            form_frame,
            text="Enrollment No",
            font=('Segoe UI', 12),
            fg=self.COLORS["text_dark"],
            bg='white'
        )
        lbl1.grid(row=0, column=0, sticky='w', pady=10)
        
        enrollment_entry = tk.Entry(
            form_frame,
            width=30,
            font=('Segoe UI', 14),
            relief=tk.FLAT,
            bg=self.COLORS["background"],
            validate="key"
        )
        enrollment_entry.grid(row=0, column=1, pady=10, padx=20, sticky='ew')
        enrollment_entry["validatecommand"] = (enrollment_entry.register(self.test_val), "%P", "%d")

        lbl2 = tk.Label(
            form_frame,
            text="Name",
            font=('Segoe UI', 12),
            fg=self.COLORS["text_dark"],
            bg='white'
        )
        lbl2.grid(row=1, column=0, sticky='w', pady=10)
        
        name_entry = tk.Entry(
            form_frame,
            width=30,
            font=('Segoe UI', 14),
            relief=tk.FLAT,
            bg=self.COLORS["background"]
        )
        name_entry.grid(row=1, column=1, pady=10, padx=20, sticky='ew')

        message = tk.Label(
            main_frame,
            text="",
            font=('Segoe UI', 12),
            fg=self.COLORS["secondary"],
            bg='white'
        )
        message.pack(pady=20)
        btn_frame = tk.Frame(main_frame, bg='white')
        btn_frame.pack(pady=20)

        button_configs = [
            {
                "text": "Capture Image", 
                "command": lambda: self.take_image(enrollment_entry, name_entry, message),
                "bg": self.COLORS["primary"],
                "hover_color": self.COLORS["hover"]
            },
            {
                "text": "Train Model", 
                "command": lambda: self.train_image(message),
                "bg": self.COLORS["secondary"],
                "hover_color": "#5D3FD3"
            }
        ]

        for config in button_configs:
            btn = AnimatedButton(
                btn_frame, 
                text=config['text'], 
                command=config['command'],
                bg=config['bg'],
                fg='white',
                width=20,
                height=2,
                hover_color=config['hover_color']
            )
            btn.pack(side=tk.LEFT, padx=10)

    def take_image(self, enrollment_entry, name_entry, message):
        if not enrollment_entry.get() or not name_entry.get():
            self.show_error_screen()
            return
        
        try:
            takeImage.TakeImage(
                enrollment_entry.get(), 
                name_entry.get(), 
                haarcasecade_path, 
                trainimage_path, 
                message, 
                self.show_error_screen, 
                self.text_to_speech
            )
            enrollment_entry.delete(0, tk.END)
            name_entry.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Image Capture Error", str(e))

    def train_image(self, notification):
        try:
            trainImage.TrainImage(
                haarcasecade_path, 
                trainimage_path, 
                trainimagelabel_path, 
                notification, 
                self.text_to_speech
            )
        except Exception as e:
            messagebox.showerror("Training Error", str(e))

   

    def automatic_attendance(self):
        automaticAttedance.subjectChoose(self.text_to_speech)
        

    def view_attendance(self):
        show_attendance.subjectchoose(self.text_to_speech)
        

    def text_to_speech(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def show_error_screen(self):
        messagebox.showerror("Error", "Enrollment & Name are required!")

    def test_val(self, inStr, acttyp):
        if acttyp == '1':
            return inStr.isdigit()
        return True

haarcasecade_path = "haarcascade_frontalface_default.xml"
trainimagelabel_path = "./TrainingImageLabel/Trainner.yml"
trainimage_path = "TrainingImage"
studentdetail_path = "./StudentDetails/studentdetails.csv"
attendance_path = "Attendance"

for path in [trainimage_path, os.path.dirname(trainimagelabel_path), os.path.dirname(studentdetail_path), attendance_path]:
    if not os.path.exists(path):
        os.makedirs(path)

def main():
    root = tk.Tk()
    root.configure(bg='white')
    app = ModernAttendanceSystem(root)
    root.mainloop()

if __name__ == "__main__":
    main()