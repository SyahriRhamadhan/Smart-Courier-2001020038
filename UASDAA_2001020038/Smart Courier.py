from __future__ import annotations
from heapq import heappop, heappush
from typing import Callable, Deque, Dict, List, NamedTuple, Optional, Set, Tuple
import pygame 
import random

# constants in call caps 
WIDTH, HEIGHT = 500, 500
ROW, COLUMN = 20, 20 
FPS = 60
WIN: pygame.Surface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Syahri Rhamadhan")

pygame.font.init()
smallFont = pygame.font.SysFont("tahoma", 14)
bigFont = pygame.font.SysFont("tahoma", 36)

# DisplayNode states 
EMPTY = (255, 255, 255) # white
BLOCKED = (0, 0, 0) # black
START = (255, 0, 0) # red 
TUJUAN = (0, 0, 255) # blue 
PATH = (255, 0, 0) # red
FRONTIER = (255, 255, 255) # white
EXPLORED = (255, 255, 255) # white

# colours
GREY = (128, 128, 128) # untuk menggambar grid
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (126, 249, 255)
RED = (250, 120, 114)

class LokasiMap(NamedTuple):
    #untuk menuju lokasi di dalam maps
    row: int
    column: int

class Stack():
    # srategi LIFO data structure dengan metode push and pop
    def __init__(self) -> None:
        self._container: List = []

    @property
    def empty(self) -> bool:
        return not self._container # kondisi "not true" ketika container(wadah) kosong 

    def push(self, item) -> None:
        self._container.append(item)

    def pop(self):
        return self._container.pop() # LIFO last in, first out

class Queue():
    # srategi LIFO data structure dengan metode push and pop
    def __init__(self) -> None:
        self._container: Deque = Deque()

    @property
    def empty(self) -> bool:
        return not self._container # kondisi "not true" ketika container(wadah) kosong  

    def push(self, item) -> None:
        self._container.append(item)

    # popping dari kiri operasi O(1) 
    # sedangkan O(n) pada list (setiap elemen harus bergerak 1 ke kiri )
    def pop(self):
        return self._container.popleft() # FIFO first in, first out

class PriorityQueue():
    #elemen dengan prioritas tertinggi ada di paling depan
    # prioritas di definisikan sebagai f(n)
    def __init__(self) -> None:
        self._container: List = []
        
    @property
    def empty(self) -> bool:
        return not self._container # kondisi "not true" ketika container(wadah) kosong 

    # heappush dan heappop membandingkan node menggunakan  < operator, __lt__ di calass Node
    def push(self, item) -> None:
        heappush(self._container, item) # prioritas 

    def pop(self):
        return heappop(self._container) # tidak prioritas 

class Node():
    # algoritma untuk maps finding
    def __init__(self, current: LokasiMap, parent: Optional[Node], 
    cost: float = 0.0, heuristic: float = 0.0) -> None:
        self.current: LokasiMap = current
        self.parent: Optional[Node] = parent

        # for astar 
        self.cost: float = cost
        self.heuristic: float = heuristic

    def __lt__(self, other: Node) -> bool:
        
        # f(n) = g(n) + h(n) dimana:
        #    g(n) adalah perkiraan seberapa lama "path/jalur/algoritma" mencapai Node n
        #    h(n) perkiraan seberapa lama dari n menuju "tujuan" menggunakan heuristic
        
        return (self.cost + self.heuristic) < (other.cost + other.heuristic)

class DisplayNode: 
    # untuk menampilkan visual Node di dalam maps
    def __init__(self, row, column):
        self.row: int = row
        self.column: int = column
        self.state: Tuple[int, int, int] = EMPTY

        # drawing maps
        self._x: float = WIDTH / COLUMN * self.column
        self._y: float = HEIGHT / ROW * self.row
        self._width: float = WIDTH / COLUMN
        self._height: float = HEIGHT / ROW
        self._rect: pygame.Rect = pygame.Rect(self._x, self._y, self._width, self._height)

    def render(self, win):
        pygame.draw.rect(win, self.state, self._rect)

