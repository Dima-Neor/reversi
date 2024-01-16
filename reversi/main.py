import pygame
import random
import copy
import bot

#  функции

# определения допустимых направлений для текущей ячейки 
def directions(x, y, minX=0, minY=0, maxX=7, maxY=7):
    validdirections = []
    if x != minX: validdirections.append((x-1, y))
    if x != minX and y != minY: validdirections.append((x-1, y-1))
    if x != minX and y != maxY: validdirections.append((x-1, y+1))

    if x!= maxX: validdirections.append((x+1, y))
    if x != maxX and y != minY: validdirections.append((x+1, y-1))
    if x != maxX and y != maxY: validdirections.append((x+1, y+1))

    if y != minY: validdirections.append((x, y-1))
    if y != maxY: validdirections.append((x, y+1))

    return validdirections

# загрузка изображения
def loadImages(path, size):
    img = pygame.image.load(f"{path}").convert_alpha()
    img = pygame.transform.scale(img, size)
    return img

# получение спрайта
def loadSpriteSheet(sheet, row, col, newSize, size):
    # создает пустую поверхность, загружает часть таблицы спрайтов на поверхность
    image = pygame.Surface((32, 32)).convert_alpha()
    image.blit(sheet, (0, 0), (row * size[0], col * size[1], size[0], size[1]))
    image = pygame.transform.scale(image, newSize)
    image.set_colorkey('Black')
    return image


#  Классы
class Reversi:
    def __init__(self):
        pygame.init()
        # создаем экран
        self.screen = pygame.display.set_mode((1100, 800))
        pygame.display.set_caption('Реверси')

        self.player1 = 1
        self.player2 = -1

        self.currentPlayer = 1

        self.time = 0

        self.rows = 8
        self.columns = 8

        self.gameOver = False

        self.grid = Grid(self.rows, self.columns, (80, 80), self)
        self.botPlayer = bot.BotPlayer(self.grid) # создаем бота

        self.RUN = True

    def run(self):
        while self.RUN == True:
            self.input()
            self.update()
            self.draw()

    def input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.RUN = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                # при нажарии ПКМ выводить поле в консоль
                if event.button == 3:
                    self.grid.printGameLogicBoard()

                # обработка нажатия ЛКМ
                if event.button == 1:
                    if self.currentPlayer == 1 and not self.gameOver:
                        x, y = pygame.mouse.get_pos()
                        x, y = (x - 80) // 80, (y - 80) // 80
                        validCells = self.grid.findAvailMoves(self.grid.gridLogic, self.currentPlayer)
                        if not validCells:
                            pass
                        else:
                            if (y, x) in validCells:
                                self.grid.insertPoint(self.grid.gridLogic, self.currentPlayer, y, x)
                                swappableTiles = self.grid.swappableTiles(y, x, self.grid.gridLogic, self.currentPlayer)
                                for tile in swappableTiles: # изменения цвета
                                    self.grid.transitions(tile, self.currentPlayer)
                                    self.grid.gridLogic[tile[0]][tile[1]] *= -1
                                self.currentPlayer *= -1
                                self.time = pygame.time.get_ticks()

                    if self.gameOver:
                        x, y = pygame.mouse.get_pos()
                        # если наживаем на конпку начать заново, перезапускаем игру
                        if x >= 320 and x <= 480 and y >= 400 and y <= 480:
                            self.grid.newGame()
                            self.gameOver = False


    def update(self):
        if self.currentPlayer == -1:
            new_time = pygame.time.get_ticks()
            if new_time - self.time >= 100: # задержка перед ходом, для плавности
                # если нет доступных ходов заканчиваем игру
                if not self.grid.findAvailMoves(self.grid.gridLogic, self.currentPlayer):
                    self.gameOver = True
                    return
                cell, score = self.botPlayer.minmaxAlgorithm(self.grid.gridLogic, 5, -64, 64, -1)
                self.grid.insertPoint(self.grid.gridLogic, self.currentPlayer, cell[0], cell[1]) # бот делает ход
                swappableTiles = self.grid.swappableTiles(cell[0], cell[1], self.grid.gridLogic, self.currentPlayer)
                for tile in swappableTiles: # меняем цвет
                    self.grid.transitions(tile, self.currentPlayer)
                    self.grid.gridLogic[tile[0]][tile[1]] *= -1
                self.currentPlayer *= -1

        self.grid.player1Score = self.grid.calculatePlayerScore(self.player1)
        self.grid.player2Score = self.grid.calculatePlayerScore(self.player2)
         # если нет доступных ходов для человека заканчиваем игру
        if not self.grid.findAvailMoves(self.grid.gridLogic, self.currentPlayer):
            self.gameOver = True
            return

    # отрисовка
    def draw(self):
        self.screen.fill((0, 0, 0))
        self.grid.drawGrid(self.screen)
        pygame.display.update()

