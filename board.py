import threading
import numpy as np
from config import *
import time

np.set_printoptions(linewidth=200)
# Duyệt 4 theo trục tung, hoành, chéo chính, chéo phụ
directions = np.array([(0, 1), (1, 0), (1, 1), (-1, 1)])
max_depth = 2
maximum_childs = 5

# Bẳng điểm đánh giá vị trí đánh dấu khi xét mỗi dòng 5, giá trị =0 tương ứng với
# điểm đã đánh, giá trị !=0 tương ứng với điểm đánh giá tùy thuộc vào từng vị trí
rating_score_table = np.array([
    # Line 1
    [0, 2, 2, 1, 1],
    [2, 0, 2, 1, 1],
    [1, 2, 0, 2, 1],
    # Line 2
    [0, 0, 20, 15, 5],
    [0, 20, 0, 15, 5],
    [0, 15, 15, 0, 5],
    [0, 5, 10, 5, 0],
    [20, 0, 0, 20, 15],
    [15, 0, 20, 0, 15],
    # Line 3
    [0, 0, 0, 200, 50],
    [0, 0, 200, 0, 50],
    [0, 0, 50, 50, 0],
    [0, 50, 0, 50, 0],
    [200, 0, 0, 0, 200],
    [0, 200, 0, 0, 50],

    # Line 4
    [1000, 0, 0, 0, 0],
    [0, 1000, 0, 0, 0],
    [0, 0, 1000, 0, 0],

])


# hàm đánh giá điểm ứng trên bảng đanh xếp hạng điểm rating_score_table
def getValue(line, pos_in_line, typeLine, blockHead, blockTail):
    if(blockHead or blockTail):
        return 0
    value = 0
    for case in rating_score_table:
        _line = np.copy(case)
        _line[case == 0] = typeLine
        _line[case != 0] = 0
        if(np.array_equal(line, _line)):
            value = case[pos_in_line]
            break
        if(np.array_equal(line, _line[::-1])):
            value = case[4-pos_in_line]
            break

    # if(blockHead or blockTail):
    #     count = np.sum(line == typeLine)
    #     if(count == 3):
    #         value = value // 4
    #     if(count == 2):
    #         value = value//4
    return value


# trả về 1 mảng 5 phần tử tương ứng trên bàn cờ, theo vị trí và hướng cho trước
def getLine5(board, pos, direct):
    line = np.zeros(5, dtype=int)
    countX = countO = 0
    for step in range(5):
        i, j = pos+direct*step
        val = line[step] = board[i, j]
        if(val == X):
            countX += 1
        if(val == O):
            countO += 1
    return line, countX, countO


# Kiểm tra chặn 2 đầu
def checkTwoEndBlocking(BoardGame, headPos, tailPos, type):
    blockHead = blockTail = False
    if(np.any(headPos < 0)):
        blockHead = True
    elif (BoardGame[headPos[0], headPos[1]] != 0):
        if(BoardGame[headPos[0], headPos[1]] != type):
            blockHead = True
    if(np.any(tailPos >= 20)):
        blockTail = True
    elif (BoardGame[tailPos[0], tailPos[1]] != 0):
        if(BoardGame[tailPos[0], tailPos[1]] != type):
            blockTail = True
    return blockHead, blockTail


next_pos = (1, 1)


# Hàm đánh giá điểm tại tất cả vị trí trên bàn cờ,
# type_eval=0 đánh giá tất cả vị trí trống trên bàn cờ, các giá trị tốt nhất sẽ được chọn để đánh tiếp, giúp giảm số ô phải đi, ko dùng để đánh giá thế trận
# type_eval=1 đánh giá tất cả vị trí trống trên bàn cờ,  tìm ra ô có giá trị dương lớn nhất, và âm nhỏ nhất, từ đó có thể biết được thế trận bàn cờ nghiêng về bên nào
def EvaluateBoard(BoardGame, player, type_eval=0):
    scoreboard = np.zeros((20, 20), dtype=int)
    # duyệt theo 4 hương [ tung, hoang, chéo chính, chéo phụ ]

    # quét tất cả ô cò trên bàn cờ
    for row in range(20):
        for col in range(20):
            values = np.zeros(4)

            for idx, direct in enumerate(directions):
                boardIdx = np.array([row, col])
                # check cell has mark
                if(BoardGame[row, col] != 0):
                    continue
                start = boardIdx+direct*-4
                bestValue = 0
                numX = numO = 0
                for step in range(5):
                    posX, posY = pos = start+step*direct
                    if(posX > 0 and posY > 0 and posX+4 < 20 and posY+4 < 20):
                        line5, countX, countO = getLine5(
                            BoardGame, pos, direct)
                        if(countO*countX == 0 and countX+countO != 0):
                            type_line = X if(countX > 0) else O
                            # CHECK HAS BLOCK HEAD OR TAIL
                            blockHead, blockTail = checkTwoEndBlocking(
                                BoardGame, pos-direct, pos+direct*5, type_line)
                            # END CHECK
                            pos_in_line = 4-step

                            value = getValue(
                                line5, pos_in_line, type_line, blockHead, blockTail)
                            if(bestValue < value):
                                bestValue = value

                                numX = countX
                                numO = countO
                values[idx] = bestValue*player

                if(type_eval == 0):
                    scoreboard[row, col] += bestValue
                elif(type_eval == 1):
                    if (numX > 0):
                        scoreboard[row, col] += bestValue
                    else:
                        scoreboard[row, col] -= bestValue
            sumX = np.sum(values >= 15)
            if(sumX >= 2):
                scoreboard[row, col] *= 2
    return scoreboard


