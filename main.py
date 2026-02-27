import sys, os
from PySide6.QtWidgets import *
from main_ui import *  # 导入你生成的 UI 类
from PySide6.QtCore import *
from PySide6.QtMultimedia import *
from PySide6.QtGui import *
import random
import pylrc
# import json
# import urllib.parse
from random import randrange
import requests
# from hashlib import md5
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import time
import sys
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QFont
from mutagen import File
from mutagen.id3 import ID3
from mutagen.id3 import APIC
from utils import api
from io import BytesIO
from PIL import Image
import base64
from pathlib import Path
# from send2trash import send2trash
from components.chat_dialog import Ui_Dialog
from components.chat_dialog_deletecache import Ui_Dialog_deletecache
import configparser


def get_bundle_dir():
    """
    获取打包后的程序目录（专门处理 PyInstaller 打包后的路径）
    
    兼容模式：
    - onedir 模式：返回 exe 所在目录
    - onefile 模式：返回 exe 所在目录（非临时目录）
    - 未打包：返回 None
    
    Returns:
        Path | None: 打包后的程序目录，未打包时返回 None
    """
    if not getattr(sys, 'frozen', False):
        return None
    
    # PyInstaller 打包后的环境
    exe_path = Path(sys.executable).resolve()
    return exe_path.parent
def get_script_dir():
    """获取脚本所在目录（兼容打包前后）"""
    if getattr(sys, 'frozen', False):
        # 打包后的环境 - 使用 EXE 所在目录
        return os.path.dirname(sys.executable)
    else:
        # 开发环境 - 使用 .py 文件所在目录
        return os.path.dirname(os.path.abspath(__file__))

def get_config_path():
    """获取配置文件路径（脚本/EXE 同目录）"""
    return os.path.join(get_script_dir(), 'config.ini')
def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)
# ============ 主逻辑 ============
config_path = get_config_path()
config = configparser.ConfigParser()

if not os.path.exists(config_path):
    # 创建默认配置文件
    print(f'配置文件不存在，创建默认配置：{config_path}')
    config['DEFAULT'] = {
        'MUSIC_U_COOKIE': '',
        'THEME': ''
    }
    with open(config_path, 'w', encoding='utf-8') as configfile:
        config.write(configfile)
else:
    # 读取现有配置文件
    print(f'加载配置文件：{config_path}')
    config.read(config_path, encoding='utf-8')

# 获取配置值
music_u_cookie = config['DEFAULT'].get('MUSIC_U_COOKIE', '')
theme=config['DEFAULT'].get('THEME', '')
print(f'MUSIC_U_COOKIE: {music_u_cookie}')


pool = QThreadPool.globalInstance()
pool.setMaxThreadCount(5)  # 设置最大线程数（根据需要调整）

class WorkerSignals(QObject):
    finished = Signal(str, float)
    progress = Signal(str, int)
    online_music_geted = Signal(str, str)  # 任务 ID, 音乐文件路径
    cover_ready = Signal(str)  # 🔑 新增：封面文件路径
    error = Signal(str, str)


class OnlineMusic_get(QRunnable):
    """在线音乐获取任务"""

    def __init__(self, task_id=None, music_id=None, cookies=None,music_u_cookie=''):
        super().__init__()
        # 使用时间戳生成唯一任务ID
        self.task_id = task_id or f"{int(time.time() * 1000)}"
        self.music_id = music_id  # 音乐ID
        self.music_u_cookie = music_u_cookie
        self.cookies = cookies or {
            "MUSIC_U": self.music_u_cookie,  # 这里需要替换为实际的 MUSIC_U cookie 值
            "os": "pc",
            "appver": "8.9.75",
        }

        # 信号发射器（必须通过QObject发射信号）
        self.signal_emitter = WorkerSignals()
        self.setAutoDelete(True)  # 任务完成后自动删除

        # 任务状态
        self.lyric = None
        self.name = None
        self.url = None
        self.filename = None

    def run(self):
        """任务执行逻辑（在线程池中运行）"""
        start = time.time()

        try:
            result = self.process_data()

            end = time.time()
            duration = end - start

            # 发射完成信号
            self.signal_emitter.finished.emit(self.task_id, duration)

            # 发射音乐获取成功信号
            if self.filename:
                self.signal_emitter.online_music_geted.emit(self.task_id, self.filename)

            if self.picture_name:
                self.signal_emitter.cover_ready.emit(self.picture_name)
        except Exception as e:
            end = time.time()
            duration = end - start
            # 发射错误信号
            self.signal_emitter.error.emit(self.task_id, str(e))
            self.signal_emitter.finished.emit(self.task_id, duration)

    def process_data(self):
        """处理音乐下载逻辑"""
        # cache_path = Path(__file__).parent / "cache" / "online_music"
        # cache_path_2 = Path(__file__).parent / "cache" / "music_cover"
        # cache_path.mkdir(parents=True, exist_ok=True)
        # os.makedirs(cache_path, exist_ok=True)
        # os.makedirs(cache_path_2, exist_ok=True)
        # chahe_path = path.get_work_directory(relative_path="cache/online_music")
        # chahe_path_2 = path.get_work_directory(relative_path="cache/music_cover")
        # cache_path = Path(chahe_path)
        # cache_path_2 = Path(chahe_path_2)
        real_path = Path(get_script_dir())  # 强制转换为 Path 对象
        cache_path = real_path / "cache" / "online_music"
        cache_path_2 = real_path / "cache" / "music_cover"
        cache_path.mkdir(parents=True, exist_ok=True)
        cache_path_2.mkdir(parents=True, exist_ok=True) 

        print(f"[调试] 脚本目录: {get_script_dir()}")
        print(f"[调试] 音乐缓存目录: {cache_path}")
        print(f"[调试] 封面缓存目录: {cache_path_2}")

        try:
            cache_path.mkdir(parents=True, exist_ok=True)
            cache_path_2.mkdir(parents=True, exist_ok=True)
            print(f"[调试] 目录创建成功")
        except Exception as e:
            print(f"[调试] 目录创建失败: {e}")
            raise
        # 获取歌词和歌曲信息
        self.lyric = api.lyric_v1(self.music_id, self.cookies)
        self.name = api.name_v1(self.music_id)

        # 生成文件名
        song_name = self.name["songs"][0]["name"]

        song_id = self.name["songs"][0]["id"]
        # self.filename = os.path.join(
        #     cache_path,
        #     f"{song_name}_{song_id}.mp3"
        # )
        self.filename = str(cache_path / f"{song_name}_{song_id}.mp3")
        # 检查缓存
        first_cover = (
            self.name["songs"][0]["al"]["picUrl"]
            if self.name and self.name.get("songs")
            else None
        )
        print(f"[任务 {self.task_id}] 歌曲封面 URL: {first_cover}")
        self.picture_name = str(cache_path_2 / f"{song_name}_{song_id}_cover.jpg")
        if os.path.isfile(self.picture_name) and os.path.getsize(self.picture_name) > 0:
            print(f"[任务 {self.task_id}] 封面已存在，使用缓存: {self.picture_name}")
        else:
            if first_cover:
                try:
                    response = requests.get(first_cover, timeout=10)
                    response.raise_for_status()
                    with open(self.picture_name, "wb") as f:
                        f.write(response.content)
                    print(f"[任务 {self.task_id}] 已下载封面: {self.picture_name}")
                except Exception as e:
                    print(f"[任务 {self.task_id}] 下载封面失败: {e}")
            else:
                print(f"[任务 {self.task_id}] 无封面 URL，跳过下载")
        if os.path.isfile(self.filename) and os.path.getsize(self.filename) > 0:
            print(f"[任务 {self.task_id}] 文件已存在，使用缓存: {self.filename}")
            print (self.filename)
            return self.lyric, self.name, self.picture_name, self.filename

        # print(f"[任务 {self.task_id}] 获取在线音乐信息成功: {self.name}")

        # 获取音乐链接
        self.url = api.url_v1(self.music_id, "standard", self.cookies)
        # print(f"[任务 {self.task_id}] 获取在线音乐链接成功: {self.url}")
        # print(f"[任务 {self.task_id}] 获取在线音乐歌词成功: {self.lyric}")

        # 下载音乐文件（优先尝试旧接口）
        download_success = False

        try:
            response2 = requests.get(
                f"http://music.163.com/song/media/outer/url?id={song_id}.mp3",
                timeout=30,
            )

            # 检查是否返回HTML页面（接口失效）
            if b"html" in response2.content[:100].lower():
                raise ValueError("旧接口返回 HTML 页面，非音频文件")

            with open(self.filename, "wb") as f:
                f.write(response2.content)
            print(f"[任务 {self.task_id}] 已使用旧接口解析方案")
            download_success = True

        except Exception as e:
            print(f"[任务 {self.task_id}] 旧接口失败: {e}，尝试VIP解析...")

            # 使用VIP解析接口
            if self.url and "data" in self.url and len(self.url["data"]) > 0:
                music_url = self.url["data"][0]["url"]
                response = requests.get(music_url, timeout=30)
                response.raise_for_status()

                with open(self.filename, "wb") as f:
                    f.write(response.content)
                print(f"[任务 {self.task_id}] 已使用VIP解析")
                download_success = True

        if not download_success:
            raise RuntimeError("音乐下载失败")

        # time.sleep(random.uniform(0.5, 1.5))  # 模拟网络延迟
        return self.lyric, self.name, self.picture_name, self.filename
    
