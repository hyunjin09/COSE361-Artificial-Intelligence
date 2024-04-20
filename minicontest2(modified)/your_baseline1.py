# your_baseline1.py
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


from os import curdir
from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game
from util import nearestPoint
import numpy as np

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'OffensiveRAgent', second = 'DefensiveRAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """

  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class MyAgent(CaptureAgent):

  def __init__(self, index):
      CaptureAgent.__init__(self, index)
      self.enemyInd = []
      self.startPos = None
      self.walls = []
      self.mapW = 0
      self.mapH = 0
      self.mapMidPos = []
      self.openings = []
      self.totalFood = 0
      self.prevState = None
      self.prevAction = None
      self.prevPos = None
      self.mapSize = 0
      self.countState = 0

  def registerInitialState(self, gameState):
    """
    This method handles the initial setup of the
    agent to populate useful fields (such as what team
    we're on).

    A distanceCalculator instance caches the maze distances
    between each pair of positions, so your agents can use:
    self.distancer.getDistance(p1, p2)

    IMPORTANT: This method may run for at most 15 seconds.
    """

    '''
    Make sure you do not delete the following line. If you would like to
    use Manhattan distances instead of maze distances in order to save
    on initialization time, please take a look at
    CaptureAgent.registerInitialState in captureAgents.py.
    '''
    CaptureAgent.registerInitialState(self, gameState)

    self.startPos = gameState.getAgentPosition(self.index)
    self.enemyInd = self.getOpponents(gameState)
    self.walls = gameState.getWalls()
    self.mapW = self.walls.width 
    self.mapH = self.walls.height
    self.mapSize = self.walls.width * self.walls.height

    #find entrances
    for i in range(1, self.walls.height):
      if self.red:
        self.mapMidPos.append(((self.mapW-2)/2, i))
      else:
        self.mapMidPos.append(((self.mapW-2)/2 +1, i))
    for pos in self.mapMidPos:
      if not gameState.hasWall(int(pos[0]), int(pos[1])) and pos != self.startPos:
        self.openings.append(pos)

    #find max score
    self.totalFood = max(1, len(self.getFood(gameState).asList()) - 2)

  def getEnemyGhosts(self, gameState):
    enemies = []
    self.enemyInd = self.getOpponents(gameState)
    for i in self.enemyInd:
      enemy = gameState.getAgentState(i)
      if not enemy.isPacman and enemy.getPosition():
        enemies.append(enemy)
    return enemies

  def getEnemyPacman(self, gameState):
    enemies = []
    self.enemyInd = self.getOpponents(gameState)
    for i in self.enemyInd:
      enemy = gameState.getAgentState(i)
      if enemy.isPacman and enemy.getPosition():
        enemies.append(enemy)
    return enemies

  def capsuleActivated(self, gameState):
    # ghosts = self.getOpponents(gameState)
    ghosts = self.getOpponents(gameState)
    enemies = [gameState.getAgentState(i) for i in ghosts]
    for ghost in enemies:
      if ghost.isPacman: continue
      else:
        if ghost.scaredTimer > 5: return True
    return False

  def returnFarthestFood(self, gameState):
    food = self.getFood(gameState).asList()
    if len(food) > 0:
      return max(food, key=lambda x: self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), x))
  
  def returnClosestFood(self,gameState):
    food = self.getFood(gameState).asList()
    if len(food) > 0:
      return min(food, key=lambda x: self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), x))

  def returnClosestOpening(self, gameState):
    return min(self.openings, key=lambda x: self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), x))

  def returnClosestCapsule(self, gameState):
    capsules = self.getCapsules(gameState)
    if len(capsules):
      return max(capsules, key=lambda x: self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), x))
    else:
      return 0

  def returnEnemyDist(self, gameState):
    ghosts = self.getEnemyGhosts(gameState)
    if len(ghosts) > 0:
        distancesToGhosts = [self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), ghost.getPosition()) for ghost in ghosts]
        return min(distancesToGhosts)
  
  def returnClosestEnemy(self, gameState):
    curPos = gameState.getAgentPosition(self.index)
    enemies = self.getEnemyPacman(gameState)
    enemyPos = []
    if len(enemies)>0:
      for enemy in enemies:
        enemyPos.append(enemy.getPosition())
      return min(enemyPos, key=lambda x: self.getMazeDistance(curPos, x))
    return None


  def returnGameTime(self, gameState):
    return gameState.data.timeleft * 1.0 / gameState.getNumAgents()

  def goalReached(self, gameState):
    check = False
    if self.curGoal == gameState.getAgentState(self.index).getPosition():
      check = True
    return check


