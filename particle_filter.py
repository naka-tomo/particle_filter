# encoding: utf8
from __future__ import unicode_literals
import cv2
import numpy as np
import random


# パーティクルフィルタの設定
sigma = 50
rectsize = 20
num_particles = 200

# パーティクル
class Particle():
    def __init__(self, x=0, y=0, w=0 ):
        self.x = x
        self.y = y
        self.weight = w


# マウスの現在位置を取得する関数
mouse_x = 0
mouse_y = 0
def onMouse( event, x, y, flag, params ):
    global mouse_x, mouse_y

    # マウスの現在位置を取得
    if event == cv2.EVENT_MOUSEMOVE:
        mouse_x = x
        mouse_y = y

    # 左ボタンが押されていたら円を消す（画像外に飛ばす）
    if flag==cv2.EVENT_FLAG_LBUTTON:
        mouse_x = -100
        mouse_y = -100


# ランダムにパーティクルを動かす
def random_move(img, particles, sigma ):
    for p in particles:
        # ランダムにパーティクルを動かす
        xx = int(p.x)
        yy = int(p.y)
        p.x = int(p.x + (random.random()-0.5)*sigma + 0.5)
        p.y = int(p.y + (random.random()-0.5)*sigma + 0.5)

        # 画像外に出ないようにする
        if p.x < 0:
            p.x = 0
        if p.x+rectsize >= 640:
            p.x = 640 - rectsize
        if p.y < 0:
            p.y = 0
        if p.y >= 640:
            p.y = 640 - rectsize

# 各パーティクルの位置で緑色のものがどれだけありそうかを表わす重みを計算
def calc_weight(img, particles ):
    sum_w = 0.0
    for p in particles:
        # パーティクル周辺の画像を切り出す
        rect_img = img[p.y:p.y+rectsize, p.x:p.x+rectsize, :]

        # 緑色の領域のピクセル数を計算
        num_green = np.sum( rect_img[:,:,1]==255 )

        # 割合に直す
        w = num_green / float(rectsize*rectsize) + 0.1 # 0になることを防ぐために微小量足す
        p.weight = w

        sum_w += w

    # 正規化
    for p in particles:
        p.weight = p.weight / sum_w

# 重みに応じてパーティクルを増殖 or 消滅
def resampling(img, particles):
    # 降順ソート
    particles.sort( key=lambda p: -p.weight )

    # パーティクルを重みに応じて増殖させる
    new_particles = []
    for p in particles:
        w = p.weight
        n = int(w * num_particles+0.5 )  # 重みに応じてパーティクルを増殖
        new_particles.extend( [ Particle(p.x, p.y, p.weight) for _ in range(n) ] )

        if len(new_particles)>=num_particles:
            break

    return new_particles[0:num_particles]


def tracking():
    img = np.zeros( (480,640,3) )

    # ウィンドウを準備
    wname = "tracking"
    cv2.namedWindow( wname )
    cv2.setMouseCallback( wname, onMouse, None)

    # パーティクル生成
    particles = [ Particle(320,240) for _ in range(num_particles) ]

    while 1:

        # マウスの現在位置に円を描く
        img *= 0
        cv2.circle( img, (mouse_x,mouse_y) , 30, (0,255,0), -1 )

        # ランダムにパーティクルを動かす
        random_move(img, particles, sigma )

        # 重み計算
        calc_weight(img, particles )

        # 重みに応じてパーティクル
        particles = resampling(img, particles)

        # 画像描画
        for p in particles:
            pt1 = ( p.x, p.y)
            pt2 = ( p.x + rectsize, p.y + rectsize)
            cv2.rectangle( img, pt1, pt2, (255,0,255) )
        cv2.imshow( wname, img )

        if cv2.waitKey(10)!=-1:
            break

    cv2.destroyAllWindows()


def main():
    tracking()

if __name__ == '__main__':
    main()