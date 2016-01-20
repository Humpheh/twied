import numpy as np
from PIL import Image, ImageDraw

show = True
scale = 4

from polyexample import dict as d
#polygon = np.array([(0,0), (180,0), (180, 180), (0, 180)]) * 2
#polygon = np.array(d[2]) * 2

d.append([(-180,-90), (-1,1), (1,1), (1,-1)])

width = 360 * scale
height = 180 * scale

img = Image.new('1' if show else 'L', (width, height), 0)

for i in d:
    polygon = [((p[0] + 180) * scale, (-p[1] + 90) * scale) for p in i]
    ImageDraw.Draw(img).polygon(polygon, outline=1, fill=1)
mask = np.array(img)

img.show()

print(mask)
print(sum(mask))