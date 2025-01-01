from pynput import keyboard, mouse
import pygetwindow as gw
import psutil
import GPUtil
import requests
import time
import logging
import sys
from logging.handlers import TimedRotatingFileHandler

file_handler = TimedRotatingFileHandler(
    "ranjyaa_alive_watch_win.log", when="midnight", interval=1, backupCount=7, encoding='utf-8'
)
file_handler.suffix = "_%Y-%m-%d.log"
file_handler.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s [%(levelname)-5s] %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, console_handler]
)

# TODO 改成你自己的
SERVER_URL = 'http://localhost:5002/api/upload'

# TODO 改成你自己的
API_KEY_UPLOAD = "API_KEY"
headers = {
    'x-api-key': API_KEY_UPLOAD
}

ALIVE_TIME_OUT = 60 * 20  # 20分钟没动静（似了
# ALIVE_TIME_OUT = 10
RESULT = {"data": {}, "type": 0}


keyboard_active = False  # 记录键盘是否有输入
mouse_active = False  # 记录鼠标是否有点击


def get_window_title():
    """获取当前前端窗口信息"""
    try:
        window = gw.getActiveWindow()
        return window.title if window else None
    except Exception as e:
        return {"error": str(e)}


def send_window_info(current_title, current_time):
    """获取并发送前端窗口信息到服务器"""
    data = {"title": current_title, "time": current_time}
    RESULT["data"] = data
    try:
        response = requests.post(SERVER_URL, json=RESULT, headers=headers)
        if response.status_code != 200:
            logging.error(f"Failed to send data: {response.status_code}")
    except Exception as e:
        logging.error(f"Error sending data: {e}")


def is_user_active(flag):
    """是否用户活跃"""
    mouse_active = check_mouse()
    if mouse_active:
        logging.info("鼠标活动")
        return True
    keyboard_active = check_keyboard()
    if keyboard_active:
        logging.info("键盘活动")
        return True
    cpu_gpu_active = check_cpu_gpu()
    if cpu_gpu_active:
        logging.info("CPU/GPU活动")
        return True
    # 全都不在活跃状态，返回False（离开电脑）
    if flag:
        logging.info("硬件未活动")
    return False


def check_cpu_gpu():
    """检查CPU和GPU使用率"""
    cpu_usage = psutil.cpu_percent(interval=1)
    gpus = GPUtil.getGPUs()
    gpu_usage = gpus[0].load * 100 if gpus else 0
    return cpu_usage > 20 or gpu_usage > 45


def check_mouse():
    """检查鼠标输入"""
    global last_mouse_pos, mouse_active
    active = mouse_active
    mouse_active = False  # 检查后立即重置活动状态
    return active


def check_keyboard():
    """检查键盘输入"""
    global keyboard_active
    active = keyboard_active
    keyboard_active = False  # 检查后立即重置活动状态
    return active


def on_press(key):
    """键盘按下事件"""
    global keyboard_active
    keyboard_active = True


def on_click(x, y, button, pressed):
    """鼠标点击事件"""
    global mouse_active
    mouse_active = True


if __name__ == '__main__':
    flag = True
    last_title = None
    last_change = time.time()
    keyboard.Listener(on_press=on_press).start()
    logging.info("键盘监听器已启动")
    mouse.Listener(on_click=on_click).start()
    logging.info("鼠标监听器已启动")

    while True:
        current_title = get_window_title()
        current_time = time.time()
        # 如果没有前端窗口，发送空数据
        if current_title is None:
            send_window_info(None, current_time)
        # 如果窗口标题未变化且用户不在电脑前，发送空数据
        elif current_time - last_change > ALIVE_TIME_OUT and current_title == last_title and not is_user_active(flag):
            if flag:
                flag = False
                logging.info("用户不在电脑前")
            send_window_info(None, current_time)
        # 如果窗口标题发生变化，发送新的窗口信息并更新
        elif current_title != last_title and current_title != "":
            flag = True
            logging.info(f"窗口更新: {current_title}")
            last_title = current_title
            last_change = time.time()
            send_window_info(current_title, current_time)
        # 如果窗口标题未变化且用户在电脑前，发送当前窗口信息
        else:
            flag = True
            send_window_info(current_title, current_time)
        time.sleep(3)
