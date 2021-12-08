import sys
import time
import random
import pygame
from pygame.locals import *

# 画面定義(X軸,Y軸,横,縦)

WIDTH = 800
HEIGHT = 1000

SURFACE = Rect(0, 0, WIDTH, HEIGHT)

#バックグラウンドクラス
class Background:
    def __init__(self):
        #画像をロードしてtransformでサイズ調整（画面サイズに合わせる）
        self.image = pygame.image.load('BG.png').convert_alpha()
        self.image = pygame.transform.scale(self.image,(WIDTH,HEIGHT))
        #画面のスクロール設定
        self.scroll = 0
        self.scroll_speed = 7
        self.x = 0
        self.y = 0
        #0と画面横サイズの二つをリストに入れておく
        self.imagesize = [HEIGHT,0]
        
        
    #描画メソッド
    def draw_BG(self,screen): 
        #for文で２つの位置に１枚づつバックグラウンドを描画する（描画するx位置は上で指定したimagesizeリスト）
        for i in range(2):      
            screen.blit(self.image,(self.x, self.scroll - self.imagesize[i]))
        self.scroll += self.scroll_speed
        #画像が端まで来たら初期位置に戻す
        if abs(self.scroll) > HEIGHT:
            self.scroll = 0

# プレイヤークラス
class Player(pygame.sprite.Sprite):
    
    # インスタンス化の際に初期位置を引数x、yで指定
    def __init__(self, x, y):
        # スプライトクラスの初期化
        pygame.sprite.Sprite.__init__(self)
        
        # 画像の読み込み
        self.image = pygame.image.load("shooter.png").convert_alpha()
        
        # 画像サイズを変更する
        self.image = pygame.transform.scale(self.image, (100, 120))
        
        # 画像のrectサイズを取得
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
        
        #radiusは当たり判定の設定に必要
        self.radius = 40
        
        #現在の状態をture,falseで管理
        #self.IDLE = True
        #self.SHOT = False
        #self.DEAD = False
        #self.READY = False
        #self.IMMORTAL = False
        
    def draw(self, surface):
        
        surface.blit(self.image, self.rect)
        
        
    def update(self):
        
        #キー操作関連
        key = pygame.key.get_pressed()
        
        #上下左右の移動
        if key[pygame.K_a]:
            self.rect.x -= 20
            if self.rect.x <= 0: 
                self.rect.x = 0 

        if key[pygame.K_d]: 
            self.rect.x += 20 
            if self.rect.x >= WIDTH - 100:
                self.rect.x = WIDTH - 100

        if key[pygame.K_w]:
            self.rect.y -= 20
            if self.rect.y <= 0: 
                self.rect.y = 0 

        if key[pygame.K_s]: 
            self.rect.y += 20 
            if self.rect.y >= HEIGHT - 100:
                self.rect.y = HEIGHT - 100
        
# エネミークラス
class Enemy(pygame.sprite.Sprite):
    
    ############################
    ### 初期化メソッド
    ############################
    def __init__(self, name, x, y):
        pygame.sprite.Sprite.__init__(self)
 
        ### ファイル読み込み
        self.image = pygame.image.load(name).convert_alpha()
 
        ### 画像サイズ変更
        self.image = pygame.transform.scale(self.image, (130, 100))
 
        ### エネミーオブジェクト生成
        self.rect = self.image.get_rect()
        #self.rect.center = [x,y]
 
        ### エネミー初期位置
        self.rect.x = x
        self.rect.y = y - 100
        #self.dx = 0
        #self.dy  = 50
    
    
    def draw(self, surface):
        
        surface.blit(self.image, self.rect)
    
 
    ############################
    ### エネミー移動
    ############################
    
    def update(self):

        #global miss

        ### エネミー速度
        self.rect.y += random.randint(6,10)

        ### 画面外に出たら消去
        if self.rect.bottom-100 > SURFACE.height:
            #miss += 1
            self.kill()
    
"""    
     #毎フレームの処理用メソッド 
    def update(self):
        self.rect.x -= self.dx
        self.rect.y -= self.dy
        #move範囲
        if self.rect.top < 0 or self.rect.bottom > HEIGHT:
            self.dy *= -1 

        if self.rect.right < 0:
            self.rect.x = WIDTH
        
        ### 画面外に出たら消去
        if self.rect.left > SURFACE.width:
            self.kill()
"""

# メイン関数 
def main():

    # 画面初期化
    pygame.init()
    surface = pygame.display.set_mode(SURFACE.size)

    # 背景インスタンス化
    BG = Background()

    # プレイヤーインスタンス化
    player = Player(400, 800)
    
    # エネミーインスタンス化
    #enemy = Enemy("Enemy_2.png")
    
    # エネミーグループを作成
    enemies = pygame.sprite.Group()

    ### 時間オブジェクト生成
    clock = pygame.time.Clock()

    ### 無限ループ
    while True:

        ### フレームレート設定
        clock.tick(25)

        ### 背景色設定
        surface.fill((0,0,0))

        # スコアを描画
        # score.draw(surface)

        # 画面更新
        pygame.display.update()

        # イベント処理
        for event in pygame.event.get():

            # 終了処理
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                exit()

        ### 敵の生成
        if len(enemies) < 5:
            if random.randint(0,20) > 19:
                x = random.randint(0,670)
                y = 0
                enemies.add(Enemy("Enemy_2.png", x, y))

        ### スプライトを更新
        player.update()
        enemies.update()

        ### スプライトを描画
        BG.draw_BG(surface)
        player.draw(surface)
        enemies.draw(surface)

        ### 画面更新
        pygame.display.update()
        pygame.time.wait(20)

        ### イベント処理
        for event in pygame.event.get():

            ### 終了処理
            if event.type == QUIT:
                exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    exit()

# 終了関数
def exit():
    pygame.quit()
    sys.exit()


# メイン関数呼び出し
if __name__ == "__main__":

    # 処理開始
    main()
