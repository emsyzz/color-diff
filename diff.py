#!/usr/bin/env python

import sys
import PIL.Image as im
import math

img1 = im.open(sys.argv[1])
rgb_im1 = img1.convert('RGB')

w, h = img1.size[:2]

if len(sys.argv) > 2 and sys.argv[2] != '-':
    img2 = im.open(sys.argv[2])
    w2, h2 = img2.size[:2]
    if (h != h2 or w != w2):
        print "Image size differs"
        exit()
else:
    # make greyscale image of img1
    img2 = im.new('RGB', (w, h))
    im2P = img2.load()
    for y in range(0, h):
        for x in range(0, w):
            r, g, b = rgb_im1.getpixel((x, y))
            g = int(math.ceil((0.2126 * r) + (0.7152 * g) + (0.0722 * b)))
            im2P[x,y] = (g, g, g)

    img2.save('greyscale-'+ sys.argv[1], 'PNG');

rgb_im2 = img2.convert('RGB')

print w, h

proc = 1
if len(sys.argv) > 3:
    proc = float(sys.argv[3])

nearby = 0
if len(sys.argv) > 4:
    nearby = int(sys.argv[4])

def getColorDiff(im1, im2):
    r1, g1, b1 = im1
    r2, g2, b2 = im2
    rDiff = abs(r1 - r2) / 255.0
    gDiff = abs(g1 - g2) / 255.0
    bDiff = abs(b1 - b2) / 255.0
    colorDiff = (rDiff + gDiff + bDiff) / 3 * 100
    return colorDiff

def getColorDiffOf(rgb1, rgb2, xy):
    px1 = rgb1.getpixel(xy)
    px2 = rgb2.getpixel(xy)
    return getColorDiff(px1, px2)

def inRange(a, aD, b):
    return a + aD >= 0 and a + aD < b

def addNearbyToGroup(grp, rgb, xy, xyD, wh):
    rgb1, rgb2 = rgb
    x, y = xy
    xD, yD = xyD
    w, h = wh
    if inRange(x, xD, w) and inRange(y, yD, h):
        grp.append(getColorDiffOf(rgb1, rgb2, (x+xD, y+yD)))
    
imgF = im.new('RGBA', (w, h))
px = imgF.load()

i = 0
ix = 0
for y in range(0, h):
    for x in range(0, w):
        im1Px = rgb_im1.getpixel((x, y))
        im2Px = rgb_im2.getpixel((x, y))
        colorDiff = getColorDiff(im1Px, im2Px)
        if nearby > 0:
            grp = [colorDiff]
            if nearby >= 1:
                for xD, yD in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
                    addNearbyToGroup(grp, (rgb_im1, rgb_im2), (x, y), (xD, yD), (w-1, h-1))
            if nearby >= 2:
                for xD, yD in [(-2, 0), (0, -2), (2, 0), (0, 2), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
                    addNearbyToGroup(grp, (rgb_im1, rgb_im2), (x, y), (xD, yD), (w-1, h-1))
            if nearby >= 3:
                for xD, yD in [(-3, 0), (0, -3), (3, 0), (0, 3), (2, 1), (-2, -1), (2, -1), (-2, 1), (1, 2), (-1, -2), (1, -2), (-1, 2), (2, 2), (-2, -2), (2, -2), (-2, 2)]:
                    addNearbyToGroup(grp, (rgb_im1, rgb_im2), (x, y), (xD, yD), (w-1, h-1))
                
            colorDiff = sum(grp) / float(len(grp))
            
        ix = ix + 1
        if colorDiff <= proc:
            px[x,y] = im1Px


imgF.save('result.png', 'PNG', transparent=0)

print "Done!\nSee result.png"
