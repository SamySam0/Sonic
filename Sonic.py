from moviepy.editor import *
import pygame, sys
from pygame.locals import *
from pygame import mixer
import time
import soundfile as sf
mixer.init()
pygame.mixer.set_num_channels(1)
pygame.init()

# --- Window Settings ---
pygame.display.set_caption("Sonic : mais en mieux..") #Set app's name (left corner) to 'Project : Sonic'
WIN_SIZE = (1280, 720)
win = pygame.display.set_mode(WIN_SIZE) #Set display mode (resolution : 1280 x 720)
#DINOSAURE : display = pygame.Surface((1280*0.5, 720*0.5)) # (F-Resolution) Create a smaller 'display' which will then be scaled to the 'window's' size (pixal art scale)
display = pygame.Surface((1280, 720))

# --- Main character's sprites (64x64) ---
char = [pygame.image.load('Sprites\Iddle\Iddle.png'), pygame.transform.flip(pygame.image.load('Sprites\Iddle\Iddle.png'), True, False)]

# --- List of sprites for character standing (Iddle) : Looking RIGHT /OR/ Looking LEFT ---
grass_image = pygame.image.load('Textures\\grass.png') #Grass Texture
dirt_image = pygame.image.load('Textures\\wool.png') #Wool Texture
TILE_SIZE = grass_image.get_width() 

# --- Backgrounds / Parallax ---
parallax = [[pygame.image.load('Parallax\\bg_6.png').convert() , 1.11], [pygame.image.load('Parallax\\bg_5.png').convert() , 1.05], [pygame.image.load('Parallax\\bg_4.png').convert() , 1.08], [pygame.image.load('Parallax\\bg_3.png').convert() , 1.10], [pygame.image.load('Parallax\\bg_2.png').convert() , 1.18], [pygame.image.load('Parallax\\bg_1.png').convert() , 1.23]]

# --- FPS Settings ---
clock = pygame.time.Clock() #Variable Img Freq (FPS)
SPEED = 70 #FPS Variable

# --- Game Map ---
def load_map(path):
    f = open(path + '.txt', 'r') #Open map document
    data = f.read() #VAR data = document text
    f.close() #Close document
    data = data.split('\n') #Spliting datas
    game_map = []
    for row in data:
        game_map.append(list(row))
    return game_map
game_map = load_map('map')

# --- Frames updating ---
def update(frame_speed):
    #DINOSAURE : surf = pygame.transform.scale(display, WIN_SIZE)
    #DINOSAURE : win.blit(surf, (0, 0))
    win.blit(display, (0, 0))
    pygame.display.update() # update display
    clock.tick(frame_speed) # maintain 'SPEED' (value) fps

# --- Default character's attributs ---
class Player():
    '''
    :param: hosts character's attributs
    :param: Entries : 'x' (int) position, 'y' (int) position, 'width' (int) char's width px, 'height' (int) char's height px
    '''
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.moving_right = False
        self.moving_left = False
        self.rect = pygame.Rect(50, 50, char[0].get_width(), char[0].get_height())
        self.y_momentum = 0
        self.movement = [0,0]
        self.air_timer = 0
        self.true_scrolling = [0,0]
        self.acceleration = 2
        self.deceleration = 2
        self.direction_of_looking = 'Right'

# --- Moving and collisions ---
def collision_test(rect, tiles):
    hit_list = []
    for tile in tiles:
        if rect.colliderect(tile):
            hit_list.append(tile)
    return hit_list

def move(rect, movement, tiles):
    collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False}
    rect.x += movement[0]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[0] > 0:
            rect.right = tile.left
            collision_types['right'] = True
            sonic.acceleration = 2
            sonic.deceleration = 2
        elif movement[0] < 0:
            rect.left = tile.right
            collision_types['left'] = True
            sonic.acceleration = 2
            sonic.deceleration = 2
    rect.y += movement[1]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[1] > 0:
            rect.bottom = tile.top
            collision_types['bottom'] = True
        elif movement[1] < 0:
            rect.top = tile.bottom
            collision_types['top'] = True
    return rect, collision_types

# --- Spritings (sprites) automatisations ---
sprite_number = 1
def spriting(type, max, direction):
    global sprite_number

    #If the sprite is the 'Skid' one
    if type == 'Skid':
        if sprite_number == 1:
            if direction == 'Left':
                display.blit(pygame.transform.flip(pygame.image.load("Sprites\\" + type + "\\" + type + "1" + ".png"), True, False), (sonic.rect.x-scrolling[0], sonic.rect.y-scrolling[1]))
            elif direction == 'Right':
                display.blit(pygame.image.load("Sprites\\" + type + "\\" + type + "1" + ".png"), (sonic.rect.x-scrolling[0], sonic.rect.y-scrolling[1]))
            sprite_number += 1
        elif sprite_number < max and sprite_number > 4:
            if sprite_number >= max-1:
                sprite_number = 5
            sprite_number += 1
        elif sprite_number < max and sprite_number <= 4:
            sprite_number += 1
        else : sprite_number = 1
        sprite_automatisation = pygame.image.load("Sprites\\" + type + "\\" + type + str(sprite_number) + ".png")
        if direction == 'Left':
            return display.blit(pygame.transform.flip(sprite_automatisation, True, False), (sonic.rect.x-scrolling[0], sonic.rect.y-scrolling[1]))
        elif direction == 'Right':
            return display.blit(sprite_automatisation, (sonic.rect.x-scrolling[0], sonic.rect.y-scrolling[1]))

    #If the sprite is another one
    if sprite_number == 1:
        if direction == 'Left':
            display.blit(pygame.transform.flip(pygame.image.load("Sprites\\" + type + "\\" + type + "1" + ".png"), True, False), (sonic.rect.x-scrolling[0], sonic.rect.y-scrolling[1]))
        elif direction == 'Right':
            display.blit(pygame.image.load("Sprites\\" + type + "\\" + type + "1" + ".png"), (sonic.rect.x-scrolling[0], sonic.rect.y-scrolling[1]))
        sprite_number += 1
    elif sprite_number < max:
        sprite_number += 1
    else : sprite_number = 1
    sprite_automatisation = pygame.image.load("Sprites\\" + type + "\\" + type + str(sprite_number) + ".png")
    if direction == 'Left':
        return display.blit(pygame.transform.flip(sprite_automatisation, True, False), (sonic.rect.x-scrolling[0], sonic.rect.y-scrolling[1]))
    elif direction == 'Right':
        return display.blit(sprite_automatisation, (sonic.rect.x-scrolling[0], sonic.rect.y-scrolling[1]))




