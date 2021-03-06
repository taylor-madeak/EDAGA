# EDGUI ver 2.01, build 8.

import tkinter
import tkinter.filedialog
import xml.etree.ElementTree as ET
import os, sys

from pygame import *
from pygame.locals import *
import pygame.gfxdraw


### GAMEPAD TYPE ###
# Set gamepad type from argument, defaults to ps4 if no arg given.
# Valid values are: 'ps3', 'ps4', 'xb360'
if len(sys.argv) < 2:
    gamepad_type = 'xb360'
else:
    if sys.argv[1] in ('ps3', 'ps4', 'xb360', 'xbone'):
        gamepad_type = sys.argv[1]
    else:
        gamepad_type = 'ps4'

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CHARCOAL = (40, 40, 40)
MEDGRAY = (160, 160, 160)
PINK = (238, 48, 167)
GREEN = (61, 145, 64)
RED = (255, 48, 48)
BLUE = (113, 113, 198)
YELLOW = (207, 207, 0)
ORANGE = (255, 102, 0)

class Button():

    def __init__(self, label, position, label_color, colorkey, align='right', buttonhighlight=None):
        self.label = label
        self.color = label_color
        self.colorkey = colorkey
        self.align = align
        self.highlight = buttonhighlight
        self.font = pygame.font.SysFont('Arial', 11)
        self.text_bitmap = self.font.render(str(self.label), True, self.color)
        self.start_pos = position
        self.position = self.set_position(self.text_bitmap, self.align, self.start_pos)

    def set_position(self, image, align, position):
    # Calculate label position
        if align == 'left':
            return (position[0] - image.get_width()), position[1]

        elif align == 'center':
            return (position[0] - (int(image.get_width() / 2))), position[1]

        else:
            return position

    def img(self):
        #self.my_screen.blit(self.text_bitmap, self.position)
        return self.text_bitmap

    def update(self, newLabel, newColor):
        self.color = newColor
        self.label = newLabel
        self.text_bitmap = self.font.render(str(newLabel), True, newColor)
        self.position = self.set_position(self.text_bitmap, self.align, self.start_pos)


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
                    or bind.tag.startswith('Cam')\
                    or bind.tag.startswith('HeadLookYaw')\
                    or bind.tag.startswith('HeadLookPitch'):
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

        elif tag == 'ToggleButtonUpInput':
            tag = 'SilentRunning'

        return tag

    def __str__(self):
        return self.label

    def __len__(self):
        return len(self.label)


