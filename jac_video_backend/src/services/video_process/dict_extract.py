from typing import Dict, Any, Optional, TypedDict

class ExtractedData(TypedDict):
    title: str
    shape: str
    shape_color: str
    arrow_color: str
    image_url: Optional[str]
    music_url: Optional[str]
    resolution: str
    aspect_ratio: str
    orientation: str
    frame_rate: int
    center_word: Dict[str, str]
    surrounding_words: Dict[str, Dict[str, str]]

def extract_data_from_dict(data: Dict[str, Any]) -> ExtractedData:
    """
    从前端传来的字典中提取所需数据
    
    Args:
        data: 包含所有步骤数据的字典
    
    Returns:
        ExtractedData: 提取的数据，包含所有需要的字段
    """
    try:
        # 提取步骤一的数据
        step1 = data.get('step1', {})
        title = step1.get('title', '')
        shape = step1.get('shape', 'rectangle')
        shape_color = step1.get('shapeColor', '#FFFFFF')
        font_color = step1.get('fontColor', '#FF3366')

        # 提取步骤三的数据
        step3 = data.get('step3', {})
        resolution = step3.get('resolution', '720p')
        aspect_ratio = step3.get('aspectRatio', '16:9')
        orientation = step3.get('orientation', 'landscape')
        frame_rate = step3.get('frameRate', 30)
        image_url = step3.get('imageUrl')

        # 提取步骤四的数据
        step4 = data.get('step4', {})
        music_url = step4.get('musicUrl')

        # 提取步骤五的语音数据
        step5 = data.get('step5', {})
        voice_data = step5.get('voiceData', {}).get('word', {})
        
        # 提取中心词数据
        center_word = voice_data.get('center_word', {})
        
        # 提取周边词数据
        surrounding_words = voice_data.get('surrounding_words', {})

        # 构建返回数据
        extracted_data: ExtractedData = {
            'title': title,
            'shape': shape,
            'shapeColor': shape_color,
            'fontColor': font_color,
            'image_url': image_url,
            'music_url': music_url,
            'resolution': resolution,
            'aspect_ratio': aspect_ratio,
            'orientation': orientation,
            'frame_rate': frame_rate,
            'center_word': center_word,
            'surrounding_words': surrounding_words
        }

        return extracted_data

    except Exception as e:
        print(f"Error extracting data: {e}")
        raise ValueError(f"Failed to extract data from dictionary: {str(e)}")

# 测试用例
if __name__ == "__main__":
    # 示例数据
    test_data = {
  "step1": {
    "title": "日语单词速记",
    "shape": "rectangle",
    "shapeColor": "#FFFFFF",
    "fontColor": "#FFA31A"
  },
  "step2": {
    "model": "Spark Max",
    "word": "寿司",
    "content": {
      "$schema": "http://json-schema.org/draft-07/schema#",
      "center_word": "寿司",
      "center_word_romaji": "すし",
      "center_word_translation": "sushi",
      "surrounding_words": [
        "刺身",
        "海苔",
        "醤油",
        "酢",
        "鮭魚",
        "鮪鱼"
      ],
      "surrounding_words_romaji": [
        "さしみ",
        "のり",
        "しょうゆ",
        "す",
        "しゃけ",
        "まぐろ"
      ],
      "surrounding_words_translation": [
        "sashimi",
        "nori",
        "shoyu",
        "su",
        "shake",
        "maguro"
      ]
    }
  },
  "step3": {
    "model": "讯飞星火认知大模型",
    "resolution": "720p",
    "aspectRatio": "16:9",
    "orientation": "portrait",
    "frameRate": 30,
    "imageUrl": "http://localhost:5000/static/images/img_1734590464381.jpg"
  },
  "step4": {
    "mode": "random",
    "musicUrl": "http://127.0.0.1:5000/static/bgm/bg1.MP3"
  },
  "step5": {
    "model": "有道智云",
    "voiceData": {
      "word": {
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
            "word_voice_url": "/static/voices/tts_醤油_1734590476388.mp3"
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
    }
  }
}

    try:
        result = extract_data_from_dict(test_data)
        print("Extracted data:")
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Test failed: {e}")
