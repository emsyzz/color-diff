#!/usr/bin/python

import sys
import PIL.Image as im
import math

img1 = im.open(sys.argv[1])
img2 = im.open(sys.argv[2])

proc = 1
if len(sys.argv) > 3:
    proc = float(sys.argv[3])

h1, w1 = img1.size[:2]
h2, w2 = img2.size[:2]

if (h1 != h2 or w1 != w2):
    print "Image size differs"
    exit()
else :
    w = w1
    h = h1
    
imgF = im.new('RGBA', (h, w))
px = imgF.load()

for y in range(0, w):
    for x in range(0, h):
        rgb_im1 = img1.convert('RGB')
        rgb_im2 = img2.convert('RGB')
        r1, g1, b1 = rgb_im1.getpixel((x, y))
        r2, g2, b2 = rgb_im2.getpixel((x, y))
        rDiff = abs(r1 - r2) / 255.0
        gDiff = abs(g1 - g2) / 255.0
        bDiff = abs(b1 - b2) / 255.0
        colorDiff = (rDiff + gDiff + bDiff) / 3 * 100
        if colorDiff < proc:
            px[x,y] = (r1, g1, b1)


imgF.save('result.png', 'PNG', transparent=0)

print "Done"