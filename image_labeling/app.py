import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap import Style
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
import os
from PIL import Image, ImageTk
import configparser
import shutil
import uuid
import sys


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

icon = resource_path("icon.ico")
icon2 = resource_path("icon2.ico")


class app:
    def __init__(self):
        self.style = Style(theme="minty") # 스타일 설정
        self.root = self.style.master
        self.root.iconbitmap(icon)
        
        self.root.geometry("600x850")
        self.root.resizable(False, False)
        self.root.title("Image Labeling")

        if getattr(sys, 'frozen', False):
            self.app_path = os.path.dirname(sys.executable)
        elif __file__:
            self.app_path = os.path.dirname(__file__)
        # app이 있는 폴더에 settings.ini가 있는 경우 불러오기
        
        self.labeling_folder_list = self.load_ini()
        self.num_labeling_folder = len(self.labeling_folder_list)

        self.select_folder() # 폴더 선택 창 배치
        
        self.folder = self.app_path
        self.folder_input.config(text=self.folder)
        self.get_file_list() # 폴더 내 파일 리스트 저장

        self.image_gui() # 이미지 화면 배치
        self.folder_names_gui() # 폴더 이름 배치
        
        self.selected_image_idx = 0
        self.display_image() # 이미지 보여주기


        self.setting_menu() # 메뉴 설정

        for i in range(self.num_labeling_folder):
            self.root.bind(str((i+1)%10), self.move_image)

        self.root.bind('<Delete>', self.delete_image)

        self.root.mainloop()


    def load_ini(self):
        "ini 파일 불러오기"
        if os.path.isfile(self.app_path + "/config.ini"):
            config = configparser.ConfigParser()
            config.read(self.app_path + "/config.ini", encoding='utf-8-sig')
            
            lines = config['folders']
            if len(lines) <= 1:
                return ['1', '2']
                
            labeling_folder_list = [line.strip() for line in lines.values()]

            return labeling_folder_list
        
        else:
            return ['1', '2']

    def setting_menu(self):
        "메뉴 설정 배치"
        menubar = ttk.Menu(self.root)
        self.root.config(menu=menubar)
        filemenu = ttk.Menu(menubar)
        menubar.add_cascade(label="설정", menu=filemenu)

        filemenu.add_command(label="라벨링 폴더", command=self.set_labeling_folder)

        theme = ttk.Menu(menubar)
        menubar.add_cascade(label="테마", menu=theme)
        theme.add_command(label="라이트 모드", command=self.light_mode)
        theme.add_command(label="다크 모드", command=self.dark_mode)


    def light_mode(self):        
        self.style.theme_use('minty')

    def dark_mode(self):
        self.style.theme_use('darkly')

        
    def set_labeling_folder(self):
        "라벨링 폴더 설정"
        "라벨링 폴더는 최소 2개, 최대 10개"
        self.sub_root = ttk.Toplevel(self.root)
        self.sub_root.geometry("500x600")
        self.sub_root.resizable(False, False)
        self.sub_root.title("설정")
        self.sub_root.iconbitmap(icon2)
        self.sub_root.focus_force()
        
        self.labeling_button_frame = ttk.Frame(self.sub_root)
        self.labeling_button_frame.pack()

        self.add_button = ttk.Button(self.labeling_button_frame, text="폴더 추가", command=self.add_labeling_folder)
        self.add_button.grid(row=0, column=0, padx=10, pady=10)
        if self.num_labeling_folder == 10:
            self.add_button.configure(state=DISABLED)

        self.delete_button = ttk.Button(self.labeling_button_frame, text="폴더 삭제", command=self.delete_labeling_folder)
        self.delete_button.grid(row=0, column=1, padx=10, pady=10)
        if self.num_labeling_folder == 2:
            self.delete_button.configure(state=DISABLED)

        self.save_button = ttk.Button(self.labeling_button_frame, text="저장", command=self.save_labeling_folder, style='danger.TButton')
        self.save_button.grid(row=0, column=2, padx=10, pady=10)

        self.labeling_folders_frame = ttk.Frame(self.sub_root)
        self.labeling_folders_frame.pack()

        self.numberings = [ttk.Label(self.labeling_folders_frame, text=f"{(i+1)%10}") for i in range(10)]
        self.labeling_folders = [ttk.Entry(self.labeling_folders_frame, width=50) for _ in range(10)]
        self.grid_labeling_folders()

        

        self.sub_root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.sub_root.mainloop()


    def save_labeling_folder(self):
        
        if messagebox.askokcancel("저장", "저장하시겠습니까?"):

            config = configparser.ConfigParser()
            config['folders'] = {}


            labeling_folder_list = [folder.get() for folder in self.labeling_folders[:self.num_labeling_folder]]
            # 폴더명이 가능해야 함(\, /, :, *, ", ?, <, >, |가 없어야 함, )
            for i, folder in enumerate(labeling_folder_list):
                if "\\" in folder or "/" in folder or ":" in folder or "*" in folder or '"' in folder or "?" in folder \
                    or "<" in folder or ">" in folder or "|" in folder or '.'==folder or len(folder)==0:
                    messagebox.showerror("오류", f"폴더 {i+1}번 이름에 특수문자가 포함되어 있습니다.")
                    self.sub_root.focus_force()
                    return
            
            
            # 동일한 이름이 있으면 안 됨
            
            if len(set(labeling_folder_list)) != len(labeling_folder_list):
                messagebox.showerror("오류", "동일한 이름을 가진 폴더가 있습니다.")
                self.sub_root.focus_force()
                return
            
            self.labeling_folder_list = labeling_folder_list
            for i, folder in enumerate(self.labeling_folder_list):
                config['folders'][str(i+1)] = folder
            
            with open(self.app_path + "/config.ini", "w", encoding='utf-8-sig') as f:
                config.write(f)

            self.folder_name_container.destroy()
            self.folder_names_gui()
            self.sub_root.destroy()

        else:
            self.sub_root.focus_force()


    def on_closing(self):
        labeling_folder_list = self.load_ini()
        new_labeling_folder_list = [folder.get() for folder in self.labeling_folders[:self.num_labeling_folder]]
        if new_labeling_folder_list == labeling_folder_list:
            self.sub_root.destroy()
        
        else:
            if messagebox.askokcancel("종료", "설정이 저장되지 않았습니다.\n그래도 종료하시겠습니까?"):
                self.labeling_folder_list = labeling_folder_list
                self.num_labeling_folder = len(self.labeling_folder_list)
                self.sub_root.destroy()

            else:
                self.sub_root.focus_force()


    def grid_labeling_folders(self):
        labeling_folder_list = [folder.get() for folder in self.labeling_folders[:self.num_labeling_folder]]
        for i, (number, folder) in enumerate(zip(self.numberings, self.labeling_folders[:self.num_labeling_folder])):
            number.grid(row=i+1, column=0, padx=10, pady=10)
            folder.grid(row=i+1, column=1, padx=10, pady=10)

            folder.delete(0, END)
            if labeling_folder_list[i] != "":
                folder.insert(0, labeling_folder_list[i])
            else:
                folder.insert(0, self.labeling_folder_list[i])



    def add_labeling_folder(self):
        "최대 10개까지"
        if self.num_labeling_folder == 10:
            return
        self.num_labeling_folder += 1
        self.labeling_folder_list.append(str(self.num_labeling_folder))

        if self.num_labeling_folder == 10:
            self.add_button.configure(state=DISABLED)
        
        if self.num_labeling_folder == 3:
            self.delete_button.configure(state=NORMAL)
        self.grid_labeling_folders()


    def delete_labeling_folder(self):
        "최소 2개 남기기"
        if self.num_labeling_folder == 2:
            return
        self.num_labeling_folder -= 1
        self.labeling_folder_list.pop()
        for number, folder in zip(self.numberings[self.num_labeling_folder:], self.labeling_folders[self.num_labeling_folder:]):
            number.grid_forget()
            folder.grid_forget()

        if self.num_labeling_folder == 9:
            self.add_button.configure(state=NORMAL)
        
        if self.num_labeling_folder == 2:
            self.delete_button.configure(state=DISABLED)
        self.grid_labeling_folders()


    def select_folder(self):
        "폴더 선택 UI 배치"
        self.select_folder_container = ttk.Frame(self.root)
        self.select_folder_container.pack()
        
        self.folder_labelframe = ttk.LabelFrame(self.select_folder_container, text="폴더명", bootstyle='dark')
        self.folder_labelframe.grid(row=0, column=0, padx=10, pady=10)
        self.folder_input = ttk.Label(self.folder_labelframe, width=50)
        self.folder_input.grid(row=0, column=0, padx=5, ipady=1)
        # self.folder_input.config(borderwidth=2, relief="solid", )
        

        self.select_folder_button = ttk.Button(self.select_folder_container, text="폴더 선택", command=self.select_folder_command, style="info.TButton")
        self.select_folder_button.grid(row=0, column=1, padx=10, pady=10, sticky=S)
        self.file_list = []

        self.file_length_label = ttk.Label(self.select_folder_container, text='')
        self.file_length_label.grid(row=1, column=0, padx=10, pady=10, columnspan=2)


    def select_folder_command(self):
        "폴더 위치 선택 커맨드"
        folder = filedialog.askdirectory()
        if folder != "":
            self.folder = folder
        self.folder_input.config(text=self.folder)
        self.selected_image_idx = 0

        self.get_file_list()
        self.display_image()

    def get_file_list(self):

        self.file_list = []
        for file in os.listdir(self.folder):
            # 대소문자 구분없이
            file_lower = file.lower()
            # 확장자 확인
            if file_lower.endswith(".jpg") or   file_lower.endswith(".png") or file_lower.endswith(".gif") or file_lower.endswith(".webp") or file_lower.endswith(".jpeg"):
                self.file_list.append(file)

        self.file_length_label.config(text=f"남은 파일 개수 : {len(self.file_list)}", font=("Malgun Gothic", 12))


    def image_gui(self):
        self.image_container = ttk.Frame(self.root, height=600)
        self.image_container.pack(fill=BOTH, expand=True)

        self.selected_image_label = ttk.Label(self.image_container)
        self.selected_image_label.pack()

        self.image_name_label = ttk.Label(self.image_container, text="")
        self.image_name_label.pack()

    
    def folder_names_gui(self):


        self.folder_name_container = ttk.Frame(self.root)
        self.folder_name_container.pack(fill=BOTH)

        # app 양 끝에 꽉 차게 grid
        for i, folder in enumerate(self.labeling_folder_list):
            ttk.Label(self.folder_name_container, text=f"{(i+1)%10}={folder}", font=("Malgun Gothic", 12)).grid(row=i//5, column=i%5, padx=10, pady=10)

            
    
    def display_image(self):
        "이미지 리스트에서 하나씩 display"
        if len(self.file_list) == 0:
            self.selected_image_label.config(image='')
            self.selected_image_label.image = ''
            self.image_name_label.config(text="")
            return
        
        self.display_image_resize()

        self.root.bind("<Right>", self.next_image)
        self.root.bind("<Left>", self.prev_image)

    def display_image_resize(self):
        "tkinter 가로 길이에 맞춰서 비율 유지하며 resize 후 display"

        file_path = os.path.join(self.folder, self.file_list[self.selected_image_idx]).replace('\\', '/')
        max_width = 600
        max_height = 600
        # width:height = max_width:max_height
        
        try:
            im = Image.open(file_path)
            width, height = im.size
            ratio = width / height
            if width > max_width:
                width = max_width
                height = int(width / ratio)
                im = im.resize((width, height))

            if height > max_height:
                height = max_height
                width = int(height * ratio)
                im = im.resize((width, height))

            ph = ImageTk.PhotoImage(im)
        except:
            ph = ''
        self.selected_image_label.config(image=ph)
        self.selected_image_label.image = ph


        self.image_name_label.config(text=self.file_list[self.selected_image_idx])


    def next_image(self, event):
        if len(self.file_list) == 0:
            self.selected_image_label.config(image='')
            self.selected_image_label.image = ''
            self.image_name_label.config(text="")
            return
        
        self.selected_image_idx += 1
        if self.selected_image_idx >= len(self.file_list):
            self.selected_image_idx = 0

        self.display_image_resize()

    def prev_image(self, event):
        if len(self.file_list) == 0:
            self.selected_image_label.config(image='')
            self.selected_image_label.image = ''
            self.image_name_label.config(text="")
            return
        self.selected_image_idx -= 1
        if self.selected_image_idx < 0:
            self.selected_image_idx = len(self.file_list) - 1
        
        self.display_image_resize()

        
    
    def move_image(self, event):
        "누른 번호와 일치하는 폴더로 이미지 이동"
        if len(self.file_list) == 0:
            return
        for i in range(self.num_labeling_folder):
            if event.char == str((i+1)%10):
                self.move_image_command(self.file_list[self.selected_image_idx], self.labeling_folder_list[i])
                self.get_file_list()


    def move_image_command(self, file_name, folder_name):
        "이미지 이동 커맨드"
        
        file_path = os.path.join(self.folder, file_name).replace('\\', '/')
        folder_path = os.path.join(self.folder, folder_name).replace('\\', '/')
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)

        # 이동할 폴더에 같은 이름이 있으면 uuid 6글자 추가하여 이동
        if os.path.exists(os.path.join(folder_path, file_name)):
            file_name, file_ext = os.path.splitext(file_name)
            file_name = f"{file_name}_{uuid.uuid4().hex[:6]}{file_ext}"
            shutil.move(file_path, os.path.join(folder_path, file_name))
        else:
            shutil.move(file_path, folder_path)
        
        self.get_file_list()
        self.display_image_resize()


    def delete_image(self, event):
        "이미지 삭제"
        if len(self.file_list) == 0:
            return
        file_path = os.path.join(self.folder, self.file_list[self.selected_image_idx]).replace('\\', '/')
        if messagebox.askyesno("삭제", "정말 삭제하시겠습니까?"):    
            os.remove(file_path)
            self.get_file_list()
            if len(self.file_list) == 0:
                self.selected_image_label.config(image='')
                self.selected_image_label.image = ''
                self.image_name_label.config(text="")
                return
            self.display_image_resize()
            

    

    
        

if __name__ == "__main__":
    app()