import client
import ast
import random

#FSM STATES
PESQUISA  = 0
VIRA_ESQ = 1
VIRA_DIR = 2
PARA = 3
VAI_FRENTE = 4

class ReactiveFSM:
    def __init__(self,address,port):
        self.state = PESQUISA
        self.c = client.Client(address, port)
        self.res = self.c.connect()
        random.seed()  # To become true random, a different seed is used! (clock time)
        self.position = None
        self.goal = None
        self.direction = None
        self.objects = []
        self.end = False

    def getConnectionState(self):
        return self.res

    def pesquisa_exe(self):
        print("PESQUISA PESQUISA PESQUISA")
        pass

    def pesquisa_exit(self):
        msg = self.c.execute("info", "goal")
        self.goal = ast.literal_eval(msg)
        msg = self.c.execute("info", "position")
        self.position = ast.literal_eval(msg)
        self.direction = self.c.execute("info", "direction")

        dx, dy = self.goal[0] - self.position[0], self.goal[1] - self.position[1]

        print(dx,dy,self.direction)

        if dx>0 and dy>0:
            if self.direction == "south" or self.direction == "east":
                    self.state = VAI_FRENTE
            else:
                self.state = VIRA_DIR if self.direction == "north" else VIRA_ESQ

        elif dx<0 and dy>0:
            if self.direction == "south" or self.direction == "west":
                    self.state = VAI_FRENTE
            else:
                self.state = VIRA_DIR if self.direction == "east" else VIRA_ESQ

        elif dx<0 and dy<0:
            if self.direction == "north" or self.direction == "east":
                    self.state = VAI_FRENTE
            else:
                self.state = VIRA_DIR if self.direction == "west" else VIRA_ESQ

        elif dx>0 and dy<0:
            if self.direction == "north" or self.direction == "west":
                    self.state = VAI_FRENTE
            else:
                self.state = VIRA_DIR if self.direction == "south" else VIRA_ESQ

        elif dx == 0:
            if dy < 0:
                if self.direction == "north":
                    self.state = VAI_FRENTE
                else:
                    self.state = VIRA_DIR
            else:
                if self.direction == "south":
                    self.state = VAI_FRENTE
                else:
                    self.state = VIRA_ESQ

        elif dy == 0:
            if dx < 0:
                if self.direction == "west":
                    self.state = VAI_FRENTE
                else:
                    self.state = VIRA_DIR
            else:
                if self.direction == "east":
                    self.state = VAI_FRENTE
                else:
                    self.state = VIRA_ESQ

        else:
            self.state = VIRA_DIR

    def virar_esq_exe(self):
        print("VIRA_ESQ VIRA_ESQ VIRA_ESQ")
        self.c.execute("command","left")

    def virar_esq_exit(self):
        msg = self.c.execute("info", "view")
        print(msg)
        self.objects = ast.literal_eval(msg)
        if 'obstacle' not in self.objects and 'bomb' not in self.objects:
            self.state = PESQUISA
        else:
            self.state = VIRA_ESQ

    def virar_dir_exe(self):
        print("VIRA_DIR VIRA_DIR VIRA_DIR")
        self.c.execute("command" , "right")


    def virar_dir_exit(self):
        msg = self.c.execute("info", "view")
        self.objects = ast.literal_eval(msg)
        if 'obstacle' not in self.objects and 'bomb' not in self.objects:
            self.state = PESQUISA
        else:
            self.state = VIRA_ESQ


    def para_exe(self):
        print("Atingi a Goal!")


    def para_exit(self):
        self.end = True

    def vai_frente_exit(self):
        msg = self.c.execute("info", "position")
        self.position = ast.literal_eval(msg)
        if "obstacle" in self.objects:
            self.state = VIRA_DIR
        elif self.position == self.goal:
            self.state = PARA
        else:
            self.state = PESQUISA

    def vai_frente_exe(self):

        self.c.execute("command", "forward")


    def run(self):
        while self.end == False:
            msg = self.c.execute("info","view")
            self.objects = ast.literal_eval(msg)
            if self.state == PESQUISA:
                self.pesquisa_exe()
                self.pesquisa_exit()

            elif self.state == VIRA_ESQ:
                self.virar_esq_exe()
                self.virar_esq_exit()

            elif self.state == VIRA_DIR:
                self.virar_dir_exe()
                self.virar_dir_exit()

            elif self.state == PARA:
                self.para_exe()
                self.para_exit()

            elif self.state == VAI_FRENTE:
                self.vai_frente_exe()
                self.vai_frente_exit()

def main():
    ag = ReactiveFSM('127.0.0.1', 50001)
    if ag.getConnectionState() != -1:
        ag.run()


main()
