import json
import os
from datetime import datetime
from pathlib import Path
import sys
from utils.retry_decorator import retry_on_exception
import requests
import time
import random
from moviepy.editor import AudioFileClip

# 添加项目根目录到系统路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from api.jieyue_api.jieyue_text import get_jieyue_text_surrounding_words
from api.jieyue_api.jieyue_pic import generate_image
from api.youdaozhiyun_voice.apidemo.TtsDemo import createRequest
from word_animation_core import WordAnimationGenerator

class VideoProjectGenerator:
    def __init__(self, input_dict):
        self.input_dict = input_dict
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.project_name = f"{self.timestamp}_{input_dict['title']}_{input_dict['center_word']}"
        self.project_path = Path("src_temp") / self.project_name
        self.config = None
        
        # 如果没有指定背景颜色且没有背景图，设置默认背景颜色
        if 'background_color' not in input_dict and 'background_image' not in input_dict:
            input_dict['background_color'] = (255, 255, 255)  # 默认白色背景
        
    def calculate_image_size(self):
        """根据分辨率、宽高比和方向计算图片尺寸"""
        resolution_map = {
            "720p": (1280, 720),
            "1080p": (1920, 1080),
            "480p": (854, 480)
        }
        base_width, base_height = resolution_map.get(self.input_dict['resolutions'], (1280, 720))
        
        aspect_ratio = list(map(int, self.input_dict['aspect_ratio'].split(":")))
        ratio = aspect_ratio[0] / aspect_ratio[1]
        
        if self.input_dict['orientation'] == "portrait":
            # 竖屏模式，交换宽高
            base_width, base_height = base_height, base_width
            
        # 确保尺寸是64的倍数（某些AI模型的要求）
        width = round(base_width / 64) * 64
        height = round(base_height / 64) * 64
        
        return f"{width}x{height}"

    def create_project_structure(self):
        """创建项目结构和初始配置文件"""
        # 创建项目目录
        self.project_path.mkdir(parents=True, exist_ok=True)
        (self.project_path / "pronunciation").mkdir(exist_ok=True)
        
        # 创建初始配置文件
        self.config = self.input_dict.copy()
        self.save_config()
        
    @retry_on_exception(retries=3, delay=1.0, exceptions=(Exception,))
    def update_word_info(self):
        """更新单词相关信息"""
        word_info = get_jieyue_text_surrounding_words(self.config['center_word'])
        self.config.update(word_info)
        self.save_config()
        
    @retry_on_exception(retries=3, delay=1.0, exceptions=(requests.RequestException, Exception))
    def generate_background(self):
        """生成背景图片"""
        image_size = self.calculate_image_size()
        prompt = f"背景颜色一定要为#D3D3D3, 生成一张和{self.config['center_word']}主题相关的图片，卡通风格"
        # 使用时间戳作为文件名，避免中文
        background_path = self.project_path / f"background_{int(time.time())}.png"
        
        saved_paths = generate_image(
            prompt=prompt,
            save_dir=str(background_path.parent),
            size=image_size
        )
        
        if saved_paths:
            self.config['background_image'] = str(saved_paths[0])
            self.save_config()
            
    @retry_on_exception(retries=3, delay=1.0, exceptions=(requests.RequestException, Exception))
    def generate_single_pronunciation(self, word: str, save_path: Path):
        """
        生成单个单词的发音
        Args:
            word: 要生成发音的单词
            save_path: 保存路径
        """
        try:
            createRequest(word, str(save_path))
            if not os.path.exists(save_path) or os.path.getsize(save_path) == 0:
                raise Exception(f"音频文件 {save_path} 生成失败或为空")
            return True
        except Exception as e:
            logger.error(f"生成单词 '{word}' 的发音失败: {e}")
            raise
    
    def generate_pronunciations(self):
        """生成发音文件"""
        # 确保发音目录存在
        pronunciation_dir = self.project_path / "pronunciation"
        pronunciation_dir.mkdir(exist_ok=True)
        
        # 生成中心词发音
        center_word_path = pronunciation_dir / f"center_word_{self.config['center_word']}.mp3"
        retry_count = 0
        max_retries = 5  # 最大重试次数
        
        while retry_count < max_retries:
            try:
                if self.generate_single_pronunciation(self.config['center_word'], center_word_path):
                    break
            except Exception as e:
                retry_count += 1
                if retry_count == max_retries:
                    logger.error(f"中心词 '{self.config['center_word']}' 发音生成失败，已达到最大重试次数")
                else:
                    logger.warning(f"中心词发音生成失败，正在进行第 {retry_count} 次重试...")
                    time.sleep(2 * retry_count)  # 递增等待时间
        
        # 生成周围单词发音
        failed_words = []
        for word in self.config['surrounding_words']:
            word_path = pronunciation_dir / f"surrounding_word_{word}.mp3"
            retry_count = 0
            success = False
            
            while retry_count < max_retries:
                try:
                    if self.generate_single_pronunciation(word, word_path):
                        success = True
                        break
                except Exception as e:
                    retry_count += 1
                    if retry_count == max_retries:
                        logger.error(f"单词 '{word}' 发音生成失败，已达到最大重试次数")
                        failed_words.append(word)
                    else:
                        logger.warning(f"单词 '{word}' 发音生成失败，正在进行第 {retry_count} 次重试...")
                        time.sleep(2 * retry_count)  # 递增等待时间
            
        # 更新配置文件
        self.config['pronunciation_folder'] = str(pronunciation_dir)
        self.save_config()
        
        # 如果有失败的单词，记录到配置文件中
        if failed_words:
            self.config['failed_pronunciations'] = failed_words
            self.save_config()
            logger.warning(f"以下单词的发音生成失败: {', '.join(failed_words)}")
    
    def set_background_music(self):
        """设置背景音乐"""
        background_music_path = Path("background.mp3")
        if background_music_path.exists():
            self.config['background_music'] = str(background_music_path)
            self.save_config()
            
    def save_config(self):
        """保存配置文件"""
        config_path = self.project_path / "config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=4)
            
    def get_random_background_music(self):
        """从背景音乐文件夹中随机选择一个音乐文件并截取前10秒"""
        bg_music_folder = Path("background_music")
        if not bg_music_folder.exists():
            print(f"错误：背景音乐文件夹不存在: {bg_music_folder}")
            return None
        
        # 获取所有音频文件
        music_files = list(bg_music_folder.glob("*.mp3")) + list(bg_music_folder.glob("*.wav"))
        if not music_files:
            print(f"错误：在 {bg_music_folder} 中没有找到音频文件")
            return None
        
        print(f"找到 {len(music_files)} 个音频文件")
        
        # 随机选择一个音频文件
        selected_music = random.choice(music_files)
        print(f"随机选择的背景音乐: {selected_music}")
        
        audio = None
        try:
            # 创建临时文件名
            temp_filename = f"temp_bgm_{int(time.time())}.mp3"
            temp_path = bg_music_folder / temp_filename
            
            # 加载音频并截取前10秒
            audio = AudioFileClip(str(selected_music))
            audio = audio.subclip(0, min(10, audio.duration))
            audio.write_audiofile(str(temp_path))
            return str(temp_path)
        except Exception as e:
            print(f"处理背景音乐时出错: {e}")
            return None
        finally:
            if audio is not None:
                try:
                    audio.close()
                except:
                    pass

    def generate_video(self):
        """生成视频"""
        generator = None
        try:
            print("6. 开始生成视频...")
            
            # 如果配置中指定了随机背景音乐
            if self.config.get('random_background_music', False):
                print("正在获取随机背景音乐...")
                random_music = self.get_random_background_music()
                if random_music:
                    print(f"成功获取随机背景音乐: {random_music}")
                    self.config['background_music'] = random_music
                else:
                    print("获取随机背景音乐失败")
            
            # RGB 转 BGR
            text_color = tuple(reversed(self.config['text_color']))
            background_color = tuple(reversed(self.config.get('background_color', (255, 255, 255))))
            
            # 检查背景音乐路径
            if self.config.get('background_music'):
                print(f"使用背景音乐: {self.config['background_music']}")
                if not os.path.exists(self.config['background_music']):
                    print(f"警告：背景音乐文件不存在: {self.config['background_music']}")
            
            # 创建视频生成器实例
            generator = WordAnimationGenerator(
                title=self.config['title'],
                center_word=self.config['center_word'],
                center_word_romaji=self.config['center_word_romaji'],
                center_word_chinese=self.config['center_word_translation'],
                surrounding_words=self.config['surrounding_words'],
                surrounding_words_romaji=self.config['surrounding_words_romaji'],
                surrounding_words_chinese=self.config['surrounding_words_translation'],
                fps=self.config['fps'],
                resolution=self.config['resolutions'],
                aspect_ratio=self.config['aspect_ratio'],
                orientation=self.config['orientation'],
                background_color=background_color,
                text_color=text_color,
                background_image=self.config.get('background_image'),
                background_opacity=self.config.get('background_opacity', 1.0),
                background_music=self.config.get('background_music'),  # 这里会包含随机选择的音乐路径
                music_volume=self.config.get('music_volume', 0.8),
                pronunciation_folder=self.config['pronunciation_folder'],
                fonts=self.config.get('fonts', {
                    'title': 'msyh.ttc',
                    'japanese': 'yugothic.ttf',
                    'romaji': 'arial.ttf',
                    'chinese': 'msyh.ttc'
                }),
            )
            
            # 生成视频文件名
            video_filename = f"{self.config['title']}_{self.config['center_word']}.mp4"
            video_path = self.project_path / video_filename
            
            # 生成视频
            generator.generate_video(str(video_path))
            print(f"视频生成完成！保存在：{video_path}")
            
            # 将视频路径添加到配置文件
            self.config['output_video'] = str(video_path)
            self.save_config()
            
            # 等待资源释放
            time.sleep(1)
            
            # 清理临时背景音乐文件
            if self.config.get('random_background_music', False) and self.config.get('background_music'):
                self._cleanup_temp_bgm()
                
            return str(video_path)
        except Exception as e:
            print(f"生成视频时出错: {e}")
            raise
        finally:
            # 确保资源被释放
            if generator is not None:
                try:
                    generator.cleanup()
                except:
                    pass

    def _cleanup_temp_bgm(self):
        """清理临时背景音乐文件"""
        if not self.config.get('background_music'):
            return
        
        try:
            # 确保所有音频资源都被释放
            import gc
            gc.collect()
            
            # 多次尝试删除文件
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    os.remove(self.config['background_music'])
                    print("已清理临时背景音乐文件")
                    break
                except Exception as e:
                    if attempt < max_attempts - 1:
                        print(f"尝试删除文件失败，等待后重试: {e}")
                        time.sleep(2)  # 增加等待时间
                    else:
                        print(f"清理临时背景音乐文件失败: {e}")
        except Exception as e:
            print(f"清理临时背景音乐文件失败: {e}")

    def generate(self):
        """执行完整的生成流程"""
        print(f"开始创建项目：{self.project_name}")
        
        print("1. 创建项目结构...")
        self.create_project_structure()
        
        print("2. 更新单词信息...")
        self.update_word_info()
        
        print("3. 生成背景图片...")
        self.generate_background()
        
        print("4. 生成发音文件...")
        self.generate_pronunciations()
        
        print("5. 设置背景音乐...")
        self.set_background_music()
        
        # 添加生成视频步骤
        self.generate_video()
        
        print(f"项目生成完成！项目路径：{self.project_path}")
        return str(self.project_path)

def create_video_project(input_dict):
    """创建视频项目的便捷函数"""
    generator = VideoProjectGenerator(input_dict)
    return generator.generate()

if __name__ == "__main__":
    # 测试用例
    test_input = {
        'title': '日语速记单词',
        'center_word': '会社員',
        'fps': 25,
        'resolutions': '720p',
        'aspect_ratio': "16:9",
        'orientation': "portrait",
        'background_color': (255,255,255),
        'text_color': (255,163,26),
        'background_opacity': 0.5,
        'music_volume': 0.8,
        'fonts': {
            'title': 'msyh.ttc',        # Microsoft YaHei 字体文件
            'japanese': 'yugothic.ttf',  # Yu Gothic 字体文件
            'romaji': 'arial.ttf',       # Arial 字体文件
            'chinese': 'msyh.ttc'        # Microsoft YaHei 字体文件
        }
    }
    
    project_path = create_video_project(test_input)
    print(f"测试完成，项目路径：{project_path}")