from constants import field_x, field_y, field_r, field_outer_r, center_r, atom_r, field_inner_r, atom_colors, rgb_adjust_a, rgb_adjust_b
import pyautogui
import keyboard
import time
import math
import cv, cv2
import numpy as np
import datetime
from PIL import Image

from field import Field
from bot import Bot

class Interactor:
    def __init__(self):
        pass

    def read_center(self):
        img = np.array(pyautogui.screenshot())
        # img = np.array(Image.open('ss.png'))
        img = img[field_y - center_r:field_y + center_r, field_x - center_r:field_x + center_r]
        cv2.imwrite('ss.png', cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
        for i in range(-4, 41):
            if (i == 0): continue
            atom = cv2.imread('img/' + str(i) + '.png')
            atom = atom[len(atom)//2 - atom_r:len(atom)//2 + atom_r,len(atom)//2 - atom_r:len(atom)//2 + atom_r]
            
            img_cv = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            match_scores = []
            for channel in range(3):  # Assuming a 3-channel color space like HSV or BGR
                result = cv2.matchTemplate(img_cv[:, :, channel], atom[:, :, channel], cv2.TM_SQDIFF_NORMED)
                match_scores.append(result)
            res = np.max(match_scores, axis=0)
            mask = res < 0.025
            coordinates = np.transpose(np.where(mask))
            for c in coordinates:
                return i
        return None
    
    def stream_center(self):
        from pynput.keyboard import Key, Listener
        space_pressed = False

        fout = open('spawned_atoms.txt', 'w+')
        last = -5
        ignore = False
        while not (keyboard.is_pressed('q') and keyboard.is_pressed('p')):
            if (keyboard.is_pressed('space')):
                print('Ignoring next')
                ignore = True
            atom = self.read_center()
            if atom is None:
                last = -5
            elif atom != last:
                if (last == -5 and ignore):
                    last = atom
                    ignore = False
                    continue
                print(str(atom) + ' ')
                fout.write(str(atom) + ' ')
                fout.flush()
                last = atom
                if (atom == -2):
                    print('(Ignoring next)')
                    ignore = True

    def read_field(self):
        scaling = 1
        img = np.array(pyautogui.screenshot())
        # img = np.array(Image.open('ss.png'))
        img = img[(field_y - field_outer_r):(field_y + field_outer_r)+1,(field_x - field_outer_r):(field_x + field_outer_r)+1]
        # print(np.shape(img))
        cv2.imwrite('ss.png', cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
        matches = []

        img = cv2.resize(img, None, fx=scaling, fy=scaling)
        for i in range(-4, 41):
            if (i == 0): continue
            # time.sleep(1)
            atom = cv2.imread('img/' + str(i) + '.png')
            atom = atom[len(atom)//2 - atom_r:len(atom)//2 + atom_r+1,len(atom)//2 - atom_r:len(atom)//2 + atom_r+1]
            
            atom = cv2.resize(atom, None, fx=scaling, fy=scaling)
            

            # mask = cv2.inRange(img, (210, 210, 210), (255, 255,255))
            # img = cv2.bitwise_and(img,img,mask=mask)
            # mask = cv2.inRange(atom, (210, 210, 210), (255, 255,255))
            # atom = cv2.bitwise_and(atom,atom,mask=mask)

            img_cv = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            # mg_cv = img
            # res = cv2.matchTemplate(img_cv, atom, cv2.TM_CCOEFF_NORMED)

            match_scores = []

            for channel in range(3):  # Assuming a 3-channel color space like HSV or BGR
                result = cv2.matchTemplate(img_cv[:, :, channel], atom[:, :, channel], cv2.TM_SQDIFF_NORMED)
                match_scores.append(result)
            res = np.max(match_scores, axis=0)

            mask = res < 0.1
            coordinates = np.transpose(np.where(mask))
            for c in coordinates:
                if (i == 10): cv2.rectangle(img, (c[1], c[0]), (c[1]+2 * atom_r * scaling, c[0]+2 * atom_r * scaling), (0, 255, 0))
                matches.append([c[0] - field_outer_r * scaling, c[1] - field_outer_r * scaling, i])
            if (i == 10): cv2.imwrite('res.png', cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
        # print(matches)
        filtered_matches = []
        for i in range(len(matches)):
            if (max(abs(matches[i][0]), abs(matches[i][1])) < 2 * atom_r * scaling):
                continue
            for j in range(len(filtered_matches)):
                if (max(abs(matches[i][0] - filtered_matches[j][0]), abs(matches[i][1] - filtered_matches[j][1]))) < 2 * atom_r:
                    if (res[int(matches[i][0] + field_outer_r * scaling)][int(matches[i][1] + field_outer_r * scaling)] < res[int(filtered_matches[j][0] + field_outer_r * scaling)][int(filtered_matches[j][1] + field_outer_r * scaling)]):
                        filtered_matches[j] = matches[i]
                    break
            else:
                filtered_matches.append(matches[i])
        # print(filtered_matches)
        filtered_matches = list(map(lambda a : [2 * math.pi - math.acos(a[1] / math.sqrt(a[0]**2 + a[1]**2)) if a[0] > 0 else math.acos(a[1] / math.sqrt(a[0]**2 + a[1]**2)), a[2]], filtered_matches))
        filtered_matches.sort()
        print(filtered_matches)
        field_atoms = []
        for i in range(len(filtered_matches)):
            field_atoms.append(filtered_matches[i][1])
        return (filtered_matches[0][0], Field(False, field_atoms))

    def capture_center(self):
        ind = 10
        while True:
            if (keyboard.is_pressed('space')):
                print('triggered')
                ss = pyautogui.screenshot()
                ss.save('temp.png')
                img = cv2.imread('temp.png')
                img = img[field_y - center_r:field_y + center_r, field_x - center_r:field_x + center_r]
                if not cv2.imwrite(r'img\\atom_' + str(ind) + '.png', img):
                    print('failed save')
                else:
                    print('saved')
                ind += 1
            if (keyboard.is_pressed('0') and keyboard.is_pressed('9')):
                break

        

    def play(self):
        bot = Bot()
        spawned_atoms = []
        op = False
        while True:
            time.sleep(0.5)
            theta, curr_field = self.read_field()
            # while (curr_field.atoms != self.read_field().atoms):
            #     print(curr_field.atoms)
            #     curr_field = self.read_field()
            
            curr_atom = self.read_center()
            print(curr_field.atoms, curr_atom)
            spawned_atoms.append(curr_atom)

            move = bot.decide(curr_field, spawned_atoms, curr_atom, op)
            print(move)
            print(theta * 360 / (2 * math.pi))
            if not (op):
                click_angle = (move - (0.5 if curr_atom != -2 else 0)) * 2 * math.pi / len(curr_field.atoms) + theta
                print(click_angle * 360 / (2 * math.pi))
                click_x, click_y = field_x + field_inner_r * math.cos(click_angle), field_y - field_inner_r * math.sin(click_angle)
                print(click_x, click_y)
                # input()
                pyautogui.click(click_x, click_y ,clicks=1, interval=1)
            else:
                if (move):
                    pyautogui.click(field_x, field_y, clicks=1, interval=1)
                op = False

            if (curr_atom == -2):
                op = True
       
         
     
interactor = Interactor() 
interactor.capture_center()
# start = datetime.datetime.now()
# print(interactor.read_field().atoms)
# print(datetime.datetime.now() - start)
# print('start')
# fout = open('spawned_atoms.txt', 'w+')
# last = -5
# while True:
#     atom = interactor.get_center()
#     if (atom != last):
#         print(atom)
#         fout.write(str(atom) + '\n')
#         last = atom
