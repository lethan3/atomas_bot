import datetime
import math
import os
import random
import time

import cv
import cv2
import keyboard
import numpy as np
import pyautogui
from PIL import Image

from bot import Bot
from constants import (atom_colors, atom_inner_r, atom_r, center_r,
                       field_edge_r, field_inner_r, field_outer_r, field_r,
                       field_x, field_y, rgb_adjust_a, rgb_adjust_b)
from field import Field

MAX_ATOM = 201


class Interactor:
    def __init__(self):
        self.atoms = []
        for i in range(-4, MAX_ATOM):
            if (i == 0):
                self.atoms.append(None)
                continue
            self.atoms.append(cv2.imread('img_gen/' + str(i) + '.png'))

    def polar_to_rect(self, r, theta):
        return [round(field_outer_r + r * math.cos(theta)),
                round(field_outer_r - r * math.sin(theta))]

    def rect_to_polar(self, x, y):
        x -= field_outer_r
        y -= field_outer_r
        r = math.sqrt(x ** 2 + y ** 2)
        if (y > 0):
            # bottom
            return [r, 2 * math.pi - math.acos(x / r)]
        else:
            # top
            return [r, math.acos(x / r)]

    def dist(self, a, b):
        return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(len(a))))

    def get_centers(self, img):
        img = img.astype(np.int32)

        shp = np.shape(img)

        bk_colors = []
        for i in range(60):
            c = self.polar_to_rect(field_edge_r, i * 2 * math.pi / 60)
            bk_colors.append(img[c[0]][c[1]])

        background_color = (np.median(bk_colors, 0))
        background_img = np.full_like(img, fill_value=background_color)

        # cv2.imwrite('bk.png', background_img)

        img = img - background_img
        img = np.abs(img)
        # cv2.imwrite('img_filtered1.png', img)
        squared_sum = img[..., 0]**2 + img[..., 1]**2 + (img[..., 2]**2 * 0.07)

        # Create a mask where the squared sum is greater than 1000
        mask = squared_sum > 1000

        # Apply the mask to set appropriate values in the image
        img_bw = np.where(mask, 255, 0)
        # cv2.imwrite('img_filtered2.png', img_bw)

        coords = []
        # whites = np.transpose(np.where(mask))
        cnt = 0
        num_samples = 60
        for i in range(num_samples):
            p = np.array(self.polar_to_rect(
                field_r, 2 * i * math.pi / num_samples))
            if img_bw[p[0]][p[1]] < 255:
                continue
            # print(img_bw[p[0]][p[1]])
            cnt += 1
            # print(cnt)
            s = datetime.datetime.now()
            ret, img_bw, fmask, rect = cv2.floodFill(
                img_bw, None, (p[1], p[0]), 64)
            fmask = fmask[1:-1, 1:-1]
            fill_coords = np.transpose(np.where(fmask))

            # cv2.imwrite('fmask_sample.png', sv + img)
            # print(rect[2], rect[3])

            if (max(abs(rect[2] - 2 * atom_r), abs(rect[3] - 2 * atom_r)) <= 3):
                c = (np.round(np.sum(fill_coords, axis=0) /
                     np.shape(fill_coords)[0]))
                # print(c)
                coords.append(c)
        # imwrite('img_filtered.png', img_bw)

        coords = list(map(lambda x: self.rect_to_polar(x[0], x[1]), coords))

        coords.sort(key=lambda a: a[1])
        # print(coords)

        min_angle = 2 * math.pi
        for i in range(len(coords) - 1):
            min_angle = min(min_angle, coords[i + 1][1] - coords[i][1])
        min_angle = min(min_angle, coords[0][1] + 2 * math.pi - coords[-1][1])

        coords_fixed = []
        for i in range(len(coords)):
            coords_fixed.append(coords[i])

        expected = round(2 * math.pi / min_angle)
        min_angle = 2 * math.pi / expected
        for i in range(expected):
            # print(coords[i][0])
            for j in range(len(coords_fixed)):
                if (self.dist(self.polar_to_rect(coords[0][0], coords[0][1] + min_angle * i), self.polar_to_rect(coords_fixed[j][0], coords_fixed[j][1])) < 5):
                    break
            else:
                coords_fixed.append(
                    [coords[0][0], coords[0][1] + min_angle * i])
        coords_fixed.sort(key=lambda x: x[1])
        coords_fixed = list(
            map(lambda x: self.polar_to_rect(x[0], x[1]), coords_fixed))
        # print(coords_fixed)
        for c in coords_fixed:
            cv2.circle(img, (round(c[1]), round(c[0])), atom_r, (0, 255, 0), 1)

        cv2.circle(img, (field_outer_r, field_outer_r), atom_r, (0, 255, 0), 1)
        cv2.imwrite('img_centers.png', img)

        return coords_fixed

    def ident_atom(self, img):
        match_scores = []
        for i in range(-4, self.r):
            if (0 <= i < self.l):
                continue
            atom = self.atoms[i + 4]
            atom = atom[len(atom)//2 - atom_inner_r:len(atom)//2 + atom_inner_r,
                        len(atom)//2 - atom_inner_r:len(atom)//2 + atom_inner_r]
            channel_scores = []
            for channel in range(3):  # Assuming a 3-channel color space like HSV or BGR
                result = cv2.matchTemplate(
                    img[:, :, channel], atom[:, :, channel], cv2.TM_SQDIFF_NORMED)
                # print(result)
                channel_scores.append(result[0][0])
            res = np.sum(channel_scores, axis=0)
            match_scores.append([res, i])
        # print(match_scores)
        match_scores.sort(key=lambda a: a[0])
        # if (match_scores[0][1] == 9):
        #     cv2.imwrite('atom.png', img)
        print(match_scores[0][1], 'match score:', match_scores[0][0])
        if (match_scores[0][0] > 0.15):
            self.uncertainties.append(img)
        return (match_scores[0][1], match_scores[0][0])

    def read_field(self):
        # img = cv2.imread('ss.png')
        img = np.array(pyautogui.screenshot())
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        # cv2.imwrite('ss.png', img)

        img = img[(field_y - field_outer_r):(field_y + field_outer_r),
                  (field_x - field_outer_r):(field_x + field_outer_r)]

        centers = self.get_centers(np.copy(img))
        # print(centers)
        field_atoms = []
        for c in centers:
            # print(c[0], c[1])
            # print(np.shape(img))
            # cv2.rectangle(img, (c[1] - atom_inner_r,c[0] - atom_inner_r), (c[1] + atom_inner_r,c[0] + atom_inner_r), (0, 0, 255))
            curr_img = img[c[0] - atom_inner_r:c[0] + atom_inner_r,
                           c[1] - atom_inner_r:c[1] + atom_inner_r]
            atom, uncertainty = self.ident_atom(curr_img)
            field_atoms.append(atom)
            if (uncertainty > 0.15):
                self.uncertainties.append(
                    img[c[0] - atom_r:c[0] + atom_r, c[1] - atom_r:c[1] + atom_r])
        # cv2.imwrite('img_marked.png', img)
        return (centers[0], field_atoms)

    def read_center(self, img):
        # cv2.imwrite('center.png', img[field_outer_r - atom_inner_r:field_outer_r + atom_inner_r,
        #                            field_outer_r - atom_inner_r:field_outer_r + atom_inner_r])
        return self.ident_atom(img[field_outer_r - atom_inner_r:field_outer_r + atom_inner_r,
                                   field_outer_r - atom_inner_r:field_outer_r + atom_inner_r])[0]

    def play(self):
        bot = Bot()
        spawned_atoms = []
        op = False
        op2 = False
        last = -5

        pause = False
        self.l, self.r = 1, MAX_ATOM
        while True:
            try:
                first_center, curr_field_atoms = self.read_field()
                while True:
                    reread = self.read_field()
                    if (curr_field_atoms != reread[1]):
                        first_center, curr_field_atoms = reread
                    else:
                        break
            except:
                for i in range(1, 10000000):
                    if (not os.path.isfile('ss/' + str(i) + '.png')):
                        cv2.imwrite('ss/' + str(i) + '.png', cv2.cvtColor(
                            np.array(pyautogui.screenshot()), cv2.COLOR_RGB2BGR))
                        break
                pyautogui.click(963, 869)
                fout = open('spawned_atoms.txt', 'w+')
                fout.write(str(spawned_atoms))
                fout.close()
                continue

            img = np.array(pyautogui.screenshot())
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            # cv2.imwrite('ss.png', img)
            img = img[(field_y - field_outer_r):(field_y + field_outer_r),
                      (field_x - field_outer_r):(field_x + field_outer_r)]
            curr_atom = self.read_center(np.copy(img))

            print(curr_field_atoms, curr_atom)

            if not (op or op2):
                spawned_atoms.append(curr_atom)
            print(spawned_atoms)

            curr_field = Field(False, curr_field_atoms)
            if (len(curr_field_atoms) >= 2):
                move = bot.decide(curr_field, spawned_atoms, curr_atom, op)
            elif len(curr_field_atoms) == 1:
                move = 0
            else:
                pyautogui.click(963, 869)

            # for i in range(1, 10000000):
            #         if (not os.path.isfile('ss/' + str(i) + '.png')):
            #             cv2.imwrite('ss/' + str(i) + '.png', cv2.cvtColor(np.array(pyautogui.screenshot()), cv2.COLOR_RGB2BGR))
            #             break
            print(move)
            if (op2):
                op2 = False
            if not (op) or curr_atom == -2:
                click_angle = (move - (0.5 if not curr_atom in [-2, -4] else 0)) * 2 * math.pi / len(
                    curr_field_atoms) + self.rect_to_polar(first_center[0], first_center[1])[1]
                print(click_angle * 360 / (2 * math.pi))
                click_coords = [self.polar_to_rect(field_r, click_angle)[
                    1], self.polar_to_rect(field_r, click_angle)[0]]
                print(click_coords)
                # input()
                pyautogui.click(
                    field_x + click_coords[0] - field_outer_r, field_y + click_coords[1] - field_outer_r, clicks=1)
            else:
                if (move):
                    pyautogui.click(field_x, field_y, clicks=1, interval=1)
                    pause = False
                op = False
                op2 = True

            if (curr_atom == -2):
                op = True

            if (curr_atom == -1):
                curr_field.place_atom(move, -1)
                curr_field.reduce()
                print(curr_field.atoms)
                print(curr_field_atoms)
                print('pause', len(curr_field_atoms) - len(curr_field.atoms))
                time.sleep(
                    max(0, 0.3 * (len(curr_field_atoms) - len(curr_field.atoms))))
            last = curr_atom
            l = max(1, min(curr_field.atoms) - 10)
            r = min(MAX_ATOM, max(curr_field.atoms) + 10)
            print(l, r)


interactor = Interactor()
# p = interactor.rect_to_polar(100, 200)
# print(p[0], p[1])
# print(interactor.polar_to_rect(p[0], p[1]))
# time.sleep(1)

start = datetime.datetime.now()
pyautogui.click(1270, 1189)
# time.sleep(1)
interactor.play()
