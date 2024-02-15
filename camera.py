import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

# Function to map a value from one range to another
def map_value(x, in_min, in_max, out_min, out_max):
    return max(min((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min, out_max), out_min)

# Function to update light intensity based on slider value
def update_intensity(value):
    global light_intensity
    light_intensity = int(value)

# Initialize camera
cap = cv2.VideoCapture(0)

# Set initial light intensity
light_intensity = 50

# Create GUI window
root = tk.Tk()
root.title("Light Intensity Control")

# Create a frame for the slider
frame = ttk.Frame(root, padding="20")
frame.grid(row=0, column=0)

# Create a slider widget
slider = ttk.Scale(frame, from_=0, to=100, orient="horizontal", command=update_intensity)
slider.set(light_intensity)
slider.grid(row=0, column=0)

# Function to update the slider position
def update_slider_position():
    slider.set(light_intensity)
    root.after(100, update_slider_position)

# Start updating slider position
update_slider_position()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Calculate average brightness of the frame
    avg_brightness = np.mean(gray)

    # Invert the brightness value, so brighter frames have lower values and vice versa
    inverted_brightness = 255 - avg_brightness

    # Calculate light intensity based on inverted brightness
    light_intensity = int(map_value(inverted_brightness, 0, 255, 0, 100))

    # Display light intensity on the frame
    cv2.putText(frame, f'Light Intensity: {light_intensity}%', (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # Convert the OpenCV frame to RGB format
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Convert the frame to ImageTk format
    img = ImageTk.PhotoImage(image=Image.fromarray(frame_rgb))

    # Display the camera feed in a Tkinter label widget
    label = ttk.Label(root, image=img)
    label.grid(row=1, column=0)

    # Update the GUI
    root.update_idletasks()
    root.update()

    # Exit the program when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close all windows
cap.release()
cv2.destroyAllWindows()
root.mainloop()
