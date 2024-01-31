import random
from tkinter import *
from tkinter import filedialog
import os


class RandomGame:

    def __init__(self, filename='명단.txt'):
        # GUI
        self.root = Tk()
        self.root.title("Random Game")
        self.root.geometry("536x600")
        self.root.minsize(width=300, height=463)
        # root.resizable(False, False)

        self.filename = filename
        self.picked = []
        self.absence = []
        self.names = self.get_names()

        self.set_icon()
        self.set_menu()
        self.set_frames()
        self.update_listbox()
        self.set_buttons()

        self.root.config(menu=self.menu)
                
        self.root.bind('<Configure>', self.resize)
        self.root.mainloop()

    def set_icon(self, filename='icon.ico'):
        icon = os.path.join(os.path.dirname(__file__), filename)
        if os.path.isfile(icon):
            self.root.iconbitmap(icon)
        self.root.iconbitmap(default = icon)


    def get_names(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r', encoding='utf-8') as f:
                names_org = f.readlines()
                names_org = sorted(names_org)
            return names_org
        
        else:
            return []


    def set_menu(self):
        self.menu = Menu(self.root)
        self.menu_open = Menu(self.menu, tearoff=0)
        self.menu_open.add_command(label='파일 열기', command=self.open_file)
        self.menu_open.add_separator()
        self.menu_open.add_command(label='끝내기', command=self.root.quit)
        self.menu.add_cascade(label='파일', menu=self.menu_open)

    def open_file(self):
        file = filedialog.askopenfilename(
            title='텍스트 파일을 선택하세요',
            filetypes=(("텍스트 파일", "*.txt"),),
            initialdir='.')
        if (file is None) or (file == ''):
            return
        with open(file, 'r', encoding='utf8') as f:
            names_org = f.readlines()
            self.names_org = sorted(names_org)

        self.names = names_org.copy()
        self.absence = []
        self.picked = []
        self.update_listbox()
        self.clear()

    def set_frames(self):

        self.frame_main = Frame(self.root)
        self.frame_main.pack(side='top', fill='both', expand=True)

        self.left = LabelFrame(self.frame_main, text='목록', height=25)
        self.left.pack(side='left', fill='both', expand=True)
        self.listbox = Listbox(self.left, selectmode='extended', height=25, font=('Malgun Gothic', 12))
        self.listbox.pack(side='left', fill='both', expand=True)

        self.scrollbar = Scrollbar(self.left, orient="vertical")
        self.scrollbar.config(command=self.listbox.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.listbox.config(yscrollcommand=self.scrollbar.set)


        self.right = LabelFrame(self.frame_main, text='뽑힘', height=25)
        self.right.pack(side='right', fill='both', expand=True)
        self.lb_p = Listbox(self.right, selectmode='extended', height=25, font=('Malgun Gothic', 12))
        self.lb_p.pack(side='left', fill='both', expand=True)

        self.scrollbar2 = Scrollbar(self.right, orient="vertical")
        self.scrollbar2.config(command=self.lb_p.yview)
        self.scrollbar2.pack(side="right", fill="y")

        self.lb_p.config(yscrollcommand=self.scrollbar2.set)

        self.frame_option = Frame(self.root)
        self.frame_option.pack(side='left', fill='both', expand=True)

        self.lf_absence = LabelFrame(self.frame_option, text='제외', height=5)
        self.lf_absence.grid(row=1, column=0, columnspan=2, sticky=NS)
        self.lb_absence = Listbox(self.lf_absence, selectmode='extended', height=5, font=('Malgun Gothic', 12))
        self.lb_absence.pack(side='left', fill='both', expand=True)

        self.scrollbar3 = Scrollbar(self.lf_absence, orient="vertical")
        self.scrollbar3.config(command=self.lb_absence.yview)
        self.scrollbar3.pack(side="right", fill="y")

        self.lb_absence.config(yscrollcommand=self.scrollbar3.set)



    def update_listbox(self):
        self.listbox.delete(0, END)
        self.lb_p.delete(0, END)
        self.lb_absence.delete(0, END)

        for i, name in enumerate(self.names):
            self.listbox.insert(i, name)

        for i, name in enumerate(self.picked):
            self.lb_p.insert(i, name)

        for i, name in enumerate(self.absence):
            self.lb_absence.insert(i, name)



    def pick_name(self):
        if len(self.names) == 0:
            return
        self.pick = random.choice(self.names)
        self.names.remove(self.pick)
        self.picked.append(self.pick)

        self.update_listbox()


    def pick_name_directly(self):
        self.picked_names = self.listbox.curselection()
        self.picked_names = [self.listbox.get(i) for i in self.picked_names]

        for name in self.picked_names:
            self.names.remove(name)
            self.picked.append(name)
        
        self.update_listbox()

    def add_name_directly(self):
        self.picked_names = self.lb_p.curselection()
        self.picked_names = [self.lb_p.get(i) for i in self.picked_names]

        for name in self.picked_names:
            self.picked.remove(name)
            self.names.append(name)
        
        self.update_listbox()


    def clear(self):
        self.names = self.names_org.copy()

        for name in self.absence:
            if name in self.names:
                self.names.remove(name)
            else:
                self.absence.remove(name)

        self.picked = []

        self.update_listbox()


    def add_absence(self):

        self.absence_names = self.listbox.curselection()
        self.absence_names = [self.names[i] for i in self.absence_names]

        for name in self.absence_names:
            self.names.remove(name)
            self.absence.append(name)

        self.update_listbox()


    def add_present(self):

        self.present_names = self.lb_absence.curselection()
        self.present_names = [self.lb_absence.get(i) for i in self.present_names]

        for name in self.present_names:
            self.names.append(name)
            self.absence.remove(name)

        self.update_listbox()


    def set_buttons(self):

        self.btn_pick = Button(self.frame_main, text='뽑기', command=self.pick_name, width=12, padx=5, pady=5, relief='groove', font=('Malgun Gothic', 14))
        self.btn_pick.pack(side='top', padx=5, pady=5)

        self.btn_clear = Button(self.frame_main, text='초기화', command=self.clear, width=12, padx=5, pady=5, relief='groove', font=('Malgun Gothic', 14))
        self.btn_clear.pack(side='top', padx=5, pady=5)

        self.btn_direct_add = Button(self.frame_main, text='▶ 추가', command=self.pick_name_directly, width=12, padx=5, pady=5, relief='groove', font=('Malgun Gothic', 14))
        self.btn_direct_add.pack(side='top', padx=5, pady=5)

        self.btn_direct_remove = Button(self.frame_main, text='◀ 제거', command=self.add_name_directly, width=12, padx=5, pady=5, relief='groove', font=('Malgun Gothic', 14))
        self.btn_direct_remove.pack(side='top', padx=5, pady=5)


        self.btn_absence = Button(self.frame_option, text='▼ 제외추가', command=self.add_absence, width=10, padx=5, pady=5, relief='ridge')
        self.btn_absence.grid(row=0, column=0, pady=5)

        self.btn_present = Button(self.frame_option, text='▲ 목록추가', command=self.add_present, width=10, padx=5, pady=5, relief='ridge')
        self.btn_present.grid(row=0, column=1, pady=5)


        self.entry_temporary = Entry(self.frame_main, font=('Malgun Gothic', 14), width=10, relief='solid')
        self.entry_temporary.pack(side='bottom', padx=5, pady=5, fill='x')

        self.btn_temporary = Button(self.frame_main, text='임시추가', command=self.temporary, width=12, padx=5, pady=5, relief='groove', font=('Malgun Gothic', 14))
        self.btn_temporary.pack(side='bottom', padx=5, pady=5)



    def temporary(self):
        name = str(self.entry_temporary.get())
        self.names.append(name)

        self.entry_temporary.delete(0, END)

        self.update_listbox()





    def resize(self, event):
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        # print(left.winfo_width())
        # 536-126:20 = w-116:x
        x = int(round(20*(w-126)/(536-126), 0))

        self.listbox.configure(width=x)
        self.lb_p.configure(width=x)

        # 730-157:25 = h-157:y
        y = int(round(25*(h-200)/(730-157), 0))
        # 730:5 = h:y2
        y2 = int(h*6/730)-1

        self.listbox.configure(height=y)
        self.lb_p.configure(height=y)
        self.lb_absence.configure(height=y2)
        if 20 <= self.listbox.config()['width'][-1]:
            self.lb_absence.configure(width=x)
        else:
            self.lb_absence.configure(width=20)



if __name__ == '__main__':
    RandomGame()