import tkinter
import tkinter.filedialog
import xml.etree.ElementTree as ET
import os

from pygame import *
from pygame.locals import *
import pygame.gfxdraw

### GAMEPAD TYPE ###
# Modify this to set gamepad type.  Supported values:
# 'ps3', 'ps4'
gamepad_type = 'ps4'

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CHARCOAL = (40, 40, 40)
MEDGRAY = (160, 160, 160)
PINK = (238, 48, 167, 128)  # Four values because gfxdraw supports alpha
GREEN = (61, 145, 64, 128)  # Four values because gfxdraw supports alpha
RED = (255, 48, 48, 128)  # Four values because gfxdraw supports alpha
BLUE = (113, 113, 198, 128)  # Four values because gfxdraw supports alpha


class Button():

    def __init__(self, my_screen, label, position, label_color, align='right', buttonhighlight=None):
        self.my_screen = my_screen
        self.label = label
        self.position = position
        self.color = label_color
        self.align = align
        self.highlight = buttonhighlight
        self.font = pygame.font.Font(None, 15)

    def printout(self):

        self.text_bitmap = self.font.render(str(self.label), True, self.color)

        if self.align == 'left':
            self.position  = ((self.position[0] - self.text_bitmap.get_width()), self.position[1])

        elif self.align == 'center':
            self.position = ((self.position[0] - int(self.text_bitmap.get_width() / 2)), self.position[1])

        else:
            self.position = self.position

        self.my_screen.blit(self.text_bitmap, self.position)

    def update(self, newLabel, newColor):
        self.color = newColor
        self.label = newLabel


class BindsHandler():
    # TODO: Add alias replacements for some of the binds that make little sense to Joe User.
    """
    BindsHandler(tree, key, <modifier>): return String

    tree        :   xml.ElemenTree object
    key         :   STRING Gamepad keybind to search for
    modifier    :   STRING Modifier (shift) gamepad keybind to search for; defaults to "None"
    """

    def __init__(self, tree, key, modifier=None):
        self.label = self.setLabel(tree, key, modifier)

    def setLabel(self, tree, key, modifier=None):

        tag = ''

        for bind in tree:
            # skip UI and Cam context
            if bind.tag.startswith('UI_') \
                    or bind.tag.endswith("_Landing") \
                    or bind.tag == "CycleNextPanel" \
                    or bind.tag == "CyclePreviousPanel"\
                    or bind.tag.startswith('Cam'):
                continue

            else:
                # drill down for devices
                devlist = list(bind)
                for device in devlist:
                    if device.get('Key') == key:
                        # drill down again and check for modifiers
                        modlist = list(device)  # returns a list, no matter what
                        if not modifier and len(modlist) < 1:
                            # if no modlist, and no modifier supplied, then we found our element
                            tag = bind.tag
                            break
                        elif modifier and len(modlist) > 0:
                            # if a modifier wss supplied and modlist is populated, check for match
                            for mod in modlist:
                                if mod.get('Key') == modifier:
                                    # if match, we found our element
                                    tag = bind.tag
                                    break

        # Replace some of the more eclectic names with more CMDR-friendly ones
        if tag.endswith('_Landing'):
            tag = tag.replace('_Landing', ' (Landing)')

        elif tag == 'ForwardKey':
            tag = 'IncreaseThrottle'

        elif tag == 'BackwardKey':
            tag = 'DecreaseThrottle'

        elif tag == 'HyperSuperCombination':
            tag = 'FrameshiftDrive'

        elif tag == 'DisableRotationCorrectToggle':
            tag = 'FlightAssistToggle'

        return tag

    def __str__(self):
        return self.label

    def __len__(self):
        return len(self.label)


