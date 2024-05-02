import numpy as np
import tensorflow as tf
import os  # mainly used to navigate file structure.
import cv2
import imghdr
import keras
import smtplib
from matplotlib import pyplot as plt
from keras.models import load_model


my_email = "js4062237@gmail.com"
password = "mjwqjaqbletdeudm"
connection = smtplib.SMTP("smtp.gmail.com", 587)
connection.starttls()
connection.login(user=my_email, password=password)
#reading image
img = cv2.imread('pico.jpg')
plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
resize = tf.image.resize(img, (256, 256))
plt.imshow(resize.numpy().astype(int))
plt.show()
np.expand_dims(resize, 0)
#loading the model and predicting and sending alert.
new_model = load_model(os.path.join('models', 'ambulancedispatch.h5'))  # reloading
yhat_new = new_model.predict(np.expand_dims(resize/255, 0))
if yhat_new > 0.5: 
    print('Prediction: Accident detected, Ambulance required.\nAlert sent. ')
    connection.sendmail(
        from_addr=my_email,
        to_addrs="sarahnaved1@gmail.com, js4062237@gmail.com, shaiza1909@gmail.com",
        msg="Subject: Lab work alert!!\n\nJust an alert for checking functionality")
else:
    print('Prediction: Non-Accident image, ambulance not required.')