class Cache_manager(QThread):
    cache_cleared = Signal(object)

    def __init__(self,filename,picture_path,key=None,):
        super().__init__()
        self.filename = filename
        self.picture_path = picture_path
        self.key = key

    def run(self):
        if os.path.exists(self.filename):
            if self.key == 'reload':
                try:
                    os.remove(self.filename)
                    print(f"已删除缓存文件: {self.filename}")
                except Exception as e:
                    print(f"删除缓存文件失败: {e}")

        elif os.path.exists(self.picture_path):
            if self.key == 'reload':
                try:
                    os.remove(self.picture_path)
                    print(f"已删除缓存图片: {self.picture_path}")
                except Exception as e:
                    print(f"删除缓存图片失败: {e}")

        elif self.key == 'delete_cache':
            root_path = Path(get_script_dir())
            cache_path = root_path / "cache" / "online_music"
            for file in cache_path.glob("*.*"):
                try:
                    os.remove(file)
                    print(f"已删除缓存文件: {file}")
                except Exception as e:
                    print(f"删除缓存文件失败: {e}")

        elif self.key == 'delete_image_cache':
            root_path = Path(get_script_dir())
            cache_path_2 = root_path / "cache" / "music_cover"
            for file in cache_path_2.glob("*.*"):
                try:
                    os.remove(file)
                    print(f"已删除缓存图片: {file}")
                except Exception as e:
                    print(f"删除缓存图片失败: {e}")

        self.cache_cleared.emit(self.filename)

class Api_163(QThread):
    search_finished = Signal(list)

    def __init__(self, keywords="", length=0, music_u_cookie=''):
        super().__init__()
        self.keywords = keywords
        self.length = length
        self.music_u_cookie = music_u_cookie
        self.cookies = {
            "MUSIC_U": self.music_u_cookie,  # 这里需要替换为实际的 MUSIC_U cookie 值
            "os": "pc",
            "appver": "8.9.75",
        }

    def run(self):
        print("搜索关键词:", self.keywords)
        print(api.search_music)
        self.songs = api.search_music(self.keywords, self.cookies, limit=100)
        if not self.songs:
            print("⚠️ 搜索无结果")
            self.search_finished.emit([])  # 或 emit 错误信息
            return

        if self.length >= len(self.songs):
            print(f"⚠️ 请求的索引 {self.length} 超出范围（共 {len(self.songs)} 首）")
            self.search_finished.emit([])
            return

        self.name = api.name_v1(self.songs[self.length]["id"])
        self.lyric = api.lyric_v1(self.songs[self.length]["id"], self.cookies)
        # self.url = api.url_v1(self.songs[self.length]["id"], "standard", self.cookies)
        # print('搜索结果:', self.songs)
        # print('歌曲信息:', self.name)
        # print('歌词信息:', self.lyric)
        self.search_finished.emit(self.songs)
        return self.songs, self.name, self.lyric