class GamepadImage():
    # Fills the background with a drawn image of the controller.

    """
    GamepadImage(surface, gamepad)

    surface :   Destination surface
    gamepad :   STRING Gamepad type, currently supported: [ps3, ps4]
    """

    def __init__(self, surface, colorkey, gamepad):
        self.gamepad = gamepad.lower()
        self.colorkey = colorkey
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

        elif gamepad == 'xb360':
            self.face_buttons = dict(
                btn_3=(380, 74), btn_2=(364, 91), btn_1=(397, 91), btn_0=(380, 107)
            )

        elif gamepad == 'xbone':
            self.face_buttons = dict(
                btn_3=(384, 77), btn_2=(361, 99), btn_1=(407, 99), btn_0=(384, 122)
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


    def drawGamepad(self):

        PI = 3.141592653
        self.screen.fill(self.colorkey)

        if self.gamepad == 'ps3':
            
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
            pygame.gfxdraw.arc(self.screen, 174, 111, 45, 65, 25, BLACK)
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

            pygame.gfxdraw.arc(self.screen, 363, 109, 45, 149, 110, BLACK)  # Face buttons pod outline

            # SELECT & START
            pygame.draw.rect(self.screen, BLACK, (235, 110, 14, 8))  # SELECT button
            pygame.draw.polygon(self.screen, BLACK, [[290, 110], [304, 114], [290, 118]])  # START button polygon

            # PS BUTTON
            # It doesn't do anything in game, but we'll draw it anyhow.
            pygame.gfxdraw.filled_circle(self.screen, 268, 135, 7, BLACK)
            pygame.gfxdraw.aacircle(self.screen, 268, 135, 7, BLACK)
            # Not sure I like this little home icon...
            pygame.gfxdraw.filled_trigon(self.screen, 268, 129, 272, 133, 264, 133, BLUE)
            self.__AAfilledRoundedRect(self.screen, (266, 134, 5, 5), BLUE, radius=0.3)

            # JOYSTICKS
            pygame.draw.ellipse(self.screen, CHARCOAL, (191, 125, 65, 65))  # LEFT circle enclosing joystick
            pygame.draw.ellipse(self.screen, BLACK, (200, 133, 48, 48), 3)  # LEFT circle outlining joystick
            pygame.draw.ellipse(self.screen, CHARCOAL, (285, 125, 65, 65))  # RIGHT circle enclosing joystick
            pygame.draw.ellipse(self.screen, BLACK, (293, 133, 48, 48), 3)  # RIGHT circle outlining joystick
            pygame.gfxdraw.arc(self.screen, 316, 156, 31, 349, 280, BLACK)  # RIGHT joystick pod outline
            pygame.gfxdraw.arc(self.screen, 222, 156, 31, 257, 182, BLACK)  # LEFT joystick pod outline

        elif self.gamepad == 'ps4':
            
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

        elif self.gamepad == 'xb360':
            font = pygame.font.SysFont('Arial', 14, bold=True)

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

            pygame.gfxdraw.filled_polygon(self.screen, outline, CHARCOAL)
            pygame.gfxdraw.filled_polygon(self.screen, r_bumper, CHARCOAL)
            pygame.gfxdraw.filled_polygon(self.screen, l_bumper, CHARCOAL)
            pygame.gfxdraw.filled_polygon(self.screen, l_trigger, CHARCOAL)
            pygame.gfxdraw.filled_polygon(self.screen, r_trigger, CHARCOAL)
            pygame.gfxdraw.polygon(self.screen, outline, BLACK)
            pygame.gfxdraw.polygon(self.screen, r_bumper, BLACK)
            pygame.gfxdraw.polygon(self.screen, l_bumper, BLACK)
            pygame.gfxdraw.polygon(self.screen, l_trigger, BLACK)
            pygame.gfxdraw.polygon(self.screen, r_trigger, BLACK)

            # HOME button
            pygame.gfxdraw.aacircle(self.screen, 295, 93, 12, BLACK)

            # FACE BUTTONS
            pygame.gfxdraw.filled_circle(self.screen, 380, 74, 8, BLACK)  # Y BUTTON fill
            pygame.gfxdraw.aacircle(self.screen, 380, 74, 8, BLACK)  # Y BUTTON outline
            self.screen.blit(font.render('Y', True, YELLOW), (376, 66))  # Y BUTTON label

            pygame.gfxdraw.filled_circle(self.screen, 364, 91, 8, BLACK)  # X BUTTON fill
            pygame.gfxdraw.aacircle(self.screen, 364, 91, 8, BLACK)  # X BUTTON outline
            self.screen.blit(font.render('X', True, BLUE), (360, 83))  # X BUTTON label

            pygame.gfxdraw.filled_circle(self.screen, 397, 91, 8, BLACK)  # B BUTTON outline
            pygame.gfxdraw.aacircle(self.screen, 397, 91, 8, BLACK)  # B BUTTON outline
            self.screen.blit(font.render('B', True, RED), (393, 83))  # B BUTTON label

            pygame.gfxdraw.filled_circle(self.screen, 380, 107, 8, BLACK)  # A BUTTON outline
            pygame.gfxdraw.aacircle(self.screen, 380, 107, 8, BLACK)  # A BUTTON outline
            self.screen.blit(font.render('A', True, GREEN), (376, 99))  # A BUTTON label

            # START AND BACK
            pygame.gfxdraw.filled_circle(self.screen, 319, 93, 4, BLACK)  # START fill
            pygame.gfxdraw.aacircle(self.screen, 319, 93, 4, BLACK)  # START outline
            pygame.gfxdraw.filled_circle(self.screen, 271, 93, 4, BLACK)  # BACK fill
            pygame.gfxdraw.aacircle(self.screen, 271, 93, 4, BLACK)  # BACK outline

            # D-PAD
            pygame.gfxdraw.filled_circle(self.screen, 253, 142, 24, CHARCOAL)
            pygame.gfxdraw.aacircle(self.screen, 253, 142, 24, BLACK)
            pygame.gfxdraw.aaellipse(self.screen, 252, 144, 27, 31, BLACK)
            self.__AAfilledRoundedRect(self.screen, (246, 120, 15, 46), BLACK)
            self.__AAfilledRoundedRect(self.screen, (230, 136, 46, 15), BLACK)

            # LEFT JOYSTICK
            pygame.gfxdraw.filled_circle(self.screen, 210, 91, 17, BLACK)
            pygame.gfxdraw.filled_circle(self.screen, 210, 91, 13, CHARCOAL)
            pygame.gfxdraw.aacircle(self.screen, 210, 91, 13, BLACK)
            pygame.gfxdraw.aacircle(self.screen, 210, 91, 17, BLACK)
            pygame.gfxdraw.aacircle(self.screen, 210, 91, 24, BLACK)

            # RIGHT JOYSTICK
            pygame.gfxdraw.filled_circle(self.screen, 337, 142, 17, BLACK)
            pygame.gfxdraw.filled_circle(self.screen, 337, 142, 13, CHARCOAL)
            pygame.gfxdraw.aacircle(self.screen, 337, 142, 13, BLACK)
            pygame.gfxdraw.aacircle(self.screen, 337, 142, 17, BLACK)
            pygame.gfxdraw.aacircle(self.screen, 337, 142, 24, BLACK)
            pygame.gfxdraw.aaellipse(self.screen, 338, 144, 27, 31, BLACK)

        elif self.gamepad == "xbone":
            font = pygame.font.SysFont('Arial', 14, bold=True)

            outline = ((300, 81), (275, 81), (270, 79), (268, 78), (240, 48), (237, 46), (225, 46), (217, 48), (206, 51),
                       (195, 56), (181, 63), (178, 65), (177, 67), (174, 71), (140, 174), (139, 180), (138, 185),
                       (137, 191), (136, 195), (136, 215), (138, 220), (142, 232), (149, 242), (153, 245), (162, 250),
                       (168, 252), (172, 252), (231, 198), (239, 196), (361, 196), (369, 198), (428, 252), (432, 252),
                       (438, 250), (447, 245), (451, 242), (458, 232), (462, 220), (464, 215), (464, 195), (463, 191),
                       (462, 185), (461, 180), (460, 174), (426, 71), (423, 67), (422, 65), (419, 63), (405, 56),
                       (394, 51), (383, 48), (375, 46), (363, 46), (360, 48), (332, 78), (330, 79), (325, 81), (300, 81))

            top = ((300, 81), (275, 81), (270, 79), (268, 78), (249, 57), (256, 41), (344, 41), (351, 57), (332, 78),
                   (330, 79), (325, 81), (300, 81))
            l_button = ((249, 57), (256, 41), (247, 35), (244, 34), (241, 33), (228, 33), (223, 34), (218, 36), (191, 48),
                        (188, 50), (186, 53), (185, 60), (217, 48), (237, 46))
            r_button = ((351, 57), (344, 41), (353, 35), (356, 34), (359, 33), (372, 33), (377, 34), (382, 36), (409, 48),
                        (412, 50), (414, 53), (415, 60), (383, 48), (375, 46), (363, 46))

            pygame.gfxdraw.filled_polygon(self.screen, outline, CHARCOAL)
            pygame.gfxdraw.filled_polygon(self.screen, l_button, CHARCOAL)
            pygame.gfxdraw.filled_polygon(self.screen, r_button, CHARCOAL)
            pygame.gfxdraw.filled_polygon(self.screen, top, CHARCOAL)
            pygame.gfxdraw.polygon(self.screen, top, BLACK)
            pygame.gfxdraw.polygon(self.screen, l_button, BLACK)
            pygame.gfxdraw.polygon(self.screen, r_button, BLACK)
            pygame.gfxdraw.polygon(self.screen, outline, BLACK)

            # HOME button
            pygame.gfxdraw.aacircle(self.screen, 300, 62, 15, BLACK)

            # FACE BUTTONS
            pygame.gfxdraw.filled_circle(self.screen, 384, 77, 11, BLACK)  # Y BUTTON fill
            pygame.gfxdraw.aacircle(self.screen, 384, 77, 11, BLACK)  # Y BUTTON outline
            self.screen.blit(font.render('Y', True, YELLOW), (380, 69))  # Y BUTTON label

            pygame.gfxdraw.filled_circle(self.screen, 361, 99, 11, BLACK)  # X BUTTON fill
            pygame.gfxdraw.aacircle(self.screen, 361, 99, 11, BLACK)  # X BUTTON outline
            self.screen.blit(font.render('X', True, BLUE), (357, 91))  # X BUTTON label

            pygame.gfxdraw.filled_circle(self.screen, 407, 99, 11, BLACK)  # B BUTTON outline
            pygame.gfxdraw.aacircle(self.screen, 407, 99, 11, BLACK)  # B BUTTON outline
            self.screen.blit(font.render('B', True, RED), (403, 91))  # B BUTTON label

            pygame.gfxdraw.filled_circle(self.screen, 384, 122, 11, BLACK)  # A BUTTON outline
            pygame.gfxdraw.aacircle(self.screen, 384, 122, 11, BLACK)  # A BUTTON outline
            self.screen.blit(font.render('A', True, GREEN), (380, 114))  # A BUTTON label

            # START AND BACK
            pygame.gfxdraw.filled_circle(self.screen, 324, 99, 7, BLACK)  # MENU fill
            pygame.gfxdraw.aacircle(self.screen, 324, 99, 7, BLACK)  # MENU outline
            # MENU label
            x = 321
            y = 97
            for i in range(3):
                pygame.gfxdraw.hline(self.screen, x, x + 6, y, WHITE)
                y += 2

            pygame.gfxdraw.filled_circle(self.screen, 277, 99, 7, BLACK)  # VIEW fill
            pygame.gfxdraw.aacircle(self.screen, 277, 99, 7, BLACK)  # VIEW outline
            # VIEW label
            pygame.gfxdraw.rectangle(self.screen, (274, 96, 5, 5), WHITE)
            pygame.gfxdraw.rectangle(self.screen, (276, 98, 5, 5), WHITE)

            # D-PAD
            pygame.gfxdraw.aacircle(self.screen, 258, 152, 27, BLACK)
            self.__AAfilledRoundedRect(self.screen, (250, 128, 17, 49), BLACK)
            self.__AAfilledRoundedRect(self.screen, (234, 144, 49, 17), BLACK)

            # LEFT JOYSTICK
            pygame.gfxdraw.filled_circle(self.screen, 218, 99, 27, BLACK)
            pygame.gfxdraw.filled_circle(self.screen, 218, 99, 19, CHARCOAL)
            pygame.gfxdraw.aacircle(self.screen, 218, 99, 27, BLACK)
            pygame.gfxdraw.aacircle(self.screen, 218, 99, 19, BLACK)

            # RIGHT JOYSTICK
            pygame.gfxdraw.filled_circle(self.screen, 343, 149, 27, BLACK)
            pygame.gfxdraw.filled_circle(self.screen, 343, 149, 19, CHARCOAL)
            pygame.gfxdraw.aacircle(self.screen, 343, 149, 27, BLACK)
            pygame.gfxdraw.aacircle(self.screen, 343, 149, 19, BLACK)

    def drawPointers(self):
        if self.gamepad == 'ps3':
            # DRAW POINTERS
            pygame.draw.lines(self.screen, MEDGRAY, False, [[361, 38], [361, 17], [430, 17]], 2)  # RIGHT TRIGGER
            pygame.draw.line(self.screen, MEDGRAY, [361, 42], [430, 42], 2)  # RIGHT BUMPER
            pygame.draw.lines(self.screen, MEDGRAY, False, [[338, 113], [338, 65], [430, 65]], 2)  # SQUARE
            pygame.draw.line(self.screen, MEDGRAY, [362, 89], [430, 89], 2)  # TRIANGLE
            pygame.draw.line(self.screen, MEDGRAY, [386, 113], [430, 113], 2)  # CIRCLE
            pygame.draw.line(self.screen, MEDGRAY, [362, 137], [430, 137], 2)  # CROSS
            pygame.draw.line(self.screen, MEDGRAY, [320, 159], [430, 159], 2)  # RIGHT STICK AXIS
            pygame.draw.lines(self.screen, MEDGRAY, False, [[400, 162], [400, 187], [430, 187]], 2)  # RIGHT STICK BUTTON

            pygame.draw.line(self.screen, MEDGRAY, [297, 113], [297, 40], 2)  # START
            pygame.draw.line(self.screen, MEDGRAY, [243, 113], [243, 40], 2)  # SELECT

            pygame.draw.lines(self.screen, MEDGRAY, False, [[178, 38], [178, 17], [112, 17]], 2)  # LEFT TRIGGER
            pygame.draw.line(self.screen, MEDGRAY, [178, 42], [112, 42], 2)  # LEFT BUMPER

            pygame.draw.lines(self.screen, MEDGRAY, False, [[195, 115], [195, 81], [112, 81]], 2)  # DPAD RIGHT
            pygame.draw.line(self.screen, MEDGRAY, [178, 97], [112, 97], 2)  # DPAD UP
            pygame.draw.line(self.screen, MEDGRAY, [160, 115], [112, 115], 2)  # DPAD LEFT
            pygame.draw.line(self.screen, MEDGRAY, [178, 133], [112, 133], 2)  # DPAD DOWN

            pygame.draw.line(self.screen, MEDGRAY, [220, 162], [112, 162], 2)  # LEFT STICK AXIS
            pygame.draw.lines(self.screen, MEDGRAY, False, [[142, 162], [142, 187], [112, 187]], 2)  # LEFT STICK BUTTON

        elif self.gamepad == 'ps4':
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

        elif self.gamepad =='xb360':
            pygame.draw.lines(self.screen, MEDGRAY, False, ((364, 91), (364, 59), (459, 59)), 2)  # X BUTTON
            pygame.draw.line(self.screen, MEDGRAY, (380, 74), (459, 74), 2)  # Y BUTTON
            pygame.draw.line(self.screen, MEDGRAY, (397, 91), (459, 91), 2)  # B BUTTON
            pygame.draw.line(self.screen, MEDGRAY, (380, 107), (459, 107), 2)  # A BUTTON

            pygame.draw.lines(self.screen, MEDGRAY, False, ((267, 142), (267, 110), (131, 110)), 2)  # DPAD RIGHT
            pygame.draw.line(self.screen, MEDGRAY, (252, 125), (131, 125), 2)  # DPAD UP
            pygame.draw.line(self.screen, MEDGRAY, (240, 142), (131, 142), 2)  # DPAD LEFT
            pygame.draw.line(self.screen, MEDGRAY, (252, 160), (131, 160), 2)  # DPAD DOWN

            pygame.draw.line(self.screen, MEDGRAY, (337, 142), (459, 142), 2)  # RIGHT STICK AXIS
            pygame.draw.lines(self.screen, MEDGRAY, False, ((413, 142), (413, 166), (459, 166)), 2)  # RIGHT STICK BUTTON
            pygame.draw.line(self.screen, MEDGRAY, (210, 91), (131, 91), 2) # LEFT STICK AXIS
            pygame.draw.lines(self.screen, MEDGRAY, False, ((176, 91), (176, 67), (131, 67)), 2) # LEFT STICK BUTTON

            pygame.draw.line(self.screen, MEDGRAY, (319, 93), (319, 25), 2) # START
            pygame.draw.line(self.screen, MEDGRAY, (271, 93), (271, 25), 2) # BACK

            pygame.draw.line(self.screen, MEDGRAY, (364, 30), (459, 30), 2) # RIGHT TRIGGER
            pygame.draw.line(self.screen, MEDGRAY, (394, 45), (459, 45), 2)# RIGHT BUMPER
            pygame.draw.line(self.screen, MEDGRAY, (226, 30), (131, 30), 2) # LEFT TRIGGER
            pygame.draw.line(self.screen, MEDGRAY, (196, 45), (131, 45), 2) # LEFT BUMPER

        elif self.gamepad == "xbone":
            pygame.draw.lines(self.screen, MEDGRAY, False, ((361, 99), (361, 55), (485, 55)), 2)  # X BUTTON
            pygame.draw.line(self.screen, MEDGRAY, (384, 77), (485, 77), 2)  # Y BUTTON
            pygame.draw.line(self.screen, MEDGRAY, (407, 99), (485, 99), 2)  # B BUTTON
            pygame.draw.line(self.screen, MEDGRAY, (384, 122), (485, 122), 2)  # A BUTTON

            pygame.draw.lines(self.screen, MEDGRAY, False, ((275, 153), (275, 114), (117, 114)), 2)  # DPAD RIGHT
            pygame.draw.line(self.screen, MEDGRAY, (258, 134), (117, 134), 2)  # DPAD UP
            pygame.draw.line(self.screen, MEDGRAY, (241, 153), (117, 153), 2)  # DPAD LEFT
            pygame.draw.line(self.screen, MEDGRAY, (258, 173), (117, 173), 2)  # DPAD DOWN

            pygame.draw.line(self.screen, MEDGRAY, (343, 149), (485, 149), 2)  # RIGHT STICK AXIS
            pygame.draw.lines(self.screen, MEDGRAY, False, ((430, 149), (430, 179), (485, 179)), 2)  # RIGHT STICK BUTTON
            pygame.draw.line(self.screen, MEDGRAY, (218, 99), (117, 99), 2) # LEFT STICK AXIS
            pygame.draw.lines(self.screen, MEDGRAY, False, ((180, 99), (180, 69), (117, 69)), 2) # LEFT STICK BUTTON

            pygame.draw.line(self.screen, MEDGRAY, (324, 99), (324, 25), 2) # MENU
            pygame.draw.line(self.screen, MEDGRAY, (277, 99), (277, 25), 2) # VIEW

            pygame.draw.lines(self.screen, MEDGRAY, False, ((365, 30), (365, 20), (435, 20)), 2) # RIGHT TRIGGER
            pygame.draw.line(self.screen, MEDGRAY, (375, 40), (485, 40), 2)# RIGHT BUMPER
            pygame.draw.lines(self.screen, MEDGRAY, False, ((235, 30), (235, 20), (167, 20)), 2) # LEFT TRIGGER
            pygame.draw.line(self.screen, MEDGRAY, (225, 40), (117, 40), 2) # LEFT BUMPER


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

    @property
    def drawBG(self):
        self.screen.set_colorkey(self.colorkey)
        self.drawGamepad()
        self.drawPointers()
        return self.screen


class ButtonHighlight():

    """
    buttonHighlight(my_screen, location, radius, color)

    my_screen   :   Destination surface
    location    :   Pixel coordinates, tuple (x, y)
    radius      :   Integer
    color       :   RGB value, tuple (r, g, b)
    """

    def __init__(self, my_screen, colorkey, radius, color):
        self.screen = my_screen
        self.colorkey = colorkey
        self.radius = radius
        self.color = color

    def draw(self):
        self.screen.fill(self.colorkey)
        self.screen.set_colorkey(self.colorkey)
        pygame.gfxdraw.filled_circle(self.screen, self.radius, self.radius, self.radius - 1, self.color)
        return self.screen


class ScreenRefresh():

    def __init__(self, surface, bgimage, static_dict, dynamic_dict, init_msg, offset=(0, 0)):
        self.screen = surface
        self.bgimage = bgimage
        self.static = static_dict
        self.dynamic = dynamic_dict
        self.offset = offset
        self.init_msg = pygame.font.SysFont('Arial', 15).render(init_msg, True, RED)

    def printbuttons(self, dict):

        """
        printbuttons(dict<Button>)

        Steps through the array and calls each member's .printout() method.

        """
        for btn in dict:
            corrected_pos = (dict[btn].position[0] + self.offset[0], dict[btn].position[1] + self.offset[1])
            self.screen.blit(dict[btn].text_bitmap, corrected_pos)

    def draw(self, highlight=-1, warn_activate=False):
        self.screen.fill(WHITE)
        self.screen.blit(self.bgimage.drawBG, self.offset)

        if 0 <= highlight < 4:
            # A little bit of voodoo is needed to get the highlights centered over the buttons
            hl_pos = self.bgimage.buttonLocation('btn_{0}'.format(highlight))
            hl = self.static['btn_{0}'.format(highlight)].highlight.draw()
            hl_size = hl.get_size()
            corrected_hl_pos = ((hl_pos[0] - (hl_size[0] / 2)) + self.offset[0],
                                (hl_pos[1] - (hl_size[1] / 2)) + self.offset[1])
            hl.set_alpha(128)
            self.screen.blit(hl, corrected_hl_pos)

        if warn_activate:
            warn_pos = (self.screen.get_size()[0] - (self.init_msg.get_size()[0] + 10),
                        self.screen.get_size()[1] - (self.init_msg.get_size()[1] + 10))
            self.screen.blit(self.init_msg, warn_pos)

        self.printbuttons(self.static)
        self.printbuttons(self.dynamic)

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
        pos_dict = dict(
            btn_0=(435, 132), btn_1=(435, 109), btn_2=(435, 60), btn_3=(435, 84), btn_4=(107, 36), btn_5=(435, 36),
            btn_6=(243, 24), btn_7=(297, 24), btn_8=(107, 181), btn_9=(435, 181), x_axis=(107, 153), y_axis=(107, 163),
            x_rot=(435, 153), y_rot=(435, 163), z_up=(107, 11), z_down=(435, 11), pov_up=(107, 92), pov_left=(107, 110),
            pov_right=(107, 76), pov_down=(107, 128)
        )

    elif gamepad.lower() == 'ps4':
        pos_dict = dict(
            btn_0=(435, 139), btn_1=(435, 117), btn_2=(435, 80), btn_3=(435, 97), btn_4=(107, 62), btn_5=(435, 62),
            btn_6=(219, 27), btn_7=(335, 27), btn_8=(107, 181), btn_9=(435, 181), x_axis=(107, 154), y_axis=(107, 164),
            x_rot=(435, 154), y_rot=(435, 164), z_up=(107, 45), z_down=(435, 45), pov_up=(107, 100), pov_left=(107, 117),
            pov_right=(107, 84), pov_down=(107, 134))

    elif gamepad.lower() == 'xb360':
        pos_dict = dict(
            btn_0=(464, 86), btn_1=(464, 102), btn_2=(464, 54), btn_3=(464, 69), btn_4=(126, 40), btn_5=(464, 40),
            btn_6=(266, 10), btn_7=(324, 10), btn_8=(126, 62), btn_9=(464, 161), x_axis=(126, 80), y_axis=(126, 90),
            x_rot=(464, 131), y_rot=(464, 141), z_up=(126, 25), z_down=(464, 25), pov_up=(126, 120), pov_left=(126, 137),
            pov_right=(126, 105), pov_down=(126, 155)
        )

    elif gamepad.lower() == 'xbone':
        pos_dict = dict(
            btn_0=(490, 117), btn_1=(490, 94), btn_2=(490, 50), btn_3=(490, 72), btn_4=(114, 35), btn_5=(490, 35),
            btn_6=(277, 15), btn_7=(324, 5), btn_8=(114, 64), btn_9=(490, 174), x_axis=(114, 80), y_axis=(114, 94),
            x_rot=(490, 144), y_rot=(490, 158), z_up=(162, 15), z_down=(440, 15), pov_up=(114, 129), pov_left=(114, 148),
            pov_right=(114, 109), pov_down=(114, 168)
        )

    return pos_dict


### MAIN
def main():
    ### INITIALIZE ###
    # Debug for testing when a gamepad is not present
    debug = False

    # Colorkey for transparent surfaces
    colorkey = (255, 0, 255)

    #  BUTTON Colors - Sony and Microsoft use different colors for their buttons.  This is future-proofing.
    if gamepad_type == 'ps3' or gamepad_type == 'ps4':
        BTN_A_COLOR = BLUE
        BTN_B_COLOR = RED
        BTN_X_COLOR = PINK
        BTN_Y_COLOR = GREEN

    elif gamepad_type == 'xb360' or gamepad_type == 'xbone':
        BTN_A_COLOR = GREEN
        BTN_B_COLOR = RED
        BTN_X_COLOR = BLUE
        BTN_Y_COLOR = YELLOW

    # Display init
    init_txt = "Click to initialize gamepad system."
    pygame.init()
    if gamepad_type == 'xbone':
        scr_size = (620, 260)
    else:
        scr_size = (600, 260)

    drawbg = GamepadImage(pygame.Surface(scr_size), colorkey, gamepad_type)

    pygame.display.set_caption("Elite: Dangerous Advanced Gamepad Controls Assistant")

    # Clock init
    clock = pygame.time.Clock()

    # Button highlight radius
    highlight_r = 13
    highlight_size = (highlight_r * 2, highlight_r * 2)

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

    source = tkinter.filedialog.askopenfilename(**file_opts)

    # quit gracefully if no file is selected
    if source is '':
        pygame.quit()

    # otherwise, continue on with file parsing
    workingtree = ET.parse(source).getroot().getchildren()  # This is a list of elements.

    # Labels go in a dict, like everything else.  Dict dict dict all over the place.
    # It doesn't necessarily make them any easier to use, but it helpful for keeping track of them.
    btn_label_dict = dict(
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
        btn_0=Button(btn_label_dict['btn_0_label'], label_pos_dict['btn_0'], BTN_A_COLOR, colorkey,
                     buttonhighlight=ButtonHighlight(pygame.Surface(highlight_size), colorkey, highlight_r, BTN_A_COLOR)),
        btn_1=Button(btn_label_dict['btn_1_label'], label_pos_dict['btn_1'], BTN_B_COLOR, colorkey,
                     buttonhighlight=ButtonHighlight(pygame.Surface(highlight_size), colorkey, highlight_r, BTN_B_COLOR,)),
        btn_2=Button(btn_label_dict['btn_2_label'], label_pos_dict['btn_2'], BTN_X_COLOR, colorkey,
                     buttonhighlight=ButtonHighlight(pygame.Surface(highlight_size), colorkey, highlight_r, BTN_X_COLOR)),
        btn_3=Button(btn_label_dict['btn_3_label'], label_pos_dict['btn_3'], BTN_Y_COLOR, colorkey,
                     buttonhighlight=ButtonHighlight(pygame.Surface(highlight_size), colorkey, highlight_r, BTN_Y_COLOR)),
        btn_4=Button(btn_label_dict['btn_4_label'], label_pos_dict['btn_4'], BLACK, colorkey, align='left'),
        btn_5=Button(btn_label_dict['btn_5_label'], label_pos_dict['btn_5'], BLACK, colorkey),
        btn_6=Button(btn_label_dict['btn_6_label'], label_pos_dict['btn_6'], BLACK, colorkey, align='center'),
        btn_7=Button(btn_label_dict['btn_7_label'], label_pos_dict['btn_7'], BLACK, colorkey, align='center'),
        btn_8=Button(btn_label_dict['btn_8_label'], label_pos_dict['btn_8'], BLACK, colorkey, align='left'),
        btn_9=Button(btn_label_dict['btn_9_label'], label_pos_dict['btn_9'], BLACK, colorkey),
        x_axis=Button(btn_label_dict['x_axis_label'], label_pos_dict['x_axis'], BLACK, colorkey, align='left'),
        y_axis=Button(btn_label_dict['y_axis_label'], label_pos_dict['y_axis'], BLACK, colorkey, align='left'),
        x_rot=Button(btn_label_dict['x_rot_label'], label_pos_dict['x_rot'], BLACK, colorkey),
        y_rot=Button(btn_label_dict['y_rot_label'], label_pos_dict['y_rot'], BLACK, colorkey),
        z_up=Button(btn_label_dict['z_up_label'], label_pos_dict['z_up'], BLACK, colorkey, align='left'),
        z_down=Button(btn_label_dict['z_down_label'], label_pos_dict['z_down'], BLACK, colorkey)
    )

    # Dynamic buttons stored in a dict as well.
    pov_button_dict = dict(
        pov_up=Button(btn_label_dict['pov_up_label'], label_pos_dict['pov_up'], BLACK, colorkey, align='left'),
        pov_left=Button(btn_label_dict['pov_left_label'], label_pos_dict['pov_left'], BLACK, colorkey, align='left'),
        pov_right=Button(btn_label_dict['pov_right_label'], label_pos_dict['pov_right'], BLACK, colorkey, align='left'),
        pov_down=Button(btn_label_dict['pov_down_label'], label_pos_dict['pov_down'], BLACK, colorkey, align='left')
    )

    # Screen refresh object
    # The program window does not appear until this fires off.
    scr_shift = (20, 0)
    refresh = ScreenRefresh(pygame.display.set_mode(scr_size), drawbg, static_button_dict, pov_button_dict, init_txt,
                            offset=scr_shift)

    refresh.draw(warn_activate=True)

    done = False

    while not done:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

            elif event.type == JOYBUTTONDOWN:
                # Debugging:
                if debug:
                    print("Button {} pressed.".format(event.button))

                if event.button == 0:
                    # CROSS / A
                    pov_button_dict['pov_up'].update(btn_label_dict['pov_up_A_label'], BTN_A_COLOR)
                    pov_button_dict['pov_left'].update(btn_label_dict['pov_left_A_label'], BTN_A_COLOR)
                    pov_button_dict['pov_right'].update(btn_label_dict['pov_right_A_label'], BTN_A_COLOR)
                    pov_button_dict['pov_down'].update(btn_label_dict['pov_down_A_label'], BTN_A_COLOR)

                    refresh.draw(event.button)

                elif event.button == 1:
                    # CIRCLE / B
                    pov_button_dict['pov_up'].update(btn_label_dict['pov_up_B_label'], BTN_B_COLOR)
                    pov_button_dict['pov_left'].update(btn_label_dict['pov_left_B_label'], BTN_B_COLOR)
                    pov_button_dict['pov_right'].update(btn_label_dict['pov_right_B_label'], BTN_B_COLOR)
                    pov_button_dict['pov_down'].update(btn_label_dict['pov_down_B_label'], BTN_B_COLOR)

                    refresh.draw(event.button)

                elif event.button == 2:
                    # SQUARE / X
                    pov_button_dict['pov_up'].update(btn_label_dict['pov_up_X_label'], BTN_X_COLOR)
                    pov_button_dict['pov_left'].update(btn_label_dict['pov_left_X_label'], BTN_X_COLOR)
                    pov_button_dict['pov_right'].update(btn_label_dict['pov_right_X_label'], BTN_X_COLOR)
                    pov_button_dict['pov_down'].update(btn_label_dict['pov_down_X_label'], BTN_X_COLOR)

                    refresh.draw(event.button)

                elif event.button == 3:
                    # TRIANGLE / Y
                    pov_button_dict['pov_up'].update(btn_label_dict['pov_up_Y_label'], BTN_Y_COLOR)
                    pov_button_dict['pov_left'].update(btn_label_dict['pov_left_Y_label'], BTN_Y_COLOR)
                    pov_button_dict['pov_right'].update(btn_label_dict['pov_right_Y_label'], BTN_Y_COLOR)
                    pov_button_dict['pov_down'].update(btn_label_dict['pov_down_Y_label'], BTN_Y_COLOR)

                    refresh.draw(event.button)

            elif event.type == JOYBUTTONUP:

                pov_button_dict['pov_up'].update(btn_label_dict['pov_up_label'], BLACK)
                pov_button_dict['pov_left'].update(btn_label_dict['pov_left_label'], BLACK)
                pov_button_dict['pov_right'].update(btn_label_dict['pov_right_label'], BLACK)
                pov_button_dict['pov_down'].update(btn_label_dict['pov_down_label'], BLACK)

                refresh.draw()

            elif debug:

                if event.type == KEYDOWN:
                    # Debugging:
                    print("Button {} pressed.".format(event.key))
                    if event.key == K_a:
                        # CROSS / A
                        pov_button_dict['pov_up'].update(btn_label_dict['pov_up_A_label'], BTN_A_COLOR)
                        pov_button_dict['pov_left'].update(btn_label_dict['pov_left_A_label'], BTN_A_COLOR)
                        pov_button_dict['pov_right'].update(btn_label_dict['pov_right_A_label'], BTN_A_COLOR)
                        pov_button_dict['pov_down'].update(btn_label_dict['pov_down_A_label'], BTN_A_COLOR)

                        refresh.draw(0)

                    elif event.key == K_s:
                        # CIRCLE / B
                        pov_button_dict['pov_up'].update(btn_label_dict['pov_up_B_label'], BTN_B_COLOR)
                        pov_button_dict['pov_left'].update(btn_label_dict['pov_left_B_label'], BTN_B_COLOR)
                        pov_button_dict['pov_right'].update(btn_label_dict['pov_right_B_label'], BTN_B_COLOR)
                        pov_button_dict['pov_down'].update(btn_label_dict['pov_down_B_label'], BTN_B_COLOR)

                        refresh.draw(1)

                    elif event.key == K_d:
                        # SQUARE / X
                        pov_button_dict['pov_up'].update(btn_label_dict['pov_up_X_label'], BTN_X_COLOR)
                        pov_button_dict['pov_left'].update(btn_label_dict['pov_left_X_label'], BTN_X_COLOR)
                        pov_button_dict['pov_right'].update(btn_label_dict['pov_right_X_label'], BTN_X_COLOR)
                        pov_button_dict['pov_down'].update(btn_label_dict['pov_down_X_label'], BTN_X_COLOR)

                        refresh.draw(2)

                    elif event.key == K_f:
                        # TRIANGLE / Y
                        pov_button_dict['pov_up'].update(btn_label_dict['pov_up_Y_label'], BTN_Y_COLOR)
                        pov_button_dict['pov_left'].update(btn_label_dict['pov_left_Y_label'], BTN_Y_COLOR)
                        pov_button_dict['pov_right'].update(btn_label_dict['pov_right_Y_label'], BTN_Y_COLOR)
                        pov_button_dict['pov_down'].update(btn_label_dict['pov_down_Y_label'], BTN_Y_COLOR)

                        refresh.draw(3)

                elif event.type == KEYUP:

                    pov_button_dict['pov_up'].update(btn_label_dict['pov_up_label'], BLACK)
                    pov_button_dict['pov_left'].update(btn_label_dict['pov_left_label'], BLACK)
                    pov_button_dict['pov_right'].update(btn_label_dict['pov_right_label'], BLACK)
                    pov_button_dict['pov_down'].update(btn_label_dict['pov_down_label'], BLACK)

                    refresh.draw()

            elif event.type == MOUSEBUTTONDOWN:
                # Debugging:
                if debug:
                    print("Mouse {} click.".format(pygame.mouse.get_pressed()))

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
                if debug:
                    print("Mouse {} click.".format(pygame.mouse.get_pressed()))

                if pygame.mouse.get_pressed() == (0, 0, 0):

                    if pygame.joystick.get_init() == 0:
                        refresh.draw(warn_activate=True)

                    else:
                        refresh.draw()

        clock.tick(10)

    pygame.quit()

# Fire it off - laser beams go pew pew pew
if __name__ == '__main__':
    main()
