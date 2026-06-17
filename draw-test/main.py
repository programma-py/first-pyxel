import pyxel
class App:
    def __init__(self):
        pyxel.init(160, 120)
        pyxel.load("my_resource.pyxres")
        pyxel.run(self.update, self.draw)

    def update(self):
        pass
        
    def draw(self):
        pyxel.cls(1)

        pyxel.text(10, 10, "HELLO, PYXEL!", 7)
        pyxel.circ(20, 30, 10, 8)
        pyxel.tri(30, 45, 10, 60, 40, 65, 9)
        for i in range(5):
            if i == 2:
                collor = 10
            else:
                collor = 11
            pyxel.rect(10 + i * 20, 70, 15, 10, collor)
        pyxel.blt(10, 90, 0, 0, 0, 15, 16, 2)
        pyxel.blt(30, 90, 0, 16, 0, 15, 16, 2)
        pyxel.blt(50, 90, 0, 0, 67, 11, 13, 2)
        pyxel.blt(70, 90, 0, 16, 69, 11, 11, 2)


App()