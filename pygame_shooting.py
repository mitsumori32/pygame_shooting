import sys
import random
import pygame
from pygame.locals import *

# 縦，横のサイズ
WIDTH = 800
HEIGHT = 1000

# プレイヤーのサイズ（x,y），速度，初期位置
PLAYER_SIZE_X = 100
PLAYER_SIZE_Y = 120
PLAYER_X_CENTER = 37
PLAYER_SPEED = 30
PLAYER_INITIAL_POSITION_X = 400
PLAYER_INITIAL_POSITION_Y = 800

# 敵のサイズ（X,Y）
ENEMY_SIZE_X = 130
ENEMY_SIZE_Y = 100

# 弾丸のサイズ（X,Y），速度
BULLET_SIZE_X = 25
BULLET_SIZE_Y = 25
BULLET_SPEED = 30

# ビームのサイズ（X,Y），速度
BEAM_SIZE_X = 50
BEAM_SIZE_Y = 50
BEAM_SPEED = 15

# 画面定義(X軸,Y軸,横,縦)
SURFACE = Rect(0, 0, WIDTH, HEIGHT)


### 背景クラス ###
class Background:
    
    def __init__(self):
        #　画像をロードしてtransformでサイズ調整（画面サイズに合わせる）
        self.image = pygame.image.load('BG.png').convert_alpha()
        self.image = pygame.transform.scale(self.image,(WIDTH,HEIGHT))
        
        #　画面のスクロール設定
        self.scroll = 0
        self.scroll_speed = 7
        self.x = 0
        self.y = 0
        
        #　0と画面横サイズの二つをリストに入れておく
        self.imagesize = [HEIGHT,0]
        
        
    #　描画メソッド
    def draw_BG(self, surface, flag): 
        #for文で２つの位置に１枚づつバックグラウンドを描画する（描画するx位置は上で指定したimagesizeリスト）
        for i in range(2):      
            surface.blit(self.image,(self.x, self.scroll - self.imagesize[i]))
        
        self.scroll += self.scroll_speed
        
        #画像が端まで来たら初期位置に戻す
        if abs(self.scroll) > HEIGHT:
            self.scroll = 0
            
        if(flag == False):
            #pygame.draw.rect(self.surface, (255,255,255), (0,200,100,180))
            draw_text(surface, "SHOOTING",  100, WIDTH - (WIDTH/2), 300, "White")
            draw_text(surface, "Press SPACE to start",  50, WIDTH - (WIDTH/2), 500, "white")
            draw_text(surface, "Press Esc to exit",  50, WIDTH - (WIDTH/2), 600, "white")            

### プレイヤークラス ###
class Player(pygame.sprite.Sprite):
    
    # インスタンス化の際に初期位置を引数x、yで指定
    def __init__(self, x, y, enemies, beams):
        # スプライトクラスの初期化
        pygame.sprite.Sprite.__init__(self)
        
        # 画像の読み込み
        self.image = pygame.image.load("shooter.png").convert_alpha()
        # 画像サイズ変更
        self.image = pygame.transform.scale(self.image, (PLAYER_SIZE_X, PLAYER_SIZE_Y))
        # 画像のrectサイズを取得
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
        
        # プレイヤーの残機
        self.remaining_lives = 5
        
        # エネミーグループ，ビームグループを保存
        self.enemy = enemies
        self.beam = beams
        
        # 無敵時間カウンターを初期化
        self.counter = 0
        
        # 現在の状態をture,falseで管理
        #self.IDLE = True
        #self.SHOT = False
        self.DEAD = False
        #self.READY = False
        #self.IMMORTAL = False
        self.INVINCIBLE = False
        
    
    # プレイヤーを描画するメソッド
    def draw(self, surface):
        surface.blit(self.image, self.rect)
        draw_text(surface, "remaining lives:{:02d}".format(self.remaining_lives), 50, 640, 0, "white")
        
        
    # 描画メソッド
    def update(self):
        # キー操作関連
        key = pygame.key.get_pressed()
        
        # 上下左右の移動
        if key[pygame.K_a]:
            self.rect.x -= PLAYER_SPEED
            if self.rect.x <= 0: 
                self.rect.x = 0 

        if key[pygame.K_d]:
            self.rect.x += PLAYER_SPEED 
            if self.rect.x >= WIDTH - PLAYER_SIZE_X:
                self.rect.x = WIDTH - PLAYER_SIZE_X

        if key[pygame.K_w]:
            self.rect.y -= PLAYER_SPEED
            if self.rect.y <= 0: 
                self.rect.y = 0 

        if key[pygame.K_s]: 
            self.rect.y += PLAYER_SPEED
            if self.rect.y >= HEIGHT - PLAYER_SIZE_Y:
                self.rect.y = HEIGHT - PLAYER_SIZE_Y
           
        # 衝突判定メソッドを呼び出す
        self.collision_detection()
                
        
    # 衝突判定メソッド
    def collision_detection(self):
        # 無敵時間カウンターを加算
        self.counter += 1
        
        # 接触しているものをリストで返す
        enemy_list = pygame.sprite.spritecollide(self, self.enemy, True)
        beam_list = pygame.sprite.spritecollide(self, self.beam, True)
        
        # 衝突判定
        if self.INVINCIBLE == False:
            # 敵とプレイヤーの衝突判定
            if enemy_list:
                self.counter = 0
                self.INVINCIBLE = True
                self.init_position()
                self.remaining_lives -= 1
                
            # ビームとプレイヤーの衝突判定
            if beam_list:
                self.counter = 0
                self.INVINCIBLE = True
                self.init_position()
                self.remaining_lives -= 1
            
        # 無敵時間
        if self.INVINCIBLE == True and self.counter > 150:
            self.counter = 0
            self.INVINCIBLE = False
            
        # ゲームオーバー
        if self.remaining_lives <= 0:
            self.DEAD = True
            exit()
    
    
    # 位置を初期化するメソッド
    def init_position(self):
        self.rect.centerx = PLAYER_INITIAL_POSITION_X
        self.rect.centery = PLAYER_INITIAL_POSITION_Y
                
        
