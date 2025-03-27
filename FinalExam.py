import pygame
import pygame_menu
from pygame.locals import MOUSEBUTTONDOWN, MOUSEBUTTONUP
from random import randint

pygame.init()

SCREEN_WIDTH = 1000            #화면 넓이
SCREEN_HEIGHT = 600            #화면 높이
SURFACE = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))     #SURFACE
pygame.display.set_caption("기말과제 메이플 철권게임")                #윈도우

FPSCLOCK = pygame.time.Clock()
mousepos = []                  #마우스 인식을 위해 넣었음

#카운트 다운
intro_count = 3                 #게임 라운드 들어가기전에 카운트 다운
score = [0,0]                   #1p 2p 점수판
round_over = False              #라운드 종료 판별
ROUND_OVER_COOLDOWN = 2000      #게임 종료 쿨타임

#애니메이션 관련
P1_SIZE = 162                             #1p 이미지 하나당 픽셀 크기 
P1_SCALE = 4                              #1p 이미지 크기 배수                              
P1_OFFSET = [72,56]                       #초기
P1_DATA = [P1_SIZE,P1_SCALE, P1_OFFSET]
P2_SIZE = 250
P2_SCALE = 3
P2_OFFSET = [112,107]
P2_DATA = [P2_SIZE,P2_SCALE,P2_OFFSET]

player1_sound = pygame.mixer.Sound("1p_attack.wav")
player1_sound.set_volume(0.3)
player2_sound = pygame.mixer.Sound("2p_attack.wav")
player2_sound.set_volume(0.5)

#이미지
bg_image = pygame.image.load("arcss.png")
p1_sheet = pygame.image.load("1p_sprite_sheet.png")
p2_sheet = pygame.image.load("2p_sprite_sheet.png")
gameset_image = pygame.image.load("game_set.png")
how_to_control_image = pygame.image.load("how_to_control.png")
click_anywhere_image = pygame.image.load("click_anywhere.png")
p1_win_image = pygame.image.load("1pwin.png")
p2_win_image = pygame.image.load("2pwin.png")
game_icon = pygame.image.load("icon.png")

#그림 따오기
P1_FRAME = [1,4,1,6,7,3,8]    
P2_FRAME = [1,4,1,6,7,3,7]


