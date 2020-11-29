import game_board as gb
import socket
import sys
import random
import tkinter as tk
import json


class Server(BaseException):
    def __init__(self, host_ip, port_number, config):
        self.host = host_ip
        self.port = port_number

        self.config = config

        if "use_maps?" in config and config["use_maps?"]:
            config["board_dimensions"] = (len(config["object_map"][0]), len(config["object_map"]))
            config["bomb_coordinates"], config["goal_coordinates"], config["obstacle_coordinates"] = [], [], []
            config["weights"] = {}
            for row_index, row in enumerate(config["object_map"]):
                for char_index, char in enumerate(row):
                    if char == "O":
                        config["obstacle_coordinates"].append((char_index, row_index))
                    elif char == "I":
                        config["obstacle_coordinates"].append((char_index, row_index, "invisible"))
                    elif char == "B":
                        config["bomb_coordinates"].append((char_index, row_index))
                    elif char == "G":
                        config["goal_coordinates"].append((char_index, row_index))
                    elif char == "A":
                        config["start_position"] = (char_index, row_index)

                for char_index, char in enumerate(config["weight_map"][row_index]):
                    if char in "1234":
                        config["weights"][str(char_index)+","+str(row_index)] = config["weight_dictionary"][char]

        # Size of the world ...
        print("Starting the Game Board")
        columns, rows = config["board_dimensions"]

        self.root = tk.Tk()

        # Create gameboard
        self.board = gb.GameBoard(self.root, self.config, columns, rows)
        self.board.pack(side="top", fill="both", expand="true", padx=4, pady=4)

        # Initialize the weights ...
        self.initialize_weights()

        self.initialize_obstacles()
        self.initialize_goals()
        self.initialize_bombs()

        self.player = gb.Player('player', *self.config["start_position"], 'south', 'front', self.config)
        self.player.set_home((0, 0))
        self.player.close_eyes()

        # Add player ...
        self.board.add(self.player, *self.config["start_position"])
        self.root.update()

    def initialize_obstacles(self):
        for i, obst in enumerate(self.config["obstacle_coordinates"]):
            ob = gb.Obstacle('ob' + str(i), obst[0], obst[1], self.config, obst[-1] != "invisible")
            self.board.add(ob, obst[0], obst[1])

    def initialize_goals(self):
        i = 1
        for g in self.config["goal_coordinates"]:
            goal = gb.Goal('goal' + str(i), g[0], g[1], self.config)
            self.board.add(goal, g[0], g[1])
            i += 1

    def initialize_bombs(self):
        columns, rows = self.config["board_dimensions"][0], self.config["board_dimensions"][1]
        i = 1
        for b in self.config["bomb_coordinates"]:
            bomb = gb.Bomb('bomb' + str(i), b[0], b[1], self.config)
            self.board.add(bomb, b[0], b[1])

            bomb_s = gb.BombSound('bomb_sound_s' + str(i), b[0], (b[1]+1) % rows, self.config)
            self.board.add(bomb_s, b[0], (b[1]+1) % rows)

            bomb_s = gb.BombSound('bomb_sound_e' + str(i), (b[0] + 1) % columns, b[1], self.config)
            self.board.add(bomb_s, (b[0] + 1) % columns, b[1])

            bomb_s = gb.BombSound('bomb_sound_n' + str(i), b[0], (b[1] - 1) % rows, self.config)
            self.board.add(bomb_s, b[0], (b[1] - 1) % rows)

            bomb_s = gb.BombSound('bomb_sound_w' + str(i), (b[0] - 1) % columns, b[1], self.config)
            self.board.add(bomb_s, (b[0] - 1) % columns, b[1])
            i += 1

    def initialize_weights(self):
        weights = {tuple([int(coord) for coord in k.split(",")]): v for k, v in self.config["weights"].items()}
        names = {1.0: "patch_clear",
                 1.1: "patch_lighter",
                 1.2: "patch_middle",
                 1.3: "patch_heavy"}
        patch = [[0]*self.board.columns]*self.board.rows

        weight = 1.0
        name = ''
        for row in range(0, self.board.rows):
            for column in range(0, self.board.columns):
                print("column:", column, "row:", row)
                if (column, row) in weights:
                    weight = weights[(column, row)]
                    name = names[weight]
                else:
                    res = random.uniform(0, 1.0)
                    if res <= 0.3:
                        name = "patch_clear"
                        weight = 1.0
                    elif res <= 0.5:
                        weight = 1.1  # 2.0
                        name = "patch_lighter"
                    elif res <= 0.7:
                        weight = 1.2  # 4.0
                        name = "patch_middle"
                    elif res <= 1.0:
                        weight = 1.3  # 8.0
                        name = "patch_heavy"
                patch[row][column] = gb.Patch('patch' + str(column) + "-" + str(row), name, column, row,
                                              weight, self.config)
                self.board.add(patch[row][column], column, row)

    def execute(self, cmd_type, value, conn):
        res = ""
        if cmd_type == 'command':
            # -----------------------
            # movements without considering the direction
            # of the face of the object but testing the objects
            # -----------------------
            if value == 'north':
                self.player.close_eyes()
                res = self.board.move_north(self.player, 'forward')
                if not self.board.is_target_obstacle(res):
                    self.board.change_position(self.player, res[0], res[1])

            elif value == 'south':
                self.player.close_eyes()
                res = self.board.move_south(self.player, 'forward')
                if not self.board.is_target_obstacle(res):
                    self.board.change_position(self.player, res[0], res[1])

            elif value == 'east':
                self.player.close_eyes()
                res = self.board.move_east(self.player, 'forward')
                if not self.board.is_target_obstacle(res):
                    self.board.change_position(self.player, res[0], res[1])

            elif value == 'west':
                self.player.close_eyes()
                res = self.board.move_west(self.player, 'forward')
                if not self.board.is_target_obstacle(res):
                    self.board.change_position(self.player, res[0], res[1])

            # -----------------------
            # move to home
            # -----------------------
            elif value == 'home':
                res = self.board.move_home(self.player)

            elif value == 'forward':
                res = self.board.move(self.player, 'forward')

            elif value == 'backward':
                res = self.board.move(self.player, 'backward')

            elif value == 'left':
                res = self.board.turn_left(self.player)

            elif value == 'right':
                res = self.board.turn_right(self.player)

            elif value == "set_steps":
                res = self.board.set_steps_view(self.player)

            elif value == "reset_steps":
                res = self.board.reset_steps_view(self.player)

            elif value == "open_eyes":
                res = self.player.open_eyes()

            elif value == "close_eyes":
                res = self.player.close_eyes()
            elif value == "clean_board":
                res = self.board.clean_board()
            elif value == "bye" or value == "exit":
                conn.close()
                exit(1)
            else:
                pass
        elif cmd_type == 'info':
            if value == 'direction':
                res = self.player.get_direction()
            elif value == 'view':
                front = self.board.get_place_ahead(self.player)
                res = self.board.view_object(*front)
                res.reverse()
            elif value == "weights":
                # recebia self.player
                res = self.board.view_weights(self.player, 'front')
            elif value == 'map':
                # recebia self.player
                print('Map:', self.board.view_global_weights())
                res = self.board.view_global_weights()
            elif value == 'obstacles':
                # recebia self.player
                print('Obstacles:', self.board.view_obstacles())
                res = self.board.view_obstacles()
            elif value == 'goal' or value == 'target':
                res = self.board.get_goal_position()
                # print('Goal:',res)
            elif value == 'position':
                res = (self.player.get_x(), self.player.get_y())
                # print('Position:', res)
            elif value == 'maxcoord':
                res = self.board.get_max_coord()
                # print('MaxCoordinates:', res)
            elif value == 'north':
                front = self.board.get_place_direction(self.player, 'north')
                res = self.board.view_object(*front)
            elif value == 'south':
                front = self.board.get_place_direction(self.player, 'south')
                res = self.board.view_object(*front)
            elif value == 'east':
                front = self.board.get_place_direction(self.player, 'east')
                res = self.board.view_object(*front)
            elif value == 'west':
                front = self.board.get_place_direction(self.player, 'west')
                res = self.board.view_object(*front)
            else:
                pass

        # EXAMPLE_AGENT_SEARCH
        elif cmd_type == "mark":
            try:
                self.board.mark(*[int(i) for i in value.split("_")[0].split(",")], value.split("_")[1])
                res = True
            except:
                res = ""

        elif cmd_type == "unmark":
            try:
                self.board.unmark(*[int(i) for i in value.split(",")])
                res = True
            except:
                res = ""
        return res

    def connect(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            print("Listening...")
            s.listen()
            print("Listened")
            return s.accept()

    def loop(self, conn, addr):
        print("LOOP!")
        with conn:
            print('Connected by', addr)
            while True:
                conn.settimeout(0.5)
                try:
                    data = conn.recv(1024)
                    data = data.decode().split()

                    cmd_type, value = "", ""
                    if len(data) >= 2:
                        cmd_type, value = data

                    res = self.execute(cmd_type, value, conn)

                    if res != '':
                        return_data = str.encode(str(res))
                    else:
                        return_data = str.encode(
                            "what?\ncommand = <forward,left,right,set_steps,reset_steps, open_eyes, close_eyes> "
                            + "\ninfo = <direction,view,weights,map,goal,postion,obstacles,maxcoord> "
                            + "\nmark = <{x},{y}_{color} (no spaces!)> \nunmark = <{x},{y}> (no spaces!)")
                    conn.sendall(return_data)
                    self.root.update()
                except socket.timeout:
                    # test
                    # print("Timeout!")
                    self.root.update()


def main():
    with open("config.json") as config_file:
        config = json.load(config_file)
    # Host and Port
    if len(sys.argv) == 3:
        host, port = sys.argv[1], int(sys.argv[2])
    else:
        host = config["host"]
        port = config["port"]

    # Initialize the server
    server = Server(host, port, config)
    # Wait for connection
    conn, addr = server.connect()
    # Loop ...
    server.loop(conn, addr)


if __name__ == "__main__":
    main()
