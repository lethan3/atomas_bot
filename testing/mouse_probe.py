import pyautogui
import time
import os

os.system('cls')

while True:
    x, y = pyautogui.position()
    r, g, b = pyautogui.pixel(x, y)
    print('\r' + 'x:', x, 'y:', y, 'RGB:', r, g, b, '        ', end='')
