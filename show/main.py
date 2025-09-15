# screen_qr_scanner.py - 扫描屏幕指定区域（带可视化窗口）
"""
Q1:package install:
pip install pyzbar opencv-python pillow

Q2:安装pyzbar问题，libzbar-64.dll找不到
https://www.microsoft.com/zh-cn/download/details.aspx?id=40784

"""
import os
import mss
import cv2
import numpy as np
from pyzbar import pyzbar

# ------------------ 配置区域 ------------------
MONITOR_REGION = {
    'top': 100,
    'left': 100,
    'width': 400,
    'height': 400,
}

SCAN_INTERVAL = 0.5
WINDOW_NAME = "🔍 二维码扫描监控"
# ----------------------------------------------

received_data = []
received_files = {}

def parse_qr_data(data):
    try:
        if data.startswith("FILE:"):
            header, *content_lines = data.split('\n')
            _, filename = header.split('FILE:', 1)
            filename = filename.split('|')[0].strip()
            content = '\n'.join(content_lines)
            return 'CODE', filename, content
        else:
            return 'TEXT', None, data
    except Exception as e:
        return 'ERROR', None, str(e)

def main():
    global received_data, received_files

    print("🔍 屏幕二维码扫描器启动")
    print(f"监听区域: {MONITOR_REGION}")
    print(f"显示窗口: [{WINDOW_NAME}]")
    print("按 Q 键关闭窗口并停止...\n")

    # 创建显示窗口
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_GUI_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, MONITOR_REGION['width'], MONITOR_REGION['height'])

    with mss.mss() as sct:
        while True:
            # 1. 截图
            screenshot = sct.grab(MONITOR_REGION)
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

            # 2. 识别二维码
            barcodes = pyzbar.decode(frame)

            for barcode in barcodes:
                data = barcode.data.decode('utf-8')

                if data in received_data:
                    continue
                received_data.append(data)

                dtype, filename, content = parse_qr_data(data)

                if dtype == 'CODE':
                    if filename not in received_files:
                        received_files[filename] = []
                    received_files[filename].append(content)
                    print(f"📄 收到代码片段: {filename}")
                else:
                    print(f"💬 识别到: {data}")

                # 绘制二维码边框
                points = barcode.polygon
                pts = np.array(points, np.int32).reshape((-1, 1, 2))
                cv2.polylines(frame, [pts], True, (0, 255, 0), 2)

            # ✅ 显示当前扫描画面
            cv2.imshow(WINDOW_NAME, frame)

            # 按 Q 退出
            key = cv2.waitKey(int(SCAN_INTERVAL * 1000)) & 0xFF
            if key == ord('q') or key == ord('Q'):
                break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 扫描被中断，正在保存文件...")
    finally:
        output_dir = "./received_code"
        os.makedirs(output_dir, exist_ok=True)

        for filename, chunks in received_files.items():
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(''.join(chunks))
            print(f"✅ 已保存: {filepath}")

        print("🎉 所有文件保存完成！")