import os
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import datetime
import calendar

import PIL.Image
import pymongo
import gridfs
from dotenv import load_dotenv

import numpy as np
from keras.preprocessing import image
from sklearn.metrics.pairwise import cosine_similarity
from keras.applications.vgg16 import VGG16

from PIL import Image

success:bool = False
path:str = ""

def hash_password(password:str):
    ascii_sum:int = 0
    new_password:str = ""
    for i in range(0,len(password)):
        ascii_sum += ord(password[i])
    for i in range(0,len(password)):
        new_pos = ascii_sum+ord(password[i])

        while (new_pos > 126 or new_pos < 32):
            if new_pos > 126:
                new_pos = (new_pos % 126) + 32
            else:
                new_pos += 32

        new_password += chr(new_pos)
    return new_password
# Main functionalities:


def config_image(filepath):
    img = Image.open(filepath)
    new_img = img.resize((244,244))
    return new_img

def run_check():

    window.withdraw()

    def verify():
        dbClient = pymongo.MongoClient(os.getenv('VIEWER'))
        database = dbClient[os.getenv('DB')]
        table = database[os.getenv('TABLE')]

        username = e1.get()
        password = hash_password(e2.get())

        if table.count_documents({"username" : username,"password":password}) > 0 :
            global path
            path = table.find_one({"username" : username,"password":password})["_id"]
            btn['state'] = tk.NORMAL
            messagebox.showinfo("Success","You have been verified!! Welcome back :)")
        else:
            messagebox.showerror("Error","Your data was not verified!!")

    newWindow = tk.Toplevel(window)
    newWindow.title("Verify Yourself")
    newWindow.geometry('500x400')

    newWindow.rowconfigure(0,weight=1)
    newWindow.rowconfigure(1,weight=1)
    newWindow.rowconfigure(2,weight=5)
    newWindow.rowconfigure(3,weight=5)
    newWindow.columnconfigure(0,weight=1)
    newWindow.columnconfigure(1,weight=3)


    l1 = tk.Label(newWindow,text="Type in your username")
    l1.grid(row=0,column=0,sticky="NSEW")
    e1 = tk.Entry(newWindow)
    e1.grid(row=0,column=1,sticky="NSEW")

    l2 = tk.Label(newWindow,text="Type in your password")
    l2.grid(row=1,column=0,sticky="NSEW")
    e2 = tk.Entry(newWindow,show="*")
    e2.grid(row=1,column=1,sticky="NSEW")

    btn2 = tk.Button(newWindow,text="Verify Info",command=verify)
    btn2.grid(row=2,sticky="NSEW",columnspan=2)

    btn = tk.Button(newWindow,text="Upload Picture",command=upload_file)
    btn['state'] = tk.DISABLED
    btn.grid(row=3,sticky="NSEW",columnspan=2)

def check_time_limit(filePath) -> bool:
    if filePath.lower().endswith(".png") or filePath.lower().endswith(".jpg") or filePath.lower().endswith(".jpeg"):
        img = Image.open(filePath)
        exif = img.getexif()
        if exif is None:
            messagebox.showinfo("Damn!","No EXIF data in image and hence can't be used")
            return False
        else:
            if not exif[306] is None:

                presentDate = datetime.datetime.today()
                presentDate = calendar.timegm(datetime.datetime.utctimetuple(presentDate))
                picDate = datetime.datetime.strptime(exif[306],'%Y:%m:%d %H:%M:%S')
                picDate = calendar.timegm(datetime.datetime.utctimetuple(picDate))

                delta_time = presentDate - picDate

                if delta_time <= (24*60**2):
                    messagebox.showinfo("Success","Image has been clicked within 24 hrs")
                    return True
                else:
                    messagebox.showwarning("Fail","Image is older than 24 hours")
                    return False

    else:
        messagebox.showerror("Fail","Not an accepted format")
        return False

