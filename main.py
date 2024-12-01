from collections import deque, defaultdict
import pygame, sys, random
from pygame.locals import *

# Create the constants (go ahead and experiment with different values)
BOARDWIDTH = 5  # number of columns in the board
BOARDHEIGHT = 5  # number of rows in the board
TILESIZE = 60
WINDOWWIDTH = 1000
WINDOWHEIGHT = 720
FPS = 30
BLANK = None

# COLORS
# https://lospec.com/palette-list/rabbit
#                 R    G    B
WHITE = (236, 236, 224)  # Text
DARKBLUE = (92, 97, 130)  # Frame
DARKTURQUOISE = (59, 50, 74)  # BG
GREEN = (170, 211, 149)  # Buttons and tiles 0
RED = (212, 117, 100)  # Tiles 1
BRIGHTBLUE = (79, 164, 165)  # Tiles 2
PEACH = (232, 196, 152)  # 3

BLACK = DARKBLUE  # (  0,   0,   0)

BGCOLOR = DARKTURQUOISE
TILECOLOR = GREEN
TEXTCOLOR = WHITE
BORDERCOLOR = DARKBLUE
BASICFONTSIZE = 25

BUTTONCOLOR = WHITE
BUTTONTEXTCOLOR = BLACK
MESSAGECOLOR = WHITE

XMARGIN = int((WINDOWWIDTH - (TILESIZE * BOARDWIDTH + (BOARDWIDTH - 1))) / 2)
YMARGIN = int((WINDOWHEIGHT - (TILESIZE * BOARDHEIGHT + (BOARDHEIGHT - 1))) / 2)

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'


def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, NEW_SURF, NEW_RECT

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Color Fill Puzzle')
    BASICFONT = pygame.font.Font('freesansbold.ttf', BASICFONTSIZE)

    # Store the option buttons and their rectangles in OPTIONS.
    NEW_SURF, NEW_RECT = makeText('New Game', TEXTCOLOR, TILECOLOR, WINDOWWIDTH - 220, WINDOWHEIGHT - 60)

    score = 0
    scoreFlag = True
    player_x = 0
    player_y = 0
    player_image = pygame.image.load('player.png')
    player_image = pygame.transform.scale(player_image, (TILESIZE, TILESIZE))
    player_surface = pygame.Surface((TILESIZE / 2, TILESIZE / 2))
    player_surface.fill(BRIGHTBLUE)

    mainBoard, hardest_tile = generateNewPuzzle()
    allMoves = []  # list of moves made from the solved configuration
    gameIsOver = False
    while True:  # main game loop
        slideTo = None  # the direction, if any, a tile should slide
        msg = 'Use WASD or press arrow keys to slide.'  # contains the message to show in the upper left corner.

        drawBoard(mainBoard, hardest_tile, msg, score)

        checkForQuit()
        for event in pygame.event.get():  # event handling loop
            if event.type == MOUSEBUTTONUP:
                spotx, spoty = getSpotClicked(mainBoard, event.pos[0], event.pos[1])

                if (spotx, spoty) == (None, None):
                    # check if the user clicked on an option button
                    if NEW_RECT.collidepoint(event.pos):
                        player_x = 0
                        player_y = 0
                        score = 0
                        mainBoard, hardest_tile = generateNewPuzzle()  # clicked on New Game button
                        allMoves = []

            elif event.type == KEYUP:
                # check if the user pressed a key to slide a tile
                if event.key == K_r and gameIsOver:
                    gameIsOver = False
                    player_x, player_y = 0, 0
                    score = 0
                    resetBlueTiles(mainBoard)

                elif event.key == K_SPACE and gameIsOver:
                    gameIsOver = False
                    player_x = 0
                    player_y = 0
                    score = 0
                    resetBlueTiles(mainBoard)
                    mainBoard, hardest_tile = generateNewPuzzle()  # clicked on New Game button
                    allMoves = []
                elif event.key in (K_LEFT, K_a) and not gameIsOver:
                    slideTo = LEFT
                elif event.key in (K_RIGHT, K_d) and not gameIsOver:
                    slideTo = RIGHT
                elif event.key in (K_UP, K_w) and not gameIsOver:
                    slideTo = UP
                elif event.key in (K_DOWN, K_s) and not gameIsOver:
                    slideTo = DOWN
            # Loop the player around the matrix
            player_x %= BOARDWIDTH
            player_y %= BOARDHEIGHT
        DISPLAYSURF.blit(player_image, (getLeftTopOfTile(player_x, player_y)))
        _score, gameIsOver, moveToMake = doTileEffect(player_x, player_y, mainBoard, score)
        if scoreFlag:
            score += _score
            scoreFlag = False
        if (moveToMake):
            slideTo = moveToMake

        if slideTo:
            scoreFlag = True
            _x, _y = slideAnimation(mainBoard, hardest_tile, slideTo, 'Use WASD or arrow keys to move.', 8, player_x,
                                    player_y, player_image, score)  # show slide on screen
            player_x = _x
            player_y = _y
            allMoves.append(slideTo)  # record the slide
            slideTo = None
            DISPLAYSURF.blit(player_image, (getLeftTopOfTile(player_x, player_y)))
            pygame.display.update()

        pygame.display.update()
        FPSCLOCK.tick(FPS)

def resetBlueTiles(board):
    for i in range(0, BOARDWIDTH):
        for j in range (0, BOARDHEIGHT):
            if board[i][j] == -1:
                board[i][j] = 1
def doTileEffect(player_x, player_y, board, finalscore):
    score = 0
    gameIsOver = False
    moveToMake = None
    if board[player_x][player_y] == 0:  # player on green
        pass
    elif board[player_x][player_y] == 1:  # player on blue
        board[player_x][player_y] = -1 #used blue
        score += 5
    elif board[player_x][player_y] == 2:  # player on red
        gameIsOver = gameOver(board)
    elif board[player_x][player_y] == 3:  # player on orange
        moveToMake = DOWN
    elif board[player_x][player_y] == 10: # player wins
        gameIsOver = gameWon(finalscore)

    return (score, gameIsOver, moveToMake)

def gameWon(finalScore):
    DISPLAYSURF.fill(WHITE)

    # You Won message
    game_won_text = BASICFONT.render("You Won! With Score: "+str(finalScore), True, GREEN)
    text_rect = game_won_text.get_rect(center=(WINDOWWIDTH / 2, WINDOWHEIGHT / 3))
    DISPLAYSURF.blit(game_won_text, text_rect)

    # Instructions
    restart_text = BASICFONT.render("Press 'Space' to play again, or 'Q' to Quit", True, GREEN)
    restart_rect = restart_text.get_rect(center=(WINDOWWIDTH / 2, WINDOWHEIGHT / 2))
    DISPLAYSURF.blit(restart_text, restart_rect)

    pygame.display.flip()
    return True

def gameOver(mainBoard):
    DISPLAYSURF.fill(WHITE)
    game_over_text = BASICFONT.render("Game Over", True, RED)
    text_rect = game_over_text.get_rect(center=(WINDOWWIDTH / 2, WINDOWHEIGHT / 3))
    restart_text = BASICFONT.render("Press 'R' to Restart or 'Esc' to Quit", True, RED)
    restart_rect = restart_text.get_rect(center=(WINDOWWIDTH / 2, WINDOWHEIGHT / 2))
    # Game Over message
    DISPLAYSURF.blit(game_over_text, text_rect)

    # Instructions
    DISPLAYSURF.blit(restart_text, restart_rect)

    pygame.display.flip()  # Update the display
    return True


def terminate():
    pygame.quit()
    sys.exit()


def checkForQuit():
    for event in pygame.event.get(QUIT):  # get all the QUIT events
        terminate()  # terminate if any QUIT events are present
    for event in pygame.event.get(KEYUP):  # get all the KEYUP events
        if event.key == K_ESCAPE:
            terminate()  # terminate if the KEYUP event was for the Esc key
        pygame.event.post(event)  # put the other KEYUP event objects back