class Player():
    def __init__(self,player,x,y,flip,data, sprite_sheet, animation_steps,sound) :   #순서대로(플레이어,x위치,y위치,뒤집기,,)
        self.player = player                                                         #플레이어 확인용
        self.size = data[0]                                                          #플레이어 이미지 사이즈
        self.image_scale = data[1]                                                   #플레이어 이미지 사이즈
        self.offset = data[2]                                                        #플레이어 초기 사이즈
        self.flip = flip                                                             #이미지 뒤집기
        self.animation_list = self.load_images(sprite_sheet, animation_steps)        #이미지 이어지게 만들기
        self.action = 0                                                              #행동 타입 0:기본 1:뛰기 2:점프 3:공격1 4:공격2 5:맞기 6: 죽음
        self.frame_index = 0                                                         #애니메이션 초기위치
        self.image = self.animation_list[self.action][self.frame_index]              #애니메이션 모션
        self.update_time = pygame.time.get_ticks()                                   #업데이트 될때 시간재기
        self.rect = pygame.Rect((x,y,80,180))                                        #캐릭터 블록크기
        self.vel_y = 0
        self.running = False                 #뛰고 있는지 상태
        self.jump = False                    #점프 하고 있는지 상태
        self.attacking = False               #공격 하고 있는지 상태
        self.attack_type = 0                 #공격 타입
        self.attack_cooldown = 0             #공격 쿨타임(연속 공격 방지)
        self.attack_sound = sound            #공격 소리
        self.hit = False                     #피격 상태
        self.health = 100                    #현재 체력
        self.alive = True                    #생존 여부

    def load_images(self,sprite_sheet, animation_steps) :         
        animation_list = []
        for y, animation in enumerate(animation_steps) :
            temp_img_list = []
            for x in range(animation):                 #애니메이션 따오기
                temp_img = sprite_sheet.subsurface(x * self.size, y * self.size, self.size, self.size)   #162픽셀이니까 아래로 위로 162씩 곱하기, 2p는 250
                temp_img_list.append(pygame.transform.scale(temp_img,(self.size * self.image_scale, self.size * self.image_scale)))   #한줄당 이미지 프레임리스트 완성
            animation_list.append(temp_img_list)
        return animation_list


    def move(self,screen_width,screen_height,surface,target,round_over) :
        SPEED = 10
        GRAVITY = 2
        dx = 0
        dy = 0
        self.running =False  #초기값
        self.attack_type = 0 #초기값

        key = pygame.key.get_pressed()   #키가 눌러졌으면

        if self.attacking == False and self.alive ==True and round_over == False :
            #이건 1p
            if self.player == 1 :
            #움직임
                if key[pygame.K_a] :
                    dx = -SPEED
                    self.running = True
                if key[pygame.K_d] :
                    dx = SPEED
                    self.running = True
                #점프
                if key[pygame.K_w] and self.jump == False: #더블 점프 방지
                    self.vel_y = -30
                    self.jump = True
                #공격키
                if key[pygame.K_g] or key[pygame.K_h]:
                    self.attack(target)
                    #어떤공격?
                    if key[pygame.K_g] :
                        self.attack_type =1
                    if key[pygame.K_h] :
                        self.attack_type =2

            #이건 2p
            if self.player == 2 :
            #움직임
                if key[pygame.K_LEFT] :
                    dx = -SPEED
                    self.running = True
                if key[pygame.K_RIGHT] :
                    dx = SPEED
                    self.running = True
                #점프
                if key[pygame.K_UP] and self.jump == False: #더블 점프 방지
                    self.vel_y = -30
                    self.jump = True
                #공격키
                if key[pygame.K_KP1] or key[pygame.K_KP2]:
                    self.attack(target)
                    #어떤공격?
                    if key[pygame.K_KP1] :
                        self.attack_type =1
                    if key[pygame.K_KP2] :
                        self.attack_type =2

        #중력작용 (점프했을때 떨어지게)
        self.vel_y += GRAVITY
        dy += self.vel_y

        #화면 밖에 나가는거 방지
        if self.rect.left + dx < 0 :                     #플레이어가 왼쪽 화면 밖으로 나가지 않게 하기
            dx = 0 - self.rect.left                      #왼쪽 화면에 붙어있게
        if self.rect.right + dx > screen_width :         #플레이어가 오른쪽 화면 밖으로 나가지 않게 하기
            dx = screen_width - self.rect.right          #오른쪽 화면에 붙어있게
        if self.rect.bottom + dy > screen_height - 110 : #플레이어 아래가 땅바닥보다 낮을시?
            self.vel_y = 0                               #플레이어 낙하속도 0으로 만들어주기
            self.jump = False                            #점프 상태 False 로 바꾸기
            dy = screen_height - 110 - self.rect.bottom  #현재 높이 설정

        if target.rect.centerx > self.rect.centerx :     #타겟의 중심이 내 중심의 x 위치가 더 크다면
            self.flip = False                            #캐릭터 보는뱡향 전환
        else :
            self.flip = True                             #캐릭터 보는뱡향 전환

        self.rect.x += dx                                #x좌표 움직이기
        self.rect.y += dy                                #y좌표 움직이기
        
        #쿨타임
        if self.attack_cooldown > 0 :
            self.attack_cooldown -= 1

    def update(self) :
        #플레이어가 무엇을하나
        if self.health <= 0 :
            self.health = 0
            self.alive = False
            self.update_action(6)             #죽음
        elif self.hit == True :
            self.update_action(5)             #맞았을때
        elif self.attacking == True:
            if self.attack_type == 1:
                self.update_action(3)         #공격1
            elif self.attack_type == 2:
                self.update_action(4)         #공격2
        elif self.jump == True :
            self.update_action(2)             #점프
        elif self.running == True :
            self.update_action(1)             #뛰기
        else :
            self.update_action(0)             #기본상태

        animation_cooldown = 50               #이미지가 바뀌는 딜레이(쿨타임)
        #이미지 업데이트
        self.image = self.animation_list[self.action][self.frame_index]             #애니메이션 리스트
        #업데이트
        if pygame.time.get_ticks() - self.update_time > animation_cooldown :
            self.frame_index += 1                                                   #애니메이션 프레임 +1
            self.update_time = pygame.time.get_ticks()
        #만약 그림이 끝났다면?
        if self.frame_index >= len(self.animation_list[self.action]) :              #애니메이션 프레임이 마지막 프레임까지 가면?
            #플레이어가 죽어있다면?
            if self.alive == False :
                self.frame_index = len(self.animation_list[self.action]) - 1        #죽은 모션 그대로 유지
            else:
                self.frame_index = 0                                                #애니메이션 초기화
                #공격 하고있었다면?
                if self.action == 3 or self.action == 4:
                    self.attacking = False
                    self.attack_cooldown = 20
                if self.action == 5:                        #데미지 맞았다면
                    self.hit = False
                    #동시에 맞고 멈춘다면?
                    self.attacking = False
                    self.attack_cooldown = 20
    
    def draw(self,surface) :
        img = pygame.transform.flip(self.image, self.flip, False) #좌우로 뒤집게 하기 (이미지, 좌우 플립, 상하플립X)
        surface.blit(img,(self.rect.x - (self.offset[0] * self.image_scale), self.rect.y - (self.offset[1] * self.image_scale)))

    def attack(self, target):
        if self.attack_cooldown == 0:
            self.attacking = True                               
            self.attack_sound.play() #공격소리                      #여기 아래 마주보게 하기
            attacking_rect = pygame.Rect(self.rect.centerx - (2* self.rect.width * self.flip), self.rect.y, 2 * self.rect.width, self.rect.height)
            if attacking_rect.colliderect(target.rect) : #공격 성공시
                global damage
                damage = randint(5,15)
                target.health -= damage           #데미지는 5~15사이의 수
                target.hit = True

    def update_action(self, new_action) :
        #액션이 달라지는거
        if new_action != self.action :
            self.action = new_action
            #업데이트 해야함
            self.frame_index = 0

