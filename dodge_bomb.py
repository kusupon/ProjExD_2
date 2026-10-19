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


def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """
    引数: なし
    戻り値: 複数のサイズの爆弾Surfaceのリストと加速度のリスト
    """
    bb_imgs = []
    for r in range(1, 11):
        bb_img = pg.Surface((20*r, 20*r))
        pg.draw.circle(bb_img, (255, 0, 0), (10*r, 10*r), 10*r)
        bb_img.set_colorkey((0, 0, 0))
        bb_imgs.append(bb_img)
    bb_accs = [a for a in range(1, 11)]

    return bb_imgs, bb_accs


def get_kk_imgs() -> dict[tuple[int, int], pg.Surface]:
    """
    引数：なし
    戻り値：移動量のタプルとこうかとんのSurfaceを対応させた辞書
    移動する8方向と停止時の画像を用意する
    """
    kk_img = pg.image.load("fig/3.png")  # 左向きの画像
    kk_right_img = pg.transform.flip(kk_img, True, False)
    kk_dict = {
        (0, 0): pg.transform.rotozoom(kk_img, 0, 0.9),  # キー押下がない場合
        (+5, 0): pg.transform.rotozoom(kk_right_img, 0, 0.9),  # 右
        (+5, -5): pg.transform.rotozoom(kk_right_img, 45, 0.9),  # 右上
        (0, -5): pg.transform.rotozoom(kk_right_img, 90, 0.9),  # 上
        (-5, -5): pg.transform.rotozoom(kk_img, -45, 0.9),  # 左上
        (-5, 0): pg.transform.rotozoom(kk_img, 0, 0.9),  # 左
        (-5, +5): pg.transform.rotozoom(kk_img, 45, 0.9),  # 左下
        (0, +5): pg.transform.rotozoom(kk_right_img, -90, 0.9),  # 下
        (+5, +5): pg.transform.rotozoom(kk_right_img, -45, 0.9),  # 右下
    }
    return kk_dict


def calc_orientation(org: pg.Rect, dst: pg.Rect, current_xy: tuple[float, float]) -> tuple[float, float]:
    """
    引数：爆弾のRect こうかとんのRect 現在の移動方向
    戻り値：移動方向を表すタプル（vx,vy）
    距離が300未満なら現在の方向を保ち, それ以外はこうかとんへ追従する
    """
    # 爆弾からこうかとんへの方向を求める
    dx = dst.centerx - org.centerx
    dy = dst.centery - org.centery
    distance = (dx ** 2 + dy ** 2) ** 0.5  # 中心同士の距離
    if distance < 300:
        return current_xy  # 近いときは今の方向へ直進する
    speed = 50 ** 0.5  # 速度ベクトルの長さを√50に
    # 方向を保ったまま，ベクトルの長さをそろえる
    return dx / distance * speed, dy / distance * speed


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")
    kk_imgs = get_kk_imgs()
    kk_img = kk_imgs[(0, 0)]
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    bb_imgs, bb_accs = init_bb_imgs()
    bb_img = bb_imgs[0]
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

        idx = min(tmr // 500, 9)
        bb_img = bb_imgs[idx]
        bb_rct.width = bb_img.get_width()
        bb_rct.height = bb_img.get_height()

        if kk_rct.colliderect(bb_rct):  # こうかとんと爆弾のrectが重なった場合
            gameover(screen)
            pg.display.update()
            time.sleep(5)
            return

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for k, tpl in DELTA.items():
            if key_lst[k]:
                sum_mv[0] += tpl[0]  # 横方向移動量
                sum_mv[1] += tpl[1]  # 縦方向移動量

        kk_img = kk_imgs[tuple(sum_mv)]
        kk_rct = kk_img.get_rect(center=kk_rct.center)
        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):  # 座標が画面外にある場合
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])  # 先程の動きをキャンセル
        screen.blit(kk_img, kk_rct)
        # 爆弾の進む方向を更新する
        vx, vy = calc_orientation(bb_rct, kk_rct, (vx, vy))
        # 時間経過に応じた速度倍率を掛ける
        avx = vx * bb_accs[idx]
        avy = vy * bb_accs[idx]
        bb_rct.move_ip(avx, avy)
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