def getStartingBoard():
    # Return a board data structure
    # initialize board with -1
    board = [[column for column in range(BOARDHEIGHT)] for row in range(BOARDWIDTH)]
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            board[x][y] = -1
    board[0][0] = 0
    matrix = _generateMatrix(board)
    # greenifyNeighbors(matrix, 1, 1)

    # for finding path
    graph = _create_graph_from_matrix(matrix)
    start_node = (0, 0)
    paths = defaultdict(list)
    for row in range(BOARDWIDTH):
        for col in range(BOARDHEIGHT):
            path = bfs_shortest_path(graph, start_node, (row, col))
            if path:
                pathstr = str(f'({row}, {col})')
                paths[pathstr] = path
    # Using max() to find the longest list
    hardest_path = max(paths.values(), key=len)
    hardest_node = max(paths, key=lambda k: len(paths[k]))
    hardest_node = tuple(map(int, hardest_node.strip("()").split(",")))
    matrix[hardest_node[0]][hardest_node[1]] = 10
    print("\nThe hardest path is:", hardest_path)
    print("\nThe hardest path is to :", hardest_node)
    return matrix, hardest_node


def bfs_shortest_path(graph, start, goal):
    # Edge case: start is the same as goal
    if start == goal:
        return [start]

    # Queue for BFS with initial node
    queue = deque([start])

    # Distance from the start node to each node, initialized to infinity
    distances = {start: 0}

    # Dictionary to track the previous node to reconstruct the path
    previous_nodes = {start: None}

    while queue:
        current_node = queue.popleft()

        # Explore all neighbors of the current node
        for neighbor in graph[current_node]['neighbors']:
            if neighbor not in distances:  # If the neighbor hasn't been visited
                # Mark the distance from the start node to the neighbor
                distances[neighbor] = distances[current_node] + 1
                # Track the previous node to reconstruct the path
                previous_nodes[neighbor] = current_node
                # If we found the goal, we can stop and reconstruct the path
                if neighbor == goal:
                    path = []
                    while neighbor is not None:
                        path.append(neighbor)
                        neighbor = previous_nodes[neighbor]
                    return path[::-1]  # Return reversed path
                queue.append(neighbor)

    # If no path was found, return an empty list
    return []


def _create_graph_from_matrix(matrix):
    rows = len(matrix)
    cols = len(matrix[0]) if rows > 0 else 0

    # Create an empty graph as an adjacency list (dictionary)
    graph = defaultdict(lambda: {'value': None, 'neighbors': []})

    # Helper function to add edges between neighbors
    def add_edge(node1, node2):
        graph[node1]['neighbors'].append(node2)

    # Iterate through the matrix and create edges
    for row in range(rows):
        for col in range(cols):
            node = (row, col)  # This will be our node
            value = matrix[row][col]
            graph[node]['value'] = value
            neighbors = []
            if value == 0 or value == 1:  # node is green

                # Up
                if row > 0:
                    neighbors.append((row - 1, col))
                elif row == 0:
                    neighbors.append((rows - 1, col))

                if row < rows - 1:
                    neighbors.append((row + 1, col))
                elif row == rows - 1:
                    neighbors.append((0, col))

                if col > 0:
                    neighbors.append((row, col - 1))
                elif col == 0:
                    neighbors.append((row, cols - 1))

                if col < cols - 1:
                    neighbors.append((row, col + 1))
                elif col == cols - 1:
                    neighbors.append((row, 0))


            elif value == 2:  # red
                pass

            elif value == 3:  # orange
                if col < cols - 1:
                    neighbors.append((row, col + 1))
                elif col == cols - 1:
                    neighbors.append((row, 0))

            for neighbor in neighbors:
                nr, nc = neighbor
                add_edge(node, neighbor)

    return graph

