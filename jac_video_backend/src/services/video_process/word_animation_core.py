from moviepy import *
from moviepy.video.VideoClip import VideoClip
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
import os
import math
import time
import tempfile
import requests
from urllib.parse import urlparse

class WordAnimationGenerator:
    def __init__(self,
                 title,                         # 视频标题
                 center_word,                   # 中心词
                 center_word_romaji,            # 中心词罗马音
                 center_word_chinese,           # 中心词中文翻译
                 surrounding_words,             # 周围单词列表（6个）
                 surrounding_words_romaji,      # 周围单词罗马音列表（6个）
                 surrounding_words_chinese,     # 周围单词中文翻译列表（6个）
                 fps=25,                        # 视频帧率
                 resolution="720p",             # 分辨率
                 aspect_ratio="16:9",           # 宽高比
                 orientation="portrait",         # 方向：portrait或landscape
                 background_color=(0,255,255),  # 背景颜色(BGR)
                 text_color=(0,0,0),            # 文字颜色(BGR)
                 background_image=None,         # 背景图片径
                 background_opacity=0.5,        # 背景图片透明度
                 background_music=None,         # 背景音乐路径
                 music_volume=1.0,              # 背景音乐音量
                 pronunciation_folder="./pronunciation",  # 发音文件夹路径
                 fonts=None,  # 字体配置
                 ):
        # 保存标题
        self.title = title
        
        # 验证输入的单词数量
        if len(surrounding_words) != 6 or len(surrounding_words_romaji) != 6 or len(surrounding_words_chinese) != 6:
            raise ValueError("周围单词、罗马音和中文翻译必须各是6个")
            
        # 保存单词、罗马音和中文翻译
        self.center_word = center_word
        self.center_word_romaji = center_word_romaji
        self.center_word_chinese = center_word_chinese
        self.surrounding_words = surrounding_words
        self.surrounding_words_romaji = surrounding_words_romaji
        self.surrounding_words_chinese = surrounding_words_chinese
        
        # 保存其他配置
        self.fps = fps
        self.background_color = background_color
        self.text_color = text_color
        self.background_image = background_image
        self.background_opacity = background_opacity
        self.background_music = background_music
        self.music_volume = music_volume
        self.pronunciation_folder = pronunciation_folder
        self.font_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
        
        # 确保字体目录存在
        if not os.path.exists(self.font_dir):
            os.makedirs(self.font_dir)
            print(f"已创建字体目录: {self.font_dir}")
            print("请将以下字体文件复制到该目录:")
            print("1. msyh.ttc (微软雅黑)")
            print("2. YuGothR.ttc 或 msgothic.ttc (日语字体)")
            print("3. arial.ttf (Arial)")
        
        # 定义字体文件名和备选字体
        self.font_files = {
            'title': ['msyh.ttc', 'simhei.ttf', 'MSYH.TTC'],
            'japanese': ['YuGothR.ttc', 'msgothic.ttc', 'YuGothM.ttc', 'yugothic.ttf'],
            'romaji': ['arial.ttf', 'ARIAL.TTF', 'helvetica.ttf'],
            'chinese': ['msyh.ttc', 'simhei.ttf', 'MSYH.TTC']
        }
        
        # 设置默认字体路径
        self.fonts = fonts or {}
        for font_type in ['title', 'japanese', 'romaji', 'chinese']:
            if font_type not in self.fonts:
                # 尝试找到第一个存在的字体文件
                font_found = False
                for font_file in self.font_files[font_type]:
                    font_path = os.path.join(self.font_dir, font_file)
                    if os.path.exists(font_path):
                        self.fonts[font_type] = font_path
                        font_found = True
                        break
                if not font_found:
                    # 如果没有找到字体，使用第一个字体文件名作为默认值
                    self.fonts[font_type] = os.path.join(self.font_dir, self.font_files[font_type][0])
        
        # 检查字体文件是否存在
        self.check_fonts()

        # 计算视频尺寸
        height = int(resolution.replace("p", ""))
        ratio_w, ratio_h = map(int, aspect_ratio.split(":"))
        width = int(height * ratio_w / ratio_h)
        
        # 处理方向
        if orientation.lower() == "portrait":
            width, height = height, width
            
        self.width = width
        self.height = height

        # 添加字体警告记录，避免重复警告
        self.font_warnings = set()
        # 添加实际使用的字体记录
        self.active_fonts = {}

        # 将RGB转换为BGR用于OpenCV
        self.text_color = (text_color[2], text_color[1], text_color[0])
        self.background_color = (background_color[2], background_color[1], background_color[0])

    def check_fonts(self):
        """检查字体文件是否存在，并提供复制命令"""
        missing_fonts = []
        for font_type, font_path in self.fonts.items():
            if not os.path.exists(font_path):
                missing_fonts.append((font_type, font_path))
        
        if missing_fonts:
            print("\n缺少以下字体文件:")
            print("请从系统字体目录复制以下文件到", self.font_dir)
            print("\nWindows 系统:")
            for font_type, font_path in missing_fonts:
                print(f"\n{font_type} 字体可用选项:")
                for font_file in self.font_files[font_type]:
                    print(f"copy \"%SystemRoot%\\Fonts\\{font_file}\" \"{self.font_dir}\\{font_file}\"")
            
            print("\nmacOS 系统:")
            for font_type, font_path in missing_fonts:
                print(f"\n{font_type} 字体可用选项:")
                for font_file in self.font_files[font_type]:
                    print(f"cp \"/System/Library/Fonts/{font_file}\" \"{self.font_dir}\"")
            
            print("\n如果系统中没有这些字体，可以从以下位置获取替代字体:")
            print("1. 微软雅黑 (msyh.ttc) 或思源黑体:")
            print("   - Windows系统自带")
            print("   - 或下载思源黑体: https://github.com/adobe-fonts/source-han-sans/releases")
            print("2. 日语字体 (YuGothR.ttc 或 msgothic.ttc):")
            print("   - Windows 10系统自带")
            print("   - 或下载思源黑体日文版")
            print("3. Arial (arial.ttf):")
            print("   - Windows系统自带")
            print("   - 或下载 Liberation Sans: https://github.com/liberationfonts/liberation-fonts/releases")

    def calculate_positions(self):
        """计算单词位置"""
        # 将中心词位置下移一点
        center = (self.width // 2, self.height * 0.5)  # 改为正中心
        
        # 计算六边形布局的位置
        radius_x = self.width * 0.35  # 横向半径
        radius_y = self.height * 0.3  # 增加纵向半径，让分布更均匀
        
        positions = {
            'title': (self.width // 2, self.height * 0.05),  # 标题位置改为距离顶部5%
            'top': (self.width // 2, center[1] - radius_y),  # 正上方
            'top_right': (center[0] + radius_x, center[1] - radius_y * 0.5),  # 右上
            'top_left': (center[0] - radius_x, center[1] - radius_y * 0.5),   # 左上
            'bottom_right': (center[0] + radius_x, center[1] + radius_y * 0.5),  # 右下
            'bottom_left': (center[0] - radius_x, center[1] + radius_y * 0.5),   # 左下
            'bottom': (self.width // 2, center[1] + radius_y)  # 正下方
        }
        
        return center, positions

    def try_load_font(self, font_type, font_size):
        """尝试加载字体，并记录使用的字体"""
        # 如果已经成功加载过这个类型的字体，直接返回
        if font_type in self.active_fonts:
            return ImageFont.truetype(self.active_fonts[font_type], font_size)

        # 尝试加载的字体
        try:
            font = ImageFont.truetype(self.fonts[font_type], font_size)
            self.active_fonts[font_type] = self.fonts[font_type]
            return font
        except:
            if font_type not in self.font_warnings:
                print(f"警告：未找到字体 {os.path.basename(self.fonts[font_type])}，尝试使用备选字体")
                self.font_warnings.add(font_type)
            
            # 尝试备选字体
            for font_file in self.font_files[font_type]:
                try:
                    font_path = os.path.join(self.font_dir, font_file)
                    font = ImageFont.truetype(font_path, font_size)
                    self.active_fonts[font_type] = font_path
                    print(f"使用字体: {os.path.basename(font_path)} 用于 {font_type}")
                    return font
                except:
                    continue
            
            # 如果所有备选字体都失败，使用系统默认字体
            print(f"警告：未找到合适的字体，使用默认体用于 {font_type}")
            return ImageFont.load_default()

    def draw_text_with_pil(self, img, text, position, font_size):
        """使用PIL绘制文字"""
        # PIL需要RGB格式，所以将BGR转回RGB
        text_color_rgb = self.text_color[::-1]
        
        img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img_pil)
        
        # 使用新的字体加载方
        font = self.try_load_font('title', font_size)
        
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        text_x = position[0] - text_width // 2
        text_y = position[1] - text_height // 2
        
        # 添加文字描边效果来实现加粗
        stroke_width = 1  # 描边宽度
        
        # 如果标位置，则添加描边效果
        if position[1] < self.height * 0.1:  # 假设标题在顶部10%的位置
            # 先绘制描边
            for offset_x in range(-stroke_width, stroke_width + 1):
                for offset_y in range(-stroke_width, stroke_width + 1):
                    if offset_x == 0 and offset_y == 0:
                        continue
                    draw.text(
                        (text_x + offset_x, text_y + offset_y),
                        text,
                        font=font,
                        fill=text_color_rgb  # 使用RGB格式
                    )
        
        # 绘制主要文字
        draw.text(
            (text_x, text_y),
            text,
            font=font,
            fill=text_color_rgb  # 使用RGB格式
        )
        
        return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

    def draw_arrow(self, img, start_point, end_point, thickness=2, alpha=1.0):
        """绘制更美观的箭头"""
        # 计算箭头方向
        dx = end_point[0] - start_point[0]
        dy = end_point[1] - start_point[1]
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist == 0:
            return img
        
        # 创建箭头
        arrow_color = self.text_color
        cv2.arrowedLine(
            img, 
            start_point, 
            end_point,
            arrow_color,
            thickness=thickness,
            line_type=cv2.LINE_AA,  # 抗锯齿
            tipLength=0.2  # 箭头长度
        )
        
        return img

    def get_audio_clips(self):
        """获取音频片段"""
        audio_clips = []
        durations = []
        current_time = 0  # 当前时间点
        silence_duration = 1.0  # 语间的间隔时间（秒）
        
        # 取中心词发音文件
        center_word_path = os.path.join(self.pronunciation_folder, f"center_word_{self.center_word}.mp3")
        if os.path.exists(center_word_path):
            audio = AudioFileClip(center_word_path)
            audio_clips.append(audio)
            durations.append(audio.duration + silence_duration)
        else:
            audio_clips.append(None)
            durations.append(silence_duration)
        
        # 取周围单词发音文件
        for word in self.surrounding_words:
            word_path = os.path.join(self.pronunciation_folder, f"surrounding_word_{word}.mp3")
            if os.path.exists(word_path):
                audio = AudioFileClip(word_path)
                audio_clips.append(audio)
                durations.append(audio.duration + silence_duration)
            else:
                audio_clips.append(None)
                durations.append(silence_duration)
        
        # 移除最后一个间隔时间（因为最后一个音频后不需要等待）
        if durations:
            durations[-1] -= silence_duration
        
        return audio_clips, durations

    def draw_text_with_annotations(self, img, text, romaji, chinese, position, font_size):
        """绘制带注释的文字，包含振假名效果"""
        text_color_rgb = self.text_color[::-1]
        img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGBA))
        draw = ImageDraw.Draw(img_pil)
        
        # 加载字体
        main_font = self.try_load_font('japanese', font_size)
        romaji_font = self.try_load_font('romaji', int(font_size * 0.4))  # 缩小振假名字体
        chinese_font = self.try_load_font('chinese', int(font_size * 0.6))
        
        # 计算主要文字尺寸
        text_bbox = draw.textbbox((0, 0), text, font=main_font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        # 计算振假名尺寸
        romaji_bbox = draw.textbbox((0, 0), romaji, font=romaji_font)
        romaji_width = romaji_bbox[2] - romaji_bbox[0]
        
        # 计算中文翻译尺寸
        chinese_bbox = draw.textbbox((0, 0), chinese, font=chinese_font)
        chinese_width = chinese_bbox[2] - chinese_bbox[0]
        chinese_height = chinese_bbox[3] - chinese_bbox[1]
        
        # 计算最大宽度
        max_width = max(text_width, romaji_width, chinese_width)
        
        # 增加内边距
        padding_x = 35
        padding_y = 25
        
        # 文字间距
        text_spacing = 8
        furigana_spacing = 3  # 振假名和主文字之间的距离
        
        # 计算总高度（包含振假名）
        total_height = (text_height + chinese_height + 
                       text_spacing * 2 + romaji_font.size)
        
        # 计算背景框位置
        box_left = position[0] - max_width//2 - padding_x
        box_top = position[1] - total_height//2 - padding_y
        box_right = position[0] + max_width//2 + padding_x
        box_bottom = position[1] + total_height//2 + padding_y
        
        # 绘制背景框
        background_color = (255, 255, 255, 160)
        draw.rounded_rectangle(
            [box_left, box_top, box_right, box_bottom],
            radius=15,
            fill=background_color
        )
        
        # 计算起始位置
        current_y = box_top + padding_y + romaji_font.size + furigana_spacing
        
        # 绘制主要文字
        text_x = position[0] - text_width//2
        draw.text((text_x, current_y), text, 
                  font=main_font, fill=text_color_rgb)
        
        # 绘制振假名（在主文字上方）
        romaji_x = position[0] - romaji_width//2
        draw.text((romaji_x, current_y - romaji_font.size - furigana_spacing), 
                  romaji, font=romaji_font, fill=text_color_rgb)
        
        # 绘制中文翻译（在主文字下方）
        current_y += text_height + text_spacing
        chinese_x = position[0] - chinese_width//2
        draw.text((chinese_x, current_y), chinese, 
                  font=chinese_font, fill=text_color_rgb)
        
        return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGBA2BGR)

    def calculate_arrow_points(self, center_pos, target_pos, text_size):
        """计算箭头的起点和终点，避开文字框"""
        dx = target_pos[0] - center_pos[0]
        dy = target_pos[1] - center_pos[1]
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist == 0:
            return None, None
        
        # 计算单位向量
        unit_x = dx / dist
        unit_y = dy / dist
        
        # 增加文字框的边距，让箭头从更远的地方开始和结束
        center_margin = text_size * 2.5  # 增加中心词文字框的距
        target_margin = text_size * 2.2  # 增加目标词文字框的距
        
        # 从中心词文字框外开始
        arrow_start = (
            int(center_pos[0] + unit_x * center_margin),
            int(center_pos[1] + unit_y * center_margin)
        )
        
        # 到目标词文字框外结束
        arrow_end = (
            int(target_pos[0] - unit_x * target_margin),
            int(target_pos[1] - unit_y * target_margin)
        )
        
        return arrow_start, arrow_end

    def create_frame(self, t, center, positions, word_index):
        """创建个帧"""
        # 创建基础帧
        if self.background_image and os.path.exists(self.background_image):
            try:
                # 使用 PIL 读取图片
                bg_pil = Image.open(self.background_image)
                if bg_pil.mode != 'RGBA':
                    bg_pil = bg_pil.convert('RGBA')
                bg_pil = bg_pil.resize((self.width, self.height), Image.Resampling.LANCZOS)
                frame = np.array(bg_pil)
                rgb_frame = frame[..., :3]
                alpha_channel = frame[..., 3] / 255.0
                bg_color_frame = np.full((self.height, self.width, 3), self.background_color[::-1], dtype=np.uint8)
                frame = (rgb_frame * alpha_channel[..., None] + bg_color_frame * (1 - alpha_channel[..., None])).astype(np.uint8)
            except Exception as e:
                print(f"警告: 读取背景图片时出错: {e}")
                frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
                frame[:] = self.background_color[::-1]
        else:
            frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            frame[:] = self.background_color[::-1]

        # 绘制标题
        frame = self.draw_text_with_pil(frame, self.title, positions['title'], 60)
        
        # 绘制中心词
        center_font_size = 50
        frame = self.draw_text_with_annotations(frame, 
                                              self.center_word,
                                              self.center_word_romaji,
                                              self.center_word_chinese,
                                              center, center_font_size)
        
        # 获取位置键列表（跳过title）
        position_keys = ['top', 'top_right', 'top_left', 
                        'bottom_left', 'bottom_right', 'bottom']
        
        # 先绘制所有已经显示过的单词（不带动画）
        surrounding_font_size = 40
        for i, pos_key in enumerate(position_keys):
            if i < word_index:  # 于已经显示过的单词
                pos = positions[pos_key]
                
                # 计算箭头位置，传入文字大小
                arrow_start, arrow_end = self.calculate_arrow_points(
                    center, pos, surrounding_font_size)
                if arrow_start and arrow_end:
                    # 所有单词（包括第一个）都在语音播放时才显现
                    current_time = sum(self.durations[:i])
                    word_duration = self.durations[i]
                    animation_duration = word_duration * 0.7  # 使用语音时长的70%来完成动画
                    progress = max(0, min(1, (t - current_time) / animation_duration))
                    
                    if t >= current_time:  # 只有在对应的时间点才显示箭头
                        self.draw_arrow(frame, arrow_start, arrow_end, 
                                      thickness=2, alpha=progress if i == word_index - 1 else 1.0)
                
                # 绘制单词
                frame = self.draw_text_with_annotations(frame,
                                                      self.surrounding_words[i],
                                                      self.surrounding_words_romaji[i],
                                                      self.surrounding_words_chinese[i],
                                                      pos, surrounding_font_size)
        
        # 绘制当前正在显示的单词（带动画效果）
        if word_index < len(position_keys):
            pos_key = position_keys[word_index]
            pos = positions[pos_key]
            try:
                word_duration = self.durations[word_index] if hasattr(self, 'durations') else 0.5
                
                # 计算当前单词的开始时间
                current_time = sum(self.durations[:word_index])
                
                # 使用语音持续时间的70%来完成动画
                animation_duration = word_duration * 0.7
                progress = max(0, min(1, (t - current_time) / animation_duration))
                
                # 只有在对应的时间点才显示箭头和文字
                if t >= current_time:
                    # 计算箭头位置
                    arrow_start, arrow_end = self.calculate_arrow_points(
                        center, pos, surrounding_font_size)
                    if arrow_start and arrow_end:
                        self.draw_arrow(frame, arrow_start, arrow_end, 
                                      thickness=2, alpha=progress)
                    
                    # 绘制带渐入动画的单词
                    overlay = frame.copy()
                    overlay = self.draw_text_with_annotations(overlay,
                                                            self.surrounding_words[word_index],
                                                            self.surrounding_words_romaji[word_index],
                                                            self.surrounding_words_chinese[word_index],
                                                            pos, surrounding_font_size)
                    cv2.addWeighted(overlay, progress, frame, 1 - progress, 0, frame)
                
            except Exception as e:
                print(f"绘制字时出错: {e}")
        
        return frame

    def generate_video(self, output_filename="word_animation.mp4"):
        """生成视频"""
        print("\n=== 开始生成视频 ===")
        
        # 显示视频生成参数
        print("\n[参数] 视频生成配置:")
        print(f"标题: {self.title}")
        print(f"中心词: {self.center_word}")
        print("周围单词:", ", ".join(self.surrounding_words))
        print(f"\n[参数] 技术参数:")
        print(f"分辨率: {self.width}x{self.height}")
        print(f"帧率: {self.fps}fps")
        print(f"背景音乐: {os.path.basename(self.background_music) if self.background_music else '无'}")
        print(f"背景图片: {os.path.basename(self.background_image) if self.background_image else '无'}")
        print("------------------------")
        
        total_frames = int(self.fps * (len(self.surrounding_words) + 1) * 2)
        current_frame = 0
        
        # 计算位置
        center, positions = self.calculate_positions()
        
        # 获取音频
        audio_clips, durations = self.get_audio_clips()
        self.durations = durations  # 保存持续时间供create_frame使用
        total_duration = sum(durations)
        
        def make_frame(t):
            nonlocal current_frame
            # 计算当前应该显示到哪个单词
            current_time = 0
            word_index = 0
            for i, duration in enumerate(durations):
                if t > current_time and t <= current_time + duration:
                    word_index = i
                    break
                current_time += duration
            
            # 创建帧
            frame = self.create_frame(t, center, positions, word_index)
            current_frame += 1
            
            # 通过回调函数更新进度，但不打印进度信息
            if hasattr(self, 'progress_callback'):
                self.progress_callback(current_frame / total_frames)
            
            return frame
        
        # 创建视频剪辑
        video_clip = VideoClip(make_frame, duration=total_duration)
        
        # 添加音频
        current_time = 0
        audio_tracks = []
        
        # 添加发音音频
        for audio in audio_clips:
            if audio is not None:
                audio_track = audio.with_start(current_time)
                audio_tracks.append(audio_track)
            current_time += durations[audio_clips.index(audio)]
        
        # 添加背景音乐
        if hasattr(self, 'background_music') and self.background_music:
            try:
                print(f"[音频] 正在处理背景音乐: {os.path.basename(self.background_music)}")
                
                # 直接使用传入的路径
                if os.path.exists(self.background_music):
                    bg_music = AudioFileClip(self.background_music)
                    original_duration = bg_music.duration
                    
                    # 处理音乐时长
                    if bg_music.duration > total_duration:
                        print(f"[音频] 裁剪背景音乐 ({original_duration:.1f}s → {total_duration:.1f}s)")
                        bg_music = bg_music.with_duration(total_duration)
                    elif bg_music.duration < total_duration:
                        repeats = int(total_duration / bg_music.duration) + 1
                        print(f"[音频] 循环背景音乐 ({original_duration:.1f}s × {repeats})")
                        repeated_clips = [bg_music] * repeats
                        bg_music = concatenate_audioclips(repeated_clips).with_duration(total_duration)
                    
                    # 设置音量并添加到音轨
                    try:
                        bg_music = bg_music.set_volume(self.music_volume)
                    except AttributeError:
                        bg_music.volume = self.music_volume  # 直接设置属性
                    
                    audio_tracks.append(bg_music)
                    print(f"[音频] 背景音乐添加成功 (音量: {self.music_volume*100:.0f}%)")
                else:
                    print(f"[错误] 音频文件不存在: {self.background_music}")
            except Exception as e:
                print(f"[错误] 添加背景音乐失败: {str(e)}")
        else:
            print("[提示] 未设置背景音乐")
        
        # 合成所有音轨
        if audio_tracks:
            try:
                print("\n[处理] 合成音频轨道...")
                final_audio = CompositeAudioClip(audio_tracks)
                video_clip = video_clip.with_audio(final_audio)
                print("[成功] 音频轨道合成完成")
            except Exception as e:
                print(f"[错误] 音频合成失败: {str(e)}")
        
        # 输出视频
        try:
            print("\n[处理] 开始生成最终视频...")
            video_clip.write_videofile(
                output_filename,
                fps=self.fps,
                codec="libx264",
                audio_codec="aac",
                bitrate="2000k",
                threads=4,
                preset="medium",
                ffmpeg_params=[
                    "-movflags", "faststart",
                    "-profile:v", "main",
                    "-pix_fmt", "yuv420p"
                ]
            )
            print(f"\n[完成] 视频已生成: {output_filename}")
        except Exception as e:
            print(f"[错误] 视频生成失败: {str(e)}")
        finally:
            print("\n[清理] 正在释放资源...")
            # 理资源
            video_clip.close()
            for audio in audio_clips:
                if audio is not None:
                    audio.close()
            if 'bg_music' in locals():
                bg_music.close()
            print("[完成] 资源释放完成")
            print("\n=== 视频生成结束 ===\n")

    def cleanup(self):
        """清理资源"""
        try:
            if hasattr(self, '_audio_clips'):
                for audio in self._audio_clips:
                    if audio is not None:
                        try:
                            audio.close()
                        except:
                            pass
            
            if hasattr(self, '_bg_music') and self._bg_music is not None:
                try:
                    self._bg_music.close()
                except:
                    pass
        except:
            pass

# 用示例
if __name__ == "__main__":
    generator = WordAnimationGenerator(
        title="日语速记单词",  # 自定义标题
        center_word="食べ",
        center_word_romaji="taberu",
        center_word_chinese="吃",
        surrounding_words=["食事", "飲む", "料理", "レストラン", "美味い", "朝ご飯"],
        surrounding_words_romaji=["shokuji", "nomu", "ryouri", "resutoran", "oishii", "asagohan"],
        surrounding_words_chinese=["饭", "喝", "料理", "餐厅", "好吃", "早饭"],
        fps=25,
        resolution="720p",
        aspect_ratio="16:9",
        orientation="portrait",
        background_color=(0,255,255),
        text_color=(0,0,0),
        background_image="background.jpg",
        background_opacity=0.5,
        background_music="background.mp3",
        music_volume=0.8,
        pronunciation_folder="./pronunciation"
    )
    
    generator.generate_video("output.mp4")