class Maze:
    # berisi logika di maps serta path finding
    def __init__(self, start: Optional[LokasiMap] = None, tujuan: Optional[LokasiMap] = None, 
        rows: int = ROW, columns: int = COLUMN, sparseness: float = 0.2) -> None:
        
        # inisialisasi variabel dasar
        self._rows: int = rows
        self._columns: int = columns
        self.sparseness: float = sparseness
        self.start: Optional[LokasiMap] = start
        self.tujuan: Optional[LokasiMap] = tujuan 
        
        self._grid = [[DisplayNode(row, column) for column in range(self._columns)] for row in range(self._rows)]
        
        # isi start dan tujuan
        if self.start:
            self._grid[start.row][start.column].state = START
        if self.tujuan:
            self._grid[tujuan.row][tujuan.column].state = TUJUAN

    def RandomWall(self, rows: int, columns: int, sparseness: float) -> None:
        # respawn dinding secara acak di dalam maps
        for row in range(rows):
            for column in range(columns):
                if random.uniform(0, 1.0) < sparseness:
                    self._grid[row][column].state = BLOCKED

    def empty(self) -> None:
        # membersihkan maps dari semua bangunan. Resets start dan tujuan
        for row in self._grid:
            for d_node in row:
                d_node.state = EMPTY 
        
        self.start = None
        self.tujuan = None

    def maps_gen(self, gen_style: str) -> None:
        # Generate maps random
        if gen_style == "Random":
            self.RandomWall(self._rows, self._columns, self.sparseness) 


    def on_click(self, mouse_pos: Tuple[int, int]) -> LokasiMap:
        # Select start dan tujuan.
        row = int(mouse_pos[1] // (HEIGHT / self._rows))
        column = int(mouse_pos[0] // (WIDTH / self._columns))
        return LokasiMap(row, column)
        # LM =singkatan lokasi map
    def update_grid(self, LM: LokasiMap, LM_state: Tuple[int, int, int] = EMPTY) -> None:
        # update grid ketika user meng input atau menghapus Start, tujuan atau wall
        # serta mengupdate DisplayNode selama program berjalan
        
        # cek untuk meyakinkan LokasiMap vallid 
        if 0 <= LM.row <= self._rows and 0 <= LM.column <= self._columns:
            if LM_state in (EMPTY, BLOCKED, START, TUJUAN, PATH, FRONTIER, EXPLORED):
                self._grid[LM.row][LM.column].state = LM_state

    def tujuan_test(self, LM: LokasiMap) -> bool:
        # cek apakah lokasi tujuan saat ini adalah tujuannya
        return LM == self.tujuan
  
    def neighbours(self, LM: LokasiMap) -> List[LokasiMap]:
        # mencari kemungkinan lokasi dari lokasi maps tertentu
        lokasi: List[LokasiMap] = []

        # down 
        if LM.row + 1 < self._rows and self._grid[LM.row + 1][LM.column].state != BLOCKED:
            lokasi.append(LokasiMap(LM.row + 1, LM.column))

        # up
        if LM.row - 1 >= 0 and self._grid[LM.row - 1][LM.column].state != BLOCKED:
            lokasi.append(LokasiMap(LM.row - 1, LM.column))

        # right
        if LM.column + 1 < self._columns and self._grid[LM.row][LM.column + 1].state != BLOCKED:
            lokasi.append(LokasiMap(LM.row, LM.column + 1))

        # left 
        if LM.column - 1 >= 0 and self._grid[LM.row][LM.column - 1].state != BLOCKED:
            lokasi.append(LokasiMap(LM.row, LM.column - 1))

        return lokasi


    def astar(self, initial: LokasiMap, tujuan_test: Callable[[LokasiMap], bool], 
        successors: Callable[[LokasiMap], List[LokasiMap]],
        heuristic: Callable[[LokasiMap], float]) -> Optional[Node]:
        # cari jalur menggunakan algoritma A* dan return tujuan if path ada else tidak ada
        # frontier adalah tempat yg belum di cek
        frontier: PriorityQueue[Node] = PriorityQueue()
        frontier.push(Node(initial, None, 0.0, heuristic(initial)))

        # explored adalah lokasi yang pernah kita tuju
        explored: Dict[LokasiMap, float] = {initial: 0.0}

        # perogram terus berlangsung jika masih ada tempat yg belum di explore 
        while not frontier.empty:
            # pastikan kita dapat keluar dari program ketika algoritma sedang berjalan
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

            current_node: Node = frontier.pop()
            LokasiSekarang: LokasiMap = current_node.current

            # jika tujuan ditemukan, program selesai 
            if tujuan_test(LokasiSekarang):
                return current_node
            # cek ke mana terus mencari dan belum terjelajah
            for child in successors(LokasiSekarang):
                new_cost: float = current_node.cost + 1 

                if child not in explored or explored[child] > new_cost:
                    explored[child] = new_cost
                    frontier.push(Node(child, current_node, new_cost, heuristic(child)))
                    self.update_grid(child, FRONTIER)

            self.render(WIN)
            pygame.display.update()

            # updates dimana algoritma telah memeriksanya 
            if LokasiSekarang != self.tujuan:
                self.update_grid(LokasiSekarang, EXPLORED)

        return None # ketika sudah berusaha mencari tapi tak kunjung menemukannya

    def node_to_path(self, node: Node) -> List[LokasiMap]:
        # kembali ke path yang diambil dengan backward
        path: List[LokasiMap] = [node.current]

        # initial node parent is None
        while node.parent is not None:
            node = node.parent
            path.append(node.current)
        path.reverse()
        return path
        # manhattan distance Mengurangi per elemen antar 2 variabel, memutlakannya lalu menjuLMahkannya.
    def manhattan_distance(self, tujuan: LokasiMap) -> Callable[[LokasiMap], float]:
        # mengembalikan fungsi yang mengingat kordinat tunjuan
        def distance(LM: LokasiMap) -> float:
            xdist: int = abs(LM.column - tujuan.column)
            ydist: int = abs(LM.row - tujuan.row)
            return (xdist + ydist)
        return distance

    def show_path(self, path: List[LokasiMap]) -> None:
        # visual path yang ditemukan algoritma
        for maps_location in path:
            self._grid[maps_location.row][maps_location.column].state = PATH
            self._grid[self.start.row][self.start.column].state = START
            self._grid[self.tujuan.row][self.tujuan.column].state = TUJUAN

    def reset(self) -> None:
        #Clears path, frontier, explored renders. Walls, start, tujuan remains. Recolour start
        for row in self._grid:
            for d_node in row:
                if d_node.state in (PATH, FRONTIER, EXPLORED):
                    d_node.state = EMPTY
        
        # jika start dihapus dan di ubah None, fungsi ini akan berkerja
        if self.start:
            self._grid[self.start.row][self .start.column].state = START

    def render(self, win) -> None:
        # Render semua lines nodes
        gap: float = WIDTH / self._columns

        for row in self._grid:
            for display in row:
                display.render(win)

        for i in range(self._columns + 1):
            # vertical lines
            pygame.draw.line(win, GREY, (i * gap, 0), (i * gap, HEIGHT))
            # horizontal lines
            pygame.draw.line(win, GREY, (0, i * gap), (WIDTH, i * gap))

class Button:
    # implementasi tombol yang bisa di click. x dan y kordinat
    def __init__(self, name: str, x: int, y: int, width: int = 50, height: int = 50, \
            colour: Tuple[int, int, int] = WHITE, small_font: bool = True) -> None:
        self.name: str = name
        self._x: int = x
        self._y: int = y 
        self._width: int = width 
        self._height: int = height 
        self._rect: pygame.Rect = pygame.Rect(self._x - self._width / 2, self._y - self._height / 2, self._width, self._height)
        self.game_menu: Tuple[int, int, int] = colour

        self._text_colour: Tuple[int, int, int] = BLACK
        # membuat baground untuk text
        self._text_render: pygame.Surface = smallFont.render(self.name, True, self._text_colour) if small_font else \
            bigFont.render(name, True, self._text_colour)
        # membuat persegi panjang kemudian text berada di tengah 
        self._text_rect: pygame.Rect = self._text_render.get_rect(center = (self._x, self._y))

    def is_clicked(self, mouse_pos: Tuple[int, int]) -> bool:
        # mendeteksi jika tombol di click
        mouse_x, mouse_y = mouse_pos 
        if self._x - self._width / 2 <= mouse_x <= self._x + self._width / 2 and \
            self._y - self._height / 2 <= mouse_y <= self._y + self._height / 2:
            return True
        return False

    def render(self, win) -> None:
        # membuat persegi panjang dengan text di tengah nya
        pygame.draw.rect(win, self.game_menu, self._rect) 
        win.blit(self._text_render, self._text_rect)

def setting_render(win, title: Button, buttons: Dict[str, Button], instructions: List[Button]) -> None:
    # merender semua tombol dan text  di game_menu setting
    # seting warna bacground ke putih 
    win.fill((255,255,255)) 
    # renders title 
    title.render(win)
    # renders semua buttons
    for button in buttons.values():
        button.render(win)
     
    for text in instructions:
        text.render(win)
    
def main():
    #Main game logic
    maps: Maze = Maze()

    run: bool = True 
    game_menu: str = "setting" # accepted values: setting, run 
    A_star: str = "A*" # menggunakan algoritma :A*
    MapRandomp: str = "Random" 

    title = Button("Pathfinding A*", WIDTH / 2, 25, small_font=False)
    
    buttons: Dict[str, Button] = {
        "START": Button("START", WIDTH / 2, 135, width = 150, height = 50, colour = BLUE)
        }
    
    instructions: List[Button] = [Button("Space to run", WIDTH / 2, 250), \
        Button("Backspace untuk kembali", WIDTH / 2, 300), \
        Button("Enter untuk reset", WIDTH / 2, 350)]
    
    # highlight seting deafault
    for button in buttons:
        if button == A_star :
            buttons[button].game_menu = RED 

    while run:
        # set tipe dari algoritma and map tembok 
        if game_menu == "setting":
            for event in pygame.event.get():
                # tekan silang di kanan atas untuk quit 
                if event.type == pygame.QUIT:
                    run = False

                if pygame.mouse.get_pressed()[0]: #LEFT 
                    # cek jika ada tombol yang di click
                    for button in buttons.values():
                        if button.is_clicked(pygame.mouse.get_pos()):
                            if button.name == "START":
                                game_menu = "run" 
                                maps.maps_gen(MapRandomp)
                                print(A_star, MapRandomp)

            setting_render(WIN, title, buttons, instructions)
        
        # pemilihan start, tujuan dan pilihan wall, kemudian jalankan program
        elif game_menu == "run":
            for event in pygame.event.get():
                # click x untuk quit 
                if event.type == pygame.QUIT:
                    run = False

                # algoritma untuk peletakan start, tujuan dan wall
                if pygame.mouse.get_pressed()[0]: # LEFT
                    spot_clicked: LokasiMap = maps.on_click(pygame.mouse.get_pos())

                    # jika tidak ada start point dan kordinat lokasi akhir
                    if not maps.start and spot_clicked != maps.tujuan:
                        maps.start = spot_clicked
                        maps.update_grid(maps.start, START)
                    # jika tidak ada kordinat akhir dan kordinat bukanlah posisi start
                    elif not maps.tujuan and spot_clicked != maps.start:
                        maps.tujuan = spot_clicked
                        maps.update_grid(maps.tujuan, TUJUAN)

                    # jika ada start dan lokasi akhir ada, maka letakkan dinding
                    elif spot_clicked != maps.start and spot_clicked != maps.tujuan:
                        maps.update_grid(spot_clicked, BLOCKED)

                # menghapus start, tujuan dan walls
                elif pygame.mouse.get_pressed()[2]: # RIGHT
                    spot_clicked: LokasiMap = maps.on_click(pygame.mouse.get_pos())
                    # mengubah kordinat yg di klik menjadi kosong
                    maps.update_grid(spot_clicked)

                    # jik menghapus start or tujuan, ubah ke None
                    if spot_clicked == maps.start:
                        maps.start = None
                    if spot_clicked == maps.tujuan:
                        maps.tujuan = None
                
                # algoritma untuk mengaktifkan algoritma A*
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # hanya berkerja jika ada titik start dan tujuan
                        if maps.start and maps.tujuan:
                            # mencari solusi 
                            
                            if A_star == "A*":
                                distance: Callable[[LokasiMap], float] = maps.manhattan_distance(maps.tujuan)
                                solution: Optional[Node] = maps.astar(maps.start, maps.tujuan_test, maps.neighbours, distance)
                            
                            # visualisi solusi 
                            if solution is None:
                                print(f"Tidak ada jalur ditemukan")
                            else:
                                path: List[LokasiMap] = maps.node_to_path(solution)
                                maps.show_path(path)
                    
                    # mereset render jika di game terus kembali(enter)
                    if event.key == pygame.K_RETURN:
                        maps.reset()

                    # kembali ke game_menu setting, ini juga untuk mereset render (backspace)
                    if event.key == pygame.K_BACKSPACE:
                        game_menu = "setting"
                        maps.empty()

            maps.render(WIN)
            
        pygame.display.update()

if __name__ == "__main__":
    main()