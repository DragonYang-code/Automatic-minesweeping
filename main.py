#优化1：去掉所有中间提示信息的输出
#优化2：将每次取图片前定位边框位置的操作改为仅在开局定位一次
#优化3：将C++编写的扫雷算法模块移植为python
#优化4：优化图片识别的速度
#优化5：将雷的信息保存在内存中，不再插旗
#优化6：每次仅对上次未知的格子进行数字转换
#可优化7：换鼠标点击事件的接口
#可尝试优化8：直接执行点击操作 (负优化)
#专家难度时间 59->22

import pyautogui
import time
from PIL import ImageGrab,Image
import win32api
import win32con
import win32gui
from ctypes import *
import cv2
import numpy as np
from matplotlib import pyplot as plt
#import easyocr
import os
main = "auto扫雷程序.exe"
#每个小格子的高宽
gridwidth=25
gridheight=25
#棋盘左上角坐标，棋盘的行列数目
bleft=0
btop=0
bm=0
bn=0

#空：0，数字:1-8,雷:-1,非雷:-2,未知: -3
#棋盘
board=[ [-100]*100 for i in range(100)]#棋盘本身
tboard=[ [0]*100 for i in range(100)]#零时棋盘
vis= [ [0]*100 for i in range(100)]

possible=False


#鼠标事件
def mouse_move(x, y):
    windll.user32.SetCursorPos(int(x), int(y))


def mouse_click(x=None, y=None,left_button=True):
    if not x is None and not y is None:
        mouse_move(x, y)
        time.sleep(0.001)
    if left_button == True:
        if win32api.GetSystemMetrics(win32con.SM_SWAPBUTTON):  # Check if the Mouse Primary Key had been changed
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
            # time.sleep(0.001)
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
        else:
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            # time.sleep(0.001)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    else:
        if win32api.GetSystemMetrics(win32con.SM_SWAPBUTTON):  # Check if the Mouse Primary Key had been changed
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            # time.sleep(0.001)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        else:
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
            # time.sleep(0.001)
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)

def dfs(cx,cy,m,n):
    global possible,tboard,board
    if possible==False:
        return
    for i in range(-1,2):
        for j in range(-1,2):
            if not (i or j):
                continue
            nx,ny=cx+i,cy+j
            if nx<0 or nx>=m or ny<0 or ny>=n:
                continue
            if 1<=tboard[nx][ny]<=8 :
                scan(nx, ny, m, n)

def scan(cx,cy,m,n):
    global possible,tboard,board
    unknowns=[]
    if possible == False:
        return
    bomb,nbomb,unknown=0,0,0
    for i in range(-1,2):
        for j in range(-1,2):
            if not (i or j):
                continue
            nx,ny=cx+i,cy+j
            if nx<0 or nx>=m or ny<0 or ny>=n:
                continue
            value=tboard[nx][ny]
            if value == -1:
                bomb+=1
            elif value == -2:
                nbomb+=1
            elif value == -3:
                unknown+=1
                unknowns.append([nx,ny])

    maxbomb , minbomb= bomb + unknown, bomb
    expect=0

    if minbomb > tboard[cx][cy]:
        possible=False
        return
    elif maxbomb < tboard[cx][cy]:
        possible = False
        return
    elif minbomb==tboard[cx][cy]:
        expect=-2
    elif maxbomb==tboard[cx][cy]:
        expect=-1
    else:
        return

    for item in unknowns:
        nx,ny=item[0],item[1]
        tboard[nx][ny]=expect

    for item in unknowns:
        nx, ny = item[0], item[1]
        dfs(nx,ny,m,n)

def CopyList(m,n):
    global tboard,board
    for i in range(m):
        for j in range(n):
            tboard[i][j]=board[i][j]

def Quick_Click(m,n):
    global tboard, board
    out=[]
    for cx in range(m):
        for cy in range(n):
            if 1<=board[cx][cy]<=8:
                bomb, nbomb, unknown = 0, 0, 0
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        if not (i or j):
                            continue
                        nx, ny = cx + i, cy + j
                        if nx < 0 or nx >= m or ny < 0 or ny >= n:
                            continue
                        value = board[nx][ny]
                        if value == -1:
                            bomb += 1
                        elif value == -2:
                            nbomb += 1
                        elif value == -3:
                            unknown += 1
                if bomb == board[cx][cy] and unknown + nbomb >0:
                    for i in range(-1, 2):
                        for j in range(-1, 2):
                            if not (i or j):
                                continue
                            nx, ny = cx + i, cy + j
                            if nx < 0 or nx >= m or ny < 0 or ny >= n:
                                continue
                            if board[nx][ny]==-3:
                                board[nx][ny]=-4
                            elif board[nx][ny]==-2:
                                board[nx][ny]=-4
                    out.append([cx,cy,0])
    return out

def ClearVis(m,n):
    global vis
    vis= [ [0]*100 for i in range(100)]

def MyClick(i,j,boom):
    pos = GetCor(i, j)
    x=pos[0]+gridwidth/2
    y=pos[1]+gridheight/2
    if boom:#  等于1说明有炸弹
        pyautogui.click(x, y, button='right')
    else:
        pyautogui.click(x, y, button='left')