# --- Volumes Settings ---
music_volume, sound_volume, effect_volume = True, True, False

# --- Menus functions ---
def waiting_screen(time, SPEED_S):
    compteur = 1
    frame = SPEED_S * time
    waiting = True
    while waiting:
        display.fill((1,0,1))
        if compteur >= frame:
            waiting = False
        else :
            if compteur%2 == 0:
                display_image_menu('Waiting_sprite_1', 0.66, (0,0), '.png')
            else : display_image_menu('Waiting_sprite_2', 0.66, (0,0), '.png')
        compteur += 1
        update(SPEED_S)

def play_video(video):
    pygame.mixer.init()
    movies = VideoFileClip("Videos\\" + video + ".mp4")
    movies.preview(fps = 60)

def play_music(music_sound, volume = 1, playtime = -1, extension = '.mp3'):
    '''
    volume : 0 - 1, playtime: 1(one time), -1(loop)
    '''
    mixer.music.load("Musics - Sounds/" + music_sound + extension)
    if music_volume == False:
        mixer.music.set_volume(0)
    else : mixer.music.set_volume(volume)
    mixer.music.play(playtime)

def stop_music():
    mixer.music.stop()


def play_sound(sounds):
    pygame.mixer.init()
    freq = sf.SoundFile("Musics - Sounds\\" + sounds + '.wav')
    lenght_int = float(format(len(freq) / freq.samplerate))
    sound_vfx = mixer.Sound("Musics - Sounds\\" + sounds + '.wav')
    if sound_volume == True:
        mixer.find_channel().play(sound_vfx) #CRASHES WHEN SPAMMING 
    time.sleep(lenght_int)
    
def first_moving_sprite_menu(type, coo):
    image_to_display = pygame.image.load("Openning\\" + type + "\\" + type + "1.png")
    rescalation = (int(image_to_display.get_width()*2), int(image_to_display.get_height()*2))
    rescaled_to_display = pygame.transform.scale(image_to_display, rescalation)
    display.blit(rescaled_to_display, coo)

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

def display_image_menu(image, rescale, position, extension = '.png', inside = 'Others'):
    image_to_display = pygame.image.load("Openning//" + inside + "//" + image + extension)
    if rescale != 0:
        rescalation = (int(image_to_display.get_width()*rescale), int(image_to_display.get_height()*rescale))
        image_to_display_rescaled = pygame.transform.scale(image_to_display, rescalation)
        return display.blit(image_to_display_rescaled,position)
    else : return display.blit(image_to_display,position)

blinking_count, multi_4 = 1, 0
def color_blinking(x, y):
    global blinking_count, multi_4
    if blinking_count == 100:
        blinking_count = 1
    if multi_4 < 4:
        pygame.draw.rect(display, (195,37,122), pygame.Rect(x, y, 400, 90))
        multi_4 += 1
    else : 
        pygame.draw.rect(display, (172,3,3), pygame.Rect(x, y, 400, 90))
        multi_4 += 1
        if multi_4 >= 7: multi_4 = 0
    blinking_count += 1

sprite_count = 1
def animated_background_main_menu(max):
    global sprite_count
    if sprite_count > max:
        sprite_count = 1
    display_image_menu('animated_background_main_menu\\' + str(sprite_count).zfill(4), 1, (0,0), '.jpg')
    sprite_count += 1

options_count = 1
def animated_background_options_menu(max):
    global options_count
    if options_count > max:
        options_count = 1
    display_image_menu('animated_background_options_menu\\' + str(options_count).zfill(4), 1, (0,0), '.jpg')
    options_count += 1

launching_count = 1
def animated_background_launching(max):
    global launching_count
    if launching_count > max:
        launching_count = 1
    display_image_menu('animated_background_launching\\' + str(int(launching_count)).zfill(4), 1, (0,0), '.jpg')
    launching_count += 2


# --- MENUS & SCREENS ---

