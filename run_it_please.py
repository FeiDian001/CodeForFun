from tkinter import *
from tkinter import messagebox

TEXT_CONFIG = [b'\xe5\x86\x8d\xe8\x80\x83\xe8\x99\x91\xe8\x80\x83\xe8\x99\x91\xef\xbc\x9f',
                 b'\xe6\x89\x8d\xe4\xb8\x80\xe7\x82\xb9\xe7\x82\xb9\xe5\x98\x9b\xef\xbc\x9f', 
                 b'\xe4\xb8\x8d\xe5\x90\xac\xe4\xb8\x8d\xe5\x90\xac QAQ']

def closeWindow():
    msg = b'\xe4\xb8\x8d\xe8\xae\xb8\xe5\x85\xb3\xe9\x97\xad\xef\xbc\x8c\xe5\xa5\xbd\xe5\xa5\xbd\xe5\x9b\x9e\xe7\xad\x94'.decode('utf-8')
    messagebox.showinfo(title="警告",message=msg)
    return


def Love():
    # 顶级窗口
    love = Toplevel(window)
    love.geometry("150x60")
    love.title(b'\xe5\xa5\xbd\xe5\xb7\xa7\xef\xbc\x8c\xe6\x88\x91\xe4\xb9\x9f\xe6\x98\xaf'.decode('utf-8'))
    frame = Frame(love)
    frame.pack(side='top', anchor='center')
    msg = b'\xe5\xa5\xbd\xe5\xb7\xa7\xef\xbc\x8c\xe6\x88\x91\xe4\xb9\x9f\xe6\x98\xaf \xe2\x82\x8d\xe1\x90\xa2..\xe1\x90\xa2\xe2\x82\x8e\xe2\x99\xa1'.decode('utf-8')
    label = Label(frame,text = msg,font = ("宋体",10))
    label.pack()
    btn = Button(frame,text=" ♡♡♡ ",width=10,height=1,command=closeAllWindow)
    btn.pack(pady=5)
    love.protocol("WM_DELETE_WINDOW",closeLove)

def closeLove():
    return

# 关闭所有的窗口
def closeAllWindow():
    # destroy  销毁
    window.destroy()

def noLove():
    global no_love_cnt
    global top_label
    top_label['text']=TEXT_CONFIG[no_love_cnt].decode('utf-8')
    msg = b'\xe4\xb8\x80\xe7\x82\xb9\xe7\x82\xb9'.decode('utf-8')
    btn1['text']=msg
    no_love_cnt += 1
    if no_love_cnt >2:
        no_love_cnt = 0

def closeNoLove():
    noLove()

# 创建父级窗口
window = Tk()  #Tk 是一个类
# 窗口标题
window.title(b'\xe4\xbd\xa0\xe5\x96\x9c\xe6\xac\xa2\xe6\x88\x91\xe5\x90\x97\xef\xbc\x9f'.decode('utf-8'))
# 窗口大小
window.geometry('300x100')

# protocol()  用户关闭窗口触发的事件
window.protocol("WM_DELETE_WINDOW",closeWindow)
msg = b'\xe5\xae\x87\xe5\x93\xa5\xe5\xae\x87\xe5\x93\xa5\xef\xbc\x8c\xe5\x96\x9c\xe6\xac\xa2\xe6\x88\x91\xe5\x90\x97\xef\xbc\x9f'.decode('utf-8')
top_label = Label(window, text=msg, font = ('宋体，10'))
top_label.pack(side='top', pady=10)

button_frame = Frame(window)
button_frame.pack(side='top')

btn = Button(button_frame,text=b'\xe5\x96\x9c\xe6\xac\xa2'.decode('utf-8'), width=10,height=1,command=Love)
btn.pack(side='left', padx=5, pady=5)

btn1 = Button(button_frame,text=b'\xe4\xb8\x8d\xe5\x96\x9c\xe6\xac\xa2'.decode('utf-8') ,width=10,height=1, command=noLove)
btn1.pack(side='left', padx=5, pady=5)

no_love_cnt = 0

window.mainloop()