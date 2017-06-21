#!/usr/bin/env python

import sys
import random
import PIL.Image as Im
import math
from time import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('input')
parser.add_argument('-O', '--output', default='result.png')
parser.add_argument('-f', '--filter', default=['greyscale'], nargs='+')
parser.add_argument('-a', '--filter_argument', default=None, action='append')
parser.add_argument('-p', '--percent-diff', default=1, type=float)
parser.add_argument('-r', '--radius', default=0, type=int)
parser.add_argument('-o', '--output-pixel-filter', default=None)
parser.add_argument('-i', '--invert', action='store_true')
parser.add_argument('-v', '--verbose', action='store_true')
args = parser.parse_args()

startTime = time()

random.seed()

img1 = Im.open(args.input)
rgb_im1 = img1.convert('RGB')

w, h = img1.size[:2]


def print_output(i_str, i_args=()):
    print i_str % i_args
    sys.stdout.flush()


def get_filtered_image(i_input, i_filter='greyscale', i_arg=None):
    in_w, in_h = i_input.size[:2]
    img2 = Im.new('RGB', (in_w, in_h))
    im2p = img2.load()
    
    for loop_y in range(0, in_h):
        for loop_x in range(0, in_w):
            r, g, b = i_input.getpixel((loop_x, loop_y))
            g = int(math.ceil((0.2126 * r) + (0.7152 * g) + (0.0722 * b)))
            v_tuple = (r, g, b)

            if i_filter == 'none':
                v_tuple = r, g, b
            elif i_filter == 'greyscale':
                v_tuple = filter_greyscale(r, g, b)
            elif i_filter == 'invert':
                v_tuple = filter_invert(r, g, b)
            elif i_filter == 'noise':
                v_tuple = filter_random_noise(r, g, b, i_arg)
            elif i_filter == 'blur':
                v_tuple = filter_blur(loop_x, loop_y, i_input, i_arg)
            else:
                print "Image filter %s is not present" % i_filter
                exit(1)

            im2p[loop_x, loop_y] = v_tuple
    
    return img2.convert('RGB')


def get_output_pixel((r, g, b), i_filter=None):
    
    if i_filter is None:
        return r, g, b
    elif i_filter == 'grey':
        return 128, 128, 128
    else:
        print "Output pixel filter %s is not available" % i_filter
        exit(2)
    

def filter_greyscale(r, g, b):
    g = int(math.ceil((0.2126 * r) + (0.7152 * g) + (0.0722 * b)))
    return g, g, g
    
    
def filter_invert(r, g, b):
    r = max([r, 255]) - min([r, 255])
    g = max([g, 255]) - min([g, 255])
    b = max([b, 255]) - min([b, 255])
    
    return r, g, b


def filter_random_noise(r, g, b, context_var=None):
    amplify = 0.3
    if context_var is not None:
        amplify = float(context_var)
    return (random.randrange(int(r * amplify), 255),
            random.randrange(int(g * amplify), 255),
            random.randrange(int(b * amplify), 255))


def filter_blur(i_x, i_y, i_img, context_var=None):
    blur_radius = 0
    if context_var is not None:
        blur_radius = int(context_var)
    if blur_radius > 0:
        avg_r = []
        avg_g = []
        avg_b = []
        for d_x, d_y in get_circle_points(blur_radius):
            p_w, p_h = i_img.size[:2]
            t_x = i_x + d_x
            t_y = i_y + d_y
            if 0 <= t_x < p_w and 0 <= t_y < p_h:
                u_r, u_g, u_b = i_img.getpixel((i_x + d_x, i_y + d_y))
                avg_r.append(u_r)
                avg_g.append(u_g)
                avg_b.append(u_b)

        return int(sum(avg_r) / len(avg_r)), int(sum(avg_g) / len(avg_g)), int(sum(avg_b) / len(avg_b))
    org_r, org_g, org_b = i_img.getpixel((i_x, i_y))
    return org_r, org_g, org_b


def diff_colors(im1, im2):
    return diff_colors_rgb(im1, im2)
    # return diff_colors_hsl(im1, im2)
    
    
def diff_colors_hsl(im1, im2):
    r1, g1, b1 = im1
    r2, g2, b2 = im2
    rgb1 = [r1, g1, b1]
    rgb2 = [r2, g2, b2]
    im1l = (max(rgb1) - min(rgb1)) / 2
    im2l = (max(rgb2) - min(rgb2)) / 2
    
    return abs(im1l - im2l) / 255.0

    