class OffensiveRAgent(MyAgent):

  def __init__(self, index):
    MyAgent.__init__(self, index)
    self.curGoal = None
  
  def registerInitialState(self, gameState):
    MyAgent.registerInitialState(self, gameState)
    food = self.getFood(gameState).asList()
    if len(food) > 0:
      self.curGoal = self.returnClosestFood(gameState)
    capsules = self.getCapsules(gameState)
    if len(capsules) > 0:
      self.curGoal = self.returnClosestCapsule(gameState)

  def chooseAction(self, gameState):
    food = self.getFood(gameState).asList()
    if len(food) > 0:
      self.curGoal = self.returnClosestFood(gameState)
    capsules = self.getCapsules(gameState)
    if len(capsules) > 0:
      self.curGoal = self.returnClosestCapsule(gameState)
    agentState = gameState.getAgentState(self.index)
    actions = gameState.getLegalActions(self.index)
    actions.remove(Directions.STOP)
    actionsChoice = []
    values = []
    for action in actions:
      nextState = gameState.generateSuccessor(self.index, action)
      values.append(self.getMazeDistance(nextState.getAgentPosition(self.index), self.curGoal))
      actionsChoice.append(action)

    choices = []
    if len(values) > 0:
      minDist = min(values)
      for v, a in zip(values, actionsChoice):
        if v == minDist:
          choices.append(a)
      return random.choice(choices)
    else:
      return gameState.getLegalActions(self.index)[0]



class DefensiveRAgent(MyAgent):
  def __init__(self, index):
    MyAgent.__init__(self, index)
    self.curGoal = None
    self.patrol = []
    self.prevFood = None
    self.curGoalStatus = None

  def registerInitialState(self, gameState):
    MyAgent.registerInitialState(self, gameState)
    self.curGoal = None
    self.prevFood = self.getFoodYouAreDefending(gameState).asList()
    for i in self.openings: # patrol the entrances
      if self.red:
        if gameState.hasWall(int(i[0]-1), int(i[1])) and not gameState.hasWall(int(i[0]-2), int(i[1])):
          self.patrol.append((i[0]-2, i[1]))
        else:
          self.patrol.append(i)
      else:
        if gameState.hasWall(int(i[0]+1), int(i[1])) and not gameState.hasWall(int(i[0]+2), int(i[1])):
          self.patrol.append((i[0]+2, i[1]))
        else:
          self.patrol.append(i)
      # self.patrol.append(i)

      
    while len(self.patrol) > (self.mapH-2)/4:
      self.patrol.pop(0)
      self.patrol.pop(len(self.patrol)-1)   

  def chooseAction(self, gameState):
    # if self.curGoal != None:
    #   self.debugDraw(self.curGoal, (1,0,0), clear=True)
    self.searchNewGoal(gameState)
    return self.returnBestActions(gameState)

  def returnBestActions(self, gameState):
    agentState = gameState.getAgentState(self.index)
    actions = gameState.getLegalActions(self.index)
    actions.remove(Directions.STOP)
    actionsChoice = []
    values = []
    for action in actions:
      nextState = gameState.generateSuccessor(self.index, action)
      if self.getMazeDistance(self.curGoal, agentState.getPosition()) > len(self.patrol):
        values.append(self.getMazeDistance(nextState.getAgentPosition(self.index), self.curGoal))
        actionsChoice.append(action)
      else:
        if not nextState.getAgentState(self.index).isPacman:
          values.append(self.getMazeDistance(nextState.getAgentPosition(self.index), self.curGoal))
          actionsChoice.append(action)

    choices = []
    if len(values) > 0:
      minDist = min(values)
      for v, a in zip(values, actionsChoice):
        if v == minDist:
          choices.append(a)
      return random.choice(choices)
    else:
      return gameState.getLegalActions(self.index)[0]

  def searchNewGoal(self, gameState):
    curPos = gameState.getAgentPosition(self.index)
    enemies = self.getEnemyPacman(gameState)
    enemyPos = []
    if self.goalReached(gameState):
      self.curGoal = None
    self.curGoal = self.returnClosestEnemy(gameState) # find closest enemy
    if self.curGoal == None:  # check whether a food has been eaten by an unspotted enemy
      checkFood = self.returnEatenFood(gameState)
      if len(checkFood) > 0:
        self.curGoal = checkFood.pop()
    self.prevFood = self.getFoodYouAreDefending(gameState).asList()
    if self.curGoal == None:  # begin patrol
      self.curGoal = self.returnPatrol(gameState)

  def returnEatenFood(self, gameState):
    return set(self.prevFood) - set(self.getFoodYouAreDefending(gameState).asList())

  def returnPatrol(self, gameState):
    return random.choice(self.patrol)
