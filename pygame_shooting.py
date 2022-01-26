import sys
import random
import pygame
import datetime
import time
from pygame.locals import *


# 縦，横のサイズ
WIDTH = 800
HEIGHT = 1000

# プレイヤーのサイズ（x,y），速度，初期位置
PLAYER_SIZE_X = 70
PLAYER_SIZE_Y = 80
PLAYER_X_CENTER = 25
PLAYER_SPEED = 30
PLAYER_POSITION_X = 400
PLAYER_POSITION_Y = 800

# 敵のサイズ（X,Y），画面に現れる最大数
ENEMY_SIZE_X = 100
ENEMY_SIZE_Y = 100
ENEMY_CENTER = 35
MAX_ENEMIES = 3

# 弾丸のサイズ（X,Y），速度，最大弾数
BULLET_SIZE_X = 10
BULLET_SIZE_Y = 40
BULLET_SPEED = 70
MAX_BULLETS = 2

# ビームのサイズ（X,Y），初期速度
BEAM_SIZE_X = 30
BEAM_SIZE_Y = 30
BEAM_SPEED = 20

# アイテムのサイズ（X,Y），スピード，画面に現れる最大数
ITEM_SIZE_X = 30
ITEM_SIZE_Y = 30
ITEM_SPEED = 8
MAX_ITEMS = 1

# 画面定義(X軸,Y軸,横,縦)
SURFACE = Rect(0, 0, WIDTH, HEIGHT)


