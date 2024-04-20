# search.py
# ---------
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


"""
In search.py, you will implement generic search algorithms which are called by
Pacman agents (in searchAgents.py).
"""

import util

class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def getStartState(self):
        """
        Returns the start state for the search problem.
        """
        util.raiseNotDefined()

    def isGoalState(self, state):
        """
          state: Search state

        Returns True if and only if the state is a valid goal state.
        """
        util.raiseNotDefined()

    def getSuccessors(self, state):
        """
          state: Search state

        For a given state, this should return a list of triples, (successor,
        action, stepCost), where 'successor' is a successor to the current
        state, 'action' is the action required to get there, and 'stepCost' is
        the incremental cost of expanding to that successor.
        """
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
         actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.
        The sequence must be composed of legal moves.
        """
        util.raiseNotDefined()


def tinyMazeSearch(problem):
    """
    Returns a sequence of moves that solves tinyMaze.  For any other maze, the
    sequence of moves will be incorrect, so only use this for tinyMaze.
    """
    from game import Directions
    s = Directions.SOUTH
    w = Directions.WEST
    return  [s, s, w, s, w, w, s, w]

def depthFirstSearch(problem):
    """
    Search the deepest nodes in the search tree first.

    Your search algorithm needs to return a list of actions that reaches the
    goal. Make sure to implement a graph search algorithm.

    To get started, you might want to try some of these simple commands to
    understand the search problem that is being passed in:

    print("Start:", problem.getStartState())
    print("Is the start a goal?", problem.isGoalState(problem.getStartState()))
    print("Start's successors:", problem.getSuccessors(problem.getStartState()))
    """
    "*** YOUR CODE HERE ***"
    
    # print("Start:", problem.getStartState())
    # print("Is the start a goal?", problem.isGoalState(problem.getStartState()))
    # print("Start's successors:", problem.getSuccessors(problem.getStartState()))

    """
    Utilize DFS Maze Algorithm with Stack

    Push in currNode's children if the child has not been visited yet.
    The stack acts as a solution (the paths) to the problem. Only pop out a node
    when there no longer exists an unvisited child given the currNode. 
    Because backtracking is forbidden in this given problem, push in the child's
    sibilings along with the child when an unvisited node has been found.
    Thus, instead of going back to the parent when there no longer exists a path,
    travel to one of the unvisited sibiling node. Continue until the goal state 
    has been reached and popped out.
    """

    stack = util.Stack()
    actions = []
    visited = []
    head = problem.getStartState()
    stack.push(head)
    visited.append(head)
    curState = head
    while not stack.isEmpty():
        available = False
        if problem.isGoalState(curState):               # if the goal state has been found and popped out from stack, return actions
            return actions
        children = problem.getSuccessors(curState)
        for child in children:
            if child[0] not in visited:
                curState = child[0]
                tempNode = []
                tempNode.append(children)               # append the sibiling nodes to prevent backtracking
                tempNode.append(curState)
                stack.push(tempNode)
                actions.append(child[1])
                visited.append(curState)
                available = True
                break
        while not available:                            # if there no longer exists an unvisited node, pop out the node and search its sibiling nodes
            actions.pop()
            temp = stack.pop()
            for sibling in temp[0]:
                if sibling[0] not in visited:
                    curState = sibling[0]
                    tempNode = []
                    tempNode.append(temp[0])
                    tempNode.append(curState)
                    stack.push(tempNode)
                    actions.append(sibling[1])
                    visited.append(curState)
                    available = True
                    break

    #util.raiseNotDefined()

def breadthFirstSearch(problem):
    """Search the shallowest nodes in the search tree first."""
    "*** YOUR CODE HERE ***"

    """
    BFS using a Queue

    Starting from the StartState, enqueue its unvisited child nodes along with the path from the head state to each child.
    Dequeue from the queue and copy the current saved path to actions array. Repeat the process until the goalState has 
    been reached and dequeued; return actions.  
    """

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
        if problem.isGoalState(currState):                  # return actions if GoalState has been dequeued
            return actions
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
                    


    # util.raiseNotDefined()

def uniformCostSearch(problem):
    """Search the node of least total cost first."""
    "*** YOUR CODE HERE ***"

    #state action cost paths

    """
    UCS using a Priority Queue 

    Starting from the StartState, enqueue its unvisited child nodes along with the path from the head state to each child.
    Dequeue the node with least cost and copy the current saved path to actions array. Repeat the process until the goalState has 
    been reached and dequeued; return actions.  
    """

    fringe = util.PriorityQueue()
    visited = []
    actions = []
    head = problem.getStartState()
    fringe.push(head, 0)
    while not fringe.isEmpty():
        currNode = fringe.pop()
        if currNode == problem.getStartState():                 # different index used for the startState
            currState = currNode
        else:
            currState = currNode[0][0]
            actions = currNode[1]
        if problem.isGoalState(currState):                      # return actions if GoalState has been dequeued
            return actions
        if currState not in visited:
            visited.append(currState)
            children = problem.getSuccessors(currState)
            for child in children:
                if child[0] not in visited:                     # for each unvisited child node, enqueue the 
                    newPath = actions.copy()                        # node along with the path from head state to current state
                    newPath.append(child[1])
                    temp = []
                    temp.append(child)
                    temp.append(newPath)
                    cost = problem.getCostOfActions(newPath)
                    fringe.push(temp, cost)

    # util.raiseNotDefined()

def nullHeuristic(state, problem=None):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0

def aStarSearch(problem, heuristic=nullHeuristic):
    """Search the node that has the lowest combined cost and heuristic first."""
    "*** YOUR CODE HERE ***"

    """
    A* Search using a Priority Queue 

    Starting from the StartState, enqueue its unvisited child nodes along with the path from the head state to each child.
    Dequeue the node with least cost (backcost + heuristic) and copy the current saved path to actions array. Repeat the 
    process until the goalState has been reached and dequeued; return actions.  
    """

    fringe = util.PriorityQueue()
    visited = []
    actions = []
    head = problem.getStartState()
    fringe.push(head, 0)
    while not fringe.isEmpty():
        currNode = fringe.pop()
        if currNode == problem.getStartState():                     # different index used for the startState
            currState = currNode
        else:
            currState = currNode[0][0]
            actions = currNode[1]
        if problem.isGoalState(currState):                          # return actions if GoalState has been dequeued
            return actions
        if currState not in visited:
            visited.append(currState)
            children = problem.getSuccessors(currState)
            for child in children:
                if child[0] not in visited:                         # for each unvisited child node, enqueue the 
                    newPath = actions.copy()                            # node along with the path from head state to current state
                    newPath.append(child[1])
                    temp = []
                    temp.append(child)
                    temp.append(newPath)
                    backCost = problem.getCostOfActions(newPath)
                    frontCost = heuristic(child[0], problem)
                    cost = backCost + frontCost
                    fringe.push(temp, cost)

    # util.raiseNotDefined()


# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch

