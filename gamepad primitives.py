from pygame import *
from pygame.locals import *
import pygame.gfxdraw

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PINK = (238, 48, 167)
GREEN = (61, 145, 64)
RED = (255, 48, 48)
BLUE = (113, 113, 198)
YELLOW = (255, 255, 0)
CHARCOAL = (40, 40, 40)
MEDGRAY = (160, 160, 160)

PI = 3.141592653

pygame.init()

scr_size = (600, 260)
screen = pygame.display.set_mode(scr_size)

done = False
clock = pygame.time.Clock()

def AAfilledRoundedRect(surface,rect,color,radius=0.4):

    """
    AAfilledRoundedRect(surface,rect,color,radius=0.4)

    surface : destination
    rect    : rectangle
    color   : rgb or rgba
    radius  : 0 <= radius <= 1
    """

    rect         = Rect(rect)
    color        = Color(*color)
    alpha        = color.a
    color.a      = 0
    pos          = rect.topleft
    rect.topleft = 0,0
    rectangle    = Surface(rect.size,SRCALPHA)

    circle       = Surface([min(rect.size)*3]*2,SRCALPHA)
    draw.ellipse(circle,(0,0,0),circle.get_rect(),0)
    circle       = transform.smoothscale(circle,[int(min(rect.size)*radius)]*2)

    radius              = rectangle.blit(circle,(0,0))
    radius.bottomright  = rect.bottomright
    rectangle.blit(circle,radius)
    radius.topright     = rect.topright
    rectangle.blit(circle,radius)
    radius.bottomleft   = rect.bottomleft
    rectangle.blit(circle,radius)

    rectangle.fill((0,0,0),rect.inflate(-radius.w,0))
    rectangle.fill((0,0,0),rect.inflate(0,-radius.h))

    rectangle.fill(color,special_flags=BLEND_RGBA_MAX)
    rectangle.fill((255,255,255,alpha),special_flags=BLEND_RGBA_MIN)

    return surface.blit(rectangle,pos)


def aspect_scale(surface, size):
    # This function obtained from the Pygame code repository, credit to Frank Raiser.
    # Modified by me to work with Python 3, which does not support tuple argument unpacking.
    # This works well for upscaling, not so hot for downscaling.

    """
    Scales 'img' to fit into box (bx, by).
    This method will retain the original image's aspect ratio

    aspect_scale(surface, size)

    surface :   Surface Source.
    size    :   Tuple Desired size.

    """

    bx = size[0]
    by = size[1]

    ix = surface.get_size()[0]
    iy = surface.get_size()[1]

    if ix > iy:
        # fit to width
        scale_factor = bx /float(ix)
        sy = scale_factor * iy
        if sy > by:
            scale_factor = by/float(iy)
            sx = scale_factor * ix
            sy = by
        else:
            sx = bx
    else:
        # fit to height
        scale_factor = by/float(iy)
        sx = scale_factor * ix
        if sx > bx:
            scale_factor = bx/float(ix)
            sx = bx
            sy = scale_factor * iy
        else:
            sy = by

    return pygame.transform.scale(surface, (int(sx), int(sy)))


