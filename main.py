import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import datetime
import calendar

import PIL.ExifTags
from PIL import Image

def check_time_limit(filePath):
    if filePath.lower().endswith(".png") or filePath.lower().endswith(".jpg") or filePath.lower().endswith(".jpeg"):
        img = Image.open(filePath)
        exif = img.getexif()
        if exif is None:
            messagebox.showinfo("Damn!","No EXIF data in image and hence can't be used")
        else:
            if not exif[306] is None:

                presentDate = datetime.datetime.today()
                presentDate = calendar.timegm(datetime.datetime.utctimetuple(presentDate))
                picDate = datetime.datetime.strptime(exif[306],'%Y:%m:%d %H:%M:%S')
                picDate = calendar.timegm(datetime.datetime.utctimetuple(picDate))

                delta_time = presentDate - picDate

                if delta_time <= (24*60**2):
                    messagebox.showinfo("Success","Image has been clicked within 24 hrs")
                else:
                    messagebox.showwarning("Fail","Image is older than 24 hours")

    else:
        messagebox.showerror("Fail","Not an accepted format")

def upload_file():
    filepath = filedialog.askopenfilename()
    if filepath:
        try:
            messagebox.showinfo("Success","File chosen: " + filepath)
            check_time_limit(filepath)
        except Exception as e:
            messagebox.showerror("Error", "Something broke: " + str(e))
    else:
        messagebox.showwarning("Warning", "No file chosen")

window = tk.Tk()
window.title("Image comparision")
window.geometry("500x400")
icon = tk.PhotoImage(file='img.png')
window.iconphoto(True,icon)



upload_button = tk.Button(window,text="Upload File",command=upload_file)
upload_button.pack(pady=20)

messagebox.showinfo("Hello!!", "Please enter an image which has been clicked in the last 24 hrs")

window.mainloop()