### 敵クラス ###
class Enemy(pygame.sprite.Sprite):
    
    # インスタンス化の際に初期位置を引数x、yで指定
    def __init__(self, x, y, player, bullets, beams):
        pygame.sprite.Sprite.__init__(self)
 
        # 画像の読み込み
        self.image = pygame.image.load("Enemy_2.png").convert_alpha()
        # 画像サイズ変更
        self.image = pygame.transform.scale(self.image, (ENEMY_SIZE_X, ENEMY_SIZE_Y))
        # 画像のrectサイズを取得
        self.rect = self.image.get_rect()
        #self.rect.center = [x,y]
        
        # 他オブジェクト保存
        self.player = player
        self.bullet = bullets
        self.beam = beams
        
        # エネミーのスピードをランダムに決定
        self.speed = random.randint(5,10)
 
        # エネミー初期位置
        self.rect.x = x
        self.rect.y = y - ENEMY_SIZE_Y
    
    
    # 敵の移動やビーム射出
    def update(self):
        # 敵の速度
        self.rect.y += self.speed
        
        # ランダムでビーム射出
        if len(self.beam) < 10:
            if random.randint(0,200) > 199:
                x = self.rect.x
                y = self.rect.y
                self.beam.add(Beam(x, y, self.player))
            
        # 画面外に出たら消去
        if self.rect.bottom-ENEMY_SIZE_Y > SURFACE.height:
            self.kill()
            

### 弾丸クラス ###
class Bullet(pygame.sprite.Sprite):
    
    # インスタンス化の際に初期位置を引数x、yで指定
    def __init__(self, player, enemies, beams, score):
        pygame.sprite.Sprite.__init__(self)
        
        # 画像の読み込み
        self.image = pygame.image.load("Bullet.png").convert_alpha()
        # 画像サイズ変更
        self.image = pygame.transform.scale(self.image, (BULLET_SIZE_X, BULLET_SIZE_Y))
        # 画像のrectサイズを取得
        self.rect = self.image.get_rect()
        #self.rect.center = [x,y]
        
        # 他オブジェクト保存
        self.player = player
        self.enemy = enemies
        self.beam = beams
        self.score = score
        
        # 弾丸初期位置
        self.rect.x = self.player.rect.x + PLAYER_X_CENTER
        self.rect.y = self.player.rect.y
        
    
    # 描画メソッド
    def update(self):
        # 弾丸の速度
        self.rect.y -= BULLET_SPEED
        
        # 接触しているものをリストで返す
        enemy_list = pygame.sprite.spritecollide(self, self.enemy, True)
        beam_list = pygame.sprite.spritecollide(self, self.beam, True)
        
        # 衝突判定
        # 敵と衝突したら消去
        if enemy_list:
            self.score.calc(5)
            self.kill()
            
        # ビームと衝突したら消去
        if beam_list:
            self.score.calc(1)
            self.kill()
            
        # 画面外に出たら消去
        if  self.rect.bottom < 0:
            self.kill()
    

