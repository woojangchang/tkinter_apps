import tkinter as tk
import pyperclip

class newline_eliminator:
    def __init__(self):
        # tkinter 윈도우 생성
        self.window = tk.Tk()
        self.window.title("PDF 복사기")

        self.previous_clipboard_content = ""
        self.is_running = False  # check_clipboard() 함수의 실행 여부를 저장하는 변수

        self.label = tk.Label(self.window, text="PDF 복사기", font=("Arial", 16))
        self.label.pack()

        self.start_button = tk.Button(self.window, text="실행", command=self.start, state="disabled")
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(self.window, text="중단", command=self.stop, state="disabled")
        self.stop_button.pack(pady=10)

        self.start()
        self.window.mainloop()  # tkinter 윈도우 실행

    # 클립보드를 주기적으로 확인하는 함수
    def check_clipboard(self):
        current_clipboard_content = pyperclip.paste()
        # print(current_clipboard_content)
        # 이전 클립보드와 현재 클립보드 내용이 다를 경우
        if current_clipboard_content != self.previous_clipboard_content:
            # "\n"을 " "로 변경
            updated_clipboard_content = current_clipboard_content.replace("\r\n", " ").replace("\n", " ")
            # 변경된 내용을 클립보드에 복사
            pyperclip.copy(updated_clipboard_content)
                    
            # 이전 클립보드 내용 업데이트
            self.previous_clipboard_content = updated_clipboard_content

        # 1초마다 클립보드 확인
        if self.is_running:
            self.window.after(1000, self.check_clipboard)


    # tkinter 윈도우 실행
    def start(self):
        self.is_running = True
        self.check_clipboard()
        self.label.config(text="실행 중", fg="red")
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.window.title('PDF 복사기 (실행 중)')

    def stop(self):
        self.is_running = False
        self.window.after_cancel(self.check_clipboard)
        self.label.config(text="중단", fg="#555")
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.window.title('PDF 복사기 (중단)')



if __name__ == "__main__":
    newline_eliminator()