# --- TITLE SCREENS ---
def title_screen():
    global sprite_number
    play_music('Launching-menu', 0.7, 1)
    rewind = False
    banner_sprite = 1
    flickering_enable, counter = False, 0
    runing = True
    while runing:
        
        display.fill((255,255,255))
        display_image_menu('Background', 0.8, (0,0), '.jpg')

        Round_image = pygame.image.load("Openning/Others/Round.png")
        display_image_menu('Round', 2, (int(WIN_SIZE[0]/2 - Round_image.get_width()),int(WIN_SIZE[1]/2 - Round_image.get_height()*1.6)))

        Sonic_character_image = pygame.image.load("Openning/Others/Sonic.png")
        display_image_menu('Sonic', 2, (int(WIN_SIZE[0]/2 - Sonic_character_image.get_width() + 3),int(WIN_SIZE[1]/2 - Round_image.get_height()*1.5)))

        Arrow_python_image = pygame.image.load("Openning/Others/Arrow.png")
        display_image_menu('Arrow', 2, (int(WIN_SIZE[0]/2 - Arrow_python_image.get_width()),int(WIN_SIZE[1]/2 - Arrow_python_image.get_height()+64)))

        Press_button_image = pygame.image.load("Openning/Others/Press.png")

        By_Sam_image = pygame.image.load("Openning/Others/By_Sam.png")
        display_image_menu('By_Sam', 1, (int(WIN_SIZE[0] - 248), int(WIN_SIZE[1] - 148)))

        #"Press any button" management
        if flickering_enable:
            display_image_menu('Press', 2.22, (int(WIN_SIZE[0]/2 - (Press_button_image.get_width())),600))
            counter += 1
            if counter == 7:
                flickering_enable = False
                counter = 0
        else:
            counter += 1
            if counter == 7:
                flickering_enable = True
                counter = 0

        #"Finger" management
        if sprite_number == 1 and not rewind:
            first_moving_sprite_menu('Finger', (645,177))
            sprite_number += 1
        elif sprite_number < 7 and not rewind:
            sprite_number += 1
        else : 
            rewind = True
            if sprite_number == 2:
                rewind = False
            sprite_number -= 1       
        sprite_automatisation = pygame.image.load("Openning\\Finger\\Finger" + str(sprite_number) + ".png")
        rescalation = (int(sprite_automatisation.get_width()*2), int(sprite_automatisation.get_height()*2))
        rescaled_to_display = pygame.transform.scale(sprite_automatisation, rescalation)
        display.blit(rescaled_to_display, (645,177))

        #"Banner" management
        if banner_sprite == 1:
            first_moving_sprite_menu('Menu', (400,285))
            banner_sprite += 1
        elif banner_sprite < 7:
            banner_sprite += 1
        else : banner_sprite = 1   
        sprite_automatisation = pygame.image.load("Openning\\Menu\\Menu" + str(banner_sprite) + ".png")
        rescalation = (int(sprite_automatisation.get_width()*2), int(sprite_automatisation.get_height()*2))
        rescaled_to_display = pygame.transform.scale(sprite_automatisation, rescalation)
        display.blit(rescaled_to_display, (400,285))


        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                stop_music()
                play_sound('Accept')
                waiting_screen(3, 3)
                main_menu()

        update(35) #Uses the update() function to update the screen frame


# --- MAIN MENU and SOUS-MENUS ---
def main_menu():
    global launching_count
    play_music('Main-menu', 0.85, -1)
    click, clicked = False, False
    play_b, options_b, credits_b, quit_b = 'Play_Off', 'Options_Off', 'Credits_Off', 'Quit_Off'
    while True:

        #Click button 'leave' animation
        display.fill((100,100,100))
        if clicked:
            animated_background_launching(47)
            if launching_count >= 47:
                launching_count = 1
                clicked = False
                if go == 'play': play()
                elif go == 'credits': 
                    stop_music()
                    credits()
                elif go == 'options': options()
        else : animated_background_main_menu(353)

        mouse_x, mouse_y = pygame.mouse.get_pos()

        play_button_image = pygame.image.load("Openning/Buttons/Play_Off.png")
        play_button = pygame.Rect(721, 150, 513, 98)
        options_button_image = pygame.image.load("Openning/Buttons/Options_Off.png")
        options_button = pygame.Rect(765, 304, 470, 94)
        credits_button_image = pygame.image.load("Openning/Buttons/Credits_Off.png")
        credits_button = pygame.Rect(792, 471, 189, 34)
        quit_button_image = pygame.image.load("Openning/Buttons/Quit_Off.png")
        quit_button = pygame.Rect(1003, 458, 233, 47)
        # MAKE A CLASS OF THOSE BUTTONS
        if play_button.collidepoint((mouse_x, mouse_y)):
            play_b = 'Play_On'
            if click:
                clicked = True
                play_sound('Accept')
                go = 'play'
        if options_button.collidepoint((mouse_x, mouse_y)):
            options_b = 'Options_On'
            if click:
                clicked = True
                play_sound('Accept')
                go = 'options'
        if credits_button.collidepoint((mouse_x, mouse_y)):
            #color_blinking(680+34,500-70)
            credits_b = 'Credits_On'
            if click:
                clicked = True
                play_sound('Accept')
                go = 'credits'
        if quit_button.collidepoint((mouse_x, mouse_y)):
            quit_b = 'Quit_On'
            if click:
                play_sound('Return')
                pygame.quit()
                sys.exit()
        
        if not clicked:
            display_image_menu(play_b, 0.62, (int(WIN_SIZE[0] - play_button_image.get_width()*0.5 - 135),int(play_button_image.get_height()*0.5 - 50 + 40)), '.png', 'Buttons')
            #pygame.draw.rect(display, (0,0,0), play_button)
            display_image_menu(options_b, 0.5635, (int(WIN_SIZE[0] - options_button_image.get_width()*0.55 - 44),int(options_button_image.get_height()*0.85 + 58 + 40)), '.png', 'Buttons')
            #pygame.draw.rect(display, (0,0,0), options_button)
            display_image_menu(credits_b, 0.23, (int(WIN_SIZE[0] - credits_button_image.get_width()*0.50 - 63),int(quit_button_image.get_height()*0.85 + 184 + 32 + 40)), '.png', 'Buttons')
            #pygame.draw.rect(display, (0,0,0), credits_button)
            display_image_menu(quit_b, 0.285, (int(WIN_SIZE[0] - quit_button_image.get_width()*0.55 + 190),int(quit_button_image.get_height()*0.85 + 169 + 30 + 40)), '.png', 'Buttons')
            #pygame.draw.rect(display, (0,0,0), quit_button)

        play_b, options_b, credits_b, quit_b = 'Play_Off', 'Options_Off', 'Credits_Off', 'Quit_Off'
        click = False
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                runing = False
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
        update(120) #Uses the update() function to update the screen frame