### ビームクラス ###
class Beam(pygame.sprite.Sprite):
    
    def __init__(self, x, y, player):
        pygame.sprite.Sprite.__init__(self)
        
        # 画像の読み込み
        self.image = pygame.image.load("Beam.png").convert_alpha()
        # 画像サイズ変更
        self.image = pygame.transform.scale(self.image, (BEAM_SIZE_X, BEAM_SIZE_X))
        # 画像のrectサイズを取得
        self.rect = self.image.get_rect()
        #self.rect.center = [x,y]
        
        # 他オブジェクト保存
        self.player = player
        
        # ビーム初期位置
        self.rect.x = x + 50
        self.rect.y = y
        
    
    def update(self):
        # ビームの速度
        self.rect.y += BEAM_SPEED
        
        # プレイヤーとビームの当たり判定を調べる
        self.player.collision_detection()
            
        # 画面外に出たら消去
        if self.rect.bottom-BEAM_SIZE_Y > SURFACE.height:
            self.kill()
        

### スコアクラス ###            
class Score:
    
    def __init__(self):
        # スコアを保持する変数
        self.score = 0
        
        
    # スコアを計算するメソッド
    def calc(self, point):
        self.score = self.score + (point * 100)
        
        
    # スコアを描画するメソッド
    def draw(self, surface):
        draw_text(surface, "score:{:06d}".format(self.score), 50, 110, 0, "white")
        

### メインクラス（ゲームのループを行う） ###
class Main:
    
    def __init__(self):
        # 画面初期化
        pygame.init()
        self.surface = pygame.display.set_mode(SURFACE.size)
        # 背景インスタンス化
        self.BG = Background()
        # 敵グループを作成
        self.enemies = pygame.sprite.Group()
        # 弾丸グループを作成
        self.bullets = pygame.sprite.Group()
        # ビームグループを作成
        self.beams = pygame.sprite.Group()
        # プレイヤーインスタンス化
        self.player = Player(PLAYER_INITIAL_POSITION_X, PLAYER_INITIAL_POSITION_Y, self.enemies, self.beams)
        # 時間オブジェクト生成
        self.clock = pygame.time.Clock()
        # スコアインスタンス化
        self.score = Score()
        
        # 各種フラグ
        self.game_start = False
        
    # スタート画面を描画し続けるためのメソッド    
    def start(self):
        
        while True: 
            # フレームレート設定
            self.clock.tick(30)

            # 背景色設定
            self.surface.fill((0,0,0))
            
            # タイトル画面描画メソッドを呼び出す
            self.BG.draw_BG(self.surface, self.game_start)
            
            # 画面更新
            pygame.display.update()
            
            # イベント処理
            for event in pygame.event.get():
                
                # 終了処理
                if event.type == QUIT:
                    exit()
                    
                # キーが押された時のイベント処理    
                if event.type == KEYDOWN:
                    # エスケープキーが押されたら終了
                    if event.key == K_ESCAPE:         
                        exit()
                        
                    # スペースキーが押されたらゲーム開始
                    if event.key == K_SPACE:
                        self.game_start = True
                        return
            
            
    
    # メイン関数 
    def main(self):
        
        # スタートメソッドを呼び出す
        self.start()
        
        # ゲームのメインループ
        while self.game_start:
            # イベント処理
            for event in pygame.event.get():
                # 終了処理
                if event.type == QUIT:
                    exit()
                    
                # ゲームオーバー時の処理
                
                # ゲームクリア時の処理
                    
                # キーが押された時のイベント処理    
                if event.type == KEYDOWN:
                    # エスケープキーが押されたら終了
                    if event.key == K_ESCAPE:         
                        exit()
                        
                    # スペースキーが押されたら弾を発射
                    if event.key == pygame.K_SPACE:
                        self.bullets.add(Bullet(self.player, self.enemies, self.beams, self.score))
            
            # フレームレート設定
            self.clock.tick(30)
    
            # 背景色設定
            self.surface.fill((0,0,0))
    
            # 敵の生成
            if len(self.enemies) < 7:
                if random.randint(0,20) > 19:
                    x = random.randint(0, WIDTH - ENEMY_SIZE_X)
                    y = 0
                    self.enemies.add(Enemy(x, y, self.player, self.bullets, self.beams))
                    
            # スプライトを更新
            self.player.update()
            self.enemies.update()
            self.bullets.update()
            self.beams.update()
    
            # スプライトを描画
            self.BG.draw_BG(self.surface, self.game_start)
            self.player.draw(self.surface)
            self.enemies.draw(self.surface)
            self.bullets.draw(self.surface)
            self.beams.draw(self.surface)
            self.score.draw(self.surface)
    
            # 画面更新
            pygame.display.update()

                                         
# フォントの設定
font_name = pygame.font.match_font('メイリオ')

# テキスト描画関数
def draw_text(screen, text, size, x, y, color):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    screen.blit(text_surface, text_rect)


# 終了関数
def exit():
    pygame.quit()
    sys.exit()


# メインクラスのインスタンス化
Main = Main()
# main関数呼び出し
Main.main()
