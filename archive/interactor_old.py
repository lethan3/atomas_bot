from constants import field_x, field_y, field_r, field_inner_r, atom_colors, rgb_adjust_a, rgb_adjust_b
import pyautogui
import keyboard
import time
import math
import cv2

class Interactor:
    def __init__(self):
        pass

    def dist(self, a, b):
        r = 0
        for i in range(len(a)):
            r += (a[i] - b[i]) ** 2
        return r
    
    def match_atom(self, rgb):
        rgb = list(rgb)
        for j in range(3):
            rgb[j] = rgb[j] * rgb_adjust_a[j] + rgb_adjust_b[j]

        match, best_dist = 0, 1e9
        for j in range(len(atom_colors)):
                if self.dist(atom_colors[j], rgb) < best_dist:
                    best_dist = self.dist(atom_colors[j], rgb)
                    match = j

        return match - 4
    
    def get_center(self):
        rgba = pyautogui.pixel(field_x, field_y - 20)
        time.sleep(0.1)
        rgbb = pyautogui.pixel(field_x, field_y - 20)
        if (rgba != rgbb): return -1

        return self.match_atom(rgba)

    def get_field(self):
        im = pyautogui.screenshot()
        time.sleep(0.5)
        im2 = pyautogui.screenshot()
        im.save('im.png')
        num_samples = 500
        samples = [None] * num_samples

        im_marked = cv2.imread('im.png')

        for i in range(num_samples):
            x, y = field_x + int(field_r * math.cos(i * 2 * math.pi / num_samples)), field_y + int(field_r * math.sin(i * 2 * math.pi / num_samples))
            rgb = im.getpixel((x, y))
            rgb2 = im2.getpixel((x, y))
            cv2.rectangle(im_marked, (x-1,y-1),(x+1,y+1), (0,255,0), 1)
            if (rgb == rgb2): samples[i] = self.match_atom(rgb)
            else: samples[i] = -1
        cv2.imwrite('im_marked.png', im_marked)

        for i in range(len(samples) - 1, -1, -1):
            if (samples[i] == -4): samples.pop(i)
        atoms = []
        for i in range(1, len(samples) - 1):
            if (samples[i - 1] != samples[i] or samples[i + 1] != samples[i]): continue
            if (len(atoms) == 0 or atoms[-1] != samples[i]): atoms.append(samples[i])
        return atoms

    def capture_center(self):
        ind = 10
        while True:
            if (keyboard.is_pressed('space')):
                print('triggered')
                ss = pyautogui.screenshot()
                ss.save('temp.png')
                img = cv2.imread('temp.png')
                img = img[617:693,922:998]
                if not cv2.imwrite(r'img\\atom_' + str(ind) + '.png', img):
                    print('failed save')
                else:
                    print('saved')
                ind += 1
            if (keyboard.is_pressed('0')):
                break
       
         
     
interactor = Interactor() 
interactor.capture_center()
# time.sleep(1)
# print('start')
# fout = open('spawned_atoms.txt', 'w+')
# last = -5
# while True:
#     atom = interactor.get_center()
#     if (atom != last):
#         print(atom)
#         fout.write(str(atom) + '\n')
#         last = atom
