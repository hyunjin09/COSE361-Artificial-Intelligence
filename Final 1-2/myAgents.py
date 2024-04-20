# myAgents.py
# ---------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

from game import Agent
from searchProblems import PositionSearchProblem

import util
import time
import search

"""
IMPORTANT
`agent` defines which agent you will use. By default, it is set to ClosestDotAgent,
but when you're ready to test your own agent, replace it with MyAgent
"""
def createAgents(num_pacmen, agent='MyAgent'):
    return [eval(agent)(index=i) for i in range(num_pacmen)]    # num_pacmen -> 1 to significantly reduce the computation time

class MyAgent(Agent):
    """
    Implementation of your agent.
    """


    def getAction(self, state):
        """
        Returns the next action the agent will take
        """

        "*** YOUR CODE HERE ***"

        # if self.index in self.curPath and len(self.curPath[self.index]) > 0:        # if an action route has already been found, do not run the BFS again
        #     currentFood = state.getFood()
        #     if currentFood[self.curFood[self.index][0]][self.curFood[self.index][1]] == True:
        #         temp = self.curPath.pop(self.index)
        #         a = temp.pop(0)
        #         if len(temp) > 0:
        #             self.curPath[self.index] = temp
        #         return a
        if self.index in self.curPath and len(self.curPath[self.index]) > 0:        # if an action route has already been found, do not run the BFS again
            currentFood = state.getFood()
            if currentFood[self.curFood[self.index][0]][self.curFood[self.index][1]] == True:
                temp = self.curPath[self.index]
                return temp.pop(0)

        if self.index in self.stop:         # if an agent is too far from a food compared to other agents, simply stop the agent
            return 'Stop'
        
        problem = AnyFoodSearchProblem(state, self.index)
        queue = util.Queue()
        head = problem.getStartState()
        visited = []
        actions = []
        queue.push(head)

        while not queue.isEmpty():
            currNode = queue.pop()
            if currNode == problem.getStartState():             # different index used for the startState
                currState = currNode
            else:
                currState = currNode[0][0]
                actions = currNode[1]
            if problem.isGoalState(currState):                  # return actions if GoalState has been dequeued considering the following conditions:
                temp = []
                temp.append(self.index)
                dist = len(actions)
                temp.append(dist)
                if currState not in self.check or self.check[currState][0] == self.index:   # particular food has not been targeted or the current index agent is targeting it
                    self.check[currState] = temp
                    self.curPath[self.index] = actions[1:]
                    self.curFood[self.index] = currState
                    return actions[0]
                else:
                    if self.check[currState][1] > dist + 6:     # if the food (already targeted by other agent) is closer to the current agent (with constant value as comparison value)
                        self.check[currState] = temp
                        self.curPath[self.index] = actions[1:]
                        self.curFood[self.index] = currState
                        return actions[0]
            if currState not in visited:
                visited.append(currState)
                children = problem.getSuccessors(currState)
                for child in children:
                    if child[0] not in visited:                 # for each unvisited child node, enqueue the 
                        newPath = actions.copy()                    # node along with the path from head state to current state
                        newPath.append(child[1])
                        temp = []
                        temp.append(child)
                        temp.append(newPath)
                        queue.push(temp)    
        
        self.stop.append(self.index)
        return 'Stop'


    def initialize(self):
        """
        Intialize anything you want to here. This function is called
        when the agent is first created. If you don't need to use it, then
        leave it blank
        """

        "*** YOUR CODE HERE"


        MyAgent.check = {}
        MyAgent.stop = []
        MyAgent.curPath = {}
        MyAgent.curFood = {}

        # raise NotImplementedError()

"""
Put any other SearchProblems or search methods below. You may also import classes/methods in
search.py and searchProblems.py. (ClosestDotAgent as an example below)
"""

class ClosestDotAgent(Agent):

    def findPathToClosestDot(self, gameState):
        """
        Returns a path (a list of actions) to the closest dot, starting from
        gameState.
        """
        # Here are some useful elements of the startState
        startPosition = gameState.getPacmanPosition(self.index)
        food = gameState.getFood()
        walls = gameState.getWalls()
        problem = AnyFoodSearchProblem(gameState, self.index)


        "*** YOUR CODE HERE ***"

        pacmanCurrent = [problem.getStartState(), [], 0]
        visitedPosition = set()
        # visitedPosition.add(problem.getStartState())
        fringe = util.PriorityQueue()
        fringe.push(pacmanCurrent, pacmanCurrent[2])
        while not fringe.isEmpty():
            pacmanCurrent = fringe.pop()
            if pacmanCurrent[0] in visitedPosition:
                continue
            else:
                visitedPosition.add(pacmanCurrent[0])
            if problem.isGoalState(pacmanCurrent[0]):
                return pacmanCurrent[1]
            else:
                pacmanSuccessors = problem.getSuccessors(pacmanCurrent[0])
            Successor = []
            for item in pacmanSuccessors:  # item: [(x,y), 'direction', cost]
                if item[0] not in visitedPosition:
                    pacmanRoute = pacmanCurrent[1].copy()
                    pacmanRoute.append(item[1])
                    sumCost = pacmanCurrent[2]
                    Successor.append([item[0], pacmanRoute, sumCost + item[2]])
            for item in Successor:
                fringe.push(item, item[2])
        return pacmanCurrent[1]

    def getAction(self, state):
        return self.findPathToClosestDot(state)[0]

class AnyFoodSearchProblem(PositionSearchProblem):
    """
    A search problem for finding a path to any food.

    This search problem is just like the PositionSearchProblem, but has a
    different goal test, which you need to fill in below.  The state space and
    successor function do not need to be changed.

    The class definition above, AnyFoodSearchProblem(PositionSearchProblem),
    inherits the methods of the PositionSearchProblem.

    You can use this search problem to help you fill in the findPathToClosestDot
    method.
    """

    def __init__(self, gameState, agentIndex):
        "Stores information from the gameState.  You don't need to change this."
        # Store the food for later reference
        self.food = gameState.getFood()

        # Store info for the PositionSearchProblem (no need to change this)
        self.walls = gameState.getWalls()
        self.startState = gameState.getPacmanPosition(agentIndex)
        self.costFn = lambda x: 1
        self._visited, self._visitedlist, self._expanded = {}, [], 0 # DO NOT CHANGE

    def isGoalState(self, state):
        """
        The state is Pacman's position. Fill this in with a goal test that will
        complete the problem definition.
        """
        x,y = state
        if self.food[x][y] == True:
            return True
        return False

