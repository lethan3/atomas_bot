from constants import atom_colors, atom_symbols, rgb_adjust_a, rgb_adjust_b
from PIL import Image, ImageFont, ImageDraw
import numpy as np
import cv2

def draw_text_psd_style(draw, xy, text, font, tracking=0, leading=None, **kwargs):
    """
    usage: draw_text_psd_style(draw, (0, 0), "Test", 
                tracking=-0.1, leading=32, fill="Blue")

    Leading is measured from the baseline of one line of text to the
    baseline of the line above it. Baseline is the invisible line on which most
    letters—that is, those without descenders—sit. The default auto-leading
    option sets the leading at 120% of the type size (for example, 12‑point
    leading for 10‑point type).

    Tracking is measured in 1/1000 em, a unit of measure that is relative to 
    the current type size. In a 6 point font, 1 em equals 6 points; 
    in a 10 point font, 1 em equals 10 points. Tracking
    is strictly proportional to the current type size.
    """
    def stutter_chunk(lst, size, overlap=0, default=None):
        for i in range(0, len(lst), size - overlap):
            r = list(lst[i:i + size])
            while len(r) < size:
                r.append(default)
            yield r
    x, y = xy
    font_size = font.size
    lines = text.splitlines()
    if leading is None:
        leading = font.size * 1.2
    for line in lines:
        for a, b in stutter_chunk(line, 2, 1, ' '):
            w = font.getlength(a + b) - font.getlength(b)
            # dprint("[debug] kwargs")
            # print("[debug] kwargs:{}".format(kwargs))
                
            draw.text((x, y), a, font=font, **kwargs)
            x += w + (tracking / 1000) * font_size
        y += leading
        x = xy[0]

def draw_atom(num):
    font = ImageFont.truetype("font.ttf",90)
    font2 = ImageFont.truetype("font.ttf",60)
    # only positive
    color = atom_colors[5:][(num - 1) % 125]
    for i in range(len(color)):
        color[i] = (color[i] - rgb_adjust_b[i]) / rgb_adjust_a[i]
    color = np.round(np.array(color))
    symb = atom_symbols[(num - 1) % 125] + (str((num - 1) // 125) if (num >= 126) else '')
    # print(symb)
    img = np.zeros((301, 301, 3))
    img = img.astype(np.uint8)
    # print(np.shape(img))
    cv2.circle(img, (150, 150), radius=150, color = color * 1.1, thickness=-1, lineType=cv2.LINE_AA)
    cv2.circle(img, (150, 150), radius=140, color = color, thickness=-1, lineType=cv2.LINE_AA)

    
    cv2.imwrite('atom_render.png', cv2.cvtColor(img, cv2.COLOR_RGB2BGR))

    img = Image.open('atom_render.png')
    W, H = 301, 301
    image = Image.new('RGB', (W, H), (0,0,0))
    draw = ImageDraw.Draw(image)
    _, _, w, h = draw.textbbox((0, 0), symb, font=font)
    draw = ImageDraw.Draw(img)
    draw_text_psd_style(draw, ((W-w)/2+2 * (len(symb) - 1), (H-h)/2-14), symb, font=font, tracking=-25, leading=32, fill=(255,255,255))
    
    image = Image.new('RGB', (W, H), (0,0,0))
    draw = ImageDraw.Draw(image)
    _, _, w, h = draw.textbbox((0, 0), str(num), font=font2)
    draw = ImageDraw.Draw(img)
    subcolor = tuple(map(int, (((255,255,255) + color) // 2)))
    # print(subcolor)
    draw_text_psd_style(draw, ((W-w)/2+1 * (len(str(num)) - 1), (H-h)/2+75), str(num), font=font2, tracking=-25, leading=32, fill=subcolor)
    



    img.save('atom_render.png')
    img = cv2.cvtColor(cv2.imread('atom_render.png'), cv2.COLOR_RGB2BGR)
    img = cv2.GaussianBlur(img, (5, 5),cv2.BORDER_DEFAULT)
    img = cv2.resize(img, dsize=(76, 76))

    cv2.imwrite('img_gen/' + str(num) + '.png', cv2.cvtColor(img, cv2.COLOR_RGB2BGR))

    # print(np.shape(img))
    # atom_true = cv2.cvtColor(cv2.imread('img/' + str(num) + '.png'), cv2.COLOR_RGB2BGR)
    # cv2.imwrite('atom_true.png', cv2.cvtColor(atom_true * 5, cv2.COLOR_RGB2BGR))
    # cv2.imwrite('atom_diff_r.png', (img - atom_true)[:,:,2])
    # cv2.imwrite('atom_diff_g.png', (img - atom_true)[:,:,1])
    # cv2.imwrite('atom_diff_b.png', (img - atom_true)[:,:,0])

# for i in range(1, 7):
#     atom_true = cv2.cvtColor(cv2.imread('img/' + str(i) + '.png'), cv2.COLOR_RGB2BGR)
#     print(atom_true[38][19])
#     print(atom_colors[5:][i - 1])
#     print()
for i in range(1, 201):
    draw_atom(i)