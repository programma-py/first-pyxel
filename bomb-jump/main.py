import pyxel

# ======================
# キャラクターの画像データ
# (イメージバンク番号, X座標, Y座標, 幅, 高さ, 透明色)
# 状態と画像データの対応も定義
# ======================

PUTIT_GREEN = {                             # キャラクターの画像データ
    "sprites": {
        "IDLE": [(0,  0, 16, 15, 16, 2),    # 立ち止まっている状態
                 (0, 16, 16, 15, 16, 2)],
        "JUMP":  [(0, 0, 0, 15, 16, 2),     # ジャンプしている状態
                 (0, 16, 0, 15, 16, 2)]
    },
    "state_to_sprite": {                    # 状態と画像データの対応
        "idle": "IDLE",
        "run": "JUMP",
        "jump": "JUMP",
        "down": "IDLE"
    }
}

BOMB_DATA = {                               # 爆弾の画像データ
    "sprites": {
        "WAIT": [(0, 0, 67, 11, 13, 2)],    # 爆発前
        "EXPLODE": [(0, 16, 67, 11, 13, 2),
                    (0, 32, 67, 11, 13, 2)] # 爆発
    },
    "state_to_sprite": {                    # 状態と画像データの対応
        "wait": "WAIT",
        "explode": "EXPLODE"
    }
}

GROUND_Y = 80                               # 地面のY座標

def setup_sounds():
    pyxel.sound(0).set("c3", "t", "7", "n", 4)          # 歩く音
    pyxel.sound(1).set("c3g3c4", "p", "7", "n", 12)     # ジャンプ音
    pyxel.sound(2).set("c2c1c2c1", "n", "7", "n", 12)   # 爆発音

class Player:
    def __init__(self):
        self.width = 16
        self.height = 16
        self.base_y = GROUND_Y - self.height
        self.reset()

    def reset(self):
        self.x = 0
        self.y = self.base_y
        self.vy = 0
        self.state = "idle"

    def update(self):
        if self.state == "down":
            return
        
        if self.state == "idle":
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) or pyxel.btnp(pyxel.KEY_SPACE):
                self.state = "run"
            return
            
        if self.state == "run":
            self.x += 0.5
            if self.x > pyxel.width - self.width:
                self.x = 0 

            if pyxel.frame_count % 6 == 0:
                pyxel.play(0, 0)

            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) or pyxel.btnp(pyxel.KEY_SPACE):
                self.vy = -6
                self.state = "jump"
                pyxel.play(1, 1)

        if self.state == "jump": 
            self.x += 0.5
            if self.x > pyxel.width - self.width:
                self.x = 0

            self.y += self.vy
            self.vy += 0.4

            if self.y >= self.base_y:
                self.y = self.base_y
                self.vy = 0
                self.state = "run"

    def draw(self):
        sprite_name = PUTIT_GREEN["state_to_sprite"][self.state]
        frames = PUTIT_GREEN["sprites"][sprite_name]

        if self.state == "idle":
            frame = (pyxel.frame_count // 12) % len(frames)
            pyxel.blt(self.x, self.y, *frames[frame])

        elif self.state in ("run", "jump"):
            frame = (pyxel.frame_count // 6) % len(frames)
            pyxel.blt(self.x, self.y, *frames[frame])

class Bomb:
    def __init__(self, leader=None):
        self.leader = leader
        self.width = 11
        self.height = 13
        self.spawn_min_x = 70
        self.spawn_max_x = 80
        self.reset()

    def reset(self):
        if self.leader is None:
            self.x = 50
        else:
            self.x = self.leader.x + pyxel.rndi(self.spawn_min_x, self.spawn_max_x)

        self.y = GROUND_Y - self.height
        self.state = "wait"

    def update(self):
        if self.state == "wait":
            self.x -= 1

            if self.x < 0:
                if self.leader is None:
                    self.x = 210
                else:
                    self.x = self.leader.x + pyxel.rndi(self.spawn_min_x, self.spawn_max_x)
                return True

        return False

    def explode(self):
        self.state = "explode"

    def draw(self):
        sprite_name = BOMB_DATA["state_to_sprite"][self.state]
        frames = BOMB_DATA["sprites"][sprite_name]

        frame = (pyxel.frame_count // 12) % len(frames)
        pyxel.blt(self.x, self.y, *frames[frame])

class App:
    def __init__(self):
        pyxel.init(160, 120)
        pyxel.load("my_resource.pyxres")
        setup_sounds()

        self.player = Player()
        self.bomb1 = Bomb()
        self.bomb2 = Bomb(self.bomb1)
        self.bomb3 = Bomb(self.bomb2)
        self.enemies = [self.bomb1, self.bomb2, self.bomb3]
        self.score = 0
        self.high_score = 0
        self.mode = "play"
        self.explosion_pause = 0

        pyxel.run(self.update, self.draw)

    def reset(self):
        self.player.reset()
        self.score = 0
        self.mode = "play"
        self.explosion_pause = 0
        for enemy in self.enemies:
            enemy.reset()

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        if self.mode == "exploding":
            if self.explosion_pause > 0:
                self.explosion_pause -= 1
                return

            self.mode = "game_over"
            return
 
        if self.mode == "game_over" and self.player.state == "down":
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) or pyxel.btnp(pyxel.KEY_SPACE):
                self.reset()
                return

        self.player.update()

        if self.player.state in ("run", "jump"):
            for enemy in self.enemies:
                if enemy.update():
                    self.score += 1
                    if self.score > self.high_score:
                        self.high_score = self.score

                if self.check_collision(self.player, enemy):
                    enemy.explode()
                    pyxel.play(2, 2)
                    self.player.state = "down"
                    self.mode = "exploding"
                    self.explosion_pause = 30
                    break

    def check_collision(self, player, enemy):
        if (player.x < enemy.x + enemy.width and 
            enemy.x < player.x + player.width and
            player.y < enemy.y + enemy.height and
            enemy.y < player.y + player.height):
            return True
        else:
            return False

    def text_draw(self, text, x, y, color1, color2):
        pyxel.rect(x - 2, y - 2, len(text) * 4 + 4, 8, color2)
        pyxel.text(x, y, text, color1)

    def draw(self):
        pyxel.cls(1)

        self.player.draw()

        if self.player.state in ("run", "jump", "down"):
            for enemy in self.enemies:
                enemy.draw()

        text = "PETIT MONO"
        text_x = (pyxel.width - len(text) * 4) // 2
        self.text_draw(text, text_x, 10, 10, 1)

        score_text =  "SCORE " + str(self.score)
        self.text_draw(score_text, 120, 10, 7, 1)

        high_score_text = "HI " + str(self.high_score)
        self.text_draw(high_score_text, 120, 20, 10, 1)

        if self.mode in ("exploding", "game_over"):
            text = "GAME OVER"
            text_x = (pyxel.width - len(text) * 4) // 2
            self.text_draw(text, text_x, pyxel.height - 70, 8, 7)
        
        if self.mode == "game_over" or self.player.state == "idle" :
            text = "CLICK OR TAP TO START"
            text_x = (pyxel.width - len(text) * 4) // 2
            self.text_draw(text, text_x, pyxel.height - 8, 3, 7)

        elif self.player.state in ("run", "jump"):
            text = "CLICK OR TAP TO JUMP"
            text_x = (pyxel.width - len(text) * 4) // 2
            self.text_draw(text, text_x, pyxel.height - 8, 9, 7)      

App()