time_trial_state, no_life_state, slow_motion_state, no_backward_state, musics_state, easy_state, medium_state, hard_state= "Time_trial_Off", "No_life_Off", "Slow_Off", "No_back_Off", "Musics_On", "Easy_Off", "Medium_On", "Hard_Off"
time_trial_b, no_life_b, slow_motion_b, no_backward_b, musics_b, easy_b, medium_b, hard_b = time_trial_state, no_life_state, slow_motion_state, no_backward_state, musics_state, easy_state, medium_state, hard_state
level1_state, level2_state, boss1_state, level3_state, level4_state, boss2_state = "Level_1", "Level_2_Off", "Boss_1_Off", "Level_3_Off", "Level_4_Off", "Boss_2_On"
level1_b, level2_b, boss1_b, level3_b, level4_b, boss2_b = level1_state, level2_state, boss1_state, level3_state, level4_state, boss2_state
def play():
    running = True
    play_music('Start-menu', 0.85, -1)
    global time_trial_b, no_life_b, slow_motion_b, no_backward_b, musics_b, easy_b, medium_b, hard_b, time_trial_state, no_life_state, slow_motion_state, no_backward_state, musics_state, easy_state, medium_state, hard_state, level1_state, level2_state, boss1_state, level3_state, level4_state, boss2_state, level1_b, level2_b, boss1_b, level3_b, level4_b, boss2_b
    click, clicked = False, False
    while running:
        pos_locked, pos_selected, Boss_selected, excepted, return_b = (-200, -200), (-200, -200), (-200, -200), (-200, -200), "Return_Off"
        #display_image_menu('Start_test_background', 1, (0,0), '.png') #TO DELETE
        display_image_menu('Start_background', 1, (0,0), '.jpg') #TO KEEP
        display_image_menu('Right_tiles', 1, (1020,85), '.png', 'Buttons//Start_menu') #TO KEEP
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # --- Levels ---
        level1_button_image = pygame.image.load("Openning/Buttons/Start_menu/Levels/Level_1.png")
        level1_button = pygame.Rect(int(WIN_SIZE[0] - 1160),56, level1_button_image.get_width(), level1_button_image.get_height())
        level2_button_image = pygame.image.load("Openning/Buttons/Start_menu/Levels/Level_2_Off.png")
        level2_button = pygame.Rect(int(WIN_SIZE[0] - 872),52, level2_button_image.get_width(), level2_button_image.get_height())
        boss1_button_image = pygame.image.load("Openning/Buttons/Start_menu/Levels/Boss_1_Off.png")
        boss1_button = pygame.Rect(int(WIN_SIZE[0] - 584),52, boss1_button_image.get_width(), boss1_button_image.get_height())
        level3_button_image = pygame.image.load("Openning/Buttons/Start_menu/Levels/Level_3_Off.png")
        level3_button = pygame.Rect(int(WIN_SIZE[0] - 1130),372, level3_button_image.get_width(), level3_button_image.get_height())
        level4_button_image = pygame.image.load("Openning/Buttons/Start_menu/Levels/Level_4_Off.png")
        level4_button = pygame.Rect(int(WIN_SIZE[0] - 842),372, level4_button_image.get_width(), level4_button_image.get_height())
        boss2_button_image = pygame.image.load("Openning/Buttons/Start_menu/Levels/Boss_2_Off.png")
        boss2_button = pygame.Rect(int(WIN_SIZE[0] - 554),372, boss2_button_image.get_width(), boss2_button_image.get_height())

        # --- Difficulty ---
        easy_button_image = pygame.image.load("Openning/Buttons/Start_menu/Easy_Off.png")
        easy_button = pygame.Rect(int(WIN_SIZE[0] - 218),147, easy_button_image.get_width(), easy_button_image.get_height())
        medium_button_image = pygame.image.load("Openning/Buttons/Start_menu/Medium_Off.png")
        medium_button = pygame.Rect(int(WIN_SIZE[0] - 226),187, medium_button_image.get_width(), medium_button_image.get_height())
        hard_button_image = pygame.image.load("Openning/Buttons/Start_menu/Hard_Off.png")
        hard_button = pygame.Rect(int(WIN_SIZE[0] - 218),228, hard_button_image.get_width(), hard_button_image.get_height())
        
        # --- Challenges ---
        time_trial_button_image = pygame.image.load("Openning/Buttons/Start_menu/Time_trial_Off.png")
        time_trial_button = pygame.Rect(int(WIN_SIZE[0] - 233),349, time_trial_button_image.get_width(), time_trial_button_image.get_height())
        no_life_button_image = pygame.image.load("Openning/Buttons/Start_menu/No_life_Off.png")
        no_life_button = pygame.Rect(int(WIN_SIZE[0] - 209),389, no_life_button_image.get_width(), no_life_button_image.get_height())
        slow_motion_button_image = pygame.image.load("Openning/Buttons/Start_menu/Slow_Off.png")
        slow_motion_button = pygame.Rect(WIN_SIZE[0] - 257,430, slow_motion_button_image.get_width(), slow_motion_button_image.get_height())
        no_backward_button_image = pygame.image.load("Openning/Buttons/Start_menu/No_back_Off.png")
        no_backward_button = pygame.Rect(int(WIN_SIZE[0] - 259),469, no_backward_button_image.get_width(), no_backward_button_image.get_height())
        
        # --- Musics and Return ---
        return_button_image = pygame.image.load("Openning/Buttons/Start_menu/Return_Off.png")
        return_button = pygame.Rect(10,10, return_button_image.get_width(), return_button_image.get_height())
        musics_button_image = pygame.image.load("Openning/Buttons/Start_menu/Musics_Off.png")
        musics_button = pygame.Rect(int(WIN_SIZE[0] - 218),588, musics_button_image.get_width(), musics_button_image.get_height())

        if return_button.collidepoint((mouse_x, mouse_y)):
            return_b = 'Return_On'
            if click:
                play_sound('Return')
                play_music('Main-menu', 0.85, -1)
                running = False

        if level1_button.collidepoint((mouse_x, mouse_y)):
            pos_selected = (int(WIN_SIZE[0] - 1160),56-3)
            if click:
                play_sound('Accept')
                play() #Change to the playing_level

        if level2_button.collidepoint((mouse_x, mouse_y)):
            if level2_state == 'Level_2_Off':
                pos_locked = (int(WIN_SIZE[0] - 872),52)
            else : pos_selected = (int(WIN_SIZE[0] - 872),52)
            if click:
                #graphics_low(45)
                if level2_state == 'Level_2_Off':
                    play_sound('Impossible')
                else : 
                    play_sound('Accept')
                    play() #Change to the playing_level

        if boss1_button.collidepoint((mouse_x, mouse_y)):
            if boss1_state == 'Boss_1_Off':
                pos_locked = (int(WIN_SIZE[0] - 584),52)
            else : Boss_selected = (int(WIN_SIZE[0] - 584),52)
            if click:
                #graphics_low(45)
                if boss1_state == 'Boss_1_Off':
                    play_sound('Impossible')
                else : 
                    play_sound('Accept')
                    play() #Change to the playing_level

        if level3_button.collidepoint((mouse_x, mouse_y)):
            if level3_state == 'Level_3_Off':
                pos_locked = (int(WIN_SIZE[0] - 1130),372)
            else : pos_selected = (int(WIN_SIZE[0] - 1126),372)
            if click:
                #graphics_low(45)
                if level3_state == 'Level_3_Off':
                    play_sound('Impossible')
                else : 
                    play_sound('Accept')
                    play() #Change to the playing_level

        if level4_button.collidepoint((mouse_x, mouse_y)):
            if level4_state == 'Level_4_Off':
                pos_locked = (int(WIN_SIZE[0] - 842),372)
            else : pos_selected = (int(WIN_SIZE[0] - 842),372)
            if click:
                #graphics_low(45)
                if level4_state == 'Level_4_Off':
                    play_sound('Impossible')
                else : 
                    play_sound('Accept')
                    play() #Change to the playing_level

        if boss2_button.collidepoint((mouse_x, mouse_y)):
            if boss2_state == 'Boss_2_Off':
                pos_locked = (int(WIN_SIZE[0] - 554),372)
            else : Boss_selected = (int(WIN_SIZE[0] - 553),371)
            if click:
                #graphics_low(45)
                if boss2_state == 'Boss_2_Off':
                    play_sound('Impossible')
                else : 
                    play_sound('Accept')
                    play() #Change to the playing_level





        if easy_button.collidepoint((mouse_x, mouse_y)):
            display_image_menu('Arrow', 0.38, (int(WIN_SIZE[0] - 218 - 17),147 + 1), '.png', 'Buttons//Start_menu')
            if click:
                #graphics_low(45)
                if easy_state == "Easy_Off":
                    easy_state, medium_state, hard_state = "Easy_On", "Medium_Off", "Hard_Off"

        if medium_button.collidepoint((mouse_x, mouse_y)):
            display_image_menu('Arrow', 0.38, (int(WIN_SIZE[0] - 226 - 17),187 + 1), '.png', 'Buttons//Start_menu')
            if click:
                if medium_state == "Medium_Off":
                    easy_state, medium_state, hard_state = "Easy_Off", "Medium_On", "Hard_Off"

        if hard_button.collidepoint((mouse_x, mouse_y)):
            display_image_menu('Arrow', 0.38, (int(WIN_SIZE[0] - 218 - 17),228 + 1), '.png', 'Buttons//Start_menu')
            if click:
                if hard_state == "Hard_Off":
                    easy_state, medium_state, hard_state = "Easy_Off", "Medium_Off", "Hard_On"

        if time_trial_button.collidepoint((mouse_x, mouse_y)):
            display_image_menu('Arrow', 0.38, (int(WIN_SIZE[0] - 233 - 17),349 + 1), '.png', 'Buttons//Start_menu')
            if click:
                if time_trial_state == "Time_trial_Off":
                    time_trial_state = "Time_trial_On"
                else : time_trial_state = "Time_trial_Off"

        if no_life_button.collidepoint((mouse_x, mouse_y)):
            display_image_menu('Arrow', 0.38, (int(WIN_SIZE[0] - 209 - 17),389 + 1), '.png', 'Buttons//Start_menu')
            if click:
                if no_life_state == "No_life_Off":
                    no_life_state = "No_life_On"
                else : no_life_state = "No_life_Off"

        if slow_motion_button.collidepoint((mouse_x, mouse_y)):
            display_image_menu('Arrow', 0.38, (int(WIN_SIZE[0] - 257 - 17),430 + 1), '.png', 'Buttons//Start_menu')
            if click:
                if slow_motion_state == "Slow_Off":
                    slow_motion_state = "Slow_On"
                else : slow_motion_state = "Slow_Off"

        if no_backward_button.collidepoint((mouse_x, mouse_y)):
            display_image_menu('Arrow', 0.38, (int(WIN_SIZE[0] - 259 - 17),469 + 1), '.png', 'Buttons//Start_menu')
            if click:
                if no_backward_state == "No_Back_Off":
                    no_backward_state = "No_Back_On"
                else : no_backward_state = "No_Back_Off"

        if musics_button.collidepoint((mouse_x, mouse_y)):
            display_image_menu('Arrow', 0.38, (int(WIN_SIZE[0] - 218 - 17),588 + 1), '.png', 'Buttons//Start_menu')
            if click:
                if musics_state == "Musics_Off":
                    musics_state = "Musics_On"
                else : musics_state = "Musics_Off"


        if not clicked:
            display_image_menu(easy_b, 1, (int(WIN_SIZE[0] - 218),147), '.png', 'Buttons//Start_menu')
            #pygame.draw.rect(display, (0,0,0), easy_button)
            display_image_menu(medium_b, 1, (int(WIN_SIZE[0] - 226),187), '.png', 'Buttons//Start_menu')
            #pygame.draw.rect(display, (0,0,0), medium_button)
            display_image_menu(hard_b, 1, (int(WIN_SIZE[0] - 218),228), '.png', 'Buttons//Start_menu')
            #pygame.draw.rect(display, (0,0,0), hard_button)
            display_image_menu(musics_b, 1, (int(WIN_SIZE[0] - 218),588), '.png', 'Buttons//Start_menu')
            #pygame.draw.rect(display, (0,0,0), musics_button)
            display_image_menu(no_backward_b, 1, (int(WIN_SIZE[0] - 259),469), '.png', 'Buttons//Start_menu')
            #pygame.draw.rect(display, (0,0,0), no_backward_button)
            display_image_menu(no_life_b, 1, (int(WIN_SIZE[0] - 209),389), '.png', 'Buttons//Start_menu')
            #pygame.draw.rect(display, (0,0,0), no_life_button)
            display_image_menu(slow_motion_b, 1, (WIN_SIZE[0] - 257,430), '.png', 'Buttons//Start_menu')
            #pygame.draw.rect(display, (0,0,0), slow_motion_button)
            display_image_menu(time_trial_b, 1, (int(WIN_SIZE[0] - 233),349), '.png', 'Buttons//Start_menu')
            #pygame.draw.rect(display, (0,0,0), time_trial_button)
            display_image_menu(return_b, 1, (10,10), '.png', 'Buttons//Start_menu')
            #pygame.draw.rect(display, (0,0,0), time_trial_button)

            display_image_menu(level1_b, 1, (int(WIN_SIZE[0] - 1160),56), '.png', 'Buttons//Start_menu//Levels')
            #pygame.draw.rect(display, (0,0,0), level1_button)
            display_image_menu(level2_b, 1, (int(WIN_SIZE[0] - 872),52), '.png', 'Buttons//Start_menu//Levels')
            #pygame.draw.rect(display, (0,0,0), level2_button)
            display_image_menu(boss1_b, 1, (int(WIN_SIZE[0] - 584),52), '.png', 'Buttons//Start_menu//Levels')
            #pygame.draw.rect(display, (0,0,0), boss1_button)
            display_image_menu(level3_b, 1, (int(WIN_SIZE[0] - 1130),372), '.png', 'Buttons//Start_menu//Levels')
            #pygame.draw.rect(display, (0,0,0), level3_button)
            display_image_menu(level4_b, 1, (WIN_SIZE[0] - 842,372), '.png', 'Buttons//Start_menu//Levels')
            #pygame.draw.rect(display, (0,0,0), level4_button)
            display_image_menu(boss2_b, 1, (int(WIN_SIZE[0] - 554),372), '.png', 'Buttons//Start_menu//Levels')
            #pygame.draw.rect(display, (0,0,0), boss2_button)

            display_image_menu('Locked', 1, pos_locked, '.png', 'Buttons//Start_menu//Levels')
            display_image_menu('Selected', 1, pos_selected, '.png', 'Buttons//Start_menu//Levels')
            display_image_menu('Boss_Selected', 1, Boss_selected, '.png', 'Buttons//Start_menu//Levels')



        time_trial_b, no_life_b, slow_motion_b, no_backward_b, musics_b, easy_b, medium_b, hard_b = time_trial_state, no_life_state, slow_motion_state, no_backward_state, musics_state, easy_state, medium_state, hard_state
        click = False
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    play_music('Main-menu', 0.85, -1)
                    running = False
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
        update(50)