def drawGP():
    font = pygame.font.SysFont('Arial', 14, bold=True)

    # BACKGROUND
    screen.fill(WHITE)
    outline = ((300, 81), (275, 81), (270, 79), (268, 78), (240, 48), (237, 46), (225, 46), (217, 48), (206, 51),
               (195, 56), (181, 63), (178, 65), (177, 67), (174, 71), (140, 174), (139, 180), (138, 185), (137, 191),
               (136, 195), (136, 215), (138, 220), (142, 232), (149, 242), (153, 245), (162, 250), (168, 252),
               (172, 252), (231, 198), (239, 196), (361, 196), (369, 198), (428, 252), (432, 252), (438, 250),
               (447, 245), (451, 242), (458, 232), (462, 220), (464, 215), (464, 195), (463, 191), (462, 185),
               (461, 180), (460, 174), (426, 71), (423, 67), (422, 65), (419, 63), (405, 56), (394, 51), (383, 48),
               (375, 46), (363, 46), (360, 48), (332, 78), (330, 79), (325, 81), (300, 81))

    top = ((300, 81), (275, 81), (270, 79), (268, 78), (249, 57), (256, 41), (344, 41), (351, 57), (332, 78), (330, 79), (325, 81), (300, 81))
    l_button = ((249, 57), (256, 41), (247, 35), (244, 34), (241, 33), (228, 33), (223, 34), (218, 36), (191, 48),
                (188, 50), (186, 53), (185, 60), (217, 48), (237, 46))
    r_button = ((351, 57), (344, 41), (353, 35), (356, 34), (359, 33), (372, 33), (377, 34), (382, 36), (409, 48),
                (412, 50), (414, 53), (415, 60), (383, 48), (375, 46), (363, 46))

    pygame.gfxdraw.filled_polygon(screen, outline, CHARCOAL)
    pygame.gfxdraw.filled_polygon(screen, l_button, CHARCOAL)
    pygame.gfxdraw.filled_polygon(screen, r_button, CHARCOAL)
    pygame.gfxdraw.filled_polygon(screen, top, CHARCOAL)
    pygame.gfxdraw.polygon(screen, top, BLACK)
    pygame.gfxdraw.polygon(screen, l_button, BLACK)
    pygame.gfxdraw.polygon(screen, r_button, BLACK)
    pygame.gfxdraw.polygon(screen, outline, BLACK)

    # HOME button
    pygame.gfxdraw.aacircle(screen, 300, 62, 15, BLACK)

    # FACE BUTTONS
    pygame.gfxdraw.filled_circle(screen, 384, 77, 11, BLACK)  # Y BUTTON fill
    pygame.gfxdraw.aacircle(screen, 384, 77, 11, BLACK)  # Y BUTTON outline
    screen.blit(font.render('Y', True, YELLOW), (380, 69))  # Y BUTTON label

    pygame.gfxdraw.filled_circle(screen, 361, 99, 11, BLACK)  # X BUTTON fill
    pygame.gfxdraw.aacircle(screen, 361, 99, 11, BLACK)  # X BUTTON outline
    screen.blit(font.render('X', True, BLUE), (357, 91))  # X BUTTON label

    pygame.gfxdraw.filled_circle(screen, 407, 99, 11, BLACK)  # B BUTTON outline
    pygame.gfxdraw.aacircle(screen, 407, 99, 11, BLACK)  # B BUTTON outline
    screen.blit(font.render('B', True, RED), (403, 91))  # B BUTTON label

    pygame.gfxdraw.filled_circle(screen, 384, 122, 11, BLACK)  # A BUTTON outline
    pygame.gfxdraw.aacircle(screen, 384, 122, 11, BLACK)  # A BUTTON outline
    screen.blit(font.render('A', True, GREEN), (380, 114))  # A BUTTON label

    # START AND BACK
    pygame.gfxdraw.filled_circle(screen, 324, 99, 7, BLACK)  # MENU fill
    pygame.gfxdraw.aacircle(screen, 324, 99, 7, BLACK)  # MENU outline
    # MENU label
    x = 321
    y = 97
    for i in range(3):
        pygame.gfxdraw.hline(screen, x, x + 6, y, WHITE)
        y += 2

    pygame.gfxdraw.filled_circle(screen, 277, 99, 7, BLACK)  # VIEW fill
    pygame.gfxdraw.aacircle(screen, 277, 99, 7, BLACK)  # VIEW outline
    # VIEW label
    pygame.gfxdraw.rectangle(screen, (274, 96, 5, 5), WHITE)
    pygame.gfxdraw.rectangle(screen, (276, 98, 5, 5), WHITE)


    # D-PAD
    pygame.gfxdraw.aacircle(screen, 258, 152, 27, BLACK)
    AAfilledRoundedRect(screen, (250, 128, 17, 49), BLACK)
    AAfilledRoundedRect(screen, (234, 144, 49, 17), BLACK)

    # LEFT JOYSTICK
    pygame.gfxdraw.filled_circle(screen, 218, 99, 27, BLACK)
    pygame.gfxdraw.filled_circle(screen, 218, 99, 19, CHARCOAL)
    pygame.gfxdraw.aacircle(screen, 218, 99, 27, BLACK)
    pygame.gfxdraw.aacircle(screen, 218, 99, 19, BLACK)

    # RIGHT JOYSTICK
    pygame.gfxdraw.filled_circle(screen, 343, 149, 27, BLACK)
    pygame.gfxdraw.filled_circle(screen, 343, 149, 19, CHARCOAL)
    pygame.gfxdraw.aacircle(screen, 343, 149, 27, BLACK)
    pygame.gfxdraw.aacircle(screen, 343, 149, 19, BLACK)

    # DRAW POINTERS
    pygame.draw.lines(screen, MEDGRAY, False, ((361, 99), (361, 55), (485, 55)), 2)  # X BUTTON
    pygame.draw.line(screen, MEDGRAY, (384, 77), (485, 77), 2)  # Y BUTTON
    pygame.draw.line(screen, MEDGRAY, (407, 99), (485, 99), 2)  # B BUTTON
    pygame.draw.line(screen, MEDGRAY, (384, 122), (485, 122), 2)  # A BUTTON

    pygame.draw.lines(screen, MEDGRAY, False, ((275, 153), (275, 114), (117, 114)), 2)  # DPAD RIGHT
    pygame.draw.line(screen, MEDGRAY, (258, 134), (117, 134), 2)  # DPAD UP
    pygame.draw.line(screen, MEDGRAY, (241, 153), (117, 153), 2)  # DPAD LEFT
    pygame.draw.line(screen, MEDGRAY, (258, 173), (117, 173), 2)  # DPAD DOWN

    pygame.draw.line(screen, MEDGRAY, (343, 149), (485, 149), 2)  # RIGHT STICK AXIS
    pygame.draw.lines(screen, MEDGRAY, False, ((430, 149), (430, 179), (485, 179)), 2)  # RIGHT STICK BUTTON
    pygame.draw.line(screen, MEDGRAY, (218, 99), (117, 99), 2) # LEFT STICK AXIS
    pygame.draw.lines(screen, MEDGRAY, False, ((180, 99), (180, 69), (117, 69)), 2) # LEFT STICK BUTTON

    pygame.draw.line(screen, MEDGRAY, (324, 99), (324, 25), 2) # MENU
    pygame.draw.line(screen, MEDGRAY, (277, 99), (277, 25), 2) # VIEW

    pygame.draw.lines(screen, MEDGRAY, False, ((365, 30), (365, 20), (435, 20)), 2) # RIGHT TRIGGER
    pygame.draw.line(screen, MEDGRAY, (375, 40), (485, 40), 2)# RIGHT BUMPER
    pygame.draw.lines(screen, MEDGRAY, False, ((235, 30), (235, 20), (167, 20)), 2) # LEFT TRIGGER
    pygame.draw.line(screen, MEDGRAY, (225, 40), (117, 40), 2) # LEFT BUMPER


drawGP()
pygame.display.flip()

while not done:

    #screen1 = screen.copy()
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

        # elif event.type == VIDEORESIZE:
        #     scr_size = event.dict['size']
        #     screen = pygame.display.set_mode(scr_size, RESIZABLE)
        #     screen.blit(aspect_scale(screen1, scr_size), (0, 0))
        #     pygame.display.flip()

    clock.tick(5)