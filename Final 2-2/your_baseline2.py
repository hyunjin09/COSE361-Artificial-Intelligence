# your_baseline2.py
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


from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'OffensiveQAgent', second = 'DefensiveQAgent'):
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
      self.alpha = 0.1
      self.discount = 0.8
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

  def evaluate(self, gameState, action):
      """
      Computes a linear combination of features and feature weights
      """
      features = self.getFeatures(gameState, action)
      weights = self.getWeights()
      return features * weights

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

  def updateWeight(self, gameState, nextState, action, reward):
    qValues = []
    features = self.getFeatures(gameState, action)
    weights = self.getWeights()
    estimate = self.evaluate(gameState, action)
    actions = nextState.getLegalActions(self.index)
    for action in actions:
      qValues.append(self.evaluate(nextState, action))
    maxV = max(qValues)
    # print(maxV)
    sample = reward + self.discount * maxV
    diff = sample - estimate
    for feature in features:
      self.weights[feature] = weights[feature] + self.alpha * diff * features[feature]
      # print(feature, self.weights[feature])


class OffensiveQAgent(MyAgent):

  def __init__(self, index):
    MyAgent.__init__(self, index)
    self.scoreDiff = 0
    self.maxFoodCarry = 0
    self.curGoal = None
    self.weights = util.Counter()

    self.weights["bias"] = -2.9
    self.weights["goalDist"] = -28.8
    self.weights["ghostDist"] = -0.6
    

  def registerInitialState(self, gameState):
    MyAgent.registerInitialState(self, gameState)

    self.curGoal = self.returnClosestOpening(gameState)
    self.maxFoodCarry = self.totalFood
    capsules = self.getCapsules(gameState)
    food = self.getFood(gameState).asList()
    if len(food) > 0:
      self.curGoal = self.returnClosestFood(gameState)
    if len(capsules) > 0:
      self.curGoal = self.returnClosestCapsule(gameState)

  def chooseAction(self, gameState):
    self.countState += 1
    agentState = gameState.getAgentState(self.index)
    agentPos = gameState.getAgentPosition(self.index)
    actions = gameState.getLegalActions(self.index)
    actions.remove(Directions.STOP)
    ghosts = self.getEnemyPacman(gameState)
    ghostsDistance = []
    values = []
    if len(ghosts) > 0:
      for ghost in ghosts:
        ghostsDistance.append(self.getMazeDistance(agentPos, ghost.getPosition()))

    epsilon = 0.1
      
    returnAction = self.returnActionFromQ(gameState, actions)
    self.prevState = gameState
    self.prevAction = returnAction
    
    # if self.curGoal != None:
    #   self.debugDraw(self.curGoal, (1,0,0), clear=True)


    if not util.flipCoin(epsilon):
      return returnAction
    else:
      rActions = gameState.getLegalActions(self.index)
      return random.choice(rActions)    

  def searchNewGoal(self, gameState, action):
    food = self.getFood(gameState).asList()
    foodLeft = len(food)
    successor = gameState.generateSuccessor(self.index, action)
    nextAgentState = successor.getAgentState(self.index)
    nextStatePos = nextAgentState.getPosition()
    capsules = self.getCapsules(gameState)
    capsuleCount = len(capsules)
    ghosts = self.getEnemyGhosts(gameState)
    capsulePos = 0
    curGoalDist = self.getMazeDistance(nextStatePos, self.curGoal)
    time = self.returnGameTime(gameState)
    if len(ghosts) > 0:
      ghostDist = self.returnEnemyDist(gameState)
      if ghostDist >= 6 or self.capsuleActivated(successor):
        self.maxFoodCarry = self.totalFood
      else:
        self.maxFoodCarry = 10
    if self.goalReached(gameState): # search for closest food
      if foodLeft > 2:
        self.curGoal = self.returnClosestFood(successor)
    if foodLeft <=2 or time - self.getMazeDistance(self.returnClosestOpening(successor), nextStatePos) <= 2.0 \
      or (len(ghosts) > 0 and gameState.getAgentState(self.index).numCarrying >= self.maxFoodCarry and not self.capsuleActivated(gameState) \
        and ghostDist < 6):
      self.curGoal = self.returnClosestOpening(successor)   # return home
    if capsuleCount > 0:  # search for capsule
        capsulePos = self.returnClosestCapsule(successor)
        if capsulePos != 0:
          capsuleDist = self.getMazeDistance(nextStatePos, capsulePos)
          if not self.capsuleActivated(gameState) and len(ghosts) and curGoalDist > capsuleDist:
            self.curGoal = capsulePos
    
  def returnActionFromQ(self, gameState, actions):
    values = []
    for action in actions:
      values.append(self.computeQVal(gameState, action))
    maxV = max(values)
    actionsChoice = [action for action, val in zip(actions, values) if val == maxV]
    return random.choice(actionsChoice)

  def computeQVal(self, gameState, action):
    features = self.getFeatures(gameState, action)
    weights = self.getWeights()
    return features * weights

  def getFeatures(self, gameState, action): 

    curPos = gameState.getAgentState(self.index).getPosition()
    successor = gameState.generateSuccessor(self.index, action)
    sucPos = successor.getAgentState(self.index).getPosition()
    ghosts = self.getEnemyGhosts(successor)
    ghostDist = []
    minDist = 0
    compareMin = 0
    if len(ghosts) > 0:
      if successor.getAgentState(self.index).isPacman and not self.capsuleActivated(successor):
        for ghost in ghosts:
          ghostDist.append(self.getMazeDistance(sucPos, ghost.getPosition()))
      if len(ghostDist) > 0:
        minDist = min(ghostDist)
      if minDist < 3:
        compareMin = minDist



   # return features based on action
    nextState = gameState.generateSuccessor(self.index, action)
    nextStatePos = nextState.getAgentState(self.index).getPosition()
    dist = self.getMazeDistance(nextStatePos, self.curGoal)

    features = util.Counter()
    features["bias"] = 1.0
    features["goalDist"] = dist * 1.0 / self.mapSize
    features["ghostDist"] = compareMin

    self.searchNewGoal(gameState, action)
    return features

  def getWeights(self):
    return self.weights  

  def observationFunction(self, gameState):
    # called before chooseAction function
    curPos2 = gameState.getAgentState(self.index).getPosition()
    # print(curPos2)
    reward = 0
    if self.countState > 0: # a move has been made
      eaten = False
      prevPos = self.prevState.getAgentState(self.index).getPosition()
      curPos = gameState.getAgentState(self.index).getPosition()
      dist = self.getMazeDistance(curPos, prevPos)
      curFood = self.getFood(gameState).asList()
      if dist > 1:  # agent has been eaten
        eaten = True
      ###rewards###
      prevScore = self.getScore(self.prevState)
      curScore = self.getScore(gameState)
      #deduct rewards if pacman has been eaten
      if eaten:
        reward = reward - dist * 1.0 / self.mapSize
        if len(curFood) > 0: # still food left, attempt to eat the farthest food from agent
          self.curGoal = self.returnFarthestFood(gameState)
      #deduct reward if curGoal has not been reached
      if self.curGoal != curPos:
        reward = reward - 1
      else: #curGoal has been reached
      #give rewards if the agent eats food
        prevFood = self.getFood(self.prevState).asList()
        powerUps = self.getCapsules(self.prevState)
        if curPos in prevFood:
          reward = reward + 1
      #give rewards if the agent eats a powerUp
        elif curPos in powerUps:
          reward = reward + 2
        else: #give rewards if food has been brought home
          reward = reward + curScore - prevScore
    
    ###update weights###
    if self.prevState:
      self.updateWeight(self.prevState, gameState, self.prevAction, reward)
    return CaptureAgent.observationFunction(self, gameState)

class DefensiveQAgent(MyAgent):
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




