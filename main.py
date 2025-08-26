import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import datetime
import calendar

import numpy as np
from keras.preprocessing import image
from sklearn.metrics.pairwise import cosine_similarity
from keras.applications.vgg16 import VGG16

from PIL import Image

def config_image(filepath):
    img = Image.open(filepath)
    new_img = img.resize((244,244))
    return new_img


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

                similarity = get_similarity_score(filepath,'IMG_2284.jpg')
                print(similarity)

                if similarity >= 0.7:
                    messagebox.showinfo("Success","These images are acceptably similar")
                else:
                    messagebox.showwarning("Warning","These images are seemingly different")


        except Exception as e:
            messagebox.showerror("Error", "Something broke: " + str(e))
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

window = tk.Tk()
window.title("Image comparision")
window.geometry("500x400")
icon = tk.PhotoImage(file='grunt.png')
window.iconphoto(True,icon)



upload_button = tk.Button(window,text="Upload File",command=upload_file)
upload_button.pack(pady=20)

messagebox.showinfo("Hello!!", "Please enter an image which has been clicked in the last 24 hrs")

window.mainloop()