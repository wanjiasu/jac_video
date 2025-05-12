from typing import Dict, Any, Optional
from pathlib import Path
import os
import sys
import time

# 添加项目根目录到系统路径
project_root = str(Path(__file__).resolve().parents[3])
if project_root not in sys.path:
    sys.path.append(project_root)

# 修改为绝对导入
from src.services.video_process.word_animation_core import WordAnimationGenerator
from .progress_manager import ProgressManager

class VideoGenerator:
    def __init__(self, data: Dict[str, Any], fonts_config: Optional[Dict[str, str]] = None):
        self.data = data
        self.project_root = project_root
        self.videos_dir = os.path.join(self.project_root, 'static', 'videos')
        self.voices_dir = os.path.join(self.project_root, 'static', 'voices')
        self.fonts_dir = os.path.join(self.project_root, 'src/services/video_process/fonts')
        
        # 从输入数据中获取颜色，如果没有则使用默认值
        self.font_color = self._hex_to_rgb(data.get('fontColor', '#FFA31A'))  # 默认橙色
        self.shape_color = self._hex_to_rgb(data.get('shapeColor', '#FFFFFF'))  # 默认白色
        
        # 默认字体配置
        self.default_fonts = {
            'title': {
                'default': 'msyh.ttc',
                'options': ['msyh.ttc', 'simhei.ttf', 'simsun.ttc', 'simkai.ttf']
            },
            'japanese': {
                'default': 'ZenKakuGothicNew-Bold.ttf',
                'options': ['yugothic.ttf', 'msgothic.ttc', 'yumin.ttf', 'msmincho.ttc']
            },
            'romaji': {
                'default': 'msyh.ttc',
                'options': ['MPLUS1p-Regular.ttf', 'arial.ttf', 'times.ttf', 'tahoma.ttf']
            },
            'chinese': {
                'default': 'msyh.ttc',
                'options': ['msyh.ttc', 'simhei.ttf', 'simsun.ttc', 'simkai.ttf']
            }
        }
        
        # 使用传入的字体配置或默认配置
        self.fonts_config = {}
        for font_type, default_config in self.default_fonts.items():
            if fonts_config and font_type in fonts_config:
                font_file = fonts_config[font_type]
                if font_file in default_config['options']:
                    self.fonts_config[font_type] = font_file
                else:
                    print(f"Warning: Font {font_file} not in options for {font_type}, using default")
                    self.fonts_config[font_type] = default_config['default']
            else:
                self.fonts_config[font_type] = default_config['default']
        
        # 确保必要的目录存在
        for directory in [self.videos_dir, self.voices_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)

    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """将十六进制颜色转换为RGB元组"""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return (r, g, b)

    def get_available_fonts(self) -> Dict[str, list]:
        """获取所有可用的字体选项"""
        return {
            font_type: config['options']
            for font_type, config in self.default_fonts.items()
        }

    def _extract_surrounding_words(self) -> tuple[list, list, list]:
        """从surrounding_words字典中提取单词列表"""
        words = []
        romaji = []
        translations = []
        
        for i in range(1, 7):
            key = f"surrounding_word_{i}"
            word_data = self.data["surrounding_words"][key]
            words.append(word_data["word"])
            romaji.append(word_data["word_romaji"])
            translations.append(word_data["word_translation"])
            
        return words, romaji, translations

    def _get_voice_files(self) -> str:
        """获取语音文件目录，并确保语音文件名符合要求"""
        # 确保语音目录存在
        if not os.path.exists(self.voices_dir):
            os.makedirs(self.voices_dir)

        try:
            # 处理中心词语音文件 - 复制并重命名为 WordAnimationGenerator 需要的格式
            center_voice = self.data['center_word']['word_voice_url'].lstrip('/')
            center_voice_path = os.path.join(self.project_root, center_voice)
            center_word_new_name = f"center_word_{self.data['center_word']['word']}.mp3"
            center_word_new_path = os.path.join(self.voices_dir, center_word_new_name)

            # 复制并重命名中心词语音文件
            if not os.path.exists(center_word_new_path):
                if not os.path.exists(center_voice_path):
                    raise FileNotFoundError(f"中心词语音文件不存在: {center_voice_path}")
                import shutil
                shutil.copy2(center_voice_path, center_word_new_path)
                print(f"Copied center word voice file to: {center_word_new_path}")

            # 处理周边词语音文件 - 复��并重命名
            for i in range(1, 7):
                key = f"surrounding_word_{i}"
                word = self.data['surrounding_words'][key]['word']
                voice_url = self.data['surrounding_words'][key]['word_voice_url'].lstrip('/')
                voice_path = os.path.join(self.project_root, voice_url)
                
                # 创建符合 WordAnimationGenerator 求的文件名
                new_name = f"surrounding_word_{word}.mp3"
                new_path = os.path.join(self.voices_dir, new_name)

                # 复制并重命名周边词语音文件
                if not os.path.exists(new_path):
                    if not os.path.exists(voice_path):
                        raise FileNotFoundError(f"周边词语音文件不存在: {voice_path}")
                    import shutil
                    shutil.copy2(voice_path, new_path)
                    print(f"Copied surrounding word voice file to: {new_path}")

            return self.voices_dir

        except Exception as e:
            print(f"Error preparing voice files: {e}")
            import traceback
            traceback.print_exc()
            raise

    def generate(self) -> Optional[str]:
        """生成视频并返回视频URL"""
        try:
            # 初始化进度
            ProgressManager.update_progress(0)
            
            # 提取周边单词数据
            surrounding_words, surrounding_words_romaji, surrounding_words_translation = self._extract_surrounding_words()

            # 获取语音文件目录
            pronunciation_folder = self._get_voice_files()

            # 转换为RGB格式（不打印调试信息）
            rgb_text_color = self._hex_to_rgb(self.data.get('fontColor', '#FFA31A'))
            rgb_bg_color = self._hex_to_rgb(self.data.get('shapeColor', '#FFFFFF'))
            text_color = (rgb_text_color[2], rgb_text_color[1], rgb_text_color[0])
            background_color = rgb_bg_color

            # 构建字体路径，使用配置的字体
            fonts = {
                font_type: os.path.join(self.fonts_dir, font_file)
                for font_type, font_file in self.fonts_config.items()
            }

            # 检查字体文件是否存在
            for font_type, font_path in fonts.items():
                if not os.path.exists(font_path):
                    print(f"Warning: Font file not found: {font_path}")
                    # 使用默认字体
                    default_font = self.default_fonts[font_type]['default']
                    fonts[font_type] = os.path.join(self.fonts_dir, default_font)
                    print(f"Using default font for {font_type}: {default_font}")

            # 修改音乐URL处理逻辑
            music_url = self.data.get('music_url')
            if music_url:
                print(f"[音频] 收到音乐URL: {music_url}")
                # 构建本地路径
                if music_url.startswith('http'):
                    file_name = os.path.basename(music_url)
                    music_path = os.path.join(self.project_root, 'static', 'bgm', file_name)
                    print(f"[音频] 本地路径: {music_path}")
                    if os.path.exists(music_path):
                        full_music_path = music_path
                        print(f"[音频] 找到音乐文件: {full_music_path}")
                    else:
                        print(f"[错误] 音乐文件不存在: {music_path}")
                        full_music_path = None
                else:
                    # 如果不是 http 开头，假设是相对路径
                    full_music_path = os.path.join(self.project_root, music_url.lstrip('/'))
                    if not os.path.exists(full_music_path):
                        print(f"[错误] 音乐文件不存在: {full_music_path}")
                        full_music_path = None
            else:
                full_music_path = None
                print("[提示] 未提供音乐URL")

            # 创建视频生成器实例
            generator = WordAnimationGenerator(
                title=self.data['title'],
                center_word=self.data['center_word']['word'],
                center_word_romaji=self.data['center_word']['word_romaji'],
                center_word_chinese=self.data['center_word']['word_translation'],
                surrounding_words=surrounding_words,
                surrounding_words_romaji=surrounding_words_romaji,
                surrounding_words_chinese=surrounding_words_translation,
                fps=self.data['frame_rate'],
                resolution=self.data['resolution'],
                aspect_ratio=self.data['aspect_ratio'],
                orientation=self.data['orientation'],
                background_color=background_color,
                text_color=text_color,
                background_image=self.data['image_url'].replace('http://localhost:5000', self.project_root) if self.data.get('image_url') else None,
                background_opacity=0.5,
                background_music=full_music_path,  # 使用处理后的音乐路径
                music_volume=0.8,
                pronunciation_folder=pronunciation_folder,
                fonts=fonts
            )

            # 生成视频文件名
            timestamp = int(time.time() * 1000)
            video_filename = f"video_{self.data['center_word']['word']}_{timestamp}.mp4"
            video_path = os.path.join(self.videos_dir, video_filename)

            # 生成视频
            print(f"[视频] 开始生成: {video_path}")
            generator.generate_video(video_path)
            print(f"[完成] 视频生成成功: {video_filename}")

            # 返回可访问的URL
            return f"/static/videos/{video_filename}"

        except Exception as e:
            print(f"[错误] 视频生成失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

def generate_video(data: Dict[str, Any], fonts_config: Optional[Dict[str, str]] = None) -> Optional[str]:
    """
    生成视频的便捷函数
    
    Args:
        data: 包含视频生成所需的所有数据的字典
        fonts_config: 可选的字体配置，格式如 {'title': 'msyh.ttc', 'japanese': 'yugothic.ttf', ...}
    
    Returns:
        Optional[str]: 生成的视频URL，失败时返回None
    """
    generator = VideoGenerator(data, fonts_config)
    return generator.generate()

# 测试用例
if __name__ == "__main__":
    test_data = {
  "title": "日语单词速记",
  "shape": "rectangle",
  "shapeColor": "#FFFFFF",
  "fontColor": "#FFA31A",
  "image_url": "http://localhost:5000/static/images/img_1734590464381.jpg",
  "music_url": "http://127.0.0.1:5000/static/bgm/bg1.MP3",
  "resolution": "720p",
  "aspect_ratio": "16:9",
  "orientation": "portrait",
  "frame_rate": 30,
  "center_word": {
    "word": "寿司",
    "word_romaji": "すし",
    "word_translation": "sushi",
    "word_voice_url": "/static/voices/tts_寿司_1734590471281.mp3"
  },
  "surrounding_words": {
    "surrounding_word_1": {
      "word": "刺身",
      "word_romaji": "さしみ",
      "word_translation": "sashimi",
      "word_voice_url": "/static/voices/tts_刺身_1734590472980.mp3"
    },
    "surrounding_word_2": {
      "word": "海苔",
      "word_romaji": "のり",
      "word_translation": "nori",
      "word_voice_url": "/static/voices/tts_海苔_1734590474647.mp3"
    },
    "surrounding_word_3": {
      "word": "醤油",
      "word_romaji": "しょうゆ",
      "word_translation": "shoyu",
      "word_voice_url": "/static/voices/tts_油_1734590476388.mp3"
    },
    "surrounding_word_4": {
      "word": "酢",
      "word_romaji": "す",
      "word_translation": "su",
      "word_voice_url": "/static/voices/tts_酢_1734590478005.mp3"
    },
    "surrounding_word_5": {
      "word": "鮭魚",
      "word_romaji": "しゃけ",
      "word_translation": "shake",
      "word_voice_url": "/static/voices/tts_鮭魚_1734590479741.mp3"
    },
    "surrounding_word_6": {
      "word": "鮪鱼",
      "word_romaji": "まぐろ",
      "word_translation": "maguro",
      "word_voice_url": "/static/voices/tts_鮪鱼_1734590481400.mp3"
    }
  }
}
    
    # 打印可用的字体
    generator = VideoGenerator(test_data)
    print("\nAvailable fonts:")
    for font_type, options in generator.get_available_fonts().items():
        print(f"{font_type}: {', '.join(options)}")
    
    # 测试不同字体配置
    test_fonts = {
        'title': 'simhei.ttf',
        'japanese': 'msgothic.ttc',
        'romaji': 'times.ttf',
        'chinese': 'simkai.ttf'
    }
    
    try:
        print("\nTesting with custom fonts...")
        video_url = generate_video(test_data, test_fonts)
        if video_url:
            print(f"Video generated successfully with custom fonts: {video_url}")
        else:
            print("Failed to generate video with custom fonts")
            
    except Exception as e:
        print(f"Error during test: {e}")
        traceback.print_exc() 