# multiAgents.py
# --------------
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


from util import manhattanDistance
from game import Directions
import random, util

from game import Agent

class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """


    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {NORTH, SOUTH, WEST, EAST, STOP}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        curPos = currentGameState.getPacmanPosition()
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        curFood = currentGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]



        "*** YOUR CODE HERE ***"
        """
        Informations to consider:

            Number of food left

            Distance between pacman's position and food position from the successor  state

            Distance between pacman's position and ghost's; prevent pacman from colliding with ghosts

        """

        # Initialize score with 0

        score = 0

        # Compare number of foods in current state and successor  state

        newFoodList = newFood.asList()
        curFoodList = curFood.asList()

        if len(newFoodList) < len(curFoodList): # pacman has eaten a food
            score += 10

        # Distance bewteen pacman's position and food postinon

        foodDistance = []

        for food in newFoodList:
            foodDistance.append(manhattanDistance(newPos, food))

        if len(foodDistance) > 0:
            foodMinDistance = min(foodDistance)
            score += 1.0/foodMinDistance    # more score if pacman is closer to the food
        
        
        # Distance between pacman's position and ghosts' position for successor state; prevent collision if not scared

        ghostCurPos = currentGameState.getGhostPositions()
        ghostNextPos = successorGameState.getGhostPositions()
        ghostCurDistance = []
        ghostNextDistance = []
        scaredTime = sum(newScaredTimes)

        for curGhost in ghostCurPos:
            ghostCurDistance.append(manhattanDistance(curGhost, curPos))

        for nextGhost in ghostNextPos:
            ghostNextDistance.append(manhattanDistance(nextGhost, newPos))

        ghostMinDistance = min(ghostNextDistance)

        if scaredTime > 0:  # if the ghosts are scared, attempt to close the distance
            if ghostMinDistance < 2:
                score += 100
        else:   # if the ghost are not scared, prevent pacman from colliding with ghosts
            if ghostMinDistance < 2:
                score -= 100

        return score

def scoreEvaluationFunction(currentGameState):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
    Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
        Returns the minimax action from the current gameState using self.depth
        and self.evaluationFunction.

        Here are some method calls that might be useful when implementing minimax.

        gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

        gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

        gameState.getNumAgents():
        Returns the total number of agents in the game

        gameState.isWin():
        Returns whether or not the game state is a winning state

        gameState.isLose():
        Returns whether or not the game state is a losing state
        """
        "*** YOUR CODE HERE ***"
        """ Implement Minimax by implementing two functions: maxValue and minValue"""

        # A max value function for pacman that returns the max value from the successors

        def maxValue(gameState, depth):
            if self.depth == depth + 1 or gameState.isLose() or gameState.isWin():   # current state is a leaf node or has reached the limited depth 
                return self.evaluationFunction(gameState)

            v = float('-inf')   # initializer to find the max value
            pacmanActions = gameState.getLegalActions(0)    # get all possible actions for the pacman
            successorStates = []

            for action in pacmanActions:    # find the successorStates from pacman's actions
                successorStates.append(gameState.generateSuccessor(0, action))

            for successor in successorStates:   # for each successor of state: 
                v = max(v, minValue(successor, depth + 1, 1))   # next state must be the min state for the first ghost

            return v
        
        # A min value function for ghosts that returns the min value from the successors

        def minValue(gameState, depth, agentIndex):
            if self.depth == depth or gameState.isLose() or gameState.isWin():   # current state is a leaf node or has reached the limited depth 
                return self.evaluationFunction(gameState)
            
            numGhosts = gameState.getNumAgents() - 1

            v = float('inf')    # initializer to find the min value
            ghostActions = gameState.getLegalActions(agentIndex)    # get all possible actions for the ghost with index=agentIndex
            successorStates = []

            for action in ghostActions: # find the successorStates from ghost's actions
                successorStates.append(gameState.generateSuccessor(agentIndex, action))
            
            for successor in successorStates:   # for each successor of state:
                if numGhosts == agentIndex: # last ghost, next state should be of pacman's
                    v = min(v, maxValue(successor, depth))  # find the min value from pacman's maxValue states
                else:
                    v = min(v, minValue(successor, depth, agentIndex + 1))  # find the min value for the next ghost

            return v

        v = float('-inf')
        actions = gameState.getLegalActions()
        successorStates = []
        move = Directions.STOP  # temp value for move

        for action in actions:
            state = gameState.generateSuccessor(0, action)
            minScore = minValue(state, 0, 1)    # min value from the first ghost

            if minScore > v:
                v = minScore
                move = action
            
        return move

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):

         # A max value function for pacman that returns the max value from the successors

        def maxValue(gameState, depth, alpha, beta):
            if self.depth == depth + 1 or gameState.isLose() or gameState.isWin():   # current state is a leaf node or has reached the limited depth 
                return self.evaluationFunction(gameState)

            v = float('-inf')   # initializer to find the max value
            pacmanActions = gameState.getLegalActions(0)    # get all possible actions for the pacman

            for action in pacmanActions:    # find the max value for each successors and perform pruning if necessary
                v = max(v, minValue(gameState.generateSuccessor(0, action), depth + 1, 1, alpha, beta))
                if v > beta: return v

                alpha = max(alpha, v)

            return v

        def minValue(gameState, depth, agentIndex, alpha, beta):
            if self.depth == depth or gameState.isLose() or gameState.isWin():   # current state is a leaf node or has reached the limited depth 
                return self.evaluationFunction(gameState)
            
            numGhosts = gameState.getNumAgents() - 1

            v = float('inf')    # initializer to find the min value
            ghostActions = gameState.getLegalActions(agentIndex)    # get all possible actions for the ghost with index=agentIndex

            for action in ghostActions: # find min or max value (depending on whether the current ghost is the last ghost) and perform pruning
                if numGhosts == agentIndex:
                    v = min(v, maxValue(gameState.generateSuccessor(agentIndex, action), depth, alpha, beta))  

                else:
                    v = min(v, minValue(gameState.generateSuccessor(agentIndex, action), depth, agentIndex + 1, alpha, beta))

                if v < alpha: return v
                beta = min(beta, v)

            return v

        v = float('-inf')
        alpha = float('-inf')
        beta = float('inf')
        actions = gameState.getLegalActions()
        successorStates = []
        move = ''

        for action in actions:
            state = gameState.generateSuccessor(0, action)
            minScore = minValue(state, 0, 1, alpha, beta)    # min value from the first ghost

            if minScore > v:
                v = minScore
                move = action

            if v > beta:
                return move

            alpha = max(alpha, v)

        return move


class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction

        All ghosts should be modeled as choosing uniformly at random from their
        legal moves.
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()

def betterEvaluationFunction(currentGameState):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()

# Abbreviation
better = betterEvaluationFunction
