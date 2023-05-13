import sys
import cv2
import face_recognition
import pickle
import os

try:
    f=open("ref_name.pkl","rb")
    ref_dictt=pickle.load(f)
    f.close()
except:
    ref_dictt={}

try:
    f=open("ref_embed.pkl","rb")
    embed_dictt=pickle.load(f)
    f.close()
except:
    embed_dictt={}

image_dir = 'path_to_your_dataset'  # Replace with the path to your dataset

for root, dirs, files in os.walk(image_dir):
    for file in files:
        if file.endswith("png") or file.endswith("jpg"):  # Adjust the condition to match the format of your images
            path = os.path.join(root, file)
            name = os.path.splitext(file)[0]  # Use the filename as the name
            img = face_recognition.load_image_file(path)
            face_encoding = face_recognition.face_encodings(img)[0]

            if name in embed_dictt:
                embed_dictt[name] += [face_encoding]
            else:
                embed_dictt[name] = [face_encoding]
            ref_dictt[name] = name

f = open("ref_embed.pkl", "wb")
pickle.dump(embed_dictt, f)
f.close()

f=open("ref_name.pkl","wb")
pickle.dump(ref_dictt,f)
f.close()