class GamepadImage():
    # Fills the background with a drawn image of the controller.
    # TODO: Expand this to support XB360/Xbone gamepads.  Also, figure out how to link & center

    """
    GamepadImage(surface, gamepad)

    surface :   Destination surface
    gamepad :   STRING Gamepad type, currently supported: [ps3, ps4]
    """

    def __init__(self, surface, gamepad):
        self.gamepad = gamepad.lower()
        self.screen = surface            
        # Internal button location dict
        if gamepad == 'ps3':
            self.face_buttons = dict(
                btn_3=(362, 89), btn_2=(338, 113), btn_1=(386, 113), btn_0=(362, 137)
            )
            
        elif gamepad == 'ps4':
            self.face_buttons = dict(
                btn_3=(368, 101), btn_2=(346, 122), btn_1=(389, 122), btn_0=(368, 144)
            )

    def __AAfilledRoundedRect(self, surface, rect, color, radius=0.4):
        # Borrowed from pygame.org website.  Credit goes to Joel Murielle.

        """
        AAfilledRoundedRect(surface,rect,color,radius=0.4)

        surface : destination
        rect    : rectangle
        color   : rgb or rgba
        radius  : 0 <= radius <= 1
        """

        rect = Rect(rect)
        color = Color(*color)
        alpha = color.a
        color.a = 0
        pos = rect.topleft
        rect.topleft = 0, 0
        rectangle = Surface(rect.size, SRCALPHA)

        circle = Surface([min(rect.size) * 3] * 2, SRCALPHA)
        draw.ellipse(circle, (0, 0, 0), circle.get_rect(), 0)
        circle = transform.smoothscale(circle, [int(min(rect.size) * radius)] * 2)

        radius = rectangle.blit(circle, (0, 0))
        radius.bottomright = rect.bottomright
        rectangle.blit(circle, radius)
        radius.topright = rect.topright
        rectangle.blit(circle, radius)
        radius.bottomleft = rect.bottomleft
        rectangle.blit(circle, radius)

        rectangle.fill((0, 0, 0), rect.inflate(-radius.w, 0))
        rectangle.fill((0, 0, 0), rect.inflate(0, -radius.h))

        rectangle.fill(color, special_flags=BLEND_RGBA_MAX)
        rectangle.fill((255, 255, 255, alpha), special_flags=BLEND_RGBA_MIN)

        return surface.blit(rectangle, pos)


    def drawBG(self):
        # TODO: Create variables and functions for label positions to enable repositioning based on gamepad type.
        PI = 3.141592653
        self.screen.fill(WHITE)

        if self.gamepad == "ps3":
            
            ### PS3 GAMEPAD ###
            # OVERALL SHAPE
            pygame.draw.rect(self.screen, CHARCOAL, (179, 66, 184, 102))  # BACKGROUND rectangle
            pygame.draw.polygon(self.screen, CHARCOAL, [[122, 187], [128, 111], [204, 164], [175, 206]])  # LEFT HANDLE polygon
            pygame.draw.ellipse(self.screen, CHARCOAL, (122, 156, 62, 62))  # LEFT HANDLE circle
            pygame.draw.polygon(self.screen, CHARCOAL, [[415, 187], [408, 111], [337, 164], [363, 206]])  # RIGHT HANDLE polygon
            pygame.draw.ellipse(self.screen, CHARCOAL, (353, 154, 62, 62))  # RIGHT HANDLE circle
            pygame.draw.ellipse(self.screen, CHARCOAL, (153, 39, 53, 36))  # LEFT shoulder button oval
            pygame.draw.polygon(self.screen, CHARCOAL, [[153, 52], [203, 52], [209, 75], [149, 75]])  # LEFT shoulder button filler polygon
            pygame.draw.ellipse(self.screen, CHARCOAL, (335, 39, 53, 36))  # RIGHT shoulder button oval
            pygame.draw.polygon(self.screen, CHARCOAL, [[336, 52], [386, 52], [392, 75], [332, 66]])  # RIGHT shoulder button filler polygon

            # D-PAD
            pygame.draw.ellipse(self.screen, CHARCOAL, (128, 63, 101, 101))  # LEFT circle enclosing d-pad
            pygame.draw.polygon(self.screen, BLACK, [[171, 89], [186, 89], [186, 100], [179, 106], [176, 106], [171, 100]])  # DPAD UP
            pygame.draw.polygon(self.screen, BLACK, [[153, 106], [164, 106], [170, 112], [170, 115], [164, 121], [153, 121]])  # DPAD LEFT
            pygame.draw.polygon(self.screen, BLACK, [[184, 112], [190, 106], [201, 106], [201, 121], [190, 121], [184, 115]])  # DPAD RIGHT
            pygame.draw.polygon(self.screen, BLACK, [[176, 121], [179, 121], [186, 127], [186, 138], [171, 138], [171, 127]])  # DPAD DOWN

            # FACE BUTTONS
            pygame.draw.ellipse(self.screen, CHARCOAL, (309, 60, 101, 101))  # RIGHT circle enclosing face buttons

            pygame.draw.circle(self.screen, BLACK, self.face_buttons['btn_3'], 11)  # TRIANGLE
            pygame.draw.polygon(self.screen, GREEN, [[362, 82], [367, 93], [356, 93]], 2)

            pygame.draw.circle(self.screen, BLACK, self.face_buttons['btn_1'], 11)  # CIRCLE
            pygame.draw.circle(self.screen, RED, (386, 113), 7, 2)

            pygame.draw.circle(self.screen, BLACK, self.face_buttons['btn_0'], 11)  # CROSS
            pygame.draw.line(self.screen, BLUE, [356, 131], [368, 141], 2)
            pygame.draw.line(self.screen, BLUE, [356, 141], [368, 131], 2)

            pygame.draw.circle(self.screen, BLACK, self.face_buttons['btn_2'], 11)  # SQUARE
            pygame.draw.rect(self.screen, PINK, (332, 107, 11, 11), 2)

            # SELECT & START
            pygame.draw.rect(self.screen, BLACK, (235, 110, 14, 8))  # SELECT button
            pygame.draw.polygon(self.screen, BLACK, [[290, 110], [304, 114], [290, 118]])  # START button polygon

            # JOYSTICKS
            pygame.draw.ellipse(self.screen, CHARCOAL, (191, 125, 65, 65))  # LEFT circle enclosing joystick
            pygame.draw.ellipse(self.screen, BLACK, (200, 133, 48, 48), 3)  # LEFT circle outlining joystick
            pygame.draw.ellipse(self.screen, CHARCOAL, (285, 125, 65, 65))  # RIGHT circle enclosing joystick
            pygame.draw.ellipse(self.screen, BLACK, (293, 133, 48, 48), 3)  # RIGHT circle outlining joystick

        elif self.gamepad == "ps4":
            
            ### PS4 GAMEPAD ###
            self.__AAfilledRoundedRect(self.screen, (210, 82, 136, 106), CHARCOAL, radius=0.2)  # BACKGROUND
            pygame.gfxdraw.filled_ellipse(self.screen, 189, 80, 18, 10, BLACK)  # LEFT SHOULDER button
            pygame.gfxdraw.filled_polygon(self.screen, ([180, 77], [168, 80], [157, 99], [149, 120], [139, 162], [136, 184],
                                                   [130, 218], [192, 228], [207, 195], [210, 190], [213, 187], [220, 83],
                                                   [210, 77]), CHARCOAL)  # LEFT HANDLE polygon
            pygame.gfxdraw.filled_ellipse(self.screen, 162, 218, 31,35, CHARCOAL)  # LEFT HANDLE ellipse
            pygame.gfxdraw.filled_ellipse(self.screen, 365, 80, 18, 10, BLACK)  # RIGHT SHOULDER button
            pygame.gfxdraw.filled_polygon(self.screen, ([373, 77], [385, 80], [397, 99], [405, 120], [414, 162], [418, 184],
                                                   [421, 218], [360, 228], [348, 195], [346, 190], [342, 187], [338, 83],
                                                   [346, 77]), CHARCOAL)  # RIGHT HANDLE polygon
            pygame.gfxdraw.filled_ellipse(self.screen, 390, 218, 31,35, CHARCOAL)  # RIGHT HANDLE ellipse
            self.__AAfilledRoundedRect(self.screen, (228,80,98,53), BLACK)  # TOUCHPAD

            # D-PAD
            #LEFT circle enclosing DPAD
            pygame.gfxdraw.filled_circle(self.screen, 187, 124, 36, CHARCOAL)
            pygame.gfxdraw.arc(self.screen, 187, 124, 36, 65, 25, BLACK)

            # DPAD UP
            self.__AAfilledRoundedRect(self.screen, (178, 99, 17, 16), BLACK, radius=0.5)
            pygame.gfxdraw.filled_polygon(self.screen, ([194, 112], [188, 120], [184, 120], [178, 112]), BLACK)

            # DPAD LEFT
            self.__AAfilledRoundedRect(self.screen, (162, 116, 16, 17), BLACK, radius=0.5)
            pygame.gfxdraw.filled_polygon(self.screen, ([176, 116], [183, 122], [183, 126], [176, 131]), BLACK)

            # DPAD RIGHT
            self.__AAfilledRoundedRect(self.screen, (196, 116, 16, 17), BLACK, radius=0.5)
            pygame.gfxdraw.filled_polygon(self.screen, ([197, 131], [190, 126], [190, 122], [197, 116]), BLACK)

            # DPAD DOWN
            self.__AAfilledRoundedRect(self.screen, (178, 134, 17, 16), BLACK, radius=0.5)
            pygame.gfxdraw.filled_polygon(self.screen, ([184, 127], [188, 127], [194, 134], [178, 134]), BLACK)

            # FACE BUTTONS
            # RIGHT circle enclosing face buttons.
            pygame.gfxdraw.filled_circle(self.screen, 368, 123, 36, CHARCOAL)
            pygame.gfxdraw.arc(self.screen, 368, 123, 36, 150, 115, BLACK)

            # TRIANGLE
            pygame.gfxdraw.filled_circle(self.screen, self.face_buttons['btn_3'][0], self.face_buttons['btn_3'][1], 11, BLACK)
            pygame.gfxdraw.aacircle(self.screen, self.face_buttons['btn_3'][0], self.face_buttons['btn_3'][1], 11, BLACK)
            pygame.gfxdraw.trigon(self.screen, 368, 94, 375, 105, 362, 105, GREEN)

            # CIRCLE
            pygame.gfxdraw.filled_circle(self.screen, self.face_buttons['btn_1'][0], self.face_buttons['btn_1'][1], 11, BLACK)
            pygame.gfxdraw.aacircle(self.screen, self.face_buttons['btn_1'][0], self.face_buttons['btn_1'][1], 11, BLACK)
            pygame.gfxdraw.aacircle(self.screen, self.face_buttons['btn_1'][0], self.face_buttons['btn_1'][1], 6, RED)

            # SQUARE
            pygame.gfxdraw.filled_circle(self.screen, self.face_buttons['btn_2'][0], self.face_buttons['btn_2'][1], 11, BLACK)
            pygame.gfxdraw.aacircle(self.screen, self.face_buttons['btn_2'][0], self.face_buttons['btn_2'][1], 11, BLACK)
            pygame.gfxdraw.rectangle(self.screen, (341, 117, 11, 11), PINK)

            # CROSS
            pygame.gfxdraw.filled_circle(self.screen, self.face_buttons['btn_0'][0], self.face_buttons['btn_0'][1], 11, BLACK)
            pygame.gfxdraw.aacircle(self.screen, self.face_buttons['btn_0'][0], self.face_buttons['btn_0'][1], 11, BLACK)
            pygame.gfxdraw.line(self.screen, 363, 139, 372, 148, BLUE)
            pygame.gfxdraw.line(self.screen, 372, 139, 363, 148, BLUE)

            # SHARE & OPTIONS
            self.__AAfilledRoundedRect(self.screen, (215, 87, 10, 17), BLACK, radius=1)
            self.__AAfilledRoundedRect(self.screen, (330, 87, 10, 17), BLACK, radius=1)

            # JOYSTICKS
            # To get a clean filled circle with no jaggies, have to have two operations: filled circle and AA outline.
            # This sections creates two sets of concentric circles, producing two CHARCOAL joysticks with 3px BLACK
            # outlines, which then has another CHARCOAL circle surrounded by a 1px BLACK outline.  These form the
            # thumbstick pods.
            pygame.gfxdraw.filled_circle(self.screen, 231, 165, 29, CHARCOAL)  # LEFT joystick pod
            pygame.gfxdraw.arc(self.screen, 231, 165, 29, 245, 200, BLACK)  # LEFT joystick pod outline
            pygame.gfxdraw.filled_circle(self.screen, 231, 163, 20, BLACK)  # LEFT enclosing circle fill
            pygame.gfxdraw.aacircle(self.screen, 231, 163, 20, BLACK)  # LEFT enclosing circle AA outline

            pygame.gfxdraw.filled_circle(self.screen, 324, 165, 29, CHARCOAL)  # RIGHT joystick pod
            pygame.gfxdraw.arc(self.screen, 324, 165, 29, 340, 295, BLACK)  # RIGHT joystick pod outline
            pygame.gfxdraw.filled_circle(self.screen, 324, 163, 20, BLACK)  # RIGHT enclosing circle fill
            pygame.gfxdraw.aacircle(self.screen, 324, 163, 20, BLACK)  # RIGHT enclosing circle AA outline

            pygame.gfxdraw.filled_circle(self.screen, 231, 163, 17, CHARCOAL)  # LEFT JOYSTICK fill
            pygame.gfxdraw.aacircle(self.screen, 231, 163, 17, CHARCOAL)  # LEFT JOYSTICK circle AA outline
            pygame.gfxdraw.filled_circle(self.screen, 324, 163, 17, CHARCOAL)  # RIGHT JOYSTICK circle fill
            pygame.gfxdraw.aacircle(self.screen, 324, 163, 17, CHARCOAL)  # RIGHT JOYSTICK circle AA outline

            # PS BUTTON
            # It doesn't do anything in game, but we'll draw it anyhow.
            pygame.gfxdraw.filled_circle(self.screen, 277, 167, 7, BLACK)
            pygame.gfxdraw.aacircle(self.screen, 277, 167, 7, BLACK)
            pygame.gfxdraw.filled_trigon(self.screen, 277, 162, 281, 166, 273, 166, BLUE)
            # Not sure I like this little home icon...
            self.__AAfilledRoundedRect(self.screen, (275, 167, 5, 5), BLUE, radius=0.2)

            # SPEAKER
            # This is an array 3 rows of 3x3 black circles with 3px spacing, reducing 1 per row
            startrowpos = 140
            startcolpos = 265
            holes = 5
            rad = 2  # Disproportionately large, but 2 is the smallest we can go and still get a circle. Int only here.
            rowstep = 6
            colstep = 6

            while holes > 2:
                colpos = startcolpos
                rowpos = startrowpos

                for hole in range(0, holes):
                    pygame.gfxdraw.filled_circle(self.screen, colpos, rowpos, rad, BLACK)
                    pygame.gfxdraw.aacircle(self.screen, colpos, rowpos, rad, BLACK)
                    colpos += colstep

                startrowpos += rowstep
                startcolpos += 3
                holes -= 1

    def drawPointers(self):
        if self.gamepad == "ps3":
            # DRAW POINTERS
            pygame.draw.lines(self.screen, MEDGRAY, False, [[361, 38], [361, 17], [430, 17]], 2)  # RIGHT TRIGGER
            pygame.draw.line(self.screen, MEDGRAY, [361, 42], [430, 42], 2)  # RIGHT BUMPER
            pygame.draw.lines(self.screen, MEDGRAY, False, [[338, 113], [338, 65], [430, 65]], 2)  # SQUARE
            pygame.draw.line(self.screen, MEDGRAY, [362, 89], [430, 89], 2)  # TRIANGLE
            pygame.draw.line(self.screen, MEDGRAY, [386, 113], [430, 113], 2)  # CIRCLE
            pygame.draw.line(self.screen, MEDGRAY, [362, 137], [430, 137], 2)  # CROSS
            pygame.draw.line(self.screen, MEDGRAY, [320, 159], [430, 159], 2)  # RIGHT STICK AXIS
            pygame.draw.lines(self.screen, MEDGRAY, False, [[400, 162], [400, 180], [430, 180]], 2)  # RIGHT STICK BUTTON

            pygame.draw.line(self.screen, MEDGRAY, [297, 113], [297, 40], 2)  # START
            pygame.draw.line(self.screen, MEDGRAY, [243, 113], [243, 40], 2)  # SELECT

            pygame.draw.lines(self.screen, MEDGRAY, False, [[178, 38], [178, 17], [112, 17]], 2)  # LEFT TRIGGER
            pygame.draw.line(self.screen, MEDGRAY, [178, 42], [112, 42], 2)  # LEFT BUMPER
            pygame.gfxdraw.aacircle(self.screen, 178, 114, 18, MEDGRAY)  # D-PAD 1
            pygame.draw.line(self.screen, MEDGRAY, [160, 113], [112, 113], 2)  # D-PAD 2
            pygame.draw.line(self.screen, MEDGRAY, [220, 162], [112, 162], 2)  # LEFT STICK AXIS
            pygame.draw.lines(self.screen, MEDGRAY, False, [[142, 162], [142, 180], [112, 180]], 2)  # LEFT STICK BUTTON

        elif self.gamepad == "ps4":
            pygame.draw.lines(self.screen, MEDGRAY, False, [[361, 68], [361, 50], [430, 50]], 2)  # RIGHT TRIGGER
            pygame.draw.line(self.screen, MEDGRAY, [361, 66], [430, 66], 2)  # RIGHT BUMPER
            pygame.draw.lines(self.screen, MEDGRAY, False, [[346, 122], [346, 85], [430, 85]], 2)  # SQUARE
            pygame.draw.line(self.screen, MEDGRAY, [368, 101], [430, 101], 2)  # TRIANGLE
            pygame.draw.line(self.screen, MEDGRAY, [389, 122], [430, 122], 2)  # CIRCLE
            pygame.draw.line(self.screen, MEDGRAY, [368, 144], [430, 144], 2)  # CROSS
            pygame.draw.line(self.screen, MEDGRAY, [324, 163], [430, 163], 2)  # RIGHT STICK AXIS
            pygame.draw.lines(self.screen, MEDGRAY, False, [[400, 163], [400, 186], [430, 186]], 2)  # RIGHT STICK BUTTON

            pygame.draw.line(self.screen, MEDGRAY, [335, 95], [335, 40], 2)  # OPTIONS
            pygame.draw.line(self.screen, MEDGRAY, [219, 95], [219, 40], 2)  # SHARE

            pygame.draw.lines(self.screen, MEDGRAY, False, [[190, 68], [190, 50], [112, 50]], 2)  # LEFT TRIGGER
            pygame.draw.line(self.screen, MEDGRAY, [190, 66], [112, 66], 2)  # LEFT BUMPER
            pygame.draw.lines(self.screen, MEDGRAY, False, [[205, 126], [205, 90], [112, 90]], 2)  # DPAD RIGHT
            pygame.draw.line(self.screen, MEDGRAY, [186, 106], [112, 106], 2)  # DPAD UP
            pygame.draw.line(self.screen, MEDGRAY, [172, 123], [112, 123], 2)  # DPAD LEFT
            pygame.draw.line(self.screen, MEDGRAY, [186, 140], [112, 140], 2)  # DPAD DOWN
            pygame.draw.line(self.screen, MEDGRAY, [231, 163], [112, 163], 2)  # LEFT STICK AXIS
            pygame.draw.lines(self.screen, MEDGRAY, False, [[142, 163], [142, 186], [112, 186]], 2)  # LEFT STICK BUTTON

    def buttonLocation(self, button):
        # Spit out the (x, y) of the requested button.  Supports only Sony buttons for now.
        # A switch block would be really nice here...damn Python.
        if button.lower() == 'btn_3':
            return self.face_buttons['btn_3']

        elif button.lower() == 'btn_2':
            return self.face_buttons['btn_2']

        elif button.lower() == 'btn_1':
            return self.face_buttons['btn_1']

        elif button.lower() == 'btn_0':
            return self.face_buttons['btn_0']


class ButtonHighlight():

    """
    buttonHighlight(my_screen, location, radius, color)

    my_screen   :   Destination surface
    location    :   Pixel coordinates, tuple (x, y)
    radius      :   Integer
    color       :   RGB value, tuple (r, g, b)
    """

    def __init__(self, my_screen, location, radius, color):
        self.screen = my_screen
        self.location = location
        self.radius = radius
        self.color = color

    def draw(self):
        # Have to break the position out because gfxdraw doesn't accept tuples.
        pygame.gfxdraw.filled_circle(self.screen, self.location[0], self.location[1], self.radius, self.color)


class ScreenRefresh():

    def __init__(self, surface, newsurface, bgimage, static_dict, dynamic_dict, init_msg, offset=(0, 0)):
        self.source = surface
        self.screen = newsurface
        self.bgimage = bgimage
        self.static = static_dict
        self.dynamic = dynamic_dict
        self.offset = offset
        self.init_msg = pygame.font.Font(None, 15).render(init_msg, True, RED)

    def printbuttons(self, dict):

        """
        printbuttons(dict<Button>)

        Steps through the array and calls each member's .printout() method.

        """

        for btn in dict:
            dict[btn].printout()

    def draw(self, highlight=-1, warn_activate=False):

        self.screen.fill(WHITE)

        self.bgimage.drawBG()
        self.bgimage.drawPointers()
        self.printbuttons(self.static)
        self.printbuttons(self.dynamic)

        if 0 <= highlight < 4:
            self.static['btn_{0}'.format(highlight)].highlight.draw()

        if warn_activate:
            self.screen.blit(self.init_msg, (375, 214))

        self.screen.blit(self.source, self.offset)

        pygame.display.flip()


