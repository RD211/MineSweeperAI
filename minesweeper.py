import sys
import random
from selenium import webdriver
from selenium.webdriver import *
from selenium.webdriver.firefox.options import Options
table = []
times = 0
difficulty = {
    'Beginner':((9,9),10,721),
    'Intermediate':((16,16),40,721),
    'Expert':((30,16),99,711),
    'Custom':((80,40),400,300)
}
gameType = "Beginner"
def recursive_solution(permutation, constraints, mine,n,questions):
    global table
    global times
    if times>30000:
        return 0
    if n<0:
        return 0
    times+=1
    for constraint in constraints:
        sum = 0
        unknown = 0
        for friend in constraint[1]:
            if permutation[friend]!=-1:
                sum+=permutation[friend]
            else:
                unknown += 1
        if not(sum-unknown <= constraint[0] <= sum + unknown):
            return 0
    if mine >= len(permutation):
        if questions<n:
            return 0
        
        for idx,el in enumerate(permutation):
            table[idx][el]+=1
        return 1
    isOne = False
    permutation[mine] = random.randrange(2)
    if permutation[mine]==1:
        isOne = True
        n-=1
    recursive_solution(permutation, constraints, mine+1,n,questions)
    if isOne:
        n+=1
    permutation[mine] = (permutation[mine]+1)%2
    isOne = False
    if permutation[mine]==1:
        n-=1
        isOne = True
    recursive_solution(permutation, constraints, mine+1,n,questions)  
    if isOne:
        n+=1
    permutation[mine] = -1
    return 0

def solve_mine(map,n,driver):
    sys.setrecursionlimit(50000)
    result = solve_mine2(map,n,driver)

def Open(y,x,map,driver):
    click(16*x+8+difficulty[gameType][2],16*y+8+155)
    #ActionChains(driver).click(driver.find_element_by_id('cell_'+str(x)+'_'+str(y))).perform()
    
def Mark(y,x,map,driver):
    rightClick(16*x+8+difficulty[gameType][2],16*y+8+155)

def solve_mine2(map, n, driver):
    global table
    global times
    map = GetMap(driver)
    addX = [1,-1,0,0,1,-1,-1,1]
    addY = [0,0,1,-1,1,-1,1,-1]
    attack_points = {}
    attack_points_reversed = {}
    constraints = []
    working = True
    while working:
        working = False
        for y in range(len(map)):
            for x in range(len(map[y])):
                if map[y][x]>=0:
                    empty = 0
                    for i in range(8):
                        nx, ny = x+addX[i], y+addY[i]
                        if  0 <= ny < len(map) and 0 <= nx < len(map[y]):
                            if map[ny][nx]==-1:
                                if map[y][x]==0:
                                    Open(ny,nx,map,driver)
                                    map = GetMap(driver)
                                    working=True
                                empty += 1
                            elif map[ny][nx]==-2:
                                empty+=1
                            
                    
                    if map[y][x]==empty:
                        for i in range(8):
                            nx, ny = x+addX[i], y+addY[i]
                            if  0 <= ny < len(map) and 0 <= nx < len(map[y]) and map[ny][nx]==-1:
                                Mark(ny,nx,map,driver)
                                map[ny][nx]=-2
                                working=True
                    if map[y][x]==0:
                        for i in range(8):
                            nx, ny = x+addX[i], y+addY[i]
                            if  0 <= ny < len(map) and 0 <= nx < len(map[y]) and map[ny][nx]==-1:
                                Open(ny,nx,map,driver)
                                map = GetMap(driver)
                                working=True
    questions = 0
    for y in range(len(map)):
        for x in range(len(map[y])):
            if map[y][x]==-1:
                questions+=1
            if map[y][x] > 0:
                connections = []
                marked = 0
                for i in range(8):
                    nx, ny = x+addX[i], y+addY[i]
                    if  0 <= ny < len(map) and 0 <= nx < len(map[y]):
                        if map[ny][nx] == -1:
                            connections.append((nx,ny))
                        elif map[ny][nx]==-2:
                            marked+=1
                for connection in connections:
                    if not connection in attack_points_reversed.keys():
                        attack_points[len(attack_points)] = connection
                        attack_points_reversed[connection] = len(attack_points)-1
                constraints.append((map[y][x]-marked, [attack_points_reversed[elem] for elem in connections]))
                
    permutations = [-1 for i in range(len(attack_points))]
    questions-=len(attack_points)
    times = 0
    changed = 0
    table = [[0,0] for i in range(len(attack_points))]


    minesLeft = n
    for y in range(len(map)):
        for x in range(len(map[y])):
            if map[y][x]==-2:
                minesLeft-=1
    recursive_solution(permutations, constraints, 0,minesLeft,questions)

    questions+=len(attack_points)
    best_marked=table.index(max(table, key=lambda x: x[0]/(x[1]+0.001)))
    best_open=table.index(max(table, key=lambda x: x[0]/(x[1]+0.001)))
    for i in range(len(table)):
        if table[i][0] == 0:
            Mark(attack_points[i][1],attack_points[i][0],map,driver)
            map[attack_points[i][1]][attack_points[i][0]] = -2
            questions-=1
            if questions<=1:
                time.sleep(3)
            changed = 1
        elif table[i][1] == 0:


            Open(attack_points[i][1], attack_points[i][0],map,driver)
            questions-=1
            if questions<=1:
                time.sleep(3)
            changed = 1
    if changed==0:
        questions-=1
        if questions<=1:
            time.sleep(3)
        Open(attack_points[best_open][1],attack_points[best_open][0],map,driver)
    map = GetMap(driver)
    return solve_mine2(map, n,driver)

class_to_num = {
    "square bombflagged":-2,
    "square blank":-1,
    "square open0":0,
    "square open1":1,
    "square open2":2,
    "square open3":3,
    "square open4":4,
    "square open5":5,
    "square open6":6,    
    "square open7":7,
    "square open8":8,
    "square open9":9,
}
from bs4 import BeautifulSoup

def GetMap(driver, width=difficulty[gameType][0][0], height=difficulty[gameType][0][1]):
    map = [[0 for i in range(width)] for j in range(height)]
    text = driver.page_source
    soup = BeautifulSoup(text)
    for value in class_to_num.items():
        for ele in soup.find_all('div',attrs={'class':value[0]}):
            if ele.get('style')=="display: none;":
                continue
            map[int(ele.get('id').split('_')[0])-1][int(ele.get('id').split('_')[1])-1]=value[1]

    return map
firefox_options = Options()
firefox_options.add_argument('--no-proxy-server')
firefox_options.add_argument("--proxy-server='direct://'");
firefox_options.add_argument("--proxy-bypass-list=*");
driver = webdriver.Firefox(executable_path=r'C:\webdrivers\geckodriver.exe',options=firefox_options)
driver.get('http://minesweeperonline.com/#')
driver.implicitly_wait(0)
import time
import win32api, win32con
def click(x,y):
    #time.sleep(0.01)
    win32api.SetCursorPos((x,y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
    #time.sleep(0.01)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)
def rightClick(x,y):
    #time.sleep(0.01)
    win32api.SetCursorPos((x,y))
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN,x,y,0,0)
    #time.sleep(0.01)
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP,x,y,0,0)
time.sleep(10)

while 1:
    try:
        solve_mine(GetMap(driver),difficulty[gameType][1],driver)
    except Exception as e:
        print(str(e))