# | 音质名称（显示名） | 内部 level 标识 | 码率（kbps） | 音频格式 | 采样率/位深 | 所需会员 | 说明 |
# |------------------|----------------|-------------|----------|--------------|----------|------|
# | 标准音质 | `standard` | 128 kbps | MP3 / AAC | 44.1kHz / 16bit | 免费用户 | 基础音质，适合弱网或省流量 |
# | 较高音质 | `higher` | 192 kbps | MP3 / AAC | 44.1kHz / 16bit | 免费用户 | 清晰度提升，日常推荐 |
# | 极高音质 | `exhigh` 或 `lossless`（旧版） | 320 kbps | MP3 / AAC | 44.1kHz / 16bit | 普通 VIP | 主流高音质，接近 CD 水平 |
# | 无损音质 | `lossless` | ≈900–1411 kbps | FLAC | 44.1kHz / 16bit | SVIP | 无损压缩，保留原始细节 |
# | Hi-Res 音质 | `hires` | 可达 9216 kbps | FLAC | 96kHz/24bit 或 192kHz/24bit | SVIP | 超高清，支持 Hi-Res Audio 认证设备 |
# | 超清母带（Master） | `jyeffect` 或 `master` | ≈17.8 MB/min（≈2370 kbps） | FLAC | 192kHz / 24bit | SVIP | 母带级重制，还原录音室细节 |
# | 沉浸式空间音频 | `spatial` / `dolby` | 动态码率 | AAC / Dolby Atmos | 多声道（如 5.1） | SVIP + 支持设备 | 环绕声体验，需耳机/音响支持 |
class ChatDialog(QDialog, Ui_Dialog):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowFlags( Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.textEdit.setReadOnly(True)
        self.tabWidget.tabBar().hide()
        
        self.pushButton.setAutoDefault(False)
        self.pushButton_2.setAutoDefault(False)
        self.pushButton.clicked.connect(self.accept)
        self.pushButton_2.clicked.connect(self.reject) 
        self.maindialog = parent
        self.setWindowModality(Qt.ApplicationModal)
        # self.maindialog=MusicPlayerDialog()


    def accept(self):
        cookie_value = self.lineEdit.text().strip()
        if self.maindialog and hasattr(self.maindialog, 'lineEdit_163_usercookie'):
            
                # 更新配置文件
            config_path = get_config_path()
            config = configparser.ConfigParser()
            config.read(config_path, encoding='utf-8')
            if not cookie_value:
                return super().accept()  # 直接关闭对话框，不保存空值
            self.maindialog.lineEdit_163_usercookie.setText(cookie_value)
            global music_u_cookie
            music_u_cookie = cookie_value  # 更新全局变量
            if 'DEFAULT' not in config:
                config['DEFAULT'] = {}
            config['DEFAULT']['MUSIC_U_COOKIE'] = cookie_value
            with open(config_path, 'w', encoding='utf-8') as configfile:
                config.write(configfile)
        super().accept()
    def showEvent(self, event):
        """窗口显示时强制激活"""
        super().showEvent(event)
        self.activateWindow()
        self.raise_()
# first_cover = self.songs[0]['picUrl'] if self.songs else None

class ChatDialog_delete_cache(QDialog,Ui_Dialog_deletecache):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.textEdit.setReadOnly(True)
        self.textEdit.setText("此操作会永久删除所有音乐缓存文件，是否继续？")
        self.setWindowFlags( Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.pushButton.clicked.connect(self.accept)
        self.pushButton_2.clicked.connect(self.reject)
        self.maindialog = parent
        self.setWindowModality(Qt.ApplicationModal)
        self.tabWidget.tabBar().hide()

    def accept(self):
        self.chachemanager = Cache_manager(filename='',picture_path='',key='delete_cache')
        self.chachemanager.cache_cleared.connect(self.on_cache_cleared)
        self.pushButton.setEnabled(False)  # 禁用按钮，防止重复点击
        self.pushButton_2.setEnabled(False)
        if not self.chachemanager.isRunning():
            self.chachemanager.start()


    def on_cache_cleared(self, filename):
        print(f"缓存已清除: {filename}")
        self.pushButton.setEnabled(True)  # 重新启用按钮
        self.pushButton_2.setEnabled(True)
        super().accept()  # 关闭对话框

class ChatDialog_delete_image_cache(QDialog,Ui_Dialog_deletecache):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setupUi(self)
        
        self.textEdit.setReadOnly(True)
        self.textEdit.setText("此操作会永久删除所有音乐封面缓存文件，是否继续？")
        self.setWindowFlags( Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.pushButton.clicked.connect(self.accept)
        self.pushButton_2.clicked.connect(self.reject)
        self.maindialog = parent
        self.setWindowModality(Qt.ApplicationModal)
        self.tabWidget.tabBar().hide()

    def accept(self):
        self.chachemanager = Cache_manager(filename='',picture_path='',key='delete_image_cache')
        self.chachemanager.cache_cleared.connect(self.on_cache_cleared)
        self.pushButton.setEnabled(False)  # 禁用按钮，防止重复点击
        self.pushButton_2.setEnabled(False)
        if not self.chachemanager.isRunning():
            self.chachemanager.start()


    def on_cache_cleared(self, filename):
        print(f"缓存已清除: {filename}")
        self.pushButton.setEnabled(True)  # 重新启用按钮
        self.pushButton_2.setEnabled(True)
        super().accept()  # 关闭对话框

class LyricWindow(QWidget):
    def __init__(self):
        super().__init__()

        # 设置窗口属性：无边框、置顶、工具窗口、背景透明
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.resize(400, 80)

        # 歌词标签
        self.lyric_label = QLabel("等待歌词...", self)
        self.lyric_label.setAlignment(Qt.AlignCenter)
        self.lyric_label.setStyleSheet(
            """
            color: white;
            background-color: rgba(0, 0, 0, 160);
            border-radius: 8px;
            padding: 8px;
            border: 1px solid rgba(255, 255, 255, 50);
        """
        )
        font = QFont("Microsoft YaHei", 12, QFont.Bold)
        self.lyric_label.setFont(font)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.lyric_label)
        self.setLayout(layout)

        # 用于拖拽的变量
        self._dragging = False
        self._offset = QPoint()

    def update_lyric(self, text):
        self.lyric_label.setText(text)

    # ===== 拖拽支持 =====
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            
            self._dragging = True
            self._offset = event.position().toPoint()

    def mouseMoveEvent(self, event):
        if self._dragging:
            # 移动窗口：当前鼠标全局位置 - 初始点击偏移
            self.move(event.globalPosition().toPoint() - self._offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragging = False

    def musiclrcchange(self, current_time, lyrics):
        sectime = current_time / 1000.0  # 转为秒（float）
        current_lyric = ""
        for line in lyrics:
            if line[0] <= sectime:
                current_lyric = line[1]
        self.update_lyric(current_lyric)


class MusicPlayerDialog(QDialog, Ui_Daybreak_music):
    def __init__(self, folderpath=""):
        super().__init__()
        self.setupUi(self)
        self.setObjectName("DaybreakMusicWindow")
        self.setFixedSize(1400, 900)
        x=(1400-self.tabWidget.width())//2
        y=(900-self.tabWidget.height())//2
        self.tabWidget.move(x,y)
        
        self.setWindowIcon(QIcon('icon.ico'))
        self.lineEdit_163keywords.setPlaceholderText("回车以搜索网易云音乐. . .")
        # self.tabWidget.move(-2, -40)  # 初始位置，可以根据需要调整
        

        # self.root_dir = get_resource_path("assets/qss/style1.qss")
        # self.load_qss(self.root_dir)

        # self.root_dir=Path(get_script_dir())  # 获取打包后或脚本所在目录
        # self.qss_src = self.root_dir / "assets" / "qss" / "style1.qss"
        # print(f"QSS 文件路径: {self.qss_src}")
        # self.load_qss(self.qss_src)

        self.chatdialog = ChatDialog(parent=self)
        self.chatdialog_deletecache = ChatDialog_delete_cache(parent=self)
        # 连接按钮点击信号到槽函数
        self.listWidget.setFocusPolicy(Qt.NoFocus)
        self.onlinesearch_tablewidget.setFocusPolicy(Qt.NoFocus)
        self.setMouseTracking(True)



        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.border_radius = 15



        self.playmusic_control = 1
        self.rightfolderpath = []
        self.pushButton.clicked.connect(self.open_folder)
        self.listWidget.doubleClicked.connect(self.playmusic)
        self.listWidget.doubleClicked.connect(self.process_music)
        self.onlinesearch_tablewidget.doubleClicked.connect(self.process_music_2)
        self.listWidget.doubleClicked.connect(self.clickcolorset)
        self.folderpath = folderpath

        self.play_control = 0


        self.pushButton_playmusic.clicked.connect(self.playmusic_button)
        self.pushButton_playmusic_2.clicked.connect(self.playmusic_button_2)
        self.timeprocess = 0
        self.horizontalSlider_processbar.setRange(0, 0)
        self.horizontalSlider_processbar_2.setRange(0, 0)
        self.horizontalSlider_processbar.setValue(0)
        self.horizontalSlider_processbar_2.setValue(0)
        self.horizontalSlider_processbar.setEnabled(False)
        self.horizontalSlider_processbar_2.setEnabled(False)
        self.audio_output = QAudioOutput()

        self.index = 0

        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.audio_output)

        self.timer = QTimer()
        self.timer.timeout.connect(self.process_music)
        self.timer.timeout.connect(self.process_music_2)
        self.timer.start(10)  # 10 ms = 0.01 秒

        self.slider_is_being_dragged = False
        self.slider_is_being_dragged_2 = False

        self.horizontalSlider_processbar.sliderPressed.connect(self.on_slider_pressed)
        self.horizontalSlider_processbar_2.sliderPressed.connect(
            self.on_slider_pressed_2
        )
        self.horizontalSlider_processbar.sliderReleased.connect(self.musicseek)
        self.horizontalSlider_processbar_2.sliderReleased.connect(self.musicseek_2)


        self.verticalSlider_setvoice.setRange(0, 100)
        self.verticalSlider_setvoice.setValue(50)
        self.audio_output.setVolume(0.5)  # 初始音量为50
        self.verticalSlider_setvoice.valueChanged.connect(self.change_volume)
        self.verticalSlider_setvoice_2.setRange(0, 100)
        self.verticalSlider_setvoice_2.setValue(50)
        self.verticalSlider_setvoice_2.valueChanged.connect(self.change_volume_2)

        self.pushButton_beforesong.clicked.connect(self.beforesong)
        self.pushButton_nextsong.clicked.connect(self.nextsong)
        self.label_musicprocesstext.setText("00:00 / 00:00")
        self.label_musicprocesstext_2.setText("00:00 / 00:00")

        self.checkBox_lrcshow.stateChanged.connect(self.lrc_show_hide)
        self.lyric_window = LyricWindow()

        self.lrc_handler = lrcchange()

        self.current_lyrics = []  # 用于缓存当前歌曲的歌词
        self.lrc_handler.lyricsLoaded.connect(self.on_lyrics_loaded)
        self.listWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.listWidget.setColumnWidth(0, 500)
        self.listWidget.setColumnWidth(1, 200)
        self.listWidget.setColumnWidth(2, 109)
        self.listWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.listWidget.verticalHeader().setVisible(False)
        self.label_songname.setText("未选择")
        self.label_songname_2.setText("未选择")

        self.onlinesearch_tablewidget.setColumnWidth(0, 500)
        self.onlinesearch_tablewidget.setColumnWidth(1, 309)
        self.onlinesearch_tablewidget.setColumnWidth(2, 0)
        self.player.mediaStatusChanged.connect(self.on_media_status_changed_2)
        self.onlinesearch_tablewidget.horizontalHeader().setSectionResizeMode(
            QHeaderView.Interactive
        )
        self.onlinesearch_tablewidget.verticalHeader().setVisible(False)
        self.onlinesearch_tablewidget.clicked.connect(self.clickcolorset)

        self.pushButton_beforesong_2.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSkipBackward)
        )
        self.pushButton_nextsong_2.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSkipForward)
        )
        self.pushButton_beforesong_2.clicked.connect(self.beforesong_2)
        self.pushButton_nextsong_2.clicked.connect(self.nextsong_2)
        # 设置第0行高度为40像素
        self.listWidget.setRowHeight(0, 40)

        # 设置所有行高为30
        for row in range(self.listWidget.rowCount()):
            self.listWidget.setRowHeight(row, 30)

        # 更可靠的替代方案（视觉上接近）
        self.pushButton_beforesong.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSkipBackward)
        )
        self.pushButton_nextsong.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSkipForward)
        )
        self.pushButton_playmusic.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
        )

        self.pushButton_localmusicsearch.clicked.connect(
            lambda: self.tabWidget.setCurrentWidget(self.tab)
        )
        self.pushButton_internetmusicsearch.clicked.connect(
            lambda: self.tabWidget.setCurrentWidget(self.tab_2)
        )
        self.pushButton_localmusicsearch_2.clicked.connect(
            lambda: self.tabWidget.setCurrentWidget(self.tab)
        )
        self.pushButton_internetmusicsearch_2.clicked.connect(
            lambda: self.tabWidget.setCurrentWidget(self.tab_2)
        )
        self.pushButton_tab_music_settings.clicked.connect(lambda:self.tabWidget_2.setCurrentWidget(self.tab_4))
        self.pushButton_information.clicked.connect(lambda:self.tabWidget_2.setCurrentWidget(self.tab_5))
        self.pushButton_tab_music_settings_2.clicked.connect(lambda:self.tabWidget_2.setCurrentWidget(self.tab_4))
        self.pushButton_information_2.clicked.connect(lambda:self.tabWidget_2.setCurrentWidget(self.tab_5))
        self.lineEdit_163_usercookie.setEnabled(False)
        
        self.lineEdit_163keywords.returnPressed.connect(self.search_music)
        self.onlinesearch_tablewidget.doubleClicked.connect(self.playmusic_online)
        self.pushButton_settings.clicked.connect(lambda:self.tabWidget.setCurrentWidget(self.tab_3))
        self.pushButton_settings_2.clicked.connect(lambda:self.tabWidget.setCurrentWidget(self.tab_3))
        self.pushButton_internetmusicsearch_3.clicked.connect(lambda:self.tabWidget.setCurrentWidget(self.tab_2))
        self.pushButton_localmusicsearch_3.clicked.connect(lambda:self.tabWidget.setCurrentWidget(self.tab))
        self.tabWidget_2.tabBar().hide()  # 隐藏内层 tabWidget 的标签页
        self.tabWidget.tabBar().hide()  # 隐藏外层 tabWidget 的标签页
        self.pushButton_settings_addcookie.clicked.connect(self.open_addcookie_dialog)
        self.lineEdit_163_usercookie.setText(music_u_cookie)
        
        self.label_pictureload_2.setText("")
        self.label_pictureload.setText("")
        self.label_window_title_bar.setAttribute(Qt.WidgetAttribute.WA_Hover)
        self.label_window_title_bar_2.setAttribute(Qt.WidgetAttribute.WA_Hover)
        self.label_window_title_bar_3.setAttribute(Qt.WidgetAttribute.WA_Hover)
        self.pushButton_reloadonlinemusic.clicked.connect(self.reload_online_music)
        self.filename = ''
        self.picture_path = ''
        self.pushButton_delmusiccache.clicked.connect(self.del_music_cache)
        self.pushButton_delmusicimagecache.clicked.connect(self.del_music_image_cache)
        self.label_processbar_text.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.label_processbar_text_2.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self._disable_auto_default()
        self.del_music_image_cache_dialog = ChatDialog_delete_image_cache(parent=self)
        count = self.comboBox_playmode_qssload.count()
        try:
            target = int(theme) # 假设你想选最后一个
        except:
            target=0

        

        if 0 <= target < count:
            self.comboBox_playmode_qssload.setCurrentIndex(target)
            print("设置成功")
        else:
            print(f"设置失败！索引 {target} 超出范围 [0, {count-1}]")
        self.comboBox_playmode_qssload.currentIndexChanged.connect(self.read_gobal_qss)
        self.read_gobal_qss()




    def read_gobal_qss(self):

        self.tabWidget.setStyleSheet("")
        self.qss_mode=self.comboBox_playmode_qssload.currentIndex()
        config['DEFAULT']['THEME'] = str(self.qss_mode)
        with open(config_path, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
        if self.qss_mode==0:
            
            if get_bundle_dir() !=None:
                qss_path = get_resource_path("assets/qss/style1.qss")
                with open(qss_path,'r',encoding='utf-8') as f:
                    self.setStyleSheet(f.read())
            else:
                root_dir=Path(get_script_dir())
                qss_path=root_dir / 'assets' / 'qss' / 'style1.qss'
                with open(qss_path,'r',encoding='utf-8') as f:
                    self.setStyleSheet(f.read())
        elif self.qss_mode==1:
            
            self.setStyleSheet("")
        elif self.qss_mode==2:
            
            if get_bundle_dir() !=None:
                qss_path = get_resource_path("assets/qss/style2.qss")
                png_path=get_resource_path("assets/qss/dragon.png")
                with open(qss_path,'r',encoding='utf-8') as f:
                    self.setStyleSheet(f.read())
                # with open(qss_path_2,'r',encoding='utf-8') as f:
                #     self.chatdialog.setStyleSheet(f.read())
                #     self.chatdialog_deletecache.setStyleSheet(f.read())
                    
            else:
                root_dir=Path(get_script_dir())
                qss_path=root_dir / 'assets' / 'qss' / 'style2.qss'
                qss_path_2=root_dir / 'assets' / 'qss' / 'style2_chatdialog.qss'
                png_path=root_dir / 'assets' /'qss' /'dragon.png'
                with open(qss_path,'r',encoding='utf-8') as f:
                    self.setStyleSheet(f.read())
                # with open(qss_path_2,'r',encoding='utf-8') as f:
                #     self.chatdialog.setStyleSheet(f.read())
                #     self.chatdialog_deletecache.setStyleSheet(f.read())
            bg_image_path = str(png_path).replace('\\', '/')
            tab_background_style = f"""
            QTabWidget#tabWidget::pane {{
                border-image: url('{bg_image_path}');
                border: 1px solid #444466;
                border-radius: 8px;
                }}
                """

            self.tabWidget.setStyleSheet(tab_background_style)
            

        print(self.qss_mode)
        if get_bundle_dir() !=None:
            picture_zycdzyj_path=get_resource_path("assets/icon/zycdzyj.jpg")
            picture_qq_path=get_resource_path("assets/icon/qq.png")
            print(picture_zycdzyj_path)

        else:
            root_dir=Path(get_script_dir())
            picture_zycdzyj_path=root_dir / 'assets' / 'icon' / 'zycdzyj.jpg'
            picture_qq_path=root_dir / 'assets' / 'icon' / 'qq.png'
            print(picture_zycdzyj_path)

        picture_zycdzyj=QPixmap(picture_zycdzyj_path)
        qq_icon=QPixmap(picture_qq_path)
        self.label_qq.setPixmap(qq_icon)
        self.label_qq.setScaledContents(True)
        self.label_picture_zycdzyj.setPixmap(picture_zycdzyj)
        self.label_picture_zycdzyj.setScaledContents(True)
        font = QFont("Microsoft YaHei", 14)
        self.textEdit.setFont(font)



    def _disable_auto_default(self):
        for btn in self.findChildren(QPushButton):
            btn.setAutoDefault(False)
            btn.setDefault(False)
    def del_music_cache(self):
        self.chatdialog_deletecache.show()

    def del_music_image_cache(self):
        self.del_music_image_cache_dialog.show()

    def reload_online_music(self):
        if not self.filename or not self.picture_path:
            return
        self.cachemanager_reloadmusic = Cache_manager(self.filename,self.picture_path,key='reload')
        self.cachemanager_reloadmusic.cache_cleared.connect(self.on_cache_cleared)
        if hasattr(self, 'player') and self.player:
            self.player.stop()
            self.player.setSource("")
            # 确保不再访问后才删除
            self.pushButton_reloadonlinemusic.setEnabled(False)

            self.player = None

            self.player = QMediaPlayer()
            self.audio_output = QAudioOutput()
            self.player.setAudioOutput(self.audio_output)
            if not self.cachemanager_reloadmusic.isRunning():
                self.cachemanager_reloadmusic.start()

    def on_cache_cleared(self, filename):
        print(f"缓存已清除: {filename}")
        self.pushButton_reloadonlinemusic.setEnabled(True)
        self.playmusic_online()
    def keyPressEvent(self, event):
        # 拦截 ESC 键
        if event.key() == Qt.Key_Escape:
            event.ignore()
            return
        # 其他按键正常处理
        super().keyPressEvent(event)
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.label_window_title_bar.underMouse() or self.label_window_title_bar_2.underMouse() or self.label_window_title_bar_3.underMouse():
                self._dragging = True
                self._offset = event.position().toPoint()
            elif self.label_Minimize.underMouse() or self.label_Minimize_2.underMouse() or self.label_Minimize_3.underMouse():
                self.showMinimized()
            else:
                if self.label_close_window.underMouse() or self.label_close_window_2.underMouse() or self.label_close_window_3.underMouse():
                    self.close()
        return super().mousePressEvent(event)
    def mouseMoveEvent(self, event):
        if hasattr(self, '_dragging') and self._dragging:
            self.move(event.globalPosition().toPoint() - self._offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragging = False
            global_pos = event.globalPosition().toPoint()
            target_process = None 
            if self.horizontalSlider_processbar.underMouse():
                target_process=self.horizontalSlider_processbar
                
            elif self.horizontalSlider_processbar_2.underMouse():
                target_process=self.horizontalSlider_processbar_2

            if target_process:
                local_pos = target_process.mapFromGlobal(global_pos)
                mouse_x = local_pos.x()
                
                width = target_process.width()
                tolerance = 20
                if mouse_x < -tolerance or mouse_x > width + tolerance:
                    super().mouseReleaseEvent(event)
                    return
                clamped_x = max(0, min(width, mouse_x))

                if width > 0:
                    current_percent = clamped_x / width
                    current_percent = max(0.0, min(1.0, current_percent))
                    duration = self.player.duration()
                    if duration > 0:
                        target_position = int(duration * current_percent)
                        self.player.setPosition(target_position)
                # mouse_x = event.position().x() 
                # try:
                #     current_percent=mouse_x / self.horizontalSlider_processbar.width()
                # except:
                #     current_percent=mouse_x / self.horizontalSlider_processbar_2.width()
                # if current_percent is not None:
                #     duration = self.player.duration()
                #     target_position = int(duration * current_percent)
                #     self.player.setPosition(target_position)
                #     print("debug")




            
            

    def open_addcookie_dialog(self):
        self.chatdialog.show()
        result = self.chatdialog.exec()
        if result == QDialog.Accepted:
            print("用户点击了确定")
        else:
            print("用户点击了取消")

    def playmusic_online(self):
        length = self.onlinesearch_tablewidget.currentRow()
        if not self.songs:
            QMessageBox.warning(self, "错误", "请先搜索歌曲")
            return

        song_id = self.songs[length]["id"]
        task_id = f"{song_id}_{int(time.time() * 1000)}"
        self.current_play_task_id = task_id
        music_u=self.lineEdit_163_usercookie.text().strip()
        task = OnlineMusic_get(music_id=song_id, music_u_cookie=music_u, task_id=task_id)
        task.signal_emitter.online_music_geted.connect(self.play_online_music)
        task.signal_emitter.cover_ready.connect(self.music_image_load)
        pool.start(task)

    def play_online_music(self, task_id, filename):
        self.filename = filename
        # print(f"任务ID: {self.current_play_task_id}")
        # print(f"文件路径: {filename}")
        # print(f"任务 ID: {task_id}")
        # print(f"文件存在: {os.path.exists(filename)}")
        # print(f"文件大小: {os.path.getsize(filename) if os.path.exists(filename) else 0} 字节")

        url = QUrl.fromLocalFile(filename)
        self.player.setSource(url)

        self.player.play()
        self.pushButton_playmusic_2.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause)
        )

        self.label_songname_2.setText(
            self.onlinesearch_tablewidget.item(
                self.onlinesearch_tablewidget.currentRow(), 0
            ).text()
        )
        self.label_songname.setText(self.label_songname_2.text())
        # self.player.mediaStatusChanged.connect(self.on_media_status_changed_2)
    #     self.player.positionChanged.connect(self.on_position_changed)

    # def on_position_changed(self, position):
    #     if self.player.duration() > 0:
    #         self.horizontalSlider_processbar.setRange(0, self.player.duration())
    #         self.horizontalSlider_processbar.setValue(position)
    #         self.horizontalSlider_processbar_2.setRange(0, self.player.duration())
    #         self.horizontalSlider_processbar_2.setValue(position)

    def search_music(self):
        keywords = self.lineEdit_163keywords.text().strip()
        music_u=self.lineEdit_163_usercookie.text().strip()
        self.api_thread = Api_163(keywords,music_u_cookie=music_u)
        if hasattr(self, "api_thread") and self.api_thread.isRunning():
            QMessageBox.information(self, "提示", "搜索正在进行，请稍后再试")
            return
        self.api_thread.search_finished.connect(self.on_search_finished)

        self.lineEdit_163keywords.setEnabled(False)
        self.api_thread.start()

    def music_image_load(self, picture_path):
        self.picture_path = picture_path
        if not os.path.exists(picture_path):
            return

        # 1. 加载原始图片
        original_pixmap = QPixmap(picture_path)
        if original_pixmap.isNull():
            return

        # 2. 设置目标尺寸（Label 的大小）
        target_width = self.label_pictureload_2.width()
        target_height = self.label_pictureload_2.height()

        # 如果 Label 尺寸为 0，使用默认值
        if target_width <= 0 or target_height <= 0:
            target_width = 300
            target_height = 300

        # 3. 裁剪并缩放图片（核心代码）
        cropped_pixmap = self.crop_pixmap_center(
            original_pixmap, target_width, target_height
        )

        # 4. 设置到 Label
        self.label_pictureload_2.setPixmap(cropped_pixmap)
        self.label_pictureload_2.setAlignment(Qt.AlignCenter)
        self.label_pictureload.setPixmap(cropped_pixmap)
        self.label_pictureload.setAlignment(Qt.AlignCenter)

    def crop_pixmap_center(self, pixmap, target_width, target_height):
        """
        从图片中心裁剪并缩放到目标尺寸
        保持宽高比，裁剪多余部分
        """
        if pixmap.isNull():
            return pixmap

        # 原始尺寸
        src_width = pixmap.width()
        src_height = pixmap.height()

        # 计算缩放比例（取较大的比例，确保覆盖整个目标区域）
        scale_ratio = max(target_width / src_width, target_height / src_height)

        # 缩放后的尺寸
        scaled_width = int(src_width * scale_ratio)
        scaled_height = int(src_height * scale_ratio)

        # 缩放图片
        scaled_pixmap = pixmap.scaled(
            scaled_width, scaled_height, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )

        # 计算裁剪区域（从中心裁剪）
        x = (scaled_width - target_width) // 2
        y = (scaled_height - target_height) // 2

        # 裁剪
        cropped_pixmap = scaled_pixmap.copy(x, y, target_width, target_height)

        return cropped_pixmap

    def on_search_finished(self, songs):
        self.songs = songs
        self.lineEdit_163keywords.setEnabled(True)
        table = self.onlinesearch_tablewidget
        table.setRowCount(0)  # 清空

        for i, song in enumerate(songs):
            table.insertRow(i)
            table.setItem(i, 0, QTableWidgetItem(song.get("name", "")))
            table.setItem(i, 1, QTableWidgetItem(song.get("artists", "")))

    def on_lyrics_loaded(self, lyrics):
        self.current_lyrics = lyrics
        # if not lyrics:
        #     self.current_lyrics = [[0.0,'未找到歌词或歌词文件损坏']]
        # print("歌词加载完成:", lyrics)
        if lyrics == []:
            self.current_lyrics = [[0.0, "未找到歌词或歌词文件损坏"]]

    def change_volume_2(self):
        volume = self.verticalSlider_setvoice_2.value() / 100.0
        self.audio_output.setVolume(volume)

    def change_volume(self):
        volume = self.verticalSlider_setvoice.value() / 100.0
        self.audio_output.setVolume(volume)

    def load_qss(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                qss = f.read()
                self.setStyleSheet(qss)
        except Exception as e:
            print(f"加载 QSS 文件失败: {e}")

    def _detect_image_format(self, data):
        try:
            img = Image.open(BytesIO(data))
            fmt = img.format.lower()
            return ".jpg" if fmt == "jpeg" else f".{fmt}"

        except Exception as e:
            print(f"无法识别图片格式, 使用默认 '.jpg': {e}")
            return ".jpg"

    def nextsong(self):
        if self.listWidget.currentRow() < self.listWidget.rowCount() - 1:
            self.listWidget.setCurrentCell((self.listWidget.currentRow() + 1), 0)
            url = QUrl.fromLocalFile(self.rightfolderpath[self.listWidget.currentRow()])
            self.player.setSource(url)
            self.player.play()
            self.play_control = 1
            self.label_songname.setText(
                self.listWidget.item(self.listWidget.currentRow(), 0).text()
            )
            self.label_songname_2.setText(self.label_songname.text())
            self.song_picture()
        else:

            url = QUrl.fromLocalFile(self.rightfolderpath[self.listWidget.currentRow()])
            self.listWidget.setCurrentCell(
                (self.listWidget.currentRow() - self.listWidget.rowCount()), 0
            )
            self.player.setSource(url)
            self.player.play()
            self.play_control = 1
        self.label_songname.setText(
            self.listWidget.item(self.listWidget.currentRow(), 0).text()
        )
        self.label_songname_2.setText(self.label_songname.text())
        self.song_picture()

    def song_picture(self):
        try:
            audio_path = self.rightfolderpath[self.listWidget.currentRow()]
        except IndexError:
            self.label_pictureload.clear()  # 清空封面
            return

        try:
            audio = File(audio_path)
        except Exception as e:
            print(f"无法读取音频文件: {e}")
            self.label_picture.clear()
            return

        if audio is None:
            self.label_picture.clear()
            return

        cover_data = None

        # ====== 提取封面数据（保持原逻辑）======
        if audio.__class__.__name__ == "MP3":
            if hasattr(audio, "tags") and audio.tags:
                apic_list = [
                    tag for tag in audio.tags.values() if isinstance(tag, APIC)
                ]
                if apic_list:
                    cover_data = apic_list[0].data

        elif audio.__class__.__name__ == "FLAC":
            if audio.pictures:
                cover_data = audio.pictures[0].data

        elif audio.__class__.__name__ in ("OggVorbis", "OggOpus"):
            if "metadata_block_picture" in audio:
                b64_pic = audio["metadata_block_picture"][0]
                try:
                    cover_data = base64.b64decode(b64_pic)
                except Exception as e:
                    print(f"Base64 解码失败: {e}")

        elif audio.__class__.__name__ == "MP4":
            if "covr" in audio:
                cover_data = bytes(audio["covr"][0])

        # ====== 直接从内存加载到 QPixmap ======
        if cover_data:
            pixmap = QPixmap()
            pixmap.loadFromData(cover_data)
            if not pixmap.isNull():
                # 缩放以适应 label（可选）
                scaled_pixmap = pixmap.scaled(
                    self.label_pictureload.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
                self.label_pictureload.setPixmap(scaled_pixmap)
                self.label_pictureload_2.setPixmap(scaled_pixmap)
                self.label_pictureload_2.setAlignment(Qt.AlignCenter)
                
                return

        # 若无封面，显示默认图或清空
        self.label_pictureload_2.clear()
        self.label_pictureload.clear()  # 或 setPixmap(QPixmap("default_cover.png"))
        
    def beforesong(self):
        if self.listWidget.currentRow() > 0:
            self.listWidget.setCurrentCell((self.listWidget.currentRow() - 1), 0)
            url = QUrl.fromLocalFile(self.rightfolderpath[self.listWidget.currentRow()])
            self.player.setSource(url)
            self.player.play()
            self.play_control = 1
        else:
            url = QUrl.fromLocalFile(self.rightfolderpath[self.listWidget.currentRow()])
            self.listWidget.setCurrentCell((self.listWidget.rowCount() - 1), 0)
            self.player.setSource(url)
            self.player.play()
            self.play_control = 1

        self.label_songname.setText(
            self.listWidget.item(self.listWidget.currentRow(), 0).text()
        )
        self.label_songname_2.setText(self.label_songname.text())
        self.song_picture()

    def beforesong_2(
        self,
    ):
        current_row = self.onlinesearch_tablewidget.currentRow()
        total_rows = self.onlinesearch_tablewidget.rowCount()

        # 安全检查：没有歌曲或未选中任何行
        if total_rows == 0:
            return
        if current_row == -1:  # 无选中项
            current_row = 0  # 或者 return，根据需求

        # 计算上一首的目标行号（循环）
        if current_row > 0:
            target_row = current_row - 1
        else:
            target_row = total_rows - 1  # 回到最后一首

        # 更新表格选中项
        self.onlinesearch_tablewidget.setCurrentCell(target_row, 0)

        # 获取对应歌曲 ID 并启动在线获取
        song_id = self.songs[target_row]["id"]
        self.songs_url = OnlineMusic_get(song_id)
        self.playmusic_online()
        self.play_control = 1

    def on_slider_pressed_2(self):
        self.slider_is_being_dragged_2 = True
        self.slider_is_being_dragged = True  # 同时设置另一个标志，确保在拖动过程中不更新进度条

    def musicseek_2(self):
        new_position = self.horizontalSlider_processbar_2.value()
        print (new_position)
        self.player.setPosition(new_position)
        self.slider_is_being_dragged_2 = False
        self.slider_is_being_dragged = False  # 确保两个标志都重置

    def nextsong_2(self):
        current_row = self.onlinesearch_tablewidget.currentRow()
        total_rows = self.onlinesearch_tablewidget.rowCount()

        # 安全检查：没有歌曲或表格为空
        if total_rows == 0:
            return
        if current_row == -1:  # 无选中项，默认从第一首开始
            current_row = 0

        # 计算下一首的目标行号（循环）
        if current_row < total_rows - 1:
            target_row = current_row + 1
        else:
            target_row = 0  # 回到第一首

        # 更新表格选中项
        self.onlinesearch_tablewidget.setCurrentCell(target_row, 0)

        # 获取对应歌曲 ID 并启动在线获取
        song_id = self.songs[target_row]["id"]
        self.songs_url = OnlineMusic_get(song_id)
        self.playmusic_online()
        self.play_control = 1

    def open_folder(self):
        # 打开文件夹选择对话框
        self.folderpath = QFileDialog.getExistingDirectory(
            self,
            "选择音乐文件夹",
            "",  # 起始目录，可设为 "C:/" 或上次路径
            QFileDialog.ShowDirsOnly,
        )
        if not self.folderpath:
            return  # 用户取消选择
        if self.folderpath:
            self.listWidget.clearContents()
            self.listWidget.setRowCount(0)  # 设置行数为 0
            self.rightfolderpath = []
            print("选中的文件夹路径:", self.folderpath)
            for c in os.listdir(self.folderpath):
                if c.endswith(
                    (".mp3", ".wav", ".flac", ".ogg", "mgg", "mflac")
                ):  # 支持的音乐文件格式
                    print("找到音乐文件:", os.path.join(self.folderpath, c))
                    self.rightfolderpath.append(os.path.join(self.folderpath, c))
                else:
                    print("非音乐文件，跳过:", os.path.join(self.folderpath, c))

            for path in self.rightfolderpath:
                row_position = self.listWidget.rowCount()
                self.listWidget.insertRow(row_position)

                filename = os.path.basename(path)
                self.listWidget.setItem(row_position, 0, QTableWidgetItem(filename))

                audio = File(path)
                if audio:
                    # 获取时长
                    duration = (
                        int(audio.info.length) if hasattr(audio.info, "length") else 0
                    )
                    minutes, seconds = divmod(duration, 60)
                    self.listWidget.setItem(
                        row_position, 1, QTableWidgetItem(f"{minutes:02}:{seconds:02}")
                    )

                    # 获取标签的辅助 lambda
                    get_tag = lambda tag: (
                        audio.tags.get(tag, [None])[0]
                        if audio.tags and tag in audio.tags
                        else None
                    )

                    # 修复：不要用不存在的 get_path_safe
                    artist = get_tag("artist") or get_tag("TPE1") or "未知作者"
                    title = (
                        get_tag("title")
                        or get_tag("TIT2")
                        or os.path.splitext(filename)[0]
                    )

                    self.listWidget.setItem(row_position, 1, QTableWidgetItem(artist))
                    self.listWidget.setItem(
                        row_position, 2, QTableWidgetItem(f"{minutes:02}:{seconds:02}")
                    )
                    # self.listWidget.setItem(row_position, 3, QTableWidgetItem(title))

                else:
                    print("无法读取音频文件")

    def playmusic_button(self):
        self.playmusic_control += 1
        if self.playmusic_control == 2:
            self.player.pause()
            self.pushButton_playmusic.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
            )
            self.playmusic_control = 0
        else:
            try:
                self.player.play()
                self.pushButton_playmusic.setIcon(
                    self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause)
                )
            except:
                self.on_media_status_changed(QMediaPlayer.Error)
            self.playmusic_control = 1

    def playmusic_button_2(self):
        self.playmusic_control += 1
        if self.playmusic_control == 2:
            self.player.pause()
            self.pushButton_playmusic_2.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
            )
            self.playmusic_control = 0
        else:
            try:
                self.player.play()
                self.pushButton_playmusic_2.setIcon(
                    self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause)
                )
            except Exception as e:
                self.on_media_status_changed_2(QMediaPlayer.Error)
            self.playmusic_control = 1

    def clickcolorset(self):
        table = self.listWidget
        table.show()

        for col in range(self.listWidget.columnCount()):
            for row in range(self.listWidget.rowCount()):
                item = self.listWidget.item(row, col)
                if item:
                    item.setForeground(QColor("black"))
        item = self.listWidget.currentItem()
        if item:
            item.setForeground(QColor("red"))

    def playmusic(self):
        url = QUrl.fromLocalFile(self.rightfolderpath[self.listWidget.currentRow()])
        self.player.setSource(url)
        self.player.play()
        self.pushButton_playmusic.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause)
        )
        self.label_songname.setText(
        self.listWidget.item(self.listWidget.currentRow(), 0).text()
        )
        self.label_songname_2.setText(self.label_songname.text())
        self.song_picture()


    def process_music_2(self):
        self.horizontalSlider_processbar_2.setEnabled(True)
        try:
            duration = self.player.duration()  # 获取音乐总时长（毫秒）
            position = self.player.position()  # 获取当前播放位置（毫秒）
        except:
            duration = 0
            position = 0
        if self.slider_is_being_dragged or self.slider_is_being_dragged_2:
            return
        else:
            self.horizontalSlider_processbar_2.setRange(0, duration)
            self.horizontalSlider_processbar_2.setValue(position)
            self.horizontalSlider_processbar.setRange(0, duration)
            self.horizontalSlider_processbar.setValue(position)

        totall_seconds = duration // 1000
        current_seconds = position // 1000

        totall_minutes = totall_seconds // 60
        totall_seconds = totall_seconds % 60
        current_minutes = current_seconds // 60
        current_seconds = current_seconds % 60
        self.label_musicprocesstext_2.setText(
            f"{current_minutes:02}:{current_seconds:02} / {totall_minutes:02}:{totall_seconds:02}"
        )
        self.lyric_window.musiclrcchange(position, self.current_lyrics)

    def process_music(self):
        self.horizontalSlider_processbar.setEnabled(True)
        try:
            duration = self.player.duration()  # 获取音乐总时长（毫秒）
            position = self.player.position()  # 获取当前播放位置（毫秒）
        except:
            duration = 0
            position = 0
        if self.slider_is_being_dragged or self.slider_is_being_dragged_2:
            return
        else:
            self.horizontalSlider_processbar.setRange(0, duration)
            self.horizontalSlider_processbar.setValue(position)
            self.horizontalSlider_processbar_2.setRange(0, duration)
            self.horizontalSlider_processbar_2.setValue(position)

        totall_seconds = duration // 1000
        current_seconds = position // 1000

        totall_minutes = totall_seconds // 60
        totall_seconds = totall_seconds % 60
        current_minutes = current_seconds // 60
        current_seconds = current_seconds % 60
        self.label_musicprocesstext.setText(
            f"{current_minutes:02}:{current_seconds:02} / {totall_minutes:02}:{totall_seconds:02}"
        )
        self.lyric_window.musiclrcchange(position, self.current_lyrics)

    def on_slider_pressed(self):
        self.slider_is_being_dragged = True
        self.slider_is_being_dragged_2 = True

    def musicseek(self):
        new_position = self.horizontalSlider_processbar.value()
        self.player.setPosition(new_position)
        self.slider_is_being_dragged = False
        self.slider_is_being_dragged_2 = False

    def on_media_status_changed_2(self, status):
        if status != QMediaPlayer.EndOfMedia:
            return

        self.index_2 = self.comboBox_playmode_2.currentIndex()

        # 根据播放模式更新选中行
        if self.index_2 == 0:  # 顺序播放
            if (
                self.onlinesearch_tablewidget.currentRow()
                < self.onlinesearch_tablewidget.rowCount() - 1
            ):
                self.onlinesearch_tablewidget.setCurrentCell(
                    self.onlinesearch_tablewidget.currentRow() + 1, 0
                )
            else:
                self.onlinesearch_tablewidget.setCurrentCell(0, 0)

        elif self.index_2 == 1:  # 逆序播放
            if self.onlinesearch_tablewidget.currentRow() > 0:
                self.onlinesearch_tablewidget.setCurrentCell(
                    self.onlinesearch_tablewidget.currentRow() - 1, 0
                )
            else:
                last_index = self.onlinesearch_tablewidget.rowCount() - 1
                self.onlinesearch_tablewidget.setCurrentCell(last_index, 0)

        elif self.index_2 == 2:  # 循环播放
            # 当前行不变
            pass

        elif self.index_2 == 3:  # 随机播放
            random_index = random.randint(
                0, self.onlinesearch_tablewidget.rowCount() - 1
            )
            self.onlinesearch_tablewidget.setCurrentCell(random_index, 0)

        # 直接调用 playmusic_online() ← 统一入口
        self.playmusic_online()

    def on_media_status_changed(self, status):

        self.index = self.comboBox_playmode.currentIndex()

        if status == QMediaPlayer.EndOfMedia:
            if self.index == 0:  # 顺序播放
                if self.listWidget.currentRow() < self.listWidget.rowCount() - 1:
                    self.listWidget.selectRow(self.listWidget.currentRow() + 1)
                    url = QUrl.fromLocalFile(
                        self.rightfolderpath[self.listWidget.currentRow()]
                    )
                    self.player.setSource(url)
                    try:
                        self.player.play()
                    except Exception as e:
                        self.on_media_status_changed(QMediaPlayer.Error)
                        print("播放音乐时出错:", e)
                else:

                    url = QUrl.fromLocalFile(
                        self.rightfolderpath[self.listWidget.currentRow()]
                    )
                    self.listWidget.selectRow(
                        self.listWidget.currentRow() - self.listWidget.rowCount()
                    )
                    self.player.setSource(url)
                    self.player.play()
            elif self.index == 1:  # 逆序播放
                if self.listWidget.currentRow() > 0:
                    self.listWidget.selectRow(self.listWidget.currentRow() - 1)
                    url = QUrl.fromLocalFile(
                        self.rightfolderpath[self.listWidget.currentRow()]
                    )
                    self.player.setSource(url)
                    try:
                        self.player.play()
                    except:
                        self.on_media_status_changed(status)

                else:

                    url = QUrl.fromLocalFile(
                        self.rightfolderpath[self.listWidget.currentRow()]
                    )
                    self.listWidget.selectRow(self.listWidget.rowCount() - 1)
                    self.player.setSource(url)
                    try:
                        self.player.play()
                    except:
                        self.on_media_status_changed(QMediaPlayer.Error)

            elif self.index == 2:  # 循环播放
                url = QUrl.fromLocalFile(
                    self.rightfolderpath[self.listWidget.currentRow()]
                )
                self.player.setSource(url)
                try:
                    self.player.play()
                except:
                    self.on_media_status_changed(QMediaPlayer.Error)

            elif self.index == 3:  # 随机播放
                random_index = random.randint(0, self.listWidget.rowCount() - 1)
                self.listWidget.selectRow(random_index)
                url = QUrl.fromLocalFile(
                    self.rightfolderpath[self.listWidget.currentRow()]
                )
                self.player.setSource(url)
                try:
                    self.player.play()
                except:
                    self.on_media_status_changed(QMediaPlayer.Error)
        audio_path = self.rightfolderpath[self.listWidget.currentRow()]
        try:
            self.lrcpath = (
                audio_path.rsplit(".", 1)[0] + ".lrc"
            )  # 假设歌词文件与音频文件同名但扩展名为 .lrc
        except:
            print("获取歌词路径失败")

        self.lrc_handler.set_path(self.lrcpath)
        if not self.lrc_handler.isRunning():
            self.lrc_handler.start()
            # 因为 一个 QThread 实例在其生命周期中只能 start() 一次。如果你在它还在运行时再次调用 start()，Qt 会抛出警告甚至引发未定义行为。
        self.playmusic_control = 1
        self.label_songname.setText(
            self.listWidget.item(self.listWidget.currentRow(), 0).text()
        )
        self.label_songname_2.setText(self.label_songname.text())
        self.song_picture()

    def lrc_show_hide(self):
        if self.checkBox_lrcshow.isChecked():
            self.lyric_window.show()
        else:
            self.lyric_window.hide()
            # self.listWidget.setCurrentRow(self.listWidget.currentRow()+1)
            # url = QUrl.fromLocalFile(self.rightfolderpath[self.listWidget.currentRow()])
            # self.player.setSource(url)
            # self.player.play()