### 背景クラス ###
class Background:
    
    def __init__(self, main):
        #　画像をロードしてtransformでサイズ調整（画面サイズに合わせる）
        self.image = pygame.image.load('./image/background.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (WIDTH, HEIGHT))
        
        #　画面のスクロール設定
        self.scroll = 0
        self.scroll_speed = 5
        
        # 他のオブジェクトを保存
        self.main = main
        
        #　画面縦サイズと0と二つをリストに入れておく
        self.imagesize = [HEIGHT, 0]
        
        
    #　描画メソッド
    def draw_BG(self, surface, flag, level, score): 
        # for文で２つの位置に１枚ずつ背景を描画
        for i in range(2):      
            surface.blit(self.image,(0, self.scroll - self.imagesize[i]))
        
        self.scroll += self.scroll_speed
        
        # 画像が端まで来たら初期位置に戻す
        if abs(self.scroll) > HEIGHT:
            self.scroll = 0
            
        # 状態に応じてテキストを表示する    
        # スタート画面
        if flag == 0:
            draw_text(surface, "SUPER",  80, WIDTH - (WIDTH/2), 200, "White", "m")
            draw_text(surface, "SHOOTING",  80, WIDTH - (WIDTH/2), 300, "White", "m")
            draw_text(surface, "Press Enter to start",  40, WIDTH - (WIDTH/2), 500, "white", "m")
            draw_text(surface, "Press R to open the scoreboard",  40, WIDTH - (WIDTH/2), 600, "white", "m")
            draw_text(surface, "Press Esc to exit",  40, WIDTH - (WIDTH/2), 700, "white", "m")
            
        # ゲームクリア
        elif flag == 2:
            draw_text(surface, "STAGE {:01d} CLEAR!".format(level),  80, WIDTH - (WIDTH/2), 300, "White", "m")
            draw_text(surface, "Press Enter to next stage",  40, WIDTH - (WIDTH/2), 500, "white", "m")
            draw_text(surface, "Press Esc to exit",  40, WIDTH - (WIDTH/2), 600, "white", "m")
            
        # ゲームオーバー
        elif flag == 3:
            draw_text(surface, "GAME OVER",  80, WIDTH - (WIDTH/2), 300, "Red", "m")
            draw_text(surface, "score : {:01d}".format(score),  60, WIDTH - (WIDTH/2), 400, "white", "m")
            draw_text(surface, "Press Enter to continue",  40, WIDTH - (WIDTH/2), 500, "white", "m")
            draw_text(surface, "Press R to open the scoreboard",  40, WIDTH - (WIDTH/2), 600, "white", "m")
            draw_text(surface, "Press Esc to exit",  40, WIDTH - (WIDTH/2), 700, "white", "m")
            
        # スコア表示
        elif flag == 4:
            with open('./Score/score.txt', 'r+') as f:
                # 全行を読む
                lines = f.read().splitlines()
                # 最新の11個だけ読み込む（最後の1個は改行のため，11個読み込む）
                last10 = lines[-10:]
                
                # スコア表示
                draw_text(surface, "SCORE BOARD", 80, 400, 50, "white", "m")
                for i in range(10):
                    draw_text(surface, last10[i], 60, 50, 200+(i*60), "white", "l")
                draw_text(surface, "Press R to return",  40, WIDTH - (WIDTH/2), 850, "white", "m")


### プレイヤークラス ###
class Player(pygame.sprite.Sprite):
    
    def __init__(self, enemies, beams, items):
        # スプライトクラスの初期化
        pygame.sprite.Sprite.__init__(self)
        
        # 画像の読み込み
        self.image = pygame.image.load("./image/shooter.png").convert_alpha()
        # 画像サイズ変更
        self.image = pygame.transform.scale(self.image, (PLAYER_SIZE_X, PLAYER_SIZE_Y))
        # 画像のrectサイズを取得
        self.rect = self.image.get_rect()
        self.rect.center = [PLAYER_POSITION_X, PLAYER_POSITION_Y]
        
        # 衝突音
        self.collision_sound = pygame.mixer.Sound('./mp3/BANG.mp3')
        self.collision_sound.set_volume(0.2)
        
        # プレイヤーの残機
        self.remaining_lives = 5
        
        # エネミーグループ，ビームグループ，アイテムグループを保存
        self.enemy = enemies
        self.beam = beams
        self.item = items
        
        # 無敵時間カウンターを初期化
        self.counter = 0
        
        # 現在の状態を管理
        self.DEAD = 1 # 1:生存 3:死亡 （フラグ管理の関係で数字が飛んでいる）
        self.INVINCIBLE = False
        self.item_flag = False
        
    
    # プレイヤー，その他テキストを描画するメソッド
    def draw(self, surface):
        surface.blit(self.image, self.rect)
        draw_text(surface, "remaining lives:{:02d}".format(self.remaining_lives), 40, WIDTH-20, 40, "white", "r")
        if self.INVINCIBLE == True and self.item_flag == False:
            draw_text(surface, "Clash!", 40, WIDTH/2, HEIGHT-100, "white", "m")
        elif self.INVINCIBLE == True and self.item_flag == True:
            draw_text(surface, "INVINCIBLE", 40, WIDTH/2, HEIGHT-100, "white", "m")
        
        
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
        # 衝突時のエポック秒を保持する変数
        global collision_UNIX_sec
        
        # 衝突判定
        if self.INVINCIBLE == False:  
            # 接触しているものをリストで返す
            enemy_list = pygame.sprite.spritecollide(self, self.enemy, True)
            beam_list = pygame.sprite.spritecollide(self, self.beam, True)
            item_list = pygame.sprite.spritecollide(self, self.item, True)
            
            # 敵とプレイヤー，ビームとプレイヤーの衝突判定
            if enemy_list or beam_list:
                self.collision_sound.play()
                # 衝突時のエポック秒を取得
                collision_UNIX_sec = time.time()
                self.INVINCIBLE = True
                self.init_position()
                self.remaining_lives -= 1
                
            elif item_list:
                # アイテムフラグをTrueにする
                self.item_flag = True
                # アイテム取得時のエポック秒
                collision_UNIX_sec = time.time()
                self.INVINCIBLE = True
            
        # 無敵時間
        if self.INVINCIBLE == True:
            # 無敵の間，エポック秒を取得し続ける
            elapse_UNIX_sec = time.time()
            # start_UNIX_secからの経過時間が2秒以上で無敵解除（2秒間無敵）
            if elapse_UNIX_sec - collision_UNIX_sec >= 2 and self.item_flag == False:
                self.INVINCIBLE = False
                self.item_flag = False
                
            elif elapse_UNIX_sec - collision_UNIX_sec >= 10 and self.item_flag == True:
                # 各フラグをFalseにする
                self.INVINCIBLE = False
                self.item_flag = False
            
        # ゲームオーバー
        if self.remaining_lives <= 0:
            self.DEAD = 3
    
    
    # 位置を初期化するメソッド
    def init_position(self):
        self.rect.centerx = PLAYER_POSITION_X
        self.rect.centery = PLAYER_POSITION_Y
                
        
### 敵クラス ###
class Enemy(pygame.sprite.Sprite):
    
    # インスタンス化の際に初期位置を引数x、yで指定
    def __init__(self, player, beams, score, level):
        pygame.sprite.Sprite.__init__(self)
 
        # 画像の読み込み
        self.image = pygame.image.load("./image/enemy.png").convert_alpha()
        # 画像サイズ変更
        self.image = pygame.transform.scale(self.image, (ENEMY_SIZE_X, ENEMY_SIZE_Y))
        # 画像のrectサイズを取得
        self.rect = self.image.get_rect()
        #self.rect.center = [x,y]
        
        self.invasion_sound = pygame.mixer.Sound('./mp3/invasion.mp3')
        self.invasion_sound.set_volume(0.2)
        
        # 他オブジェクト保存
        self.player = player
        self.beam = beams
        self.score = score
        
        # エネミーのスピードをランダムに決定
        self.speed = random.randint(3 + level , 7 + level)
 
        # エネミー初期位置
        self.rect.x = random.randint(0, WIDTH - ENEMY_SIZE_X)
        self.rect.y = 0 - ENEMY_SIZE_Y
    
    
    # 敵の移動やビーム射出
    def update(self):
        # 敵の速度
        self.rect.y += self.speed
        
        # ランダムでビーム射出
        if len(self.beam) < 5:
            if random.randint(0,100) > 99:
                x = self.rect.x
                y = self.rect.y
                self.beam.add(Beam(x, y, self.player))
            
        # 画面外に出たらオブジェクト消去 3体画面から出たらゲームオーバー
        if self.rect.bottom-ENEMY_SIZE_Y > SURFACE.height:
            self.invasion_sound.play()
            self.score.outside += 1
            self.kill()
            if self.score.outside == 3:
                self.player.DEAD = 3
            

### 弾丸クラス ###
class Bullet(pygame.sprite.Sprite):
    
    # インスタンス化の際に初期位置を引数x、yで指定
    def __init__(self, player, enemies, beams, score, main):
        pygame.sprite.Sprite.__init__(self)
        
        # 画像の読み込み
        self.image = pygame.image.load("./image/bullet.png").convert_alpha()
        # 画像サイズ変更
        self.image = pygame.transform.scale(self.image, (BULLET_SIZE_X, BULLET_SIZE_Y))
        # 画像のrectサイズを取得
        self.rect = self.image.get_rect()
        
        # 衝突音
        self.hit_sound = pygame.mixer.Sound('./mp3/BANG_2.mp3')
        self.hit_sound.set_volume(0.2)
        self.extinguishment_sound = pygame.mixer.Sound('./mp3/extinguishment.mp3')
        self.extinguishment_sound.set_volume(0.2)
        
        # 他オブジェクト保存
        self.player = player
        self.enemy = enemies
        self.beam = beams
        self.score = score
        self.main = main
        
        # 弾丸初期位置
        self.rect.x = self.player.rect.x + PLAYER_X_CENTER + 5
        self.rect.y = self.player.rect.y
        
    
    # 描画メソッド
    def update(self):
        # 弾丸の速度
        self.rect.y -= BULLET_SPEED
        
        # 接触しているものをリストで返す
        enemy_list = pygame.sprite.spritecollide(self, self.enemy, True)
        beam_list = pygame.sprite.spritecollide(self, self.beam, True)
        
        # 衝突判定
        # 敵と衝突したら消去 同時にスコア加算，敵を倒した数のカウントを行う
        if enemy_list:
            self.hit_sound.play()
            self.score.calc(5)
            self.main.count += 1
            # 敵を倒した数のトータルを保存
            self.score.count_total += 1
            self.kill()
            
        # ビームと衝突したら消去
        if beam_list:
            self.extinguishment_sound.play()
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
        self.image = pygame.image.load("./image/beam.png").convert_alpha()
        # 画像サイズ変更
        self.image = pygame.transform.scale(self.image, (BEAM_SIZE_X, BEAM_SIZE_X))
        # 画像のrectサイズを取得
        self.rect = self.image.get_rect()
        
        # 他オブジェクト保存
        self.player = player
        
        # ビーム初期位置
        self.rect.x = x + ENEMY_CENTER
        self.rect.y = y
        
    
    def update(self):
        # ビームの速度
        self.rect.y += BEAM_SPEED
        
        # プレイヤーとビームの当たり判定を調べる
        self.player.collision_detection()
            
        # 画面外に出たら消去
        if self.rect.bottom-BEAM_SIZE_Y > SURFACE.height:
            self.kill()
            

### アイテムクラス ###
class Item(pygame.sprite.Sprite):
    
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        
        # 画像の読み込み
        self.image = pygame.image.load("./image/item.png").convert_alpha()
        # 画像サイズ変更
        self.image = pygame.transform.scale(self.image, (BEAM_SIZE_X, BEAM_SIZE_X))
        # 画像のrectサイズを取得
        self.rect = self.image.get_rect()
        
        # スピードを決定
        self.speed = ITEM_SPEED
        
        # アイテム初期位置
        self.rect.x = random.randint(0, WIDTH - ITEM_SIZE_X)
        self.rect.y = 0 - ITEM_SIZE_Y
        
        
    # アイテムの移動
    def update(self):
        # アイテムの速度
        self.rect.y += self.speed
            
        # 画面外に出たらオブジェクト消去
        if self.rect.bottom-ITEM_SIZE_Y > SURFACE.height:
            self.kill()
        

### スコアクラス ###            
class Score:
    
    def __init__(self):
        # スコアを保持する変数
        self.score = 0
        # レベルを保存
        self.level = 0
        # 画面外に出た敵の数
        self.outside = 0
        # 倒した敵の数のトータル
        self.count_total = 0
        
        
    # スコアを計算するメソッド
    def calc(self, point):
        self.score = self.score + (point * 100)
        
    
    # レベルを加算するメソッド
    def add_level(self):
        self.level += 1
        
        
    # スコアやレベルを描画するメソッド
    def draw(self, surface):
        draw_text(surface, "SCORE:{:06d}".format(self.score), 40, 20, 40, "white", "l")
        draw_text(surface, "LEVEL:{:02d}".format(self.level + 1), 40, 20, 90, "white", "l")
        draw_text(surface, "KILL:{:04d}".format(self.count_total), 40, 20, 140, "white", "l")
        draw_text(surface, "RAID:{:01d}".format(self.outside), 40, 20, 190, "white", "l")
        

### メインクラス（ゲームのループを行う） ###
class Main:
    
    def __init__(self):
        # 画面初期化
        pygame.init()
        self.surface = pygame.display.set_mode(SURFACE.size)
        # 背景インスタンス化
        self.BG = Background(self)
        # 敵グループを作成
        self.enemies = pygame.sprite.Group()
        # 弾丸グループを作成
        self.bullets = pygame.sprite.Group()
        # ビームグループを作成
        self.beams = pygame.sprite.Group()
        # アイテムグループを作成
        self.items = pygame.sprite.Group()
        # プレイヤーインスタンス化
        self.player = Player(self.enemies, self.beams, self.items)
        # 時間オブジェクト生成
        self.clock = pygame.time.Clock()
        # スコアインスタンス化
        self.score = Score()
        
        # サウンドミキサーの初期化
        pygame.mixer.init() 
        # サウンド関連
        self.BGM_1 = pygame.mixer.Sound('./mp3/BGM.mp3')
        self.BGM_1.set_volume(0.2)
        self.BGM_2 = pygame.mixer.Sound('./mp3/BGM_2.mp3')
        self.BGM_2.set_volume(0.2)
        self.push_sound = pygame.mixer.Sound('./mp3/PUSH_1.mp3')
        self.push_sound.set_volume(0.2)
        self.push_sound_2 = pygame.mixer.Sound('./mp3/PUSH_2.mp3')
        self.push_sound_2.set_volume(0.2)
        self.cancel_sound = pygame.mixer.Sound('./mp3/CANCEL.mp3')
        self.cancel_sound.set_volume(0.2)
        self.shoot_sound = pygame.mixer.Sound('./mp3/SHOOT.mp3')
        self.shoot_sound.set_volume(0.2)
        
        # リスタートフラグ
        self.restart = False
        # 状態フラグ　0:初期状態 1:ゲームスタート 2:ゲームクリア 3:ゲームオーバー 4:スコア表示
        self.status_flag = 0
        # ステージのレベル設定
        self.level = 0
        # 敵を倒した数をカウント
        self.count = 0
        
        
    # スタート画面を描画し続けるためのメソッド    
    def start(self):
        
        # スタート画面用のBGMを流す
        self.BGM_1.play(-1)
        
        while True: 
            # フレームレート設定
            self.clock.tick(30)
            # 背景色設定
            self.surface.fill((0,0,0))
            
            # 背景描画メソッドを呼び出す
            self.BG.draw_BG(self.surface, self.status_flag, self.level, self.score.score)
            
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
                        
                    # Rキーが押されたらスコア確認画面へ
                    if event.key == K_r:
                        self.push_sound_2.play()
                        self.score_confirmation() 
                        
                    # エンターキーが押されたらゲーム開始
                    if event.key == K_RETURN:
                        self.push_sound.play()
                        self.BGM_1.stop()
                        self.BGM_2.play(-1)
                        self.status_flag = 1
                        return
                    
    
    # スコアを表示し続けるための関数
    def score_confirmation(self):
        # 元のフラグの状態を保存
        old_flag = self.status_flag
        # フラグをステータス表示に切り替え
        self.status_flag = 4
        
        while True: 
            # フレームレート設定
            self.clock.tick(30)
            # 背景色設定
            self.surface.fill((0,0,0))
            
            # 背景描画メソッドを呼び出す
            self.BG.draw_BG(self.surface, self.status_flag, self.level, self.score.score)
            
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
                        
                    # Rキーが押されたら元の画面に戻る
                    if event.key == K_r:
                        self.cancel_sound.play()
                        # フラグを元に戻す
                        self.status_flag = old_flag
                        return
                            

    # 結果の保存やステージクリア画面またはリザルト画面を描画し続けるためのメソッド    
    def result(self):
        # ゲームオーバー時，結果を保存する
        if self.status_flag == 3:
            # ファイルを追記でオープン
            with open('./Score/score.txt', 'a') as f:
                #日付とスコアをtxtファイルに保存
                print(datetime.datetime.now().strftime("%Y/%m/%d %H:%M"), ':', self.score.score, file=f)
        
        # ステージクリア画面またはリザルト画面を表示し続ける
        while True:      
            # フレームレート設定
            self.clock.tick(30)
            # 背景色設定
            self.surface.fill((0,0,0))
            
            # 背景描画メソッドを呼び出す
            self.BG.draw_BG(self.surface, self.status_flag, self.level, self.score.score)
            
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
                        # ステージクリア状態で終了する場合，結果の保存
                        if self.status_flag == 2:
                            # ファイルを追記でオープン
                            with open('./Score/score.txt', 'a') as f:
                                # 日付とスコアをtxtファイルに保存
                                print(datetime.datetime.now().strftime("%Y/%m/%d %H:%M"), ':', self.score.score, file=f)
                        exit()
                        
                    # Rキーが押されたらスコア確認画面へ
                    if event.key == K_r and self.status_flag == 3:
                        self.push_sound_2.play()
                        self.score_confirmation() 
                        
                    # エンターが押されたら再スタート
                    if event.key == K_RETURN:
                        self.push_sound.play()
                        self.restart = True
                        return
                            

    # メイン関数 
    def main(self):
        # スタートメソッドを呼び出す
        self.start()

        # ゲームのメインループ
        while self.status_flag:
             
            # フレームレート設定
            self.clock.tick(30)
            # 背景色設定
            self.surface.fill((0,0,0))
            
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
                        
                    # スペースキーが押されたら弾を発射（画面に存在できるのは2つまで）
                    if event.key == pygame.K_SPACE and len(self.bullets) < MAX_BULLETS:
                        self.shoot_sound.play()
                        self.bullets.add(Bullet(self.player, self.enemies, self.beams, self.score, self))   
    
            # 敵の生成
            if len(self.enemies) < MAX_ENEMIES + self.level:
                # 1ループごとに，1/40の確率で敵を生成
                if random.randint(0,40) > 39:
                    self.enemies.add(Enemy(self.player, self.beams, self.score, self.level))
                    
            # アイテムの生成
            if len(self.items) < MAX_ITEMS:
                # 1ループごとに，1/1000の確率でアイテムを生成
                if random.randint(0,1000) > 999:
                    self.items.add(Item())
                    
            # スプライトを更新
            self.player.update()
            self.enemies.update()
            self.bullets.update()
            self.beams.update()
            self.items.update()
    
            # スプライトを描画
            self.BG.draw_BG(self.surface, self.status_flag, self.level, self.score.score)
            self.enemies.draw(self.surface)
            self.player.draw(self.surface)
            self.bullets.draw(self.surface)
            self.beams.draw(self.surface)
            self.score.draw(self.surface)
            self.items.draw(self.surface)
            
            # プレイヤーの死亡情報を保存
            self.status_flag = self.player.DEAD
            
            # 敵を10+(level*3)体倒したらステージクリア
            if self.count == 10 + (self.level * 3):
                self.status_flag = 2
                # レベルを加算
                self.score.add_level()
                self.level = self.score.level
            
            # ゲームクリア・オーバー処理
            if self.status_flag == 2 or self.status_flag == 3:
                # リザルト画面を表示し続けるメソッドを呼び出す
                self.result()
            
            # リスタート処理
            if self.restart:
                # グループの中身を空にする
                self.enemies.empty()
                self.bullets.empty()
                self.beams.empty()
                self.items.empty()
                
                if self.status_flag == 3:
                    # レベルを初期化
                    self.level = 0
                    # プレイヤーインスタンス化
                    self.player = Player(self.enemies, self.beams, self.items)
                    # スコアインスタンス化（スコア初期化）
                    self.score = Score()
                    # 背景インスタンス化
                    self.BG = Background(self)
                
                # フラグ初期化
                self.status_flag = 1
                self.restart = False
                
                # 敵を倒した数を初期化
                self.count = 0
                
                continue
    
            # 画面更新
            pygame.display.update()

                                    
# フォントの設定
font_name = pygame.font.match_font('stencil')

# テキスト描画関数
def draw_text(screen, text, size, x, y, color, position):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if position == "l":
        text_rect.midleft = (x, y)
    elif position == "r":
        text_rect.midright = (x, y)
    elif position == "m":
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
