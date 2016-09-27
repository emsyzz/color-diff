#!/usr/bin/env python

import sys
import PIL.Image as im
import math
from time import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('input')
parser.add_argument('-O', '--output', default='result.png')
parser.add_argument('-f', '--filter', default='greyscale')
parser.add_argument('-p', '--percent-diff', default=1, type=float)
parser.add_argument('-r', '--radius', default=0, type=int)
parser.add_argument('-m', '--mix-colors', action='store_true')
parser.add_argument('-i', '--invert', action='store_true')
parser.add_argument('-v', '--verbose', action='store_true')
args = parser.parse_args()

startTime = time()

img1 = im.open(args.input)
rgb_im1 = img1.convert('RGB')

w, h = img1.size[:2]

def getFilteredImage(input, filter='greyscale'):
    inW, inH = input.size[:2]
    img2 = im.new('RGB', (inW, inH))
    im2P = img2.load()
    
    for y in range(0, inH):
        for x in range(0, inW):
            r, g, b = rgb_im1.getpixel((x, y))
            g = int(math.ceil((0.2126 * r) + (0.7152 * g) + (0.0722 * b)))
            tuple = (r, g, b)
            
            if filter == 'greyscale':
                tuple = filterGreyscale(r, g, b)
            elif filter == 'invert':
                tuple = filterInvert(r, g, b)
            else:
                print "Filter %s is not present" % filter
                exit()
            
            im2P[x,y] = tuple
    
    return img2.convert('RGB')


def filterGreyscale(r, g, b):
    g = int(math.ceil((0.2126 * r) + (0.7152 * g) + (0.0722 * b)))
    return (g, g, g)
    
    
def filterInvert(r, g, b):
    r = max([r, 255]) - min([r, 255])
    g = max([g, 255]) - min([g, 255])
    b = max([b, 255]) - min([b, 255])
    
    return (r, g, b)

def getColorDiff(im1, im2):
    return getRGBColorDiff(im1, im2)
    #return getHSLColorDiff(im1, im2)
    
    
def getHSLColorDiff(im1, im2):
    r1, g1, b1 = im1
    r2, g2, b2 = im2
    rgb1 = [r1, g1, b1]
    rgb2 = [r2, g2, b2]
    im1L = (max(rgb1) - min(rgb1)) / 2
    im2L = (max(rgb2) - min(rgb2)) / 2
    
    return abs(im1L - im2L) / 255.0

    
def getRGBColorDiff(im1, im2):
    r1, g1, b1 = im1
    r2, g2, b2 = im2
    rDiff = max([r1, r2]) - min([r1, r2])
    gDiff = max([g1, g2]) - min([g1, g2])
    bDiff = max([b1, b2]) - min([b1, b2])
    colVol = (rDiff+1) * (gDiff+1) * (bDiff+1)
    if args.verbose:
        print 255+1*255+1*255+1, colVol, "rgb:", rDiff, gDiff, bDiff
    totalVol = (255+1 * 255+1 * 255+1) / 1.0
    colorDiff = (100 - (((totalVol - colVol) / ((totalVol + colVol) / 2)) * 50)) / 2
    if args.verbose:
        print "%.f2%%" % colorDiff
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
    
    
def getCirclePoints(radius):
    points = set([])
    for i in range(1, radius+1):
        x = i
        y = 0
        d = 1 - x
        while x >= y:
            points.add(( x + 0,  y + 0))
            points.add(( x + 0, -y + 0))
            points.add((-x + 0,  y + 0))
            points.add((-x + 0, -y + 0))
            
            points.add(( y + 0,  x + 0))
            points.add(( y + 0, -x + 0))
            points.add((-y + 0,  x + 0))
            points.add((-y + 0, -x + 0))
            y = y + 1
            if d <= 0:
                d = d + (2 * y + 1)
            else:
                x = x - 1
                d = d + (2 * (y - x) + 1)
    
    return list(points)
    
    
def setAlpha(color, alpha):
    r,g,b = color
    return (r, g, b, alpha)
    
    
rgb_im2 = getFilteredImage(rgb_im1, args.filter)
    
imgF = im.new('RGBA', (w * 3, h))
px = imgF.load()

dI = 0
counter = 0
for y in range(0, h):
    for x in range(0, w):
        im1Px = rgb_im1.getpixel((x, y))
        im2Px = rgb_im2.getpixel((x, y))
        
        px[x,y] = im1Px
        px[x+(2*w), y] = im2Px
        
radius = args.radius
c = (radius + 1)

for i in range(0, c):
    for y in range(0, h):
        for x in range(0, w):
            iDr = radius - i
            iDa = i
            c1 = c / 1.0
            alpha = (c1 - iDa) / c1
            a = int(255 * alpha)
            pxVal = px[x+w,y]
            pxR, pxG, pxB, pxA = pxVal
            if pxVal == (0,0,0,0):
                im1Px = rgb_im1.getpixel((x, y))
                im2Px = rgb_im2.getpixel((x, y))
                colorDiff = 100
                colorDiffPx = getColorDiff(im1Px, im2Px)
                    
                if iDr > 0:
                    circleColorDiff = []
                    grp = [colorDiffPx]
                    for xD, yD in getCirclePoints(iDr):
                        addNearbyToGroup(grp, (rgb_im1, rgb_im2), (x, y), (xD, yD), (w-1, h-1))
                            
                    colorDiff = sum(grp) / float(len(grp))
                else:
                    colorDiff = colorDiffPx
                    
                diffDir = False
                if args.invert:
                    diffDir = colorDiff > args.percent_diff
                else:
                    diffDir = colorDiff <= args.percent_diff
                    
                if diffDir:
                    counter = counter + 1
                    if args.mix_colors:
                        x1R, x1G, x1B = im1Px
                        x2R, x2G, x2B = im2Px
                        pxColor = ((x1R + x2R) / 2, (x1G + x2G) / 2, (x1B + x2B) / 2)
                    else:
                        pxColor = im1Px
                        
                    px[x+w,y] = setAlpha(pxColor, a)
                
                    if i == 0:
                        dI = dI + 1


imgF.save(args.output, 'PNG', transparent=0)

colorProc = ((w * h - dI) / ((w * h) * 0.01))

print "Process took %.4f seconds and filled %d of %d pixels" % (time() - startTime, counter, (w * h))
print "Image is %.2f%% colorful, allowing %.2f%% difference and using %dpx brush" % (colorProc, args.percent_diff, radius)
print "See %s" % args.output