class Grid:
    def __init__(self, rows, columns, size, main):
        self.GAME = main
        self.y = rows
        self.x = columns
        self.size = size
        self.whitePoint = loadImages('assets/WhitePoint.png', size)
        self.blackPoint = loadImages('assets/BlackPoint.png', size)
        self.bg = self.loadBackGroundImages()

        self.Points = {}

        self.gridBg = self.createbgimg()

        self.gridLogic = self.regenGrid(self.y, self.x)

        self.player1Score = 0
        self.player2Score = 0

        self.font = pygame.font.SysFont('Arial', 20, True, False)

    def newGame(self):
        self.Points.clear()
        self.gridLogic = self.regenGrid(self.y, self.x)

    # загрузка фона
    def loadBackGroundImages(self):
        alpha = 'ABCDEFGHI'
        spriteSheet = pygame.image.load('assets/wood.png').convert_alpha()
        imageDict = {}
        for i in range(3):
            for j in range(7):
                imageDict[alpha[j]+str(i)] = loadSpriteSheet(spriteSheet, j, i, (self.size), (32, 32))
        return imageDict
    
    # создание фонового изображения
    def createbgimg(self):
        gridBg = [
            ['C0', 'D0', 'D0', 'D0', 'D0', 'D0', 'D0', 'D0', 'D0', 'E0'],
            ['C1', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'E1'],
            ['C1', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'E1'],
            ['C1', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'E1'],
            ['C1', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'E1'],
            ['C1', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'E1'],
            ['C1', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'E1'],
            ['C1', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'E1'],
            ['C1', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'B0', 'A0', 'E1'],
            ['C2', 'D2', 'D2', 'D2', 'D2', 'D2', 'D2', 'D2', 'D2', 'E2'],
        ]
        image = pygame.Surface((960, 960))
        for j, row in enumerate(gridBg):
            for i, img in enumerate(row):
                image.blit(self.bg[img], (i * self.size[0], j * self.size[1]))
        return image

    # создание пустой сетки
    def regenGrid(self, rows, columns):
        grid = []
        for y in range(rows):
            line = []
            for x in range(columns):
                line.append(0)
            grid.append(line)
        # растовляем начальные жетоны
        self.insertPoint(grid, 1, 3, 3)
        self.insertPoint(grid, -1, 3, 4)
        self.insertPoint(grid, 1, 4, 4)
        self.insertPoint(grid, -1, 4, 3)

        return grid

    def calculatePlayerScore(self, player):
        score = 0
        for row in self.gridLogic:
            for col in row:
                if col == player:
                    score += 1
        return score

    def drawScore(self, player, score):
        textImg = self.font.render(f'{player} : {score}', 1, 'White')
        return textImg

    # экран окончания игры
    def endScreen(self):
        if self.GAME.gameOver:
            endScreenImg = pygame.Surface((320, 320))
            endText = self.font.render(f'{"Поздравляю, ты выиграл !" if self.player1Score > self.player2Score else "Ты проиграл"}', 1, 'White')
            endScreenImg.blit(endText, (0, 0))
            newGame = pygame.draw.rect(endScreenImg, 'White', (80, 160, 160, 80))
            newGameText = self.font.render('Начать заново', 1, 'Black')
            endScreenImg.blit(newGameText, (100, 190))
        return endScreenImg


    def drawGrid(self, window):
        window.blit(self.gridBg, (0, 0))

        window.blit(self.drawScore('Белый', self.player1Score), (900, 100))
        window.blit(self.drawScore('Черный', self.player2Score), (900, 200))

        for Point in self.Points.values():
            Point.draw(window)

        availMoves = self.findAvailMoves(self.gridLogic, self.GAME.currentPlayer)
        if self.GAME.currentPlayer == 1: # отображаем ходы только для игрока
            for move in availMoves:
                pygame.draw.rect(window, 'White', (80 + (move[1] * 80) + 30, 80 + (move[0] * 80) + 30, 20, 20))

        if self.GAME.gameOver:
            window.blit(self.endScreen(), (240, 240))

    # вывод игрового поля в консоль
    def printGameLogicBoard(self):
        print('  | A | B | C | D | E | F | G | H |')
        for i, row in enumerate(self.gridLogic):
            line = f'{i} |'.ljust(3, " ")
            for item in row:
                line += f"{item}".center(3, " ") + '|'
            print(line)
        print()

    # нахожнение подходящие для хода ячеек
    def findValidCells(self, grid, curPlayer):
        # надит все пустые ячейки, которые находятся рядом с противником
        validCellToClick = []
        for gridX, row in enumerate(grid):
            for gridY, col in enumerate(row):
                if grid[gridX][gridY] != 0:
                    continue # пропускаем заполненые клетки
                DIRECTIONS = directions(gridX, gridY)

                for direction in DIRECTIONS:
                    dirX, dirY = direction
                    checkedCell = grid[dirX][dirY]

                    if checkedCell == 0 or checkedCell == curPlayer:
                        continue 

                    if (gridX, gridY) in validCellToClick:
                        continue

                    validCellToClick.append((gridX, gridY))
        return validCellToClick

    # список заменяемыех плиток
    def swappableTiles(self, x, y, grid, player):
        surroundCells = directions(x, y)
        if len(surroundCells) == 0:
            return []

        swappableTiles = []
        for checkCell in surroundCells:
            checkX, checkY = checkCell
            difX, difY = checkX - x, checkY - y
            currentLine = []

            RUN = True
            while RUN:
                if grid[checkX][checkY] == player * -1:
                    currentLine.append((checkX, checkY))
                elif grid[checkX][checkY] == player:
                    RUN = False
                    break
                elif grid[checkX][checkY] == 0:
                    currentLine.clear()
                    RUN = False
                checkX += difX
                checkY += difY

                if checkX < 0 or checkX > 7 or checkY < 0 or checkY > 7:
                    currentLine.clear()
                    RUN = False

            if len(currentLine) > 0:
                swappableTiles.extend(currentLine)

        return swappableTiles

    # поиск доступных ходов
    def findAvailMoves(self, grid, currentPlayer):
        # берет список допустимых ячеек и проверяет каждую, чтобы убедиться, что она играбельна
        validCells = self.findValidCells(grid, currentPlayer)
        playableCells = []

        for cell in validCells:
            x, y = cell
            if cell in playableCells:
                continue # пропускаем если эта ячейка уже играбельна
            swapTiles = self.swappableTiles(x, y, grid, currentPlayer)

            if len(swapTiles) > 0:
                playableCells.append(cell)

        return playableCells

    def insertPoint(self, grid, curplayer, y, x):
        PointImage = self.whitePoint if curplayer == 1 else self.blackPoint
        self.Points[(y, x)] = Point(curplayer, y, x, PointImage, self.GAME)
        grid[y][x] = self.Points[(y, x)].player

    def transitions(self, cell, player):
        if player == 1:
            self.Points[(cell[0], cell[1])].image = self.whitePoint
        else:
            self.Points[(cell[0], cell[1])].image = self.blackPoint

class Point:
    def __init__(self, player, gridX, gridY, image, main):
        self.player = player
        self.gridX = gridX
        self.gridY = gridY
        self.posX = 80 + (gridY * 80)
        self.posY = 80 + (gridX * 80)
        self.GAME = main

        self.image = image

    def draw(self, window):
        window.blit(self.image, (self.posX, self.posY))


# вызов игры
if __name__ == '__main__':
    game = Reversi()
    game.run()
    pygame.quit()