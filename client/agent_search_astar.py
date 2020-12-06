import client
import ast
import random


VISITED_COLOR = "#FFA23A"
FRONTIER_COLOR = "#FC6238"


# AUXILIAR

class Queue:
    def __init__(self):
        self.queue_data = []

    def isEmpty(self):
        if len(self.queue_data) == 0:
            return True
        else:
            return False

    def pop(self):
        return self.queue_data.pop(0)

    def insert(self, element):
        return self.queue_data.append(element)

    def remove(self, node):
        return self.queue_data.remove(node)

    def getQueue(self):
        return self.queue_data


# SEARCH AGENT
class Node:
    def __init__(self, state, parent, action, path_cost, heuristic):
        self.state = state
        self.parent = parent
        self.action = action
        self.children = Queue()
        self.path_cost = path_cost
        self.heuristic = heuristic

    def getHeuristic(self):
        return self.heuristic

    def getState(self):
        return self.state

    def getParent(self):
        return self.parent

    def getAction(self):
        return self.action

    def getPathCost(self):
        return self.path_cost

    def getChildren(self):
        return self.children


class Agent:
    def __init__(self):
        self.c = client.Client('127.0.0.1', 50001)
        random.seed()  # To become true random, a different seed is used! (clock time)
        self.visited_nodes = Queue()
        self.frontier_nodes = Queue()
        self.weightMap = []
        self.goalNodePos = (0, 0)
        self.state = (0, 0)
        self.maxCoord = (0, 0)

    def getConnection(self):
        return self.c.connect()

    def getDirectionNow(self):
        return self.c.execute("info", "direction")

    def getGoalPosition(self):
        msg = self.c.execute("info", "goal")
        goal = ast.literal_eval(msg)
        # test
        print('Goal is located at:', goal)
        return goal

    def getSelfPosition(self):
        msg = self.c.execute("info", "position")
        pos = ast.literal_eval(msg)
        # test
        print('Received agent\'s position:', pos)
        return pos

    def getWeightMap(self):
        msg = self.c.execute("info", "map")
        w_map = ast.literal_eval(msg)
        # test
        print('Received map of weights:', w_map)
        return w_map

    def getPatchCost(self, pos):
        return self.weightMap[pos[0]][pos[1]]

    def getMaxCoord(self):
        msg = self.c.execute("info", "maxcoord")
        max_coord = ast.literal_eval(msg)
        # test
        print('Received maxcoord', max_coord)
        return max_coord

    def getObstacles(self):
        msg = self.c.execute("info", "obstacles")
        obst = ast.literal_eval(msg)
        # test
        print('Received map of obstacles:', obst)
        return obst

    def getObjectsAt(self, x, y):
        msg = self.c.execute("info", str(x) + "," + str(y))
        return ast.literal_eval(msg)

    def isVisitable(self, x, y):
        return all(obj != "obstacle" and obj != "bomb" for obj in self.getObjectsAt(x, y))

    def step(self, pos, action):
        if action == "east":
            if pos[0] + 1 < self.maxCoord[0]:
                new_pos = (pos[0] + 1, pos[1])
            else:
                new_pos = (0, pos[1])

        if action == "west":
            if pos[0] - 1 >= 0:
                new_pos = (pos[0] - 1, pos[1])
            else:
                new_pos = (self.maxCoord[0] - 1, pos[1])

        if action == "south":
            if pos[1] + 1 < self.maxCoord[1]:
                new_pos = (pos[0], pos[1] + 1)
            else:
                new_pos = (pos[0], 0)

        if action == "north":
            if pos[1] - 1 >= 0:
                new_pos = (pos[0], pos[1] - 1)
            else:
                new_pos = (pos[0], self.maxCoord[1] - 1)
        return new_pos

    def getNode(self, parent_node, action):
        state = self.step(parent_node.getState(), action)
        pathCost = parent_node.getPathCost() + self.getPatchCost(state)
        heuristic = self.heuristic(state)

        return Node(state, parent_node, action, pathCost, heuristic)

    def printNodes(self, type, nodes, i):
        print(type, " (round ", i, " )")
        print("state | path cost")
        for node in nodes.getQueue():
            print(node.getState(), "|", node.getPathCost())

    def printPath(self, node):
        n = node
        n_list = []
        while n.getPathCost() != 0:
            n_list.insert(0, [n.getState(), n.getPathCost()])
            n = n.getParent()
        n_list.insert(0, [self.getSelfPosition(), 0])
        print("Final Path", n_list)

    def mark_visited(self, node):
        # self.c.execute("mark_visited", str(node.getState())[1:-1].replace(" ", ""))
        self.c.execute("mark", str(node.getState())[1:-1].replace(" ", "") + "_" + VISITED_COLOR)

    def mark_frontier(self, node):
        # self.c.execute("mark_frontier", str(node.getState())[1:-1].replace(" ", ""))
        self.c.execute("mark", str(node.getState())[1:-1].replace(" ", "") + "_" + FRONTIER_COLOR)

    def run(self):
        # Get the position of the Goal
        self.goalNodePos = self.getGoalPosition()
        # Get information of the weights for each step in the world ...
        self.weightMap = self.getWeightMap()
        # Get max coordinates
        self.maxCoord = self.getMaxCoord()
        # Get the initial position of the agent
        self.state = self.getSelfPosition()
        # Execução do código enviando o goal node
        self.exe(self.aStar(self.buscarObstaculos()))

    def aStar(self, obstaculos):
        node = Node(self.state, None, "", 0, self.heuristic(self.state))
        end = False
        n = None
        marked = []
        marked2 = []
        self.visited_nodes.insert(node)
        # Pesquisar os primeiros nós fronteira, children do node inicial, e inseri-los na queue frontier_nodes
        for di in ["north", "east", "south", "west"]:
            nodeNew1 = self.getNode(node, di)
            self.frontier_nodes.insert(nodeNew1)
        """
        Percorrer os nodes enquanto não encontrar o node final não vai acabar o ciclo.
        Cria variável minimo que inicializa em None, iguala esse minimo à soma ds heuristica com o pathcost do node
        que foi encontrar nos frontiers, (no próximo ciclo irá verificar se a soma da heuristica com o pathcost é 
        menor que o do minimo então atualiza um novo minimo). Após isso verifica se o node encontrado corresponde ao goal
        se sim então retorna esse node se não irá procurar os children desse node e coloca-los na queue de frontier_nodes
        se não tiverem já sido visitados.
        """
        while end is not True:
            minimo = None
            for nodeF in self.frontier_nodes.getQueue():
                if nodeF not in marked:
                    marked.append(nodeF)
                    self.mark_frontier(nodeF)
                if nodeF.getState() not in obstaculos:
                    if minimo is None:
                        n = nodeF
                        minimo = nodeF.getPathCost() + nodeF.getHeuristic()

                    elif nodeF.getPathCost() + nodeF.getHeuristic() < minimo:
                        n = nodeF
                        minimo = nodeF.getPathCost() + nodeF.getHeuristic()

            if n.getState() == self.goalNodePos:
                print(n.getState())
                return n
            if n not in marked2:
                marked2.append(n)
                self.mark_visited(n)
            self.state = n.getState()
            self.frontier_nodes.remove(n)
            self.visited_nodes.insert(n)
            for di in ["north", "east", "west", "south"]:
                nodeNew = self.getNode(n, di)
                visited = []
                for nod in self.visited_nodes.getQueue():
                    visited.append(nod.getState())
                if nodeNew.getState() not in visited:
                    self.frontier_nodes.insert(nodeNew)

    """
    Irá calcular a heuristica de todos os nodes, obtendo a distância do entre os nodes e o node objetivo.
    """

    def heuristic(self, node):
        return abs(node[0] - self.goalNodePos[0]) + abs(node[1] - self.goalNodePos[1])

    def exe(self, final_node):
        actual_dir = self.getDirectionNow()
        actual_pos = self.getSelfPosition()
        actual_step = None
        steps = []
        actual_node = final_node
        # Follow from the goal leaf to root...
        while actual_node.getPathCost() != 0:
            steps.insert(0, [actual_node.getState(), actual_node.getPathCost()])
            actual_node = actual_node.getParent()
        steps.insert(0, [actual_pos, 0])

        print("Final Path", steps)

        actions = []
        fim = False
        i = 0
        print("Length of steps:", len(steps))
        while fim is not True:
            actual_step = steps[i]
            next_step = steps[i + 1]
            print("Actual step:", actual_step)
            print("Next step:", next_step)
            next_dir = self.direction(actual_step[0], next_step[0])
            turns = self.turningDirection(actual_dir, next_dir)
            for turn_action in turns:
                actions.append(turn_action)
            i = i + 1
            if i >= len(steps) - 1:
                fim = True
            else:
                actual_dir = next_dir
        print("Actions:", actions)
        self.c.execute("command", "set_steps")

        i = -1
        for action in actions:
            self.c.execute("command", action)

    """
    Retorna a direção do próximo step
    """

    def direction(self, step, nextStep):
        if step[0] == nextStep[0]:
            if step[1] + 1 == nextStep[1]:
                return "south"
            elif step[1] - 1 == nextStep[1]:
                return "north"
        elif step[1] == nextStep[1]:
            if step[0] + 1 == nextStep[0]:
                return "east"
            elif step[0] - 1 == nextStep[0]:
                return "west"

    """
    Retorna os comandos que o agente tem de executar para andar na próximo direção
    """

    def turningDirection(self, directionBefore, directionNow):
        if directionBefore == "north" and directionNow == "east":
            return ["right", "forward"]
        if directionBefore == "north" and directionNow == "west":
            return ["left", "forward"]
        if directionBefore == "north" and directionNow == "south":
            return ["right", "right", "forward"]

        if directionBefore == "south" and directionNow == "east":
            return ["left", "forward"]
        if directionBefore == "south" and directionNow == "west":
            return ["right", "forward"]
        if directionBefore == "south" and directionNow == "north":
            return ["right", "right", "forward"]

        if directionBefore == "east" and directionNow == "north":
            return ["left", "forward"]
        if directionBefore == "east" and directionNow == "south":
            return ["right", "forward"]
        if directionBefore == "east" and directionNow == "west":
            return ["right", "right", "forward"]

        if directionBefore == "west" and directionNow == "north":
            return ["right", "forward"]
        if directionBefore == "west" and directionNow == "south":
            return ["left", "forward"]
        if directionBefore == "west" and directionNow == "east":
            return ["left", "left", "forward"]
        return ["forward"]

    """
    Irá procurar de entre todos os espaços no gameboard quais são obstaculos e retornar uma lista com as coordenadas
    dos obstaculos
    """

    def buscarObstaculos(self):
        obstaculosAux = []
        obstaculos = []
        for obstaculo in self.getObstacles():
            obstaculosAux.append(obstaculo)
        for collumn in range(len(obstaculosAux)):
            for row in range(len(obstaculosAux[collumn])):
                if obstaculosAux[collumn][row]:
                    obstaculos.append((collumn, row))
        return obstaculos


# STARTING THE PROGRAM:
def main():
    print("Starting client!")
    ag = Agent()
    if ag.getConnection() != -1:
        ag.run()


main()