return_state, high_state, low_state, music_state, sound_state, effect_state = 'Return_Off', 'High_On', 'Low_Off', "On_On", "On_On", "Off_Off"
return_b, high_b, low_b, music_b, sound_b, effect_b = return_state, high_state, low_state, music_state, sound_state, effect_state
def options():
    running = True
    click, clicked = False, False
    global music_volume, sound_volume, effect_volume, return_b, high_b, low_b, music_b, sound_b, effect_b, return_state, high_state, low_state, music_state, sound_state, effect_state #To make them fixed and not reset when leaving the options menu
    
    while running:
        animated_background_options_menu(480)
        display_image_menu('Options_background', 1, (0,0), '.png')
        
        #draw_text('OPTIONS', pygame.font.SysFont('Arial', 20), (250,250,250), display, 20, 20)
        mouse_x, mouse_y = pygame.mouse.get_pos()

        return_button_image = pygame.image.load("Openning/Buttons/Return_Off.png")
        return_button = pygame.Rect(15, 11, return_button_image.get_width(), return_button_image.get_height())
        music_button_image = pygame.image.load("Openning/Buttons/Off_Off.png")
        music_button = pygame.Rect(int(WIN_SIZE[0] - 125),245, music_button_image.get_width(), music_button_image.get_height())
        sound_button_image = pygame.image.load("Openning/Buttons/Off_Off.png")
        sound_button = pygame.Rect(int(WIN_SIZE[0] - 125),300, sound_button_image.get_width(), sound_button_image.get_height())
        effect_button_image = pygame.image.load("Openning/Buttons/Off_Off.png")
        effect_button = pygame.Rect(int(WIN_SIZE[0] - 125),355, effect_button_image.get_width(), effect_button_image.get_height())
        high_button_image = pygame.image.load("Openning/Buttons/High_Off.png")
        high_button = pygame.Rect(int(WIN_SIZE[0] - 420), 535, high_button_image.get_width(), high_button_image.get_height())
        low_button_image = pygame.image.load("Openning/Buttons/Low_Off.png")
        low_button = pygame.Rect(int(WIN_SIZE[0] - 260),535, low_button_image.get_width(), low_button_image.get_height())
        # MAKE A CLASS OF THOSE BUTTONS
        if return_button.collidepoint((mouse_x, mouse_y)):
            return_b = 'Return_On'
            if click:
                play_sound('Return')
                running = False
        if high_button.collidepoint((mouse_x, mouse_y)):
            display_image_menu('Arrow', 0.43, (int(WIN_SIZE[0] - 420 - 17),535 + 5), '.png', 'Buttons//Start_menu')
            if click:
                #graphics_high(60)
                if high_state == "High_Off":
                    high_state, low_state = "High_On", "Low_Off"
        if low_button.collidepoint((mouse_x, mouse_y)):
            display_image_menu('Arrow', 0.43, (int(WIN_SIZE[0] - 260 - 17),535 + 5), '.png', 'Buttons//Start_menu')
            if click:
                #graphics_low(45)
                if low_state == "Low_Off":
                    high_state, low_state = "High_Off", "Low_On"
        if music_button.collidepoint((mouse_x, mouse_y)):
            display_image_menu('Arrow', 0.43, (int(WIN_SIZE[0] - 125 - 17),245 + 5), '.png', 'Buttons//Start_menu')
            if click:
                if music_state == "Off_Off":
                    music_state = "On_On"
                    music_volume = True
                    mixer.music.set_volume(1)
                else : 
                    music_volume, music_state = False, "Off_Off"
                    mixer.music.set_volume(0)
        if sound_button.collidepoint((mouse_x, mouse_y)):
            display_image_menu('Arrow', 0.43, (int(WIN_SIZE[0] - 125 - 17),300 + 5), '.png', 'Buttons//Start_menu')
            #color_blinking(680+34,500-70)
            if click:
                if sound_state == "Off_Off":
                    sound_state = "On_On"
                    sound_volume = True
                else : sound_state, sound_volume = "Off_Off", False
        if effect_button.collidepoint((mouse_x, mouse_y)):
            display_image_menu('Arrow', 0.43, (int(WIN_SIZE[0] - 125 - 17),355 + 5), '.png', 'Buttons//Start_menu')
            if click:
                if effect_state == "Off_Off":
                    effect_state = "On_On"
                    effect_volume = True
                else : effect_state, effect_volume = "Off_Off", False
        
        if not clicked:
            display_image_menu(return_b, 1, (15,11), '.png', 'Buttons')
            #pygame.draw.rect(display, (0,0,0), return_button)
            display_image_menu(high_b, 1, (int(WIN_SIZE[0] - 420),535), '.png', 'Buttons')
            #pygame.draw.rect(display, (0,0,0), high_button)
            display_image_menu(low_b, 1, (int(WIN_SIZE[0] - 260),535), '.png', 'Buttons')
            #pygame.draw.rect(display, (0,0,0), low_button)
            display_image_menu(music_b, 1, (int(WIN_SIZE[0] - 125),245), '.png', 'Buttons')
            #pygame.draw.rect(display, (0,0,0), music_button)
            display_image_menu(sound_b, 1, (int(WIN_SIZE[0] - 125),300), '.png', 'Buttons')
            #pygame.draw.rect(display, (0,0,0), sound_button)
            display_image_menu(effect_b, 1, (int(WIN_SIZE[0] - 125),355), '.png', 'Buttons')
            #pygame.draw.rect(display, (0,0,0), effect_button)

        return_b, high_b, low_b, music_b, sound_b, effect_b = return_state, high_state, low_state, music_state, sound_state, effect_state
        click = False
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
        update(60)

