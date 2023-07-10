import random
import time
import webbrowser
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message
from time import sleep
import json

"""
Agent2 play with Randomly
"""

# Global Variables
human_piece = "O"
agent_piece = "X"

BOARD = [
    [0, 0, 0],
    [0, 0, 0],
    [0, 0, 0]
]

ACTIONS = {
    1: [0, 0], 2: [0, 1], 3: [0, 2],
    4: [1, 0], 5: [1, 1], 6: [1, 2],
    7: [2, 0], 8: [2, 1], 9: [2, 2],
}

AGENT_ACTIONS = []

HUMAN = -1
AGENT = +1
NONE = 0

BLANK = ' '
LINE = '\n---------------'

js = {
    "Human": {
        "Piece": " ",
        "moves": []
    },
    "Agent": {
        "Piece": " ",
        "moves": []
    }
}


# Functions
def eval(state):
    """
    Evaluation function.
    Returns: +1 if Agent wins, -1 if Human wins, 0 for draw.
    """

    if winner(state, AGENT):
        return +1
    elif winner(state, HUMAN):
        return -1
    else:
        return 0


def createJson():
    jsFile = open("data2.json", "w")
    js["Human"]["Piece"] = human_piece
    js["Agent"]["Piece"] = agent_piece
    ss = json.dumps(js)
    jsFile.write(ss)


def save_move(index1, index2, player):

    game = [index1, index2]
    for i, j in ACTIONS.items():
        if game == j:
            AGENT_ACTIONS.append(str(i))
            if player == -1:
                js["Human"]["moves"].append(i)
            if player == 1:
                js["Agent"]["moves"].append(i)
            createJson()
            return i


def winner(state, player):
    """
    Function to checks if a player has a winning combination.
    Returns: True if the player specified has won.
    """
    win_state = [
        [state[0][0], state[0][1], state[0][2]],  # Row 1
        [state[1][0], state[1][1], state[1][2]],  # Row 2
        [state[2][0], state[2][1], state[2][2]],  # Row 3
        [state[0][0], state[1][0], state[2][0]],  # Col 1
        [state[0][1], state[1][1], state[2][1]],  # Col 2
        [state[0][2], state[1][2], state[2][2]],  # Col 3
        [state[0][0], state[1][1], state[2][2]],  # Diag 1
        [state[2][0], state[1][1], state[0][2]],  # Diag 2
    ]

    return True if [player, player, player] in win_state else False


def game_over(state):
    """
    Function to test if one of the players has won.
    Returns: True if Agent or Human wins.
    """
    return winner(state, AGENT) or winner(state, HUMAN)


def blank_tiles(state):
    """
    Function that checks for blank cells.
    Returns: a list of blank cells.
    """
    blanks = list()
    for i, row in enumerate(state):
        for j, tile in enumerate(row):
            if not tile:
                blanks.append([i, j])

    return blanks


def valid_action(i, j):
    """
    Function checks if an action is valid.
    Returns: True if cell is empty.
    """
    return True if [i, j] in blank_tiles(BOARD) else False


def apply_action(i, j, player):
    """
    Applies an action to the board given the action is valid.
    Returns: None, it just applies an action if it's valid.
    """
    if valid_action(i, j):
        BOARD[i][j] = player
        return True
    else:
        return False


def print_board(state, agent_piece, human_piece):
    """
    Prints the current board state.
    Returns: None, just prints to terminal.
    """
    pieces = {
        HUMAN: human_piece,
        AGENT: agent_piece,
        NONE: BLANK
    }
    print(LINE)
    for row in state:
        for tile in row:
            print(f"| {pieces[tile]} |", end='')
        print(LINE)


def agent(agent_piece, human_piece):
    """
    Agent function to call minimax.
    No depth limit  (going to regret this)
    Returns: None, just applies a move.
    """
    AgentChoice = []
    depth = len(blank_tiles(BOARD))
    if depth == 0 or game_over(BOARD):
        # GAME OVER
        return None

    for x in range(1, 10):
        if x not in AGENT_ACTIONS:
            AgentChoice.append(x)

    move = random.choice(AgentChoice)
    apply_action(ACTIONS[move][0], ACTIONS[move][1], AGENT)
    x = save_move(ACTIONS[move][0], ACTIONS[move][1], AGENT)
    return x


class Agent2(Agent):
    class Game(CyclicBehaviour):
        async def run(self):
            if len(blank_tiles(BOARD)) == 0 or game_over(BOARD):
                self.kill(exit_code=10)
                webbrowser.open("http://127.0.0.1:5500/XO2.html")
                return
            print("Wait action form agent_1")
            msg = await self.receive(timeout=10)  # wait for a message for 10 seconds
            if msg:
                print("Agent_2 Turn")
                action = str(msg.body)
                if action.isdigit() and (int(action) in range(10)):
                    action = int(action)
                    coord = ACTIONS[action]
                    apply_action(coord[0], coord[1], HUMAN)
                    save_move(coord[0], coord[1], HUMAN)
                x = agent(agent_piece, human_piece)
                print_board(BOARD, agent_piece, human_piece)
                print(f"Agent's Turn (Piece: {agent_piece})")
                msg1 = Message(to="agent_1_example@anonym.im")  # Instantiate the message
                msg1.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
                msg1.body = str(x)
                sleep(5)
                await self.send(msg1)
            else:
                print("Did not received any message after 10 seconds")

        async def on_end(self):
            if winner(BOARD, AGENT):
                print("YOU WIN!")
                print_board(BOARD, agent_piece, human_piece)
            elif winner(BOARD, HUMAN):
                print("You muppet, you've lost :(")
                print_board(BOARD, agent_piece, human_piece)
            else:
                print("DRAW!")
                print_board(BOARD, agent_piece, human_piece)

    class FirstGame(OneShotBehaviour):
        async def run(self):
            print("Agent_2 Turn")
            x = agent(agent_piece, human_piece)
            print_board(BOARD, agent_piece, human_piece)
            print(f"Agent's Turn (Piece: {agent_piece})")
            msg1 = Message(to="mohammedelfateh4@anonym.im")  # Instantiate the message
            msg1.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
            msg1.body = str(x)
            await self.send(msg1)

    async def setup(self):
        print("Agent_2 started")
        if agent_piece == "O":
            FirstGame = self.FirstGame()
            self.add_behaviour(FirstGame)
        Game = self.Game()
        self.add_behaviour(Game)


if __name__ == "__main__":
    Agent2 = Agent2("agent_2_example@anonym.im", "P3473jDUDV7j8Fc")
    future = Agent2.start()
    Agent2.web.start(hostname="127.0.0.1", port="10000")
    future.result()
    webbrowser.open('http://127.0.0.1:10000/spade')
    while Agent2.is_alive():
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            Agent2.stop()
            break
    print("Agents finished")
