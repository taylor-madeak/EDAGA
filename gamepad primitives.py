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
    outline = ((295, 49), (326, 48), (351, 37), (357, 39), (356, 42), (369, 46), (381, 46), (404, 54), (411, 59),
                   (427, 105), (437, 141), (442, 167), (444, 184), (444, 195), (443, 207), (441, 215), (439, 221),
                   (436, 229), (430, 236), (423, 239), (415, 239), (404, 236), (391, 229), (383, 221), (376, 215),
                   (368, 207), (362, 200), (355, 195), (342, 188), (327, 184), (305, 182), (295, 181), (285, 182),
                   (263, 184), (248, 188), (235, 195), (228, 200), (222, 207), (214, 215), (207, 221), (199, 229),
                   (186, 236), (175, 239), (167, 239), (160, 236), (154, 229), (151, 221), (149, 215), (147, 207),
                   (146, 195), (146, 184), (148, 167), (153, 141), (163, 105), (179, 59), (186, 54), (209, 46),
                   (221, 46), (234, 42), (233, 39), (239, 37), (264, 48), (295, 49))

    r_bumper = ((356, 42), (361, 33), (373, 34), (379, 35), (385, 37), (391, 40), (396, 42), (405, 46), (405, 48),
               (408, 50), (408, 57), (404, 54), (381, 46), (369, 46))

    l_bumper = ((234, 42), (229, 33), (217, 34), (211, 35), (205, 37), (199, 40), (194, 42), (185, 46), (185, 48),
               (182, 50), (182, 57), (186, 54), (209, 46), (221, 46))

    l_trigger = ((215, 34), (215, 28), (217, 25), (219, 21), (230, 21), (232, 25), (233, 28), (234, 39), (232, 39),
                 (229, 33), (217, 34))

    r_trigger = ((375, 34), (375, 28), (373, 25), (371, 21), (360, 21), (358, 25), (357, 28), (356, 39), (358, 39),
                 (361, 33), (373, 34))

    pygame.gfxdraw.filled_polygon(screen, outline, CHARCOAL)
    pygame.gfxdraw.filled_polygon(screen, r_bumper, CHARCOAL)
    pygame.gfxdraw.filled_polygon(screen, l_bumper, CHARCOAL)
    pygame.gfxdraw.filled_polygon(screen, l_trigger, CHARCOAL)
    pygame.gfxdraw.filled_polygon(screen, r_trigger, CHARCOAL)
    pygame.gfxdraw.polygon(screen, outline, BLACK)
    pygame.gfxdraw.polygon(screen, r_bumper, BLACK)
    pygame.gfxdraw.polygon(screen, l_bumper, BLACK)
    pygame.gfxdraw.polygon(screen, l_trigger, BLACK)
    pygame.gfxdraw.polygon(screen, r_trigger, BLACK)


    # HOME button
    pygame.gfxdraw.aacircle(screen, 295, 93, 12, BLACK)

    # FACE BUTTONS
    pygame.gfxdraw.filled_circle(screen, 380, 74, 8, BLACK)  # Y BUTTON fill
    pygame.gfxdraw.aacircle(screen, 380, 74, 8, BLACK)  # Y BUTTON outline
    screen.blit(font.render('Y', True, YELLOW), (376, 66))  # Y BUTTON label

    pygame.gfxdraw.filled_circle(screen, 364, 91, 8, BLACK)  # X BUTTON fill
    pygame.gfxdraw.aacircle(screen, 364, 91, 8, BLACK)  # X BUTTON outline
    screen.blit(font.render('X', True, BLUE), (360, 83))  # X BUTTON label

    pygame.gfxdraw.filled_circle(screen, 397, 91, 8, BLACK)  # B BUTTON outline
    pygame.gfxdraw.aacircle(screen, 397, 91, 8, BLACK)  # B BUTTON outline
    screen.blit(font.render('B', True, RED), (393, 83))  # B BUTTON label

    pygame.gfxdraw.filled_circle(screen, 380, 107, 8, BLACK)  # A BUTTON outline
    pygame.gfxdraw.aacircle(screen, 380, 107, 8, BLACK)  # A BUTTON outline
    screen.blit(font.render('A', True, GREEN), (376, 99))  # A BUTTON label

    # START AND BACK
    pygame.gfxdraw.filled_circle(screen, 319, 93, 4, BLACK)  # START fill
    pygame.gfxdraw.aacircle(screen, 319, 93, 4, BLACK)  # START outline
    pygame.gfxdraw.filled_circle(screen, 271, 93, 4, BLACK)  # BACK fill
    pygame.gfxdraw.aacircle(screen, 271, 93, 4, BLACK)  # BACK outline


    # D-PAD
    pygame.gfxdraw.filled_circle(screen, 253, 142, 24, CHARCOAL)
    pygame.gfxdraw.aacircle(screen, 253, 142, 24, BLACK)
    pygame.gfxdraw.aaellipse(screen, 252, 144, 27, 31, BLACK)
    AAfilledRoundedRect(screen, (246, 120, 15, 46), BLACK)
    AAfilledRoundedRect(screen, (230, 136, 46, 15), BLACK)

    # LEFT JOYSTICK
    pygame.gfxdraw.filled_circle(screen, 210, 91, 17, BLACK)
    pygame.gfxdraw.filled_circle(screen, 210, 91, 13, CHARCOAL)
    pygame.gfxdraw.aacircle(screen, 210, 91, 13, BLACK)
    pygame.gfxdraw.aacircle(screen, 210, 91, 17, BLACK)
    pygame.gfxdraw.aacircle(screen, 210, 91, 24, BLACK)

    # RIGHT JOYSTICK
    pygame.gfxdraw.filled_circle(screen, 337, 142, 17, BLACK)
    pygame.gfxdraw.filled_circle(screen, 337, 142, 13, CHARCOAL)
    pygame.gfxdraw.aacircle(screen, 337, 142, 13, BLACK)
    pygame.gfxdraw.aacircle(screen, 337, 142, 17, BLACK)
    pygame.gfxdraw.aacircle(screen, 337, 142, 24, BLACK)
    pygame.gfxdraw.aaellipse(screen, 338, 144, 27, 31, BLACK)

    # DRAW POINTERS
    pygame.draw.lines(screen, MEDGRAY, False, ((364, 91), (364, 59), (459, 59)), 2)  # X BUTTON
    pygame.draw.line(screen, MEDGRAY, (380, 74), (459, 74), 2)  # Y BUTTON
    pygame.draw.line(screen, MEDGRAY, (397, 91), (459, 91), 2)  # B BUTTON
    pygame.draw.line(screen, MEDGRAY, (380, 107), (459, 107), 2)  # A BUTTON

    pygame.draw.lines(screen, MEDGRAY, False, ((267, 142), (267, 110), (131, 110)), 2)  # DPAD RIGHT
    pygame.draw.line(screen, MEDGRAY, (252, 125), (131, 125), 2)  # DPAD UP
    pygame.draw.line(screen, MEDGRAY, (240, 142), (131, 142), 2)  # DPAD LEFT
    pygame.draw.line(screen, MEDGRAY, (252, 160), (131, 160), 2)  # DPAD DOWN

    pygame.draw.line(screen, MEDGRAY, (337, 142), (459, 142), 2)  # RIGHT STICK AXIS
    pygame.draw.lines(screen, MEDGRAY, False, ((413, 142), (413, 166), (459, 166)), 2)  # RIGHT STICK BUTTON
    pygame.draw.line(screen, MEDGRAY, (210, 91), (131, 91), 2) # LEFT STICK AXIS
    pygame.draw.lines(screen, MEDGRAY, False, ((176, 91), (176, 67), (131, 67)), 2) # LEFT STICK BUTTON

    pygame.draw.line(screen, MEDGRAY, (319, 93), (319, 35), 2) # START
    pygame.draw.line(screen, MEDGRAY, (271, 93), (271, 35), 2) # BACK

    pygame.draw.line(screen, MEDGRAY, (364, 30), (459, 30), 2) # RIGHT TRIGGER
    pygame.draw.line(screen, MEDGRAY, (394, 45), (459, 45), 2)# RIGHT BUMPER
    pygame.draw.line(screen, MEDGRAY, (226, 30), (131, 30), 2) # LEFT TRIGGER
    pygame.draw.line(screen, MEDGRAY, (196, 45), (131, 45), 2) # LEFT BUMPER


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