def upload_file():
    print(path)
    filepath = filedialog.askopenfilename()
    if filepath:
        try:
            messagebox.showinfo("Success","File chosen: " + filepath)
            first_pass = check_time_limit(filepath)

            if first_pass:
                global vgg16
                vgg16 = VGG16(weights='imagenet',include_top=False,pooling='max',input_shape=(244,244,3))
                for model_layer in vgg16.layers:
                    model_layer.trainable = False

                dbClient = pymongo.MongoClient(os.getenv('VIEWER'))
                database = dbClient[os.getenv('DB')]

                image_target = gridfs.GridFS(database).find_one({'filename': str(path)})

                similarity = get_similarity_score(filepath, image_target)
                print(similarity)

                if similarity >= 0.7:
                    messagebox.showinfo("Success", "These images are acceptably similar")
                else:
                    messagebox.showwarning("Warning", "These images are seemingly different")


        except Exception as e:
            messagebox.showerror("Error", "Something broke: " + str(e))
            print(str(e))
    else:
        messagebox.showwarning("Warning", "No file chosen")


def create_img_tensor(object_image:image):
    tensor = np.expand_dims(image.img_to_array(object_image),axis=0)
    embedding = vgg16.predict(tensor)
    return embedding

def get_similarity_score(img1,img2):
    img1 = config_image(img1)
    img2 = config_image(img2)

    img1_array = create_img_tensor(img1)
    img2_array = create_img_tensor(img2)

    similarity_score = cosine_similarity(img1_array,img2_array).reshape(1,)
    return similarity_score

def push_new_user():

    window.withdraw()
    pic:str

    def new_pic():
        global photos
        photos= filedialog.askopenfilename()
        if photos:
            messagebox.showinfo("Success","New Photo chosen")
        else:
            messagebox.showwarning("Warning","No Photo chosen")

    def submit():
        db = os.getenv('VIEWER')

        try:
           dbClient = pymongo.MongoClient(db)
           database = dbClient[os.getenv('DB')]
           table = database[os.getenv('TABLE')]

           password = password_entry.get()
           username = user_entry.get()

           invalid:bool
           invalid = (password == "") or (username == "") or (photos == "")

           if not invalid:
               fs = gridfs.GridFS(database)

               with open(photos,'rb') as f:
                contents = f.read()

               password = hash_password(password)
               x = table.insert_one({"username":username,"password":password})
               insert_id = x.inserted_id
               fs.put(contents,filename=str(insert_id))

               window.deiconify()
           else:
               messagebox.showerror("Error","You missed a field")

        except Exception as e:
           print("Something broke: " + str(e))



        sign_up_window.destroy()

    sign_up_window = tk.Toplevel(window)
    sign_up_window.title("Sign Up!")
    sign_up_window.geometry("500x400")

    sign_up_window.rowconfigure(0,weight=1)
    sign_up_window.rowconfigure(1, weight=1)
    sign_up_window.rowconfigure(2, weight=1)
    sign_up_window.columnconfigure(0,weight=1)
    sign_up_window.columnconfigure(1,weight=4)

    l1 = tk.Label(sign_up_window,text="New Username")
    l1.grid(row = 0, column=0,sticky=tk.EW)
    user_entry = tk.Entry(sign_up_window, font=('calibre', 10, 'normal'))
    user_entry.grid(row=0,column=1,sticky=tk.NSEW)

    l2 = tk.Label(sign_up_window,text="New Password")
    l2.grid(row = 1, column=0,sticky=tk.EW)
    password_entry = tk.Entry(sign_up_window, font=('calibre', 10, 'normal'),show="*")
    password_entry.grid(row=1,column=1,sticky=tk.NSEW)

    upload_pic = tk.Button(sign_up_window,text="Upload Picture", command=new_pic)
    upload_pic.grid(row=2,column=0,sticky=tk.NSEW)
    submit_button = tk.Button(sign_up_window,text="Submit", command=submit)
    submit_button.grid(row=2,column=1,sticky=tk.NSEW)



load_dotenv()

window = tk.Tk()
window.title("Image comparision")
window.geometry("500x400")
icon = tk.PhotoImage(file='grunt.png')
window.iconphoto(True,icon)



upload_button = tk.Button(window,text="Upload File",command=run_check)
upload_button.pack(side="top", anchor="ne" ,pady=1, fill="both",expand=True)

photos:str = ""

new_user_button = tk.Button(window,text="New User",command=push_new_user)
new_user_button.pack(side="top", anchor="nw" ,pady=1,fill="both",expand=True)

messagebox.showinfo("Hello!!", "Please enter an image which has been clicked in the last 24 hrs")

window.mainloop()