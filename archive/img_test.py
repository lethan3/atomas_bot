import pyautogui
import time
import os

# os.system('cls')

# while True:
#     x, y = pyautogui.position()
#     r, g, b = pyautogui.pixel(x, y)
#     print('\r' + 'x:', x, 'y:', y, 'RGB:', r, g, b, '        ', end='')

import cv, cv2
import pytesseract
pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

from PIL import Image, ImageOps
from skimage.morphology import rectangle, disk, ball
from skimage.filters.rank import maximum

# print('start')

# time.sleep(3)

# ss = pyautogui.screenshot()
# ss.save('ss.png')
# ss.save('ss_marked.png')

img = cv2.imread('ss.png')

print('Processing:')
# img = img[300:1000,640:1280]
img = img[640:670,945:975]
## convert to hsv

img = cv2.resize(img, None, fx=100, fy=100)
mask = cv2.inRange(img, (210, 210, 210), (255, 255,255))
img = cv2.bitwise_and(img,img,mask=mask)
img = cv2.bitwise_not(img, img)
print('Writing to file:')
cv2.imwrite('ss_processed.png', img)

print('OCR:')
data = pytesseract.image_to_data(img, output_type='dict', config=(
                  "_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
                  " --psm 11"))


print('Drawing boxes:')
boxes = len(data['level'])
for i in range(boxes):
    (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
    # Draw box
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
print(data['text'])
print('Writing to file:')
cv2.imwrite('ss_marked.png', img)