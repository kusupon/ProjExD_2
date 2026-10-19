import os
import random
import time
import sys
import pygame as pg


WIDTH, HEIGHT = 1100, 650
DELTA = {
    pg.K_UP: (0, -5),
    pg.K_DOWN: (0, +5),
    pg.K_LEFT: (-5, 0),
    pg.K_RIGHT: (+5, 0),
}
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def check_bound(rect: pg.Rect) -> tuple[bool, bool]:
    """
    引数：こうかとんまたは爆弾のRect
    戻り値：タプル（横方向判定結果，縦方向判定結果）
    画面内ならTrue 画面外ならFalse
    """
    yoko, tate = True, True
    if rect.left < 0 or WIDTH < rect.right:  # 横方向判定
        yoko = False
    if rect.top < 0 or HEIGHT < rect.bottom:  # 縦方向判定
        tate = False
    return yoko, tate


def gameover(screen: pg.Surface) -> None:
    """
    引数：画面のSurface
    戻り値：なし
    画面を暗くしGame Overの文字とこうかとんを描画する
    """
    go_img = pg.Surface((WIDTH, HEIGHT))
    go_rct = pg.Rect(0,0,WIDTH, HEIGHT)
    pg.draw.rect(go_img, (0, 0, 0), go_rct)
    go_img.set_alpha(220)
    
    message_font = pg.font.Font(None, 80)
    txt = message_font.render("Game Over", True, (255, 255, 255))
    go_img.blit(txt, [400, 300])

    kk_img = pg.image.load("fig/8.png")
    k_rct = kk_img.get_rect()
    k_rct.center = WIDTH // 4, HEIGHT // 2
    go_img.blit(kk_img, k_rct)

    kk2_img = pg.image.load("fig/8.png")
    k2_rct = kk2_img.get_rect()
    k2_rct.center = WIDTH * 3 // 4, HEIGHT // 2
    go_img.blit(kk2_img, k2_rct)
    screen.blit(go_img, [0,0])

def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    bb_img = pg.Surface((20, 20))
    pg.draw.circle(bb_img, (255, 0, 0), (10, 10), 10)
    bb_img.set_colorkey((0, 0, 0))
    bb_rct = bb_img.get_rect()
    bb_rct.centerx = random.randint(0, WIDTH)
    bb_rct.centery = random.randint(0, HEIGHT)
    vx, vy = +5, +5
    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        screen.blit(bg_img, [0, 0]) 

        if kk_rct.colliderect(bb_rct): # こうかとんと爆弾のrectが重なった場合
            gameover(screen)
            pg.display.update()
            time.sleep(5)
            return

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        # if key_lst[pg.K_UP]:
        #     sum_mv[1] -= 5
        # if key_lst[pg.K_DOWN]:
        #     sum_mv[1] += 5
        # if key_lst[pg.K_LEFT]:
        #     sum_mv[0] -= 5
        # if key_lst[pg.K_RIGHT]:
        #     sum_mv[0] += 5
        for k, tpl in DELTA.items():
            if key_lst[k]:
                sum_mv[0] += tpl[0] # 横方向移動量
                sum_mv[1] += tpl[1] # 縦方向移動量

        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):  # 座標が画面外にある場合
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])  # 先程の動きをキャンセル
        screen.blit(kk_img, kk_rct)
        bb_rct.move_ip(vx, vy)
        yoko, tate = check_bound(bb_rct)
        if not yoko:  
            vx *= -1
        if not tate:  
            vy *= -1
        screen.blit(bb_img, bb_rct)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