#글씨체
count_font = pygame.font.SysFont(None, 200)
score_font = pygame.font.SysFont(None, 30)
player_font = pygame.font.SysFont(None,70)
timer_font = pygame.font.SysFont(None,110)
damage_font = pygame.font.SysFont(None, 80)


def draw_text(text,font,text_col,x,y):
    img = font.render(text,True,text_col)
    SURFACE.blit(img,(x,y))

#색깔
RED = (255,0,0)
YELLOW = (255,255,0)
WHITE = (255,255,255)

def draw_health_bar(hp,x,y,) :
    ratio = hp / 100
    pygame.draw.rect(SURFACE,RED, (x,y,330,40))
    pygame.draw.rect(SURFACE,YELLOW,(x,y,330 * ratio ,40))

def main() :
    pygame.mixer.music.load("mainmusic.mp3") #음악파일 불러오기
    pygame.mixer.music.set_volume(0.3)       #음악파일 volume
    pygame.mixer.music.play(-1)              #무한반복
    intro_count = 3
    last_count_update = pygame.time.get_ticks()
    score = [0,0]  #1p 2p 점수판
    round_over = False
    #플레이어
    player1 = Player(1,200,310, False, P1_DATA, p1_sheet, P1_FRAME, player1_sound)
    player2 = Player(2,700,310,True, P2_DATA ,p2_sheet, P2_FRAME ,player2_sound)
    game_countdown = 30

    run = True
    while run :
        
        FPSCLOCK.tick(60)
        #damage = randint(5,15)     #여기에 한번더 써야 데미지가 새로 또 바뀜
        #배경화면 그리기
        SURFACE.blit(bg_image,(0,0))

        #체력 바 & 점수 표기
        draw_health_bar(player1.health,90,20)
        draw_health_bar(player2.health,580,20)
        draw_text(str(score[0]), score_font, (0,0,0), 410, 60)
        draw_text(str(score[1]), score_font, (0,0,0), 580, 60)
        draw_text("1P", player_font, (0,0,0), 20, 20)
        draw_text("2P", player_font, (0,0,0), 930, 20)
        

        if intro_count <= 0 :    #3 2 1 카운트 다운 끝날 시
            #플레이어 움직이기
            player1.move(SCREEN_WIDTH, SCREEN_HEIGHT, SURFACE, player2,round_over)
            player2.move(SCREEN_WIDTH, SCREEN_HEIGHT, SURFACE, player1,round_over)
            if game_countdown > 0 :
                draw_text(str(game_countdown),timer_font, WHITE, 460, 30)                   #게임 제한시간 이미지
                if pygame.time.get_ticks()  - game_countdown > ROUND_OVER_COOLDOWN:              
                    if player1.action == 5 :                                                #1p피격 상태일 시
                        if pygame.time.get_ticks()  - game_countdown > ROUND_OVER_COOLDOWN:
                            draw_text(str(damage),damage_font, YELLOW, player1.rect.centerx - 50 , player1.rect.centery - 200)
                    elif player2.action == 5 :                                              #2p피격 상태일 시
                        draw_text(str(damage),damage_font, YELLOW, player2.rect.centerx , player2.rect.centery - 200)
                        
            else : #비겼을시(타임아웃)
                round_over == True
                if pygame.time.get_ticks() > ROUND_OVER_COOLDOWN:
                    round_over = False
                    game_countdown = 30
                    intro_count = 3
                    player1 = Player(1,200,310, False, P1_DATA, p1_sheet, P1_FRAME, player1_sound)
                    player2 = Player(2,700,310,True, P2_DATA ,p2_sheet, P2_FRAME ,player2_sound)
                
            if (pygame.time.get_ticks() - last_count_update) >= 1000 : #시간 감소
                last_count_update = pygame.time.get_ticks()
                game_countdown -= 1
        else :
            #시작 타이머 작동
            draw_text(str(intro_count),count_font, RED, SCREEN_WIDTH /2 - 50, 250)
            if (pygame.time.get_ticks() - last_count_update) >= 1000 :
                intro_count -= 1
                last_count_update = pygame.time.get_ticks()

        player1.update()
        player2.update()
        player1.draw(SURFACE)
        player2.draw(SURFACE)

        #플레이어 사망시
        if round_over == False :                             #라운드가 끝나지 않았을때
            if player1.alive == False :                      #생존 해 있을 때
                score[1] += 1                                #2p 승리로 점수 추가
                round_over = True
                round_over_time = pygame.time.get_ticks()
            elif player2.alive == False :                    #위와 동일
                score[0] += 1
                round_over = True
                round_over_time = pygame.time.get_ticks()
        else :
            if score[0] < 3 and score[1] < 3 :
                SURFACE.blit(gameset_image,(SCREEN_WIDTH / 2 - 200,180))
            elif score[0] == 3:                                            #1P가 3점 가져갔을 시
                SURFACE.blit(p1_win_image,(SCREEN_WIDTH / 2 - 250,180))
                if pygame.time.get_ticks() - round_over_time > ROUND_OVER_COOLDOWN:
                    run = False                                            #게임 종료 -> 메뉴로 가기
            elif score[1] == 3:                                            #2P가 3점 가져갔을 시
                SURFACE.blit(p2_win_image,(SCREEN_WIDTH / 2 - 250,180))
                if pygame.time.get_ticks() - round_over_time > ROUND_OVER_COOLDOWN:
                    run = False                                            #게임 종료 -> 메뉴로 가기
            if pygame.time.get_ticks() - round_over_time > ROUND_OVER_COOLDOWN:
                round_over = False
                game_countdown = 30                                        #게임 제한 시간 30초
                intro_count = 3                                            #게임 시작전 대기시간 3초
                player1 = Player(1,200,310, False, P1_DATA, p1_sheet, P1_FRAME, player1_sound)
                player2 = Player(2,700,310,True, P2_DATA ,p2_sheet, P2_FRAME ,player2_sound)      

        for event in pygame.event.get() :
            if event.type == pygame.QUIT :
                run = False                                                #윈도우키 X 누르면 메뉴로 나가게

        pygame.display.update()

def show_controls() :
    control_run = True
    while control_run:
        SURFACE.blit(bg_image,(0,0))                  #게임 배경화면과 동일하게
        SURFACE.blit(how_to_control_image,(180,150))  #게임 설명서
        SURFACE.blit(click_anywhere_image,(325,500))  #아무곳 클릭 문구
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                control_run = False
            elif event.type == MOUSEBUTTONDOWN:       #마우스클릭(down)인식
                mousepos.append(event.pos)
            elif event.type == MOUSEBUTTONUP:         #마우스클립(up) 인식
                control_run = False
                mousepos.clear()

            pygame.display.update()

def show_start_menu():
    pygame.display.set_icon(game_icon)
    hanfont = pygame.font.SysFont("malgungothic", 30)
    t = pygame_menu.themes.THEME_BLUE.copy()
    t.widget_font=hanfont
    menu = pygame_menu.Menu("Maple Tekken", 500, 300,theme=t)
    menu.add.button("게임 시작", main)
    menu.add.button("조작 방법", show_controls)
    menu.add.button("게임 종료", pygame_menu.events.EXIT)
    menu.mainloop(SURFACE)

if __name__ == '__main__':
    show_start_menu()
