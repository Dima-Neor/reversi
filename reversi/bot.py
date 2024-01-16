import copy
    
class BotPlayer:
    def __init__(self, gridObject):
        self.grid = gridObject

    # оценка игровой доски (по сути сложность бота задается данной функцией)
    def evaluateBoard(self, grid, player):
        score = 0
        for y, row in enumerate(grid):
            for x, col in enumerate(row):
                score -= col
        # в данный момет бот пытается сделать так чтобы у него было больше очков чем у игрока
        return score

    def minmaxAlgorithm(self, grid, depth, alpha, beta, player):
        # переменной depth задается кол-во просчитываемых ходов
        newGrid = copy.deepcopy(grid)
        availMoves = self.grid.findAvailMoves(newGrid, player)

        # если глубина 0 или нет доступных ходов возвращаям счет
        if depth == 0 or len(availMoves) == 0:
            bestMove, Score = None, self.evaluateBoard(grid, player)
            return bestMove, Score

        # max часть алгаритма
        if player < 0: # определяем бота
            bestScore = -64
            bestMove = None

            for move in availMoves: # проходим по всем доступным ходам
                x, y = move
                swappableTiles = self.grid.swappableTiles(x, y, newGrid, player)
                newGrid[x][y] = player
                for tile in swappableTiles: # обновляем все доступные для замены плитки
                    newGrid[tile[0]][tile[1]] = player 

                # рекурсивный вызов этогого метода (просчитываем следующий ход)
                bMove, value = self.minmaxAlgorithm(newGrid, depth-1, alpha, beta, player *-1)

                if value > bestScore:
                    bestScore = value
                    bestMove = move
                alpha = max(alpha, bestScore) # выбираем макс балы, чтобы отсечь менее выгодные пути
                if beta <= alpha:
                    break

                newGrid = copy.deepcopy(grid) # востанавливаем сетку на текущее положение
            return bestMove, bestScore

        if player > 0: # определяем игрока
            bestScore = 64
            bestMove = None

            for move in availMoves: # проходим по всем доступным ходам
                x, y = move
                swappableTiles = self.grid.swappableTiles(x, y, newGrid, player)
                newGrid[x][y] = player
                for tile in swappableTiles: # обновляем все доступные для замены плитки
                    newGrid[tile[0]][tile[1]] = player

                # рекурсивный вызов этогого метода (просчитываем следующий ход)
                bMove, value = self.minmaxAlgorithm(newGrid, depth-1, alpha, beta, player)

                if value < bestScore:
                    bestScore = value
                    bestMove = move
                beta = min(beta, bestScore) # выбираем минимальные балы
                if beta <= alpha:
                    break

                newGrid = copy.deepcopy(grid) # востанавливаем сетку на текущее положение
            return bestMove, bestScore