def _generateMatrix(matrix):
    numbers = [0, 1, 2, 3]
    for row in range(BOARDWIDTH):
        for col in range(BOARDHEIGHT):
            if matrix[row][col] != -1:  # if the current spot in the matrix is preassigned a value then skip
                continue
            # try placing a valid number in the current position
            valid = False
            while not valid:
                num = random.choice(numbers)
                if _isValidNumber(matrix, row, col, num):
                    matrix[row][col] = num
                    valid = True
    return matrix


def _isValidNumber(matrix, row, col, num):
    # Check the cell above
    if row > 0 and matrix[row - 1][col] == num:
        return False
    # Check the cell below
    if row < 4 and matrix[row + 1][col] == num:
        return False
    # Check the cell to the left
    if col > 0 and matrix[row][col - 1] == num:
        return False
    # Check the cell to the right
    if col < 4 and matrix[row][col + 1] == num:
        return False
    return True


def getBlankPosition(board):
    # Return the x and y of board coordinates of the blank space.
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if board[x][y] == BLANK:
                return (x, y)


def makeMove(move):
    # This function does not check if the move is valid.
    if move == UP:
        return 0, -1
    elif move == DOWN:
        return 0, 1
    elif move == LEFT:
        return -1, 0
    else:
        return 1, 0


def getLeftTopOfTile(tileX, tileY):
    left = XMARGIN + (tileX * TILESIZE) + (tileX - 1)
    top = YMARGIN + (tileY * TILESIZE) + (tileY - 1)
    return (left, top)


def getSpotClicked(board, x, y):
    # from the x & y pixel coordinates, get the x & y board coordinates
    for tileX in range(BOARDHEIGHT):
        for tileY in range(BOARDWIDTH):
            left, top = getLeftTopOfTile(tileX, tileY)
            tileRect = pygame.Rect(left, top, TILESIZE, TILESIZE)
            if tileRect.collidepoint(x, y):
                return (tileX, tileY)
    return (None, None)


def drawTile(tilex, tiley, tile_value, hardest_tile, adjx=0, adjy=0):
    # draw a tile at board coordinates tilex and tiley, optionally a few
    # pixels over (determined by adjx and adjy)
    left, top = getLeftTopOfTile(tilex, tiley)

    # TILECOLOR =
    match (tile_value):
        case 0:
            TILECOLOR = GREEN
        case 1:
            TILECOLOR = BRIGHTBLUE
        case 2:
            TILECOLOR = RED
        case 3:
            TILECOLOR = PEACH
        case 10:
            TILECOLOR = GREEN
        case -1: #used tile
            TILECOLOR = BRIGHTBLUE
        case _:
            TILECOLOR = BLACK

    pygame.draw.rect(DISPLAYSURF, TILECOLOR, (left + adjx, top + adjy, TILESIZE, TILESIZE))
    if (tilex, tiley) == hardest_tile:
        textSurf = BASICFONT.render("End", True, TEXTCOLOR)
        textRect = textSurf.get_rect()
        textRect.center = left + int(TILESIZE / 2) + adjx, top + int(TILESIZE / 2) + adjy
        DISPLAYSURF.blit(textSurf, textRect)
    elif (tilex, tiley) == (0, 0):
        textSurf = BASICFONT.render("Start", True, TEXTCOLOR)
        textRect = textSurf.get_rect()
        textRect.center = left + int(TILESIZE / 2) + adjx, top + int(TILESIZE / 2) + adjy
        DISPLAYSURF.blit(textSurf, textRect)
    # textSurf = BASICFONT.render(str(tile_value), True, TEXTCOLOR)
    # textRect = textSurf.get_rect()
    # textRect.center = left + int(TILESIZE / 2) + adjx, top + int(TILESIZE / 2) + adjy
    # DISPLAYSURF.blit(textSurf, textRect)


def makeText(text, color, bgcolor, top, left):
    # create the Surface and Rect objects for some text.
    textSurf = BASICFONT.render(text, True, color, bgcolor)
    textRect = textSurf.get_rect()
    textRect.topleft = (top, left)
    return (textSurf, textRect)