def Saolei(m,n):
    out=[]
    #op_cnt=0
    ClearVis(m,n)
    global possible
    for x in range(m):
        for y in range(n):
            if 1<=board[x][y]<=8:
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        if not (i or j):
                            continue
                        nx, ny = x + i, y + j
                        if nx < 0 or nx >= m or ny < 0 or ny >= n or vis[nx][ny]:
                            continue
                        if board[nx][ny] == -3:
                            vis[nx][ny]=1
                            #1.假设为雷
                            possible=True
                            CopyList(m,n)
                            tboard[nx][ny]=-1
                            dfs(nx,ny,m,n)
                            if possible == False:
                                out.append([nx,ny,0])
                                #MyClick(nx,ny,0)
                                #op_cnt+=1
                                board[nx][ny]=-2
                            #2.假设为非雷
                            possible=True
                            CopyList(m, n)
                            tboard[nx][ny] = -2
                            dfs(nx, ny, m, n)
                            if possible == False:
                                #out.append([nx, ny, 1])
                                board[nx][ny] = -1#标记为非雷即可，不用插旗，下轮该标记还在
    """
    out.extend(Quick_Click(m,n))
    for x in range(m):
        for y in range(n):
            if board[x][y]==-2:
                out.append([x,y,0])
    """
    return out

def LocateFrame():
    global bleft,btop,bm,bn
    while True:
        blefttop=pyautogui.locateOnScreen('pictures/lefttop.png')
        brightbottom=pyautogui.locateOnScreen('pictures/rightbottom.png')
        if (blefttop is not None) and (brightbottom is not None):
            break
    #print('左上:',blefttop)
    #print('右下:',brightbottom)
    bleft=blefttop.left+blefttop.width
    btop=blefttop.top+blefttop.height
    bwidth=brightbottom.left-bleft
    bheight=brightbottom.top-btop
    bm = int(bheight/gridheight)
    bn = int(bwidth/gridwidth)
    #print(bm,' ',bn)

#获得第i行第j列的左上角坐标(left,top)
def GetCor(i,j):
    #print(i,j)
    return [bleft+j*gridwidth,btop+i*gridheight]

#转换图片为数字
def P2N(pix):
    red=False
    black=False
    cnt5=0 #由于128,0,0可能会在🚩中出现，所以计数到4个（阈值）才确定确实是5
    for j in range(gridheight//5,gridheight//5*4):#range(10, 20):
        i=gridwidth//2-2#偏离两个像素，为了适应旗子的情况
        r, g, b = pix[i, j]
        if r==0 and g==0 and b == 255:
            return 1
        if r==0 and g==128 and b == 0:
            return 2
        if r==255 and g==0 and b == 0:
            red=True
        if r==0 and g==0 and b == 0:# 3等会儿再判断
            black=True
        if r==0 and g==0 and b == 128:
            return 4
        if r == 128 and g == 0 and b == 0:
            cnt5=cnt5+1
        if r == 0 and g == 128 and b == 128:
            return 6
        if r == 128 and g == 128 and b == 128:
            return 8

    if cnt5 >= 4 :
        return 5

    if red and black:#红黑都有，是旗
        return -1
    elif red:#仅仅是红色，3
        return 3
    elif black:#仅仅黑色，7
        return 7
    else:
        r, g, b = pix[gridwidth//2, gridheight//2]
        if r == 192:
            return -3
        elif r== 190:
            return 0

    return 10#错误码

def OnInit():
    global board,tboard
    board = [[-100] * 100 for i in range(100)]  # 棋盘本身
    tboard = [[0] * 100 for i in range(100)]  # 零时棋盘
    LocateFrame()

# 创建reader对象,用于ocr转换
#reader = easyocr.Reader(['en'])

OnInit()

while True:

    #pyautogui.moveTo(bleft, btop-20)#移开鼠标，避免截图中鼠标覆盖网格影响识别
    mouse_move(bleft, btop-20)
    #print('边框定位成功\n扫描转换中...')
    im = ImageGrab.grab()
    for i in range(bm):
        for j in range(bn):
            if -1<= board[i][j] <= 8:#每次仅对上次未知的格子进行数字转换
                continue
            xy=GetCor(i,j)
            box=(int(xy[0]),int(xy[1]),int(xy[0]+gridwidth),int(xy[1]+gridheight))
            region = im.crop(box)
            #path='./caches/'+str(i*bn+j)+'.png'
            #region.save(path)
            pix = region.load()
            board[i][j]=P2N(pix)
            if(board[i][j]==10):
                print('扫描时出现错误')
                exit(0)
    data = Saolei(bm, bn)

    #print(data)
    #exit(0)

    for operation in data:
        pos=GetCor(int(operation[0]),int(operation[1]))
        x=pos[0]+gridwidth/2
        y=pos[1]+gridheight/2
        if int(operation[2]):#  等于1说明有炸弹
            pyautogui.click(x, y, button='right')
        else:
            #pyautogui.click(x, y, button='left')
            mouse_click(x,y)

    time.sleep(0.13)#睡一会，避免棋盘扫描错误

    if len(data)==0:
        smile=pyautogui.locateOnScreen('pictures/smile.png')
        if smile is not None:
            center = pyautogui.center(smile)
            pyautogui.click(center)
            OnInit()
        else:
            print('\a')
            input()
            OnInit()