def diff_colors_rgb(im1, im2):
    r1, g1, b1 = im1
    r2, g2, b2 = im2
    r_diff = max([r1, r2]) - min([r1, r2])
    g_diff = max([g1, g2]) - min([g1, g2])
    b_diff = max([b1, b2]) - min([b1, b2])
    col_vol = (r_diff+1) * (g_diff+1) * (b_diff+1)
    total_vol = (255+1 * 255+1 * 255+1) / 1.0
    return (100 - (((total_vol - col_vol) / ((total_vol + col_vol) / 2)) * 50)) / 2

    
def diff_colors_xy(rgb1, rgb2, xy):
    px1 = rgb1.getpixel(xy)
    px2 = rgb2.getpixel(xy)
    return diff_colors(px1, px2)

    
def is_in_range(i_a, a_d, i_b):
    return 0 <= i_a + a_d < i_b


def add_nearby_to_group(i_grp, rgb, xy, xy_d, wh):
    rgb_1, rgb_2 = rgb
    v_x, v_y = xy
    x_d, y_d = xy_d
    v_w, v_h = wh
    if is_in_range(v_x, x_d, v_w) and is_in_range(v_y, y_d, v_h):
        i_grp.append(diff_colors_xy(rgb_1, rgb_2, (v_x + x_d, v_y + y_d)))
    
    
def get_circle_points(i_radius):
    points = set([])
    for v_i in range(1, i_radius+1):
        v_x = v_i
        v_y = 0
        v_d = 1 - v_x
        while v_x >= v_y:
            points.add((v_x + 0, v_y + 0))
            points.add((v_x + 0, -v_y + 0))
            points.add((-v_x + 0, v_y + 0))
            points.add((-v_x + 0, -v_y + 0))
            
            points.add((v_y + 0, v_x + 0))
            points.add((v_y + 0, -v_x + 0))
            points.add((-v_y + 0, v_x + 0))
            points.add((-v_y + 0, -v_x + 0))
            v_y += 1
            if v_d <= 0:
                v_d += 2 * v_y + 1
            else:
                v_x -= 1
                v_d += 2 * (v_y - v_x) + 1
    
    return list(points)
    
    
def set_alpha(color, i_alpha):
    r, g, b = color
    return r, g, b, i_alpha


f_ix = 0
rgb_im2 = get_filtered_image(rgb_im1, 'none')
for im_filter in args.filter:
    if args.verbose:
        print_output("Applying filter: %s...", (im_filter,))
    rgb_im2 = get_filtered_image(rgb_im2, im_filter, args.filter_argument[f_ix])
    f_ix += 1
    
imgF = Im.new('RGBA', (w * 3, h))
px = imgF.load()

dI = 0
counter = 0
for y in range(0, h):
    for x in range(0, w):
        im1Px = rgb_im1.getpixel((x, y))
        im2Px = rgb_im2.getpixel((x, y))
        
        px[x, y] = im1Px
        px[x+(2*w), y] = im2Px
        
radius = args.radius
c = (radius + 1)

if args.verbose:
    print_output("Differencing colors...")

for i in range(0, c):
    for y in range(0, h):
        for x in range(0, w):
            iDr = radius - i
            iDa = i
            c1 = c / 1.0
            alpha = (c1 - iDa) / c1
            a = int(255 * alpha)
            pxVal = px[x+w, y]
            pxR, pxG, pxB, pxA = pxVal
            if pxVal == (0, 0, 0, 0):
                im1Px = rgb_im1.getpixel((x, y))
                im2Px = rgb_im2.getpixel((x, y))
                colorDiff = 100
                colorDiffPx = diff_colors(im1Px, im2Px)
                    
                if iDr > 0:
                    circleColorDiff = []
                    grp = [colorDiffPx]
                    for xD, yD in get_circle_points(iDr):
                        add_nearby_to_group(grp, (rgb_im1, rgb_im2), (x, y), (xD, yD), (w - 1, h - 1))
                            
                    colorDiff = sum(grp) / float(len(grp))
                else:
                    colorDiff = colorDiffPx
                    
                diffDir = False
                if args.invert:
                    diffDir = colorDiff > args.percent_diff
                else:
                    diffDir = colorDiff <= args.percent_diff
                    
                if diffDir:
                    counter += 1
                    pxColor = get_output_pixel(im1Px, args.output_pixel_filter)
                        
                    px[x+w, y] = set_alpha(pxColor, a)
                
                    if i == 0:
                        dI += dI


imgF.save(args.output, 'PNG', transparent=0)

color_percent = ((w * h - dI) / ((w * h) * 0.01))

if args.verbose:
    print "Process took %.4f seconds and filled %d of %d pixels" % (time() - startTime, counter, (w * h))
    print "Image is %.2f%% colorful, tolerating %.2f%% difference " \
          "and using %dpx feather brush" % (color_percent, args.percent_diff, radius)
    print "See %s" % args.output

exit(0)  # process successful
