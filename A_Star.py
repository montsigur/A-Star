import time

try: # 3.x
    import tkinter as tk
    import tkinter.font as tkFont
except: # 2.x
    import Tkinter as tk
    import tkFont

class Block:
    def __init__(self, x, y, parent, end_coords):
        self.__coords = (x, y)
        self.__parent = parent
        self.__end_coords = end_coords

        if end_coords:
            self.__H = 4 * min(abs(end_coords[0] - x),\
                               abs(end_coords[1] - y)) +\
                10 * max(abs(end_coords[0] - x),\
                         abs(end_coords[1] - y))
        else:
            self.__H = 0

        if parent:
            self.__G = parent.getG() +\
                       int(10 * ((parent.getY() - y) ** 2 +\
                                 (parent.getX() - x) ** 2) ** (1/2))
        else:
            self.__G = 0

        self.__F = self.__G + self.__H


    def getCoords(self):
        return self.__coords
        
    def getParent(self):
        return self.__parent

    def setParent(self, parent):
        self.__parent = parent
        self.__G = parent.getG() +\
                   int(10 * ((parent.getY() - self.getY()) ** 2 +\
                             (parent.getX() - self.getX()) ** 2) ** (1/2))

    def getX(self):
        return self.__coords[0]
    
    def getY(self):
        return self.__coords[1]

    def getH(self):
        return self.__H

    def getG(self):
        return self.__G

    def getF(self):
        return self.__F

class Board(tk.Canvas):
    def __init__(self, master, width, height, block_size):
        tk.Canvas.__init__(self, master,\
                           width=width*block_size,\
                           height=height*block_size)
        self.__width = block_size * width
        self.__height = block_size * height
        self.__size = block_size
        self.__obstacles = []
        self.__grid = []
        self.__start = None
        self.__end_coords = None

        border = 1 if block_size > 10 else 0
        for i in range(width):
            for j in range(height):
                self.__grid.append(self.create_rectangle(\
                                    i * block_size + border,\
                                    j * block_size + border,\
                                    (i+1) * block_size - border,\
                                    (j+1) * block_size - border))

    def mark_block(self, coords, state):
        color_dict = {"open": "orange1", "closed": "orange4",\
                      "path": "cyan", "obstacle": "gray",\
                      "start": "green", "end": "red"}
        if 0 <= coords[0] < self.__width / self.__size and\
           0 <= coords[1] < self.__height / self.__size:
            tag = int(self.__height / self.__size) * coords[0] + coords[1] + 1
            self.itemconfig(tag, fill=color_dict[state])
            self.update_idletasks()

    def create_point(self, x, y):
        return tk.Canvas.create_line(self, x, y, x+1, y+1)

    def scale_coords(self, x1, y1, x2, y2, scale):
        aver_x = (x1 + x2) / 2
        aver_y = (y1 + y2) / 2
        x1 = (x1 - aver_x) * scale + aver_x
        y1 = (y1 - aver_y) * scale + aver_y
        x2 = (x2 - aver_x) * scale + aver_x
        y2 = (y2 - aver_y) * scale + aver_y

        return (x1, y1, x2, y2)

    def setStart(self, x, y):
        self.__start = Block(x, y, None, self.__end_coords)
        self.mark_block((x, y), "start")

    def getStart(self):
        return self.__start

    def setEndCoords(self, x, y):
        self.__end_coords = (x, y)
        self.mark_block((x, y), "end")

    def getEndCoords(self):
        return self.__end_coords

    def setObstacle(self, coords, convert=False):
        coords = (coords[0], coords[1])                                        
        if convert:
            coords = self.board_coords(coords)
        self.mark_block(coords, "obstacle")
        self.__obstacles.append((coords[0], coords[1]))

    def getObstacles(self):
        return self.__obstacles

    def getSize(self):
        return self.__size

    def board_coords(self, canvas_coords):
        return (int(canvas_coords[0] / self.__size),\
                int(canvas_coords[1] / self.__size))

    def canvas_coords(self, board_coords):
        canvas_coords = []
        for coords in board_coords:
            canvas_coords.append((coords[0] * self.__size,\
                                  coords[1] * self.__size))
        return canvas_coords

    def getDims(self):
        return (int(self.__width / self.__size),\
                int(self.__height / self.__size))