def aspect_scale(surface, size):
    # This function obtained from the Pygame code repository, credit to Frank Raiser.
    # Modified by me to work with Python 3, which does not support tuple argument unpacking.
    # This works well for upscaling, not so hot for downscaling.

    """
    Scales surface to fit into box (bx, by).
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


def create_label_pos_dict(gamepad):

    """
    :param gamepad: String Gamepad type.
    :return:        Dictionary Label positions
    """

    if gamepad.lower() == 'ps3':
        # TODO: These need adjustment.
        pos_dict = dict(
            btn_0=(435, 133),
            btn_1=(435, 110),
            btn_2=(435, 61),
            btn_3=(435, 85),
            btn_4=(42, 37),
            btn_5=(435, 37),
            btn_6=(190, 25),
            btn_7=(285, 25),
            btn_8=(75, 175),
            btn_9=(435, 175),
            x_axis=(50, 154),
            y_axis=(50, 164),
            x_rot=(435, 154),
            y_rot=(435, 164),
            z_up=(35, 12),
            z_down=(435, 12),
            pov_up=(35, 95),
            pov_left=(1, 115),
            pov_right=(65, 115),
            pov_down=(35, 135)
        )

    # This part is largely finished, just need to sort out how to display the DPAD labels.
    elif gamepad.lower() == 'ps4':
        pos_dict = dict(
            btn_0=(435, 140), btn_1=(435, 118), btn_2=(435, 81), btn_3=(435, 98), btn_4=(107, 63), btn_5=(435, 63),
            btn_6=(219, 28), btn_7=(335, 28), btn_8=(107, 182), btn_9=(435, 182), x_axis=(107, 155), y_axis=(107, 165),
            x_rot=(435, 155), y_rot=(435, 165), z_up=(107, 46), z_down=(435, 47), pov_up=(107, 101),
            pov_left=(107, 118), pov_right=(107, 85), pov_down=(107, 135))

    return pos_dict


### MAIN
def main():
    # TODO: SERIOUS refactoring.
    ### INITIALIZE ###
    # Debug for testing when a gamepad is not present
    debug = True

    #  BUTTON Colors - Sony and Microsoft use different colors for their buttons.  This is future-proofing.
    if gamepad_type == 'ps3' or gamepad_type == 'ps4':
        BTN_A_COLOR = BLUE
        BTN_B_COLOR = RED
        BTN_X_COLOR = PINK
        BTN_Y_COLOR = GREEN

    # Display init
    init_txt = "Click to initialize gamepad system."
    pygame.init()
    scr_size = (600, 260)
    screen = pygame.display.set_mode(scr_size)

    drawbg = GamepadImage(pygame.display.set_mode(scr_size), gamepad_type)

    pygame.display.set_caption("ED Advanced Gamepad Controls")

    # Clock init
    clock = pygame.time.Clock()

    # Button highlight radius
    highlight_r = 13

    # Custom.binds file path and XML handler setup
    win = tkinter.Tk()
    win.withdraw()

    file_opts = options = {}
    options['defaultextension'] = '.binds'
    options['filetypes'] = [('all files', '.*'), ('XML files', '.binds')]
    options['initialdir'] = '{0}\Frontier Developments\Elite Dangerous\Options\Bindings'.format(os.getenv('localappdata'))
    options['initialfile'] = 'Custom.binds'
    options['parent'] = win
    options['title'] = 'Open File'

    # Create the background drawing object. Commented out: this is created directly in the refresh object init
    #GamepadImage(screen, gamepad_type)

    source = tkinter.filedialog.askopenfilename(**file_opts)

    # quit gracefully if no file is selected
    if source is '':
        pygame.quit()

    # otherwise, continue on with file parsing
    # Can these three be combined?
    #tree = ET.parse(source)
    #root = tree.getroot()
    # drill down once
    #workingtree = root.getchildren()  # this is a list of elements
    workingtree = ET.parse(source).getroot().getchildren()

    # Labels go in a dict, like everything else.  Dict dict dict all over the place.
    # It doesn't necessarily make them any easier to use, but it helpful for keeping track of them.
    label_dict = dict(
        # UNMODIFIED
        pov_up_label=BindsHandler(workingtree, "Pad_DPadUp").label,
        pov_left_label=BindsHandler(workingtree, "Pad_DPadLeft").label,
        pov_right_label=BindsHandler(workingtree, "Pad_DPadRight").label,
        pov_down_label=BindsHandler(workingtree, "Pad_DPadDown").label,

        # Modifier: CROSS / A
        pov_up_A_label=BindsHandler(workingtree, "Pad_DPadUp", "Pad_A").label,
        pov_left_A_label=BindsHandler(workingtree, "Pad_DPadLeft", "Pad_A").label,
        pov_right_A_label=BindsHandler(workingtree, "Pad_DPadRight", "Pad_A").label,
        pov_down_A_label=BindsHandler(workingtree, "Pad_DPadDown", "Pad_A").label,

        # Modifier: CIRCLE / B
        pov_up_B_label=BindsHandler(workingtree, "Pad_DPadUp", "Pad_B").label,
        pov_left_B_label=BindsHandler(workingtree, "Pad_DPadLeft", "Pad_B").label,
        pov_right_B_label=BindsHandler(workingtree, "Pad_DPadRight", "Pad_B").label,
        pov_down_B_label=BindsHandler(workingtree, "Pad_DPadDown", "Pad_B").label,

        # Modifier: SQUARE / X
        pov_up_X_label=BindsHandler(workingtree, "Pad_DPadUp", "Pad_X").label,
        pov_left_X_label=BindsHandler(workingtree, "Pad_DPadLeft", "Pad_X").label,
        pov_right_X_label=BindsHandler(workingtree, "Pad_DPadRight", "Pad_X").label,
        pov_down_X_label=BindsHandler(workingtree, "Pad_DPadDown", "Pad_X").label,

        # Modifier: TRIANGLE / Y
        pov_up_Y_label=BindsHandler(workingtree, "Pad_DPadUp", "Pad_Y").label,
        pov_left_Y_label=BindsHandler(workingtree, "Pad_DPadLeft", "Pad_Y").label,
        pov_right_Y_label=BindsHandler(workingtree, "Pad_DPadRight", "Pad_Y").label,
        pov_down_Y_label=BindsHandler(workingtree, "Pad_DPadDown", "Pad_Y").label,

        # Modifier button labels - Not sourced from XML
        btn_0_label='Shift (Hardpoints)',
        btn_1_label='Shift (System)',
        btn_2_label='Shift (Flight/Sensors)',
        btn_3_label='Shift (Targeting)',

        # These labels are fetched from the binds file.
        btn_4_label=BindsHandler(workingtree, 'Pad_LBumper').label,
        btn_5_label=BindsHandler(workingtree, 'Pad_RBumper').label,
        btn_6_label=BindsHandler(workingtree, 'Pad_Back').label,
        btn_7_label="Menu",  # I can't find a entry for the Start button in my Custom.binds file *shrug*
        btn_8_label=BindsHandler(workingtree, 'Pad_LThumb').label,
        btn_9_label=BindsHandler(workingtree, 'Pad_RThumb').label,
        x_axis_label='Hor: ' + BindsHandler(workingtree, 'Pad_LStickX').label,
        y_axis_label='Ver: ' + BindsHandler(workingtree, 'Pad_LStickY').label,
        x_rot_label='Hor: ' + BindsHandler(workingtree, 'Pad_RStickX').label,
        y_rot_label='Ver: ' + BindsHandler(workingtree, 'Pad_RStickY').label,
        z_up_label=BindsHandler(workingtree, 'Pos_Pad_LTrigger').label,
        z_down_label=BindsHandler(workingtree, 'Pos_Pad_RTrigger').label
    )



    # Label positions should be stored in a dictionary label_pos_dict = {'button' : (x, y)}
    # That dict is built by a function to allow for selection based on gamepad_type
    label_pos_dict = create_label_pos_dict(gamepad_type)

    # Store buttons in a dict
    static_button_dict = dict(
        btn_0=Button(screen, btn_0_label, label_pos_dict['btn_0'], BLUE,
                     buttonhighlight=ButtonHighlight(screen, drawbg.buttonLocation('btn_0'), highlight_r, BLUE)),
        btn_1=Button(screen, btn_1_label, label_pos_dict['btn_1'], RED,
                     buttonhighlight=ButtonHighlight(screen, drawbg.buttonLocation('btn_1'), highlight_r, RED)),
        btn_2=Button(screen, btn_2_label, label_pos_dict['btn_2'], PINK,
                     buttonhighlight=ButtonHighlight(screen, drawbg.buttonLocation('btn_2'), highlight_r, PINK)),
        btn_3=Button(screen, btn_3_label, label_pos_dict['btn_3'], GREEN,
                     buttonhighlight=ButtonHighlight(screen, drawbg.buttonLocation('btn_3'), highlight_r, GREEN)),
        btn_4=Button(screen, btn_4_label, label_pos_dict['btn_4'], BLACK, align='left'),
        btn_5=Button(screen, btn_5_label, label_pos_dict['btn_5'], BLACK),
        btn_6=Button(screen, btn_6_label, label_pos_dict['btn_6'], BLACK, align='center'),
        btn_7=Button(screen, btn_7_label, label_pos_dict['btn_7'], BLACK, align='center'),
        btn_8=Button(screen, btn_8_label, label_pos_dict['btn_8'], BLACK, align='left'),
        btn_9=Button(screen, btn_9_label, label_pos_dict['btn_9'], BLACK),
        x_axis=Button(screen, x_axis_label, label_pos_dict['x_axis'], BLACK, align='left'),
        y_axis=Button(screen, y_axis_label, label_pos_dict['y_axis'], BLACK, align='left'),
        x_rot=Button(screen, x_rot_label, label_pos_dict['x_rot'], BLACK),
        y_rot=Button(screen, y_rot_label, label_pos_dict['y_rot'], BLACK),
        z_up=Button(screen, z_up_label, label_pos_dict['z_up'], BLACK, align='left'),
        z_down=Button(screen, z_down_label, label_pos_dict['z_down'], BLACK)
    )

    ### POV Display ###


    # Dynamic buttons stored in a dict as well.
    pov_button_dict = dict(
        pov_up=Button(screen, pov_label_dict['pov_up_label'], label_pos_dict['pov_up'], BLACK, align='left'),
        pov_left=Button(screen, pov_label_dict['pov_left_label'], label_pos_dict['pov_left'], BLACK, align='left'),
        pov_right=Button(screen, pov_label_dict['pov_right_label'], label_pos_dict['pov_right'], BLACK, align='left'),
        pov_down=Button(screen, pov_label_dict['pov_down_label'], label_pos_dict['pov_down'], BLACK, align='left')
    )

    # Screen refresh object
    # New surface and GamepadImage object created directly in the call
    refresh = ScreenRefresh(screen, pygame.display.set_mode(scr_size), drawbg, static_button_dict, pov_button_dict,
                            init_txt, offset=(20, 0))

    refresh.draw(warn_activate=True)

    done = False

    while not done:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

            elif event.type == JOYBUTTONDOWN:
                # TODO: Figure out why button labels aren't updating.

                # Debugging:
                if debug:
                    print("Button {} pressed.".format(event.button))

                if event.button == 0:
                    # CROSS / A
                    pov_button_dict['pov_up'].update(pov_label_dict['pov_up_A_label'], BTN_A_COLOR)
                    pov_button_dict['pov_left'].update(pov_label_dict['pov_left_A_label'], BTN_A_COLOR)
                    pov_button_dict['pov_right'].update(pov_label_dict['pov_right_A_label'], BTN_A_COLOR)
                    pov_button_dict['pov_down'].update(pov_label_dict['pov_down_A_label'], BTN_A_COLOR)

                    refresh.draw(event.button)

                elif event.button == 1:
                    # CIRCLE / B
                    pov_button_dict['pov_up'].update(pov_label_dict['pov_up_B_label'], BTN_B_COLOR)
                    pov_button_dict['pov_left'].update(pov_label_dict['pov_left_B_label'], BTN_B_COLOR)
                    pov_button_dict['pov_right'].update(pov_label_dict['pov_right_B_label'], BTN_B_COLOR)
                    pov_button_dict['pov_down'].update(pov_label_dict['pov_down_B_label'], BTN_B_COLOR)

                    refresh.draw(event.button)

                elif event.button == 2:
                    # SQUARE / X
                    pov_button_dict['pov_up'].update(pov_label_dict['pov_up_X_label'], BTN_X_COLOR)
                    pov_button_dict['pov_left'].update(pov_label_dict['pov_left_X_label'], BTN_X_COLOR)
                    pov_button_dict['pov_right'].update(pov_label_dict['pov_right_X_label'], BTN_X_COLOR)
                    pov_button_dict['pov_down'].update(pov_label_dict['pov_down_X_label'], BTN_X_COLOR)

                    refresh.draw(event.button)

                elif event.button == 3:
                    # TRIANGLE / Y
                    pov_button_dict['pov_up'].update(pov_label_dict['pov_up_Y_label'], BTN_Y_COLOR)
                    pov_button_dict['pov_left'].update(pov_label_dict['pov_left_Y_label'], BTN_Y_COLOR)
                    pov_button_dict['pov_right'].update(pov_label_dict['pov_right_Y_label'], BTN_Y_COLOR)
                    pov_button_dict['pov_down'].update(pov_label_dict['pov_down_Y_label'], BTN_Y_COLOR)

                    refresh.draw(event.button)

            elif event.type == JOYBUTTONUP:

                pov_button_dict['pov_up'].update(pov_label_dict['pov_up_label'], BLACK)
                pov_button_dict['pov_left'].update(pov_label_dict['pov_left_label'], BLACK)
                pov_button_dict['pov_right'].update(pov_label_dict['pov_right_label'], BLACK)
                pov_button_dict['pov_down'].update(pov_label_dict['pov_down_label'], BLACK)

                refresh.draw()

            elif debug:

                if event.type == KEYDOWN:
                # TODO: Figure out why button labels aren't updating.

                    # Debugging:
                    print("Button {} pressed.".format(event.key))
                    if event.key == K_a:
                        # CROSS / A
                        pov_button_dict['pov_up'].update(pov_label_dict['pov_up_A_label'], BTN_A_COLOR)
                        pov_button_dict['pov_left'].update(pov_label_dict['pov_left_A_label'], BTN_A_COLOR)
                        pov_button_dict['pov_right'].update(pov_label_dict['pov_right_A_label'], BTN_A_COLOR)
                        pov_button_dict['pov_down'].update(pov_label_dict['pov_down_A_label'], BTN_A_COLOR)

                        refresh.draw(0)

                    elif event.key == K_s:
                        # CIRCLE / B
                        pov_button_dict['pov_up'].update(pov_label_dict['pov_up_B_label'], BTN_B_COLOR)
                        pov_button_dict['pov_left'].update(pov_label_dict['pov_left_B_label'], BTN_B_COLOR)
                        pov_button_dict['pov_right'].update(pov_label_dict['pov_right_B_label'], BTN_B_COLOR)
                        pov_button_dict['pov_down'].update(pov_label_dict['pov_down_B_label'], BTN_B_COLOR)

                        refresh.draw(1)

                    elif event.key == K_d:
                        # SQUARE / X
                        pov_button_dict['pov_up'].update(pov_label_dict['pov_up_X_label'], BTN_X_COLOR)
                        pov_button_dict['pov_left'].update(pov_label_dict['pov_left_X_label'], BTN_X_COLOR)
                        pov_button_dict['pov_right'].update(pov_label_dict['pov_right_X_label'], BTN_X_COLOR)
                        pov_button_dict['pov_down'].update(pov_label_dict['pov_down_X_label'], BTN_X_COLOR)

                        refresh.draw(2)

                    elif event.key == K_f:
                        # TRIANGLE / Y
                        pov_button_dict['pov_up'].update(pov_label_dict['pov_up_Y_label'], BTN_Y_COLOR)
                        pov_button_dict['pov_left'].update(pov_label_dict['pov_left_Y_label'], BTN_Y_COLOR)
                        pov_button_dict['pov_right'].update(pov_label_dict['pov_right_Y_label'], BTN_Y_COLOR)
                        pov_button_dict['pov_down'].update(pov_label_dict['pov_down_Y_label'], BTN_Y_COLOR)

                        refresh.draw(3)

                elif event.type == KEYUP:

                    pov_button_dict['pov_up'].update(pov_label_dict['pov_up_label'], BLACK)
                    pov_button_dict['pov_left'].update(pov_label_dict['pov_left_label'], BLACK)
                    pov_button_dict['pov_right'].update(pov_label_dict['pov_right_label'], BLACK)
                    pov_button_dict['pov_down'].update(pov_label_dict['pov_down_label'], BLACK)

                    refresh.draw()

            elif event.type == MOUSEBUTTONDOWN:
                # Debugging:
                #print("Mouse {} click.".format(pygame.mouse.get_pressed()))
                if pygame.mouse.get_pressed() == (1, 0, 0):

                    # Joystick init
                    if pygame.joystick.get_init() == 1:
                        pygame.joystick.quit()

                    else:
                        pygame.joystick.init()

                        if pygame.joystick.get_count() > 0:
                            gamepad = pygame.joystick.Joystick(0)
                            gamepad.init()

            elif event.type == MOUSEBUTTONUP:
                # Debugging:
                #print("Mouse {} click.".format(pygame.mouse.get_pressed()))
                if pygame.mouse.get_pressed() == (0, 0, 0):

                    if pygame.joystick.get_init() == 0:
                        refresh.draw(warn_activate=True)

                    else:
                        refresh.draw()

            #  We'll worry about resizing later.
            # elif event.type == VIDEORESIZE:
            #     scr_size = event.dict['size']
            #     screen = pygame.display.set_mode(scr_size, RESIZABLE)
            #     screen.blit(pygame.transform.scale(screen1, scr_size), (0, 0))
            #     pygame.display.flip()

        clock.tick(10)

    pygame.quit()

# Fire it off - laser beams go pew pew pew
if __name__ == '__main__':
    main()
