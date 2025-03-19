import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import zipfile
import os
import tempfile
from tkinterdnd2 import DND_FILES, TkinterDnD

class WheelPackagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Wheel File Packager")
        self.root.geometry("600x400")
        
        # 선택한 파일 리스트
        self.selected_files = []
        
        self.python_zip_name = "python.zip"
        self.python_dir = "python"
        
        # 드래그 & 드랍 기능
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.on_drop)
        
        # 메인 컨테이너
        main_container = ttk.Frame(root, padding="10")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_container.columnconfigure(0, weight=1)
        
        ttk.Label(main_container, text="Selected Files:").grid(row=0, column=0, sticky=tk.W)
        
        # 파일 목록 트리뷰
        self.tree = ttk.Treeview(main_container, columns=("Path",), show="tree headings")
        self.tree.heading("Path", text="File Path")
        self.tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_container.rowconfigure(1, weight=1)
        
        # 스크롤바
        scrollbar = ttk.Scrollbar(main_container, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 버튼 프레임
        button_frame = ttk.Frame(main_container)
        button_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        button_frame.columnconfigure(1, weight=1)
        
        # 버튼 추가
        self.upload_btn = ttk.Button(button_frame, text="Upload Files", command=self.upload_files)
        self.upload_btn.grid(row=0, column=0, padx=5)
        
        self.clear_btn = ttk.Button(button_frame, text="Clear Selected", command=self.clear_selected)
        self.clear_btn.grid(row=0, column=1, padx=5)
        
        self.clear_all_btn = ttk.Button(button_frame, text="Clear All", command=self.clear_all)
        self.clear_all_btn.grid(row=0, column=2, padx=5)
        
        self.process_btn = ttk.Button(button_frame, text="Process Files", command=self.process_and_create_zip)
        self.process_btn.grid(row=0, column=3, padx=5)
        
        # 프로그레스 바
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(main_container, mode='determinate', variable=self.progress_var)
        self.progress.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # 상태 표시 라벨
        self.status_label = ttk.Label(main_container, text="")
        self.status_label.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        
        self.update_buttons()

    def on_drop(self, event):
        files = self.root.tk.splitlist(event.data)
        for file in files:
            if file.endswith(('.whl', '.zip')):  # zip 및 whl 파일만 허용
                self.add_file(file)
        self.update_buttons()

    def add_file(self, file):
        if file not in self.selected_files:
            self.selected_files.append(file)
            filename = os.path.basename(file)
            self.tree.insert('', 'end', text=filename, values=(file,))
    
    def on_select(self, event=None):
        self.update_buttons()

    def upload_files(self):
        files = filedialog.askopenfilenames(
            title="Select files",
            filetypes=[("Wheel and Zip files", "*.whl *.zip")]
        )
        for file in files:
            self.add_file(file)
        self.update_buttons()

    def clear_selected(self):
        selected_items = self.tree.selection()
        for item in selected_items:
            file_path = self.tree.item(item)['values'][0]
            self.selected_files.remove(file_path)
            self.tree.delete(item)
        self.update_buttons()

    def clear_all(self):
        self.tree.delete(*self.tree.get_children())
        self.selected_files.clear()
        self.update_buttons()

    def update_buttons(self):
        has_files = bool(self.selected_files)
        self.process_btn.config(state='normal' if has_files else 'disabled')
        self.clear_btn.config(state='normal' if self.tree.selection() else 'disabled')
        self.clear_all_btn.config(state='normal' if has_files else 'disabled')

    def update_progress(self, value, text):
        self.progress_var.set(value)
        self.status_label.config(text=text)
        self.root.update_idletasks()

    def extract_zip_content(self, zip_file, destination):
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            
            # python.zip 파일 처리 - 내부에 python 디렉토리가 있는지 확인
            if any(name.startswith('python/') for name in file_list):
                # python 폴더 내용만 추출
                for file_info in zip_ref.infolist():
                    if file_info.filename.startswith('python/'):
                        extracted_path = file_info.filename[len('python/'):]
                        if extracted_path:  # 빈 경로 방지
                            source = zip_ref.read(file_info.filename)
                            target_path = os.path.join(destination, extracted_path)
                            
                            # 디렉토리면 생성
                            if file_info.filename.endswith('/'):
                                os.makedirs(target_path, exist_ok=True)
                            else:
                                # 파일의 디렉토리가 없으면 생성
                                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                                with open(target_path, 'wb') as f:
                                    f.write(source)
            else:
                # 일반 zip, whl 파일은 그대로 추출
                zip_ref.extractall(destination)

    def process_and_create_zip(self):
        if not self.selected_files:
            return

        self.upload_btn.config(state='disabled')
        self.clear_btn.config(state='disabled')
        self.clear_all_btn.config(state='disabled')
        self.process_btn.config(state='disabled')

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                final_python_dir = os.path.join(temp_dir, self.python_dir)
                os.makedirs(final_python_dir, exist_ok=True)

                total_files = len(self.selected_files)
                for idx, file in enumerate(self.selected_files, start=1):
                    self.update_progress((idx / total_files) * 80, f"Processing {os.path.basename(file)}...")
                    
                    # zip 또는 whl 파일 처리
                    if file.endswith('.zip'):
                        self.extract_zip_content(file, final_python_dir)
                    else:  # whl 파일
                        with zipfile.ZipFile(file, 'r') as zip_ref:
                            zip_ref.extractall(final_python_dir)

                self.update_progress(90, "Creating final python.zip file...")

                output_zip_path = os.path.join(os.getcwd(), self.python_zip_name)
                with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
                    for root, _, files in os.walk(temp_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, temp_dir)
                            zip_ref.write(file_path, arcname)

                self.update_progress(100, "Processing complete!")

                # 기존 업로드된 파일 리스트 및 whl 삭제
                for file in self.selected_files:
                    if file.endswith(".whl"):
                        try:
                            os.remove(file)
                        except:
                            pass

                self.clear_all()

                messagebox.showinfo("Success", f"Files processed successfully!\nOutput saved as {self.python_zip_name}")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.update_progress(0, "Processing failed!")

        finally:
            self.upload_btn.config(state='normal')
            self.update_buttons()
            self.update_progress(0, "")

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = WheelPackagerApp(root)
    root.mainloop()