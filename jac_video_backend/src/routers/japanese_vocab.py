from fastapi import APIRouter, HTTPException, Response
from ..services.api_service.xinghuo_service import get_response_from_model, generate_image_with_resolution
from ..services.api_service.xinghuo_config import xinghuo_text_dict
from typing import Dict, List, Any
from ..services.youdaozhiyun_voice.apidemo.TtsDemo import createRequest, batch_create_requests
from pydantic import BaseModel
import os
import random
from pathlib import Path
from ..services.video_process.dict_extract import extract_data_from_dict
from ..services.video_process.video_generator import generate_video
from sse_starlette.sse import EventSourceResponse
import asyncio
import json
from ..services.video_process.progress_manager import ProgressManager

router = APIRouter()

# 获取项目根目录
project_root = str(Path(__file__).resolve().parents[3])

# 全局进度变量
generation_progress = 0

@router.get("/products/japanese-vocab/step2/get_text_by_model")
async def get_text_by_model(model: str, word: str):
    # 检查模型名称是否有效
    if model not in xinghuo_text_dict:
        raise HTTPException(status_code=400, detail="无效的模型名称")

    try:
        # 调用 get_response_from_model 函数
        content_dict, usage_dict = await get_response_from_model(word, model)
        return {"content_dict": content_dict}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
text2pic_model_dict = ['讯飞星火认知大模型']

@router.get("/products/japanese-vocab/step3/get_image_by_model")
async def get_image_by_model(model: str, resolution: str, aspect_ratio: str, orientation: str, word: str):
    if model not in text2pic_model_dict:
        raise HTTPException(status_code=400, detail="无效的模型名称")
    
    if model == '讯飞星火认知大模型':
        image_url = await generate_image_with_resolution(resolution, aspect_ratio, orientation, word)
        return {"image_url": image_url}

text2voice_model_dict = ['有道智云']

@router.get("/products/japanese-vocab/step4/get_voice_by_model")
async def get_voice_by_model(model: str, word: str):
    if model not in text2voice_model_dict:
        raise HTTPException(status_code=400, detail="无效的模型名称")
    

class WordRequest(BaseModel):
    center_word: str
    center_word_romaji: str
    center_word_translation: str
    surrounding_words: List[str]
    surrounding_words_romaji: List[str]
    surrounding_words_translation: List[str]

@router.post("/products/japanese-vocab/step5/get_voice_by_model")
async def get_voice_by_model(model: str, word_data: WordRequest):
    if model not in text2voice_model_dict:
        raise HTTPException(status_code=400, detail="无效的模型名称")
    
    try:
        # 收集所有需要转换的文本
        all_texts = [word_data.center_word] + word_data.surrounding_words
        
        # 批量生成语音
        voice_urls = batch_create_requests(all_texts)
        
        # 构建返回数据
        response_data = {
            "word": {
                "center_word": {
                    "word": word_data.center_word,
                    "word_romaji": word_data.center_word_romaji,
                    "word_translation": word_data.center_word_translation,
                    "word_voice_url": voice_urls[word_data.center_word]
                },
                "surrounding_words": {}
            }
        }
        
        # 加周边词
        for idx, (word, romaji, translation) in enumerate(
            zip(word_data.surrounding_words, 
                word_data.surrounding_words_romaji,
                word_data.surrounding_words_translation), 1):
            response_data["word"]["surrounding_words"][f"surrounding_word_{idx}"] = {
                "word": word,
                "word_romaji": romaji,
                "word_translation": translation,
                "word_voice_url": voice_urls[word]
            }
        
        return response_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/products/japanese-vocab/step4/get_random_bgm")
async def get_random_bgm():
    """获取随机背景音乐"""
    try:
        # 直接使用Docker容器中的固定路径
        bgm_dir = "/app/static/bgm"
        print(f"使用固定BGM目录: {bgm_dir}")
        
        # 检查目录是否存在
        if not os.path.exists(bgm_dir):
            print(f"目录不存在: {bgm_dir}")
            raise HTTPException(status_code=404, detail=f"背景音乐目录不存在: {bgm_dir}")
        
        # 列出目录内容
        try:
            dir_contents = os.listdir(bgm_dir)
            print(f"目录内容: {dir_contents}")
        except Exception as e:
            print(f"列出目录错误: {e}")
            raise HTTPException(status_code=500, detail=f"无法访问背景音乐目录: {str(e)}")
        
        # 获取所有MP3文件
        mp3_files = [f for f in dir_contents if f.lower().endswith(('.mp3', '.wav', '.MP3', '.WAV'))]
        print(f"找到的音乐文件: {mp3_files}")
        
        if not mp3_files:
            print(f"目录中没有音乐文件: {bgm_dir}")
            raise HTTPException(status_code=404, detail=f"没有可用的背景音乐文件。目录: {bgm_dir}")
        
        # 随机选择一个文件
        random_music = random.choice(mp3_files)
        print(f"选择的音乐文件: {random_music}")
        
        # 验证文件是否存在
        full_path = os.path.join(bgm_dir, random_music)
        print(f"完整路径: {full_path}")
        print(f"文件存在: {os.path.exists(full_path)}")
        
        # 返回音乐URL
        return {
            "music_url": f"/static/bgm/{random_music}"
        }
        
    except Exception as e:
        print(f"Error in get_random_bgm: {e}")  # 添加错误日志
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/products/japanese-vocab/step6/video_generator")
async def video_generator(request_data: Dict[str, Any]):
    ProgressManager.reset_progress()  # 重置进度
    
    try:
        # 提取数据
        extracted_data = extract_data_from_dict(request_data)
        
        # 生成视频
        video_url = generate_video(extracted_data)
        
        return {
            "status": "success",
            "video_url": video_url,
            "message": "视频生成成功"
        }
    except Exception as e:
        ProgressManager.reset_progress()  # 出错时重置进度
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        ProgressManager.reset_progress()  # 确保进度重置

@router.get("/products/japanese-vocab/step6/progress")
async def get_progress():
    async def event_generator():
        last_progress = -1  # 用于跟踪进度变化
        
        try:
            while True:
                current_progress = ProgressManager.get_progress()
                
                # 只在进度发生变化时发送更新
                if current_progress != last_progress:
                    print(f"Progress update: {current_progress}%")  # 调试日志
                    yield {
                        "event": "message",
                        "data": json.dumps({"progress": current_progress})
                    }
                    last_progress = current_progress
                
                # 如果进度达到100%，结束流
                if current_progress >= 100:
                    break
                    
                await asyncio.sleep(0.5)  # 每500ms检查一次进度
                
        except Exception as e:
            print(f"Error in event generator: {e}")
            
        finally:
            ProgressManager.reset_progress()

    return EventSourceResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "http://localhost:3000",
            "Access-Control-Allow-Credentials": "true"
        }
    )