def checkWinner(board, marked_pos, player):

    directions = np.array([(0, 1), (1, 0), (1, 1), (-1, 1)])
    _pos_winner = [(0, 0)]*5
    # board[marked_pos] = player
    for direct in directions:
        start = marked_pos+direct*-4
        for step in range(5):
            posX, posY = pos = start+step*direct

            if(posX > 0 and posY > 0 and posX+4 < 20 and posY+4 < 20):
                line5, countX, countO = getLine5(board, pos, direct)

                if np.sum(line5 == player) >= 4:
                    blockHead, blockTail = checkTwoEndBlocking(
                        board, pos-direct, pos+direct*5, player)
                    if(not (blockHead and blockTail)):
                        _pos_winner = [pos + i*direct for i in range(5)]
                        # board[marked_pos] = 0
                        return True, _pos_winner
    # board[marked_pos] = 0
    return False, _pos_winner


def findNextMove(Board, playerMove=X, numMove=4):
    valuedBoard = EvaluateBoard(Board, playerMove)
    array = valuedBoard.flatten()
    indices = np.argsort(array)[-numMove:]
    unraveled = np.unravel_index(indices, valuedBoard.shape)
    return np.array([(unraveled[0][i], unraveled[1][i]) for i in range(numMove)])


def minimax(Board, depth: int, player):
    global next_pos
    if(depth == 0):
        valuedBoard = EvaluateBoard(Board, player, 1)
        minvalue, maxvalue = np.min(valuedBoard), np.max(valuedBoard)
        return minvalue + maxvalue
        # return minvalue if abs(minvalue) > maxvalue else maxvalue
        # return value
    # đánh giá bàn cờ và chọn ra n ô có vị trí tốt nhất cho player sẽ được
    best_childs = findNextMove(Board, player, maximum_childs)
    if(player == X):
        Mx = -np.inf
        for move_pos in best_childs:
            r, c = move_pos
            if(checkWinner(Board, move_pos, player)[0]):
                if depth == max_depth:
                    next_pos = move_pos
                Mx = 5000.0
                break

            Board[r, c] = X
            value = minimax(Board, depth-1, O)
            Board[r, c] = 0

            if(Mx < value):
                if depth == max_depth:
                    next_pos = move_pos
                Mx = value

        return Mx
    else:
        Mn = np.inf
        for move_pos in best_childs:
            r, c = move_pos
            if checkWinner(Board, move_pos, player)[0]:
                print(123)
                Mn = - 5000.0
                break
            Board[r, c] = O
            value = minimax(Board, depth-1,  X)
            Board[r, c] = 0
            if(Mn > value):
                Mn = value
        return Mn


class BoardGame:

    def __init__(self, nCol=20, nRow=20):
        self.nCol: int = nCol
        self.nRow: int = nRow
        self.reset()

    def reset(self):
        self.Board = np.zeros((self.nCol, self.nRow), dtype=int)
        self.player = O
        self.Line = []

        self.isWin: bool = False

        # self.Board = np.array([

        #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        #     [0, 0, 0, 0, 0, 0, 0, 0, 0, O, O, O, 0, 0, 0, 0, 0, 0, 0, 0],
        #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        #     [0, 0, 0, 0, 0, 0, 0, 0, 0, X, X, X, 0, 0, 0, 0, 0, 0, 0, 0],
        #     [0, 0, 0, 0, 0, 0, 0, 0, 0, X, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        # ])
        self.Board[9, 9] = X
        self.visited_pos: list[tuple] = [(9, 9)]

        self.computer_computing: bool = False

    def __getitem__(self, items):
        if isinstance(items, tuple):
            return self.Board[items[0], items[1]]

    def __setitem__(self, items, val):
        if isinstance(items, tuple):
            self.Board[items[0], items[1]] = val

    def PlayerXGo(self):
        global next_pos
        if(self.computer_computing == False):
            print("START")
            self.thread = threading.Thread(
                target=minimax, args=((self.Board.copy()), max_depth, X))
            self.thread.start()
            self.computer_computing = True

        if(self.computer_computing and self.thread.is_alive() == False):
            idX, idY = next_pos
            # print("NEXT", next_pos)
            self.isWin, self.Line = checkWinner(self.Board, next_pos, X)

            self.Board[idX, idY] = X
            self.visited_pos.append(next_pos)
            self.computer_computing = False
            next_pos = (0, 0)
            self.player = O

    def PlayerOGo(self, marked_pos):

        idX, idY = marked_pos
        if(self.Board[idX, idY] == 0):
            self.Board[idX, idY] = O
            self.visited_pos.append((idX, idY))
            self.isWin, self.Line = checkWinner(self.Board, next_pos, O)
            self.player = X

    def undo(self):
        if len(self.visited_pos) >= 2 and self.player == O:
            pos = self.visited_pos.pop()
            self.Board[pos[0], pos[1]] = 0
            pos = self.visited_pos.pop()
            self.Board[pos[0], pos[1]] = 0
