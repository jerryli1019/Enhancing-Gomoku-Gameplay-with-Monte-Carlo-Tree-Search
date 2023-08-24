from __future__ import absolute_import, division, print_function
from math import sqrt, log
from game import Game, WHITE, BLACK, EMPTY
import copy
import time
import random

class Node:
    def __init__(self, state, actions, parent=None):
        self.state = (state[0], copy.deepcopy(state[1]))
        self.num_wins = 0 #number of wins at the node
        self.num_visits = 0 #number of visits of the node
        self.parent = parent #parent node of the current node
        self.children = [] #store actions and children nodes in the tree as (action, node) tuples
        self.untried_actions = copy.deepcopy(actions) #store actions that have not been tried
        simulator = Game(*state)
        self.is_terminal = simulator.game_over

BUDGET = 1000

class AI:
    def __init__(self, state):
        self.simulator = Game()
        self.simulator.reset(*state) #using * to unpack the state tuple
        self.root = Node(state, self.simulator.get_actions())

    def mcts_search(self):

        iters = 0
        action_win_rates = {} #store the table of actions and their ucb values

        while(iters < BUDGET):
            if ((iters + 1) % 100 == 0):
                print("\riters/budget: {}/{}".format(iters + 1, BUDGET), end="")

            s = self.select(self.root)
            winner = self.rollout(s)
            self.backpropagate(s, winner)

            iters += 1
        print()

        _, action, action_win_rates = self.best_child(self.root, 0)

        return action, action_win_rates

    def select(self, node):

        while not node.is_terminal:
            if len(node.untried_actions) != 0:
                return self.expand(node)
            else:
                node, _, _ = self.best_child(node)
        return node

    def expand(self, node):

        child_node = None #choose a child node to grow the search tree

        action = node.untried_actions.pop(0)

        self.simulator.reset(*node.state)
        if self.simulator.place(action[0], action[1]):
            child_node = Node(self.simulator.state(), self.simulator.get_actions(), node)
            node.children += [(action, child_node)]
            return child_node
        return None

    def best_child(self, node, c=1): 

        best_child_node = None # to store the child node with best UCB
        best_action = None # to store the action that leads to the best child
        action_ucb_table = {} # to store the UCB values of each child node (for testing)
        max_ucb = 0

        for child in node.children:
            action, child_node = child
            N = child_node.num_visits
            curr_ucb = (child_node.num_wins/N + c*sqrt(2*log(node.num_visits)/N))
            action_ucb_table[action] = curr_ucb
            if curr_ucb > max_ucb:
                max_ucb = curr_ucb
                best_child_node = child_node
                best_action = action
        return best_child_node, best_action, action_ucb_table

    def backpropagate(self, node, result):

        while (node is not None):
            node.num_visits += 1
            if node.parent is not None:
                node.num_wins += 1 - result[node.state[0]]
            node = node.parent

    def rollout(self, node):
        self.simulator.reset(*node.state)
        while not self.simulator.game_over:
            rand_move = self.simulator.rand_move()
            self.simulator.place(rand_move[0], rand_move[1])
        reward = {}
        if self.simulator.winner == BLACK:
            reward[BLACK] = 1
            reward[WHITE] = 0
        elif self.simulator.winner == WHITE:
            reward[BLACK] = 0
            reward[WHITE] = 1
        return reward