def drawBoard(board, hardest_tile=0, message="", score = 0):
    DISPLAYSURF.fill(BGCOLOR)
    if message:
        textSurf, textRect = makeText(message, MESSAGECOLOR, BGCOLOR, 5, 5)
        DISPLAYSURF.blit(textSurf, textRect)
        textSurf, textRect = makeText("Objective: Reach the end tile.", MESSAGECOLOR, BGCOLOR, 5, 100)
        DISPLAYSURF.blit(textSurf, textRect)
        textSurf, textRect = makeText(
            "Green is safe",
            GREEN, BGCOLOR, 5, 150)
        DISPLAYSURF.blit(textSurf, textRect)
        textSurf, textRect = makeText(
            "Orange moves you down",
            PEACH, BGCOLOR, 5, 180)
        DISPLAYSURF.blit(textSurf, textRect)
        textSurf, textRect = makeText(
            "Blue awards 5 points",
            BRIGHTBLUE, BGCOLOR, 5, 210)
        DISPLAYSURF.blit(textSurf, textRect)
        textSurf, textRect = makeText(
            "Red is game over",
            RED, BGCOLOR, 5, 240)
        DISPLAYSURF.blit(textSurf, textRect)

        textSurf, textRect = makeText(
            "Score: "+str(score),
            TEXTCOLOR, BGCOLOR, WINDOWHEIGHT/2,WINDOWHEIGHT - 60)
        DISPLAYSURF.blit(textSurf, textRect)

        textSurf, textRect = makeText(
            "Tip: You can wrap around the board",
            TEXTCOLOR, BGCOLOR, WINDOWHEIGHT-170, 5)
        DISPLAYSURF.blit(textSurf, textRect)

    for tilex in range(BOARDWIDTH):
        for tiley in range(BOARDHEIGHT):
            drawTile(tilex, tiley, board[tilex][tiley], hardest_tile)

    left, top = getLeftTopOfTile(0, 0)
    width = BOARDWIDTH * TILESIZE
    height = BOARDHEIGHT * TILESIZE
    pygame.draw.rect(DISPLAYSURF, BORDERCOLOR, (left - 5, top - 5, width + 11, height + 11), 4)
    DISPLAYSURF.blit(NEW_SURF, NEW_RECT)


def slideAnimation(board, hardest_tile, direction, message, animationSpeed, player_x, player_y, player_image,score):
    if direction == UP:
        movex = player_x
        movey = player_y - 1
    elif direction == DOWN:
        movex = player_x
        movey = player_y + 1
    elif direction == LEFT:
        movex = player_x - 1
        movey = player_y
    elif direction == RIGHT:
        movex = player_x + 1
        movey = player_y

    start_x, start_y = player_x, player_y
    target_x, target_y = movex % BOARDWIDTH, movey % BOARDHEIGHT
    dx = (target_x - start_x) / 10  # Dividing movement into 10 steps
    dy = (target_y - start_y) / 10
    steps = 0
    # Move in steps
    while steps < 10:
        player_x += dx
        player_y += dy
        steps += 1
        drawBoard(board, hardest_tile, message, score)
        # baseSurf = DISPLAYSURF.copy()  # Clear screen
        DISPLAYSURF.blit(player_image, (getLeftTopOfTile(player_x, player_y)))  # Draw player
        pygame.display.flip()  # Update the display
        pygame.time.Clock().tick(60)  # Control frame rate
    # FPSCLOCK.tick(FPS)
    return (target_x, target_y)


def generateNewPuzzle():
    # From a starting configuration, make numSlides number of moves (and
    # animate these moves).
    board, hardest_tile = getStartingBoard()
    drawBoard(board, hardest_tile, '')
    pygame.display.update()
    pygame.time.wait(500)  # pause 500 milliseconds for effect

    return board, hardest_tile


if __name__ == '__main__':
    main()