def A_Star(board):

    open_blocks = [board.getStart()]
    open_coords = [open_blocks[0].getCoords()]
    closed_blocks = []
    closed_coords = []

    board_width = board.getDims()[0]
    board_height = board.getDims()[1]

    obstacles_coords = board.getObstacles()

    end_coords = board.getEndCoords()
    start_coords = board.getStart().getCoords()

    current = open_blocks[0]
    coords = current.getCoords()

    while len(open_blocks) > 0:

        for dx in range(-1, 2):
            for dy in range(-1, 2):

                x = coords[0] + dx
                y = coords[1] + dy

                if (x, y) not in open_coords and\
                    (x, y) not in closed_coords and\
                    (x, y) not in obstacles_coords and\
                    (x, y-dy) not in obstacles_coords and\
                    (x-dx, y) not in obstacles_coords and\
                    0 <= x < board_width and 0 <= y < board_height:

                    new_block = Block(x, y, current, end_coords)
                    new_coords = (x, y)

                    open_blocks.append(new_block)
                    open_coords.append(new_coords)

                    if new_coords == end_coords:
                        return new_block

                    board.mark_block(new_coords, "open")

        try:
            suspect = open_blocks[0]

        except:
            break

        for block in open_blocks[1:]: #it works even for empty []

            if block.getF() < suspect.getF():
                suspect = block

        current = suspect
        coords = current.getCoords()

        closed_blocks.append(current)
        closed_coords.append(coords)

        index = open_coords.index(coords)
        open_blocks.remove(open_blocks[index])
        open_coords.remove(open_coords[index])

        if coords != start_coords:
            board.mark_block(coords, "closed")

        for dx in range(-1, 2):
            for dy in range(-1, 2):
               
                x = coords[0] + dx
                y = coords[1] + dy

                if (x, y) in open_coords and\
                   (x, y-dy) not in obstacles_coords and\
                   (x-dx, y) not in obstacles_coords and\
                0 <= x < board_width and 0 <= y < board_height:

                    index = open_coords.index((x, y))
                    block = open_blocks[index]

                    if block.getG() > current.getG() +\
                       int(10 * (dx ** 2 + dy ** 2) ** (1/2)):
                        block.setParent(current)

                        # if board.getSize() >= 30:
                        #     arrow_coords = board.scale_coords((coords[0] + 0.5) * size,\
                        #                                       (coords[1] + 0.5) * size,\
                        #                                       (block.getParent().getX() + 0.5) * size,\
                        #                                       (block.getParent().getY() + 0.5) * size,\
                        #                                       0.5)
                        #     board.create_line(arrow_coords[0], arrow_coords[1],\
                        #                       arrow_coords[2], arrow_coords[3], arrow="last")
                        #
                        #     G = board.create_text(((coords[0] + 0.2) * size,\
                        #                            (coords[1] + 0.2) * size),\
                        #                           text=str(block.getG()), font=GH_font)
                        #     H = board.create_text(((coords[0] + 0.8) * size,\
                        #                            (coords[1] + 0.2) * size),\
                        #                           text=str(block.getH()), font=GH_font)
                        #     F = board.create_text(((coords[0] + 0.5) * size,\
                        #                            (coords[1] + 0.6) * size),\
                        #                           text=str(block.getF()), font=F_font)

    return None


def start(board):

    start.set_off = False

    def doit(board=board):

        if not start.set_off:
            
            end = A_Star(board)
            path = []

            end_coords = board.getEndCoords()
            start_coords = board.getStart().getCoords()
            
            while end:
                path.append(end.getCoords())
                end = end.getParent()
            
                for coords in path:
                    if coords != end_coords and coords != start_coords:
                        board.mark_block(coords, "path")
                    
        start.set_off = True

    return doit

def wrap_setBlocks(board):

    def setBlocks(event, board=board):
        
        if not start.set_off:
            x, y = board.board_coords((event.x, event.y))
            
            if not board.getStart():
                board.setStart(x, y)
            elif not board.getEndCoords():
                board.setEndCoords(x, y)
            elif board.board_coords((x, y)) not in board.getObstacles():
                board.setObstacle((x, y))

    return setBlocks

if __name__ == "__main__":

    root = tk.Tk()
    board = Board(root, 80, 60, 10)
    board.pack()
    mark_func = wrap_setBlocks(board)
    board.bind("<B1-Motion>", mark_func)
    board.bind("<Button-1>", mark_func)

    button = tk.Button(root, text="go", command=start(board))
    button.pack()

    tk.mainloop()
