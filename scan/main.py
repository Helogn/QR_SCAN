"""
Q1:package install
pip install qrcode[pil] pillow

"""
# sender.py - A电脑运行
import os
import qrcode
import time
from PIL import Image, ImageTk
import tkinter as tk

# 配置
FOLDER_PATH = r"C:\code\QR_COPY\scan"  # 要同步的代码目录
INTERVAL = 2  # 每隔2秒显示一个二维码
LINES_PER_QR = 3  # 每个二维码包含3行代码


class QRDisplay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("二维码发送器")
        self.root.geometry("400x400")
        self.label = tk.Label(self.root)
        self.label.pack(expand=True)

    def generate_qr_image(self, data):
        qr = qrcode.make(data)
        qr = qr.resize((300, 300), Image.Resampling.LANCZOS)
        return qr

    def display_qr(self, image):
        photo = ImageTk.PhotoImage(image)
        self.label.image = photo  # 保持引用
        self.label.configure(image=photo)

    def start(self):
        file_count = 0
        for filename in os.listdir(FOLDER_PATH):
            filepath = os.path.join(FOLDER_PATH, filename)
            if os.path.isfile(filepath) and filename.endswith('.py'):
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                # 每 LINES_PER_QR 行生成一个二维码
                for i in range(0, len(lines), LINES_PER_QR):
                    chunk = lines[i:i + LINES_PER_QR]
                    data = f"FILE:{filename}|LINE:{i}\n" + ''.join(chunk)

                    qr_img = self.generate_qr_image(data)
                    self.display_qr(qr_img)
                    self.root.update()  # 刷新界面
                    print(f"显示二维码: {filename} 第 {i} 行")
                    time.sleep(INTERVAL)

        self.root.mainloop()


if __name__ == "__main__":
    app = QRDisplay()
    app.start()