class lrcchange(QThread):
    lyricsLoaded = Signal(list)

    def __init__(self):
        super().__init__()
        self.lrcpath = ""

    def set_path(self, path):
        self.lrcpath = path

    def run(self):
        lyric_list = []
        content = ""
        try:
            # 先尝试 UTF-8
            try:
                with open(self.lrcpath, encoding="utf-8") as f:
                    content = f.read()
                    print("歌词文件以 UTF-8 编码读取成功")
            except FileNotFoundError:
                print("歌词文件未找到")
                self.lyricsLoaded.emit([])
                return

        except UnicodeDecodeError:
            try:
                # 回退到 GBK / GB18030（支持更多中文字符）
                with open(self.lrcpath, encoding="gb18030") as f:
                    content = f.read()
                    print("歌词文件以 GB18030 编码读取成功")
            except Exception as e2:
                print(f"歌词文件编码无法识别（UTF-8/GB18030均失败）: {e2}")
                self.lyricsLoaded.emit([])
                return
        except Exception as e:
            print(f"读取歌词文件失败: {e}")
            self.lyricsLoaded.emit([])
            return

        try:
            subs = pylrc.parse(content)
            lyric_list = [(sub.time, sub.text) for sub in subs]
        except Exception as e:
            print(f"解析 LRC 失败: {e}")
            lyric_list = []

        self.lyricsLoaded.emit(lyric_list)
        # 在 PySide6（以及 Qt 框架）中，emit() 是信号（Signal） 的触发方法，用于从一个对象（通常是工作线程）向其他对象（通常是主线程中的 UI 组件）发送数据或通知。


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MusicPlayerDialog()
    window.show()
    sys.exit(app.exec())
    