def credits():
    play_video('Ending-credits')
    title_screen()



# --- Game Launch and Scenes ---
play_video('Openning-Credits')
play_video('Open')
title_screen()
#play_video('Intro-video')



# --- Main GAME code/loop ---
test_rect = pygame.Rect(100,100,100,50)
sonic = Player(0,0,34,34)
sonic.air_timer = 0

run = True
while run: # game loop
    display.fill((146,244,255))
    sonic.true_scrolling[0] += (sonic.rect.x - sonic.true_scrolling[0] - 265)/5
    sonic.true_scrolling[1] += (sonic.rect.y - sonic.true_scrolling[1] - 213)/5 #Make the camera moothing shifty and slowly
    scrolling = sonic.true_scrolling.copy() #Making an integer scrolling to avoid camera lags
    scrolling[0], scrolling[1] = int(sonic.true_scrolling[0]), int(sonic.true_scrolling[1])

    # --- Parallaxs / Backgrounds ---
    y_parallax = 0
    for backgrounds in parallax:
        bg = pygame.transform.scale(backgrounds[0], (int(backgrounds[0].get_rect().width*1), int(backgrounds[0].get_rect().height*1)))
        x_parallax = -scrolling[0]*backgrounds[1] % bg.get_rect().width
        display.blit(bg, (x_parallax - bg.get_rect().width, y_parallax))
        if x_parallax < 852*0.75:
            display.blit(bg, (x_parallax, y_parallax))
        x_parallax += 1
        #pygame.draw.line(display, (250,0,0), (x_parallax, 0), (x_parallax, 480*0.75), 3)
        y_parallax += bg.get_rect().height


    # --- Map / Blocs (tiles) / Textures ---
    tile_rects = []
    y = 0
    for row in game_map:
        x = 0
        for tile in row:
            if tile == '1':
                display.blit(dirt_image, (x * TILE_SIZE - scrolling[0], y * TILE_SIZE - scrolling[1]))
            if tile == '2':
                display.blit(grass_image, (x * TILE_SIZE - scrolling[0], y * TILE_SIZE - scrolling[1]))
            if tile != '0':
                tile_rects.append(pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            x += 1
        y += 1


    # --- Physics / Gravity ---
    sonic.movement[1] = 0
    if sonic.moving_right:
        sonic.movement[0] = sonic.acceleration
    if sonic.moving_left:
        sonic.movement[0] = -sonic.deceleration
    sonic.movement[1] += sonic.y_momentum
    sonic.y_momentum += .2
    if sonic.y_momentum > 3:
        sonic.y_momentum = 3

    sonic.rect, collisions = move(sonic.rect, sonic.movement, tile_rects)

    if collisions['bottom']:
        sonic.y_momentum = 0
        sonic.air_timer = 0
    else:
        sonic.air_timer += 1

    # --- Controls ---
    keys = pygame.key.get_pressed()
    for event in pygame.event.get(): # event loop
         if event.type == QUIT: # check for window quit
             pygame.quit() # stop pygame
             sys.exit() # stop script
         if event.type == KEYDOWN:
             if event.key == K_RIGHT and sonic.moving_left == False:
                 sonic.moving_right = True
                 sonic.direction_of_looking = 'Right'
                 sonic.deceleration = 2
             if event.key == K_LEFT and sonic.moving_right == False:
                 sonic.moving_left = True
                 sonic.direction_of_looking = 'Left'
                 sonic.acceleration = 2
             if event.key == K_RIGHT and sonic.moving_left == True:
                 sonic.movement[0] = 0
                 sonic.moving_left, sonic.moving_right = False, False
             if event.key == K_LEFT and sonic.moving_right == True:
                 sonic.movement[0] = 0
                 sonic.moving_left, sonic.moving_right = False, False
             if event.key == K_UP:
                 if sonic.air_timer < 6:
                     sonic.y_momentum = -5
         if event.type == KEYUP:
             if event.key == K_RIGHT:
                 sonic.moving_right = False
             if event.key == K_LEFT:
                 sonic.moving_left = False
         if keys[K_LALT] and keys[K_F4]:
             run = False
             

    #Acceleration / Deceleration
    if sonic.moving_left == False and sonic.moving_right == False:
        if sonic.movement[0] > 0.1:
            sonic.acceleration -= 0.08
            sonic.movement[0] = sonic.acceleration
        elif sonic.movement[0] < -0.1:
            sonic.movement[0] += 0.10
        else : sonic.movement[0] = 0
    if sonic.moving_right == True:
        if sonic.acceleration < 8:
            #spriting(walkRight)
            if sonic.acceleration < 3:
                sonic.acceleration += 0.2
            else : sonic.acceleration += 0.1
        else : 
            sonic.acceleration = 8
    if sonic.moving_left == True:
        if sonic.deceleration < 8:
            if sonic.deceleration < 3:
                sonic.deceleration += 0.2
            else : sonic.deceleration += 0.1
        else : sonic.deceleration = 8

    # --- Sprites ----
    #if sonic.air_timer > 0:
    #    if sonic.movement[1] > 1 and sonic.movement[1] < 0:
    #        spriting('Jump', 14, 'Right')
    if sonic.moving_right:
        if sonic.movement[0] >= 5:
            spriting('Run', 8, 'Right')
        elif sonic.movement[0] < 5:
            spriting('Walk', 12, 'Right')
    elif sonic.moving_left:
        if sonic.movement[0] <= -5:
            spriting('Run', 8, 'Left')
        elif sonic.movement[0] < 0:
            spriting('Walk', 12, 'Left')
    elif sonic.moving_right == False and sonic.movement[0] > 0:
        if sonic.movement[0] > 7:
            spriting('Run', 8, 'Right')
        elif sonic.movement[0] > 4:
            spriting('Walk', 12, 'Right')
        elif sonic.movement[0] > 0:
            spriting('Skid', 9, 'Right')
    elif sonic.moving_left == False and sonic.movement[0] < 0:
        if sonic.movement[0] < -7:
            spriting('Run', 8, 'Left')
        elif sonic.movement[0] < -4:
            spriting('Walk', 12, 'Left')
        elif sonic.movement[0] < 0:
            spriting('Skid', 9, 'Left')
    else : 
        if sonic.direction_of_looking == 'Left':
            display.blit(char[1], (sonic.rect.x-scrolling[0], sonic.rect.y-scrolling[1]))
        else :
            display.blit(char[0], (sonic.rect.x-scrolling[0], sonic.rect.y-scrolling[1]))


    update(SPEED) #Uses the update() function to update the screen frame

pygame.quit()
sys.exit()