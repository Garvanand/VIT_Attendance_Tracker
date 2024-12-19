import pandas as pd
from glob import glob
import os
import tkinter as tk
from tkinter import ttk, messagebox, Canvas
import csv
import random

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

def subjectchoose(text_to_speech):
    def calculate_attendance():
        Subject = tx.get()
        if Subject == "":
            t = 'Please enter the subject name.'
            text_to_speech(t)
            return

        subject_path = os.path.join("./Attendance", Subject)
        print(subject_path)
        if not os.path.exists(subject_path):
            t = f"Attendance folder for {Subject} not found."
            text_to_speech(t)
            return

        filenames = glob(os.path.join(subject_path, f"{Subject}*.csv"))
        if not filenames:
            t = f"No attendance data found for {Subject}."
            text_to_speech(t)
            return

        df_list = [pd.read_csv(f) for f in filenames]
        newdf = df_list[0]
        for i in range(1, len(df_list)):
            newdf = newdf.merge(df_list[i], how="outer")

        newdf.fillna(0, inplace=True)

        date_columns = [col for col in newdf.columns if col not in ['Enrollment', 'Name']]

        attendance_mean = newdf[date_columns].mean(axis=1)  # Compute mean across attendance columns
        newdf["Attendance"] = (attendance_mean * 100).round().astype(int).astype(str) + '%'

        newdf_display = newdf[['Enrollment', 'Name', 'Attendance']]

        summary_path = os.path.join(subject_path, "attendance_summary.csv")
        newdf_display.to_csv(summary_path, index=False)

        result_window = tk.Toplevel(subject)
        result_window.title(f"Attendance of {Subject}")
        result_window.geometry("800x600")
        
        result_window.configure(bg='white')
        
        title_label = tk.Label(
            result_window, 
            text=f"Attendance for {Subject}", 
            font=('Segoe UI', 20, 'bold'),
            fg="#2D3748",
            bg='white'
        )
        title_label.pack(pady=20)

        tree = ttk.Treeview(
            result_window, 
            columns=('Enrollment', 'Name', 'Attendance'), 
            show='headings'
        )
        tree.heading('Enrollment', text='Enrollment No')
        tree.heading('Name', text='Name')
        tree.heading('Attendance', text='Attendance')
        tree.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        for index, row in newdf_display.iterrows():
            tree.insert('', 'end', values=list(row))

    subject = tk.Tk()
    subject.title("Select Subject")
    subject.geometry("580x320")
    subject.resizable(0, 0)
    gradient_bg = GradientBackground(subject)
    
    main_frame = tk.Frame(
        subject, 
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
        text="View Attendance", 
        font=('Segoe UI', 24, 'bold'),
        fg="#2D3748",
        bg='white'
    )
    title_label.pack(pady=(30, 20))

    form_frame = tk.Frame(main_frame, bg='white')
    form_frame.pack(padx=100, fill=tk.X)

    sub = tk.Label(
        form_frame,
        text="Enter Subject",
        font=('Segoe UI', 12),
        fg="#2D3748",
        bg='white'
    )
    sub.grid(row=0, column=0, sticky='w', pady=10)
    tx = tk.Entry(
        form_frame,
        width=30,
        font=('Segoe UI', 14),
        relief=tk.FLAT,
        bg="#F4F6F9"
    )
    tx.grid(row=0, column=1, pady=10, padx=20, sticky='ew')

    btn_frame = tk.Frame(main_frame, bg='white')
    btn_frame.pack(pady=20)

    button_configs = [
        {
            "text": "Check Sheets", 
            "command": lambda: Attf(),
            "bg": "#764BA2",
            "hover_color": "#5D3FD3"
        },
        {
            "text": "View Attendance", 
            "command": calculate_attendance,
            "bg": "#4A90E2",
            "hover_color": "#3A7CA5"
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

    def Attf():
        sub = tx.get()
        if sub == "":
            t = "Please enter the subject name!!!"
            text_to_speech(t)
        else:
            subject_path = os.path.join("Attendance", sub)
            if os.path.exists(subject_path):
                os.startfile(subject_path)
            else:
                t = f"Attendance folder for {sub} not found."
                text_to_speech(t)

    subject.mainloop()

if __name__ == "__main__":
    def dummy_text_to_speech(text):
        print(text)
    
    subjectchoose(dummy_text_to_speech)