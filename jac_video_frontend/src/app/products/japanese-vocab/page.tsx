'use client';

import { useState, useRef, useEffect } from 'react';

interface StepProps {
  title: string;
  isActive: boolean;
  onClick: () => void;
}

const Step = ({ title, isActive, onClick }: StepProps) => (
  <button
    onClick={onClick}
    className={`w-full p-4 text-left rounded-lg transition-all duration-200 
      ${isActive 
        ? 'bg-white shadow-md border-l-4 border-[var(--primary)] text-[var(--primary)]' 
        : 'bg-gray-50 hover:bg-gray-100 text-gray-700'
      }`}
  >
    <div className="flex items-center gap-3">
      <div className={`w-8 h-8 rounded-full flex items-center justify-center transition-all duration-200
        ${isActive 
          ? 'bg-gradient-to-r from-[var(--primary)] to-[var(--secondary)] text-white shadow-md' 
          : 'bg-gradient-to-r from-gray-50 to-gray-100 text-gray-500 hover:from-gray-100 hover:to-gray-200'
        } border border-white/20 backdrop-blur-sm`}
      >
        <span className={`text-sm font-medium ${isActive ? 'drop-shadow-sm' : ''}`}>
          {title.match(/\d+/)?.[0]}
        </span>
      </div>
      <div className="flex flex-col">
        <span className={`text-xs text-gray-500 ${isActive ? 'text-[var(--primary)]/70' : ''}`}>
          {title.match(/步骤[一二三四五六]/)?.[0]}
        </span>
        <span className={`font-medium transition-colors duration-200
          ${isActive ? 'text-[var(--primary)]' : 'text-gray-700'}`}>
          {title.replace(/步骤[一二三四五六]、/, '')}
        </span>
      </div>
    </div>
  </button>
);

interface VideoParams {
  resolution: string;
  aspectRatio: string;
  orientation: string;
  frameRate: number;
}

// 修改 FinalData 接口定义
interface FinalData {
  step1?: {
    title: string;
    shape: string;
    shapeColor: string;  // 改为 shapeColor
    fontColor: string;
  };
  step2?: {
    model: string;
    word: string;
    content: any;  // 使用 vocabData 的类型
  };
  step3?: {
    model: string;
    resolution: string;
    aspectRatio: string;
    orientation: string;
    frameRate: number;
    imageUrl: string | null;
  };
  step4?: {
    mode: 'random' | 'upload';
    musicUrl: string | null;
  };
  step5?: {
    model: string;
    voiceData: any;  // 使用 voiceGenerationResult 的类型
  };
}

// 修改 getApiBaseUrl 函数
const getApiBaseUrl = () => {
  if (!process.env.NEXT_PUBLIC_API_BASE_URL) {
    console.warn('NEXT_PUBLIC_API_BASE_URL is not set');
    return 'http://localhost:5000'; // 默认值
  }
  return process.env.NEXT_PUBLIC_API_BASE_URL;
};

// 修改 getFullResourceUrl 函数
const getFullResourceUrl = (resourcePath: string) => {
  const baseUrl = getApiBaseUrl();
  
  // 添加调试日志
  console.log('Original resourcePath:', resourcePath);
  
  // 如果是完整URL，替换域名部分
  if (resourcePath.startsWith('http')) {
    const url = new URL(resourcePath);
    return `${baseUrl}${url.pathname}`;
  }
  
  // 确保 resourcePath 以 / 开头
  if (!resourcePath.startsWith('/')) {
    resourcePath = '/' + resourcePath;
  }
  
  // 构建完整URL
  const fullUrl = `${baseUrl}${resourcePath}`;
  console.log('Constructed full URL:', fullUrl);
  return fullUrl;
};

export default function JapaneseVocabPage() {
  const [activeStep, setActiveStep] = useState(1);
  const [loading, setLoading] = useState(false);
  
  // 修改表单状态
  const [formData, setFormData] = useState({
    title: '',
    shape: 'rectangle', // 默认矩形
    backgroundColor: '#FFFFFF', // 默认白色
    fontColor: '#FFA31A',     // 默认橙色
  });

  // 形状选项
  const shapeOptions = [
    { value: 'rectangle', label: '矩形', icon: '⬜' },
    { value: 'circle', label: '圆形', icon: '⭕' },
    { value: 'roundedRect', label: '圆角矩形', icon: '🔲' },
  ];

  // 处理表单变化
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // 添加文本内容的状态
  const [vocabInput, setVocabInput] = useState('');
  const [vocabData, setVocabData] = useState<any>(null);
  const [generating, setGenerating] = useState(false);

  // 处理生成请求
  const handleGenerate = async () => {
    if (!vocabInput.trim()) return;
    
    setGenerating(true);
    try {
      const params = new URLSearchParams({
        model: textModel,
        word: vocabInput
      });
      
      const url = `${getApiBaseUrl()}/products/japanese-vocab/step2/get_text_by_model?${params}`;
      console.log('Request URL:', url);
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '生成失败');
      }

      const data = await response.json();
      if (!data.content_dict) {
        throw new Error('返回数据格式错误');
      }
      setVocabData(data.content_dict);
    } catch (error) {
      console.error('生成失败:', error);
      // TODO: 添加错误提示UI
    } finally {
      setGenerating(false);
    }
  };

  // 添加音乐相关状态
  const [musicMode, setMusicMode] = useState<'random' | 'upload'>('random');
  const [musicFile, setMusicFile] = useState<string | null>(null);
  const [isGeneratingMusic, setIsGeneratingMusic] = useState(false);
  const audioRef = useRef<HTMLAudioElement>(null);

  // 处理随机生成音乐
  const handleGenerateRandomMusic = async () => {
    setIsGeneratingMusic(true);
    try {
      const response = await fetch(
        `${getApiBaseUrl()}/products/japanese-vocab/step4/get_random_bgm`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        throw new Error('获取背景音乐失败');
      }

      const data = await response.json();
      if (!data.music_url) {
        throw new Error('返回数据格式错误');
      }

      setMusicFile(`${getApiBaseUrl()}${data.music_url}`);
      
      // 如果有频元素，重新加载
      if (audioRef.current) {
        audioRef.current.load();
      }
    } catch (error) {
      console.error('音乐生成失败:', error);
      alert('获取背景音乐失败: ' + (error instanceof Error ? error.message : '未知错误'));
    } finally {
      setIsGeneratingMusic(false);
    }
  };

  // 处理音乐文件上传
  const handleMusicUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const url = URL.createObjectURL(file);
      setMusicFile(url);
    }
  };

  const steps = [
    { id: 1, title: '步骤一、标题形状设定' },
    { id: 2, title: '步骤二、文本内容设定' },
    { id: 3, title: '步骤三、背景图片设定' },
    { id: 4, title: '步骤四、背景音乐设定' },
    { id: 5, title: '步骤五、人物音频合成' },
    { id: 6, title: '步骤六、视频生成' },
  ];

  // 添加最终生成状态
  const [finalData, setFinalData] = useState<any>(null);
  const [isFinalGenerating, setIsFinalGenerating] = useState(false);

  // 添加视频URL状态
  const [generatedVideoUrl, setGeneratedVideoUrl] = useState<string | null>(null);

  // 添加进度状态
  const [progress, setProgress] = useState(0);
  const eventSourceRef = useRef<EventSource | null>(null);

  // 在组件卸载时清理 EventSource
  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  // 修改生成函数，添加进度监听
  const handleFinalGenerate = async () => {
    console.log('Final generate with vocab data:', vocabData);
    setLoading(true);
    setProgress(0);
    
    try {
      const allStepsData: FinalData = {
        step1: {
          title: formData.title,
          shape: formData.shape,
          shapeColor: formData.backgroundColor,
          fontColor: formData.fontColor
        },
        step2: {
          model: textModel,
          word: vocabData.center_word,
          content: vocabData
        },
        step3: {
          model: bgModel,
          resolution: videoParams.resolution,
          aspectRatio: videoParams.aspectRatio,
          orientation: videoParams.orientation,
          frameRate: videoParams.frameRate,
          imageUrl: backgroundImage
        },
        step4: {
          mode: musicMode,
          musicUrl: musicFile ? (
            musicMode === 'random' ? musicFile : getFullResourceUrl(musicFile)
          ) : null,
        },
        step5: {
          model: selectedModel,
          voiceData: voiceGenerationResult,
        }
      };

      // 设置最终数据用于显示
      setFinalData(allStepsData);
      
      // 创建新的 EventSource 来监听进度
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }

      eventSourceRef.current = new EventSource(`${getApiBaseUrl()}/products/japanese-vocab/step6/progress`);
      
      eventSourceRef.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('Progress update:', data);
          if (data && typeof data.progress === 'number') {
            setProgress(data.progress);
          }
        } catch (error) {
          console.error('Error parsing progress data:', error);
        }
      };

      eventSourceRef.current.onerror = (error) => {
        console.error('EventSource error:', error);
        // 如果连接失败，尝试重新连接
        setTimeout(() => {
          if (eventSourceRef.current) {
            eventSourceRef.current.close();
          }
          eventSourceRef.current = new EventSource(`${getApiBaseUrl()}/products/japanese-vocab/step6/progress`);
        }, 1000);
      };

      // 调用生成接口
      const response = await fetch(
        `${getApiBaseUrl()}/products/japanese-vocab/step6/video_generator`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(allStepsData)
        }
      );

      if (!response.ok) {
        throw new Error('视频生成失败');
      }

      const data = await response.json();
      if (!data.video_url) {
        throw new Error('返回数据格式错误');
      }

      setGeneratedVideoUrl(`${getApiBaseUrl()}${data.video_url}`);

    } catch (error) {
      console.error('Error generating video:', error);
      alert('视频生成失败: ' + (error instanceof Error ? error.message : String(error)));
    } finally {
      // 确保关闭 EventSource
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
      setLoading(false);
    }
  };

  // 修改 handleDownload 函数
  const handleDownload = async () => {
    if (generatedVideoUrl) {
      try {
        // 显示加载状态
        setLoading(true);
        
        // 获取视频文件
        const response = await fetch(getFullResourceUrl(generatedVideoUrl));
        const blob = await response.blob();
        
        // 创建下载链接
        const url = window.URL.createObjectURL(blob);
        
        // 创建下载对话框
        const a = document.createElement('a');
        a.href = url;
        a.download = `japanese_vocab_${Date.now()}.mp4`; // 设置文件名
        
        // 模拟点击下载
        document.body.appendChild(a);
        a.click();
        
        // 清理
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } catch (error) {
        console.error('下载失败:', error);
        alert('下载失败: ' + (error instanceof Error ? error.message : '未知错误'));
      } finally {
        setLoading(false);
      }
    }
  };

  // 添加背景设置相关状态
  const [videoParams, setVideoParams] = useState<VideoParams>({
    resolution: "720p",
    aspectRatio: "16:9",
    orientation: "portrait",
    frameRate: 30
  });

  const [bgMode, setBgMode] = useState<'ai' | 'upload'>('ai');
  const [backgroundImage, setBackgroundImage] = useState<string | null>(null);
  const [isGeneratingBg, setIsGeneratingBg] = useState(false);

  // 处理AI生成背景
  const handleGenerateBackground = async () => {
    if (!vocabInput.trim()) {
      alert('请先输入单词');
      return;
    }
    
    setIsGeneratingBg(true);
    try {
      // 使用 URLSearchParams 构建查询参数
      const params = new URLSearchParams({
        model: bgModel,
        resolution: videoParams.resolution,
        aspect_ratio: videoParams.aspectRatio,
        orientation: videoParams.orientation,
        word: vocabInput
      });

      const url = `${getApiBaseUrl()}/products/japanese-vocab/step3/get_image_by_model?${params}`;
      console.log('Request URL:', url);

      const response = await fetch(url);

      if (!response.ok) {
        if (response.status === 404) {
          alert('API 路径不存在，请检查后端路由配置');
          return;
        }
        const errorData = await response.json().catch(() => ({ detail: '请求失败' }));
        alert(errorData.detail || '图片生成失败');
        return;
      }

      const data = await response.json();
      if (!data.image_url) {
        throw new Error('返回数据格式错误');
      }
      setBackgroundImage(data.image_url);

    } catch (error) {
      console.error('背景生成失败:', error);
      alert('背景生成失败: ' + (error instanceof Error ? error.message : '未知错误'));
    } finally {
      setIsGeneratingBg(false);
    }
  };

  // 处理背景图片上传
  const handleBackgroundUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const url = URL.createObjectURL(file);
      setBackgroundImage(url);
    }
  };

  // 添加缩放相关状态
  const [scale, setScale] = useState(1);
  const [isDragging, setIsDragging] = useState(false);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [startPosition, setStartPosition] = useState({ x: 0, y: 0 });

  // 处理缩放
  const handleScaleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setScale(Number(e.target.value));
  };

  // 处理拖动开始
  const handleDragStart = (e: React.MouseEvent) => {
    setIsDragging(true);
    setStartPosition({
      x: e.clientX - position.x,
      y: e.clientY - position.y
    });
  };

  // 处理拖动
  const handleDrag = (e: React.MouseEvent) => {
    if (!isDragging) return;
    
    setPosition({
      x: e.clientX - startPosition.x,
      y: e.clientY - startPosition.y
    });
  };

  // 处理拖动结束
  const handleDragEnd = () => {
    setIsDragging(false);
  };

  // 添加语音合成相关状态
  const [selectedModel, setSelectedModel] = useState('有道智云');
  const [isGeneratingVoice, setIsGeneratingVoice] = useState(false);
  const [voiceFile, setVoiceFile] = useState<string | null>(null);

  // 语音模选项
  const voiceModels = [
    { id: '有道智云', name: '有道智云' },
    { id: '施工ing', name: '施工ing' },
  ];

  // 添加新的状态来存储语音生成结果
  const [voiceGenerationResult, setVoiceGenerationResult] = useState<any>(null);

  // 修改 handleGenerateVoice 函数
  const handleGenerateVoice = async () => {
    if (!vocabData) {
      alert('请先在第二步生成文本内容');
      return;
    }

    setIsGeneratingVoice(true);
    try {
      // 构建请求数据
      const requestData = {
        center_word: vocabData.center_word,
        center_word_romaji: vocabData.center_word_romaji,
        center_word_translation: vocabData.center_word_translation,
        surrounding_words: vocabData.surrounding_words,
        surrounding_words_romaji: vocabData.surrounding_words_romaji,
        surrounding_words_translation: vocabData.surrounding_words_translation
      };

      // 发送请
      const response = await fetch(
        `${getApiBaseUrl()}/products/japanese-vocab/step5/get_voice_by_model?model=${selectedModel}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestData)
        }
      );

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Error response:', errorText);
        throw new Error(errorText);
      }

      const data = await response.json();
      setVoiceGenerationResult(data);  // 保存返回的数据

    } catch (error) {
      console.error('语音生成失败:', error);
      const errorMessage = error instanceof Error ? error.message : JSON.stringify(error);
      alert('语音生成失败: ' + errorMessage);
    } finally {
      setIsGeneratingVoice(false);
    }
  };

  // 添加新的状态来存储所有音频文件
  const [allVoiceFiles, setAllVoiceFiles] = useState<{
    center_word: string;
    surrounding_words: string[];
  } | null>(null);

  // 添加文本生成模型选择状
  const [textModel, setTextModel] = useState('Spark Max');
  
  // 文本生成模型选项
  const textModels = [
    { id: 'Spark 4.0 Ultra', name: 'Spark 4.0 Ultra' },
    { id: 'Spark Max-32k', name: 'Spark Max-32k' },
    { id: 'Spark Max', name: 'Spark Max' },
    { id: 'Spark Lite', name: 'Spark Lite' },
    { id: 'Spark Pro', name: 'Spark Pro' },
    { id: 'Spark Pro-128k', name: 'Spark Pro-128k' },
  ];

  // 添加背景生成模型选择状态
  const [bgModel, setBgModel] = useState('讯飞星火认知大模型');
  
  // 背景生成模型选项
  const bgModels = [
    { id: '讯飞星火认知大模型', name: '讯飞星火认知大模型' },
    { id: '施工ing', name: '施工ing' },
  ];

  // 添加输入单词状态（第一步的输入）
  const [inputWord, setInputWord] = useState("");

  // 在第一步中添加单词输入的处理
  const handleWordInput = (word: string) => {
    setInputWord(word);
    // ... 其他处理辑 ...
  };

  // 在组件顶部添加状态
  const [showVoiceResult, setShowVoiceResult] = useState(false);

  // 在第二步修改数据时
  const handleVocabDataChange = (newData: any) => {
    console.log('Vocab data updated:', newData);
    setVocabData(newData);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 顶部标题区域 */}
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <h1 className="main-title">日语单词学习视频生成器</h1>
          <p className="sub-title">按以下步骤设置，快速生成日语单词学习短视频</p>
        </div>
      </div>

      {/* 主要内容区域 */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex gap-8">
          {/* 左侧步骤导航 - 优化样式 */}
          <div className="w-72 space-y-2 flex-shrink-0">
            {steps.map((step) => (
              <Step
                key={step.id}
                title={step.title}
                isActive={activeStep === step.id}
                onClick={() => setActiveStep(step.id)}
              />
            ))}
          </div>

          {/* 右侧内容区域 - 改进视觉层次 */}
          <div className="flex-1 bg-white rounded-xl shadow-sm">
            <div className="p-8">
              {/* 各步骤的内容区域 */}
              {activeStep === 1 && (
                <div className="space-y-8">
                  <div className="border-b pb-6">
                    <h2 className="text-xl font-semibold text-gray-900">标题和形状设置</h2>
                    <p className="mt-2 text-gray-600">设置视频的标题，选择合适的形状样式和颜色，这些将作为视频的主要视觉元素</p>
                  </div>

                  {/* 内容部分使用卡片式布局 */}
                  <div className="grid gap-8">
                    {/* 标题输入 */}
                    <div className="card p-6">
                      <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-4">
                        标题
                      </label>
                      <input
                        type="text"
                        id="title"
                        name="title"
                        value={formData.title}
                        onChange={handleInputChange}
                        placeholder="请输入视频标题"
                        className="w-full px-4 py-2.5 bg-white border-2 border-[var(--primary)] rounded-lg shadow-sm hover:shadow-md transition-all duration-200"
                      />
                    </div>

                    {/* 形状选择 */}
                    <div className="card p-6">
                      <label className="block text-sm font-medium text-gray-700 mb-4">
                        形状选择
                      </label>
                      <div className="flex gap-4">
                        {shapeOptions.map((option) => (
                          <label
                            key={option.value}
                            className={`flex items-center gap-2 p-3 border rounded-lg cursor-pointer
                              transition-all duration-200 hover:bg-gray-50
                              ${formData.shape === option.value 
                                ? 'border-[#FF3366] bg-pink-50' 
                                : 'border-gray-200'
                              }`}
                          >
                            <input
                              type="radio"
                              name="shape"
                              value={option.value}
                              checked={formData.shape === option.value}
                              onChange={handleInputChange}
                              className="hidden"
                            />
                            <span className="text-2xl">{option.icon}</span>
                            <span className="text-sm">{option.label}</span>
                          </label>
                        ))}
                      </div>
                    </div>

                    {/* 颜色设置 */}
                    <div className="grid grid-cols-2 gap-6">
                      {/* 背景颜色 */}
                      <div className="card p-6">
                        <label htmlFor="backgroundColor" className="block text-sm font-medium text-gray-700 mb-4">
                          形状颜色
                        </label>
                        <div className="flex items-center gap-3">
                          <input
                            type="color"
                            id="backgroundColor"
                            name="backgroundColor"
                            value={formData.backgroundColor}
                            onChange={handleInputChange}
                            className="w-10 h-10 rounded border border-gray-200 cursor-pointer"
                          />
                          <input
                            type="text"
                            value={formData.backgroundColor}
                            onChange={handleInputChange}
                            name="backgroundColor"
                            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg"
                          />
                        </div>
                      </div>

                      {/* 文字颜色 */}
                      <div className="card p-6">
                        <label htmlFor="fontColor" className="block text-sm font-medium text-gray-700 mb-4">
                          文字颜色
                        </label>
                        <div className="flex items-center gap-3">
                          <input
                            type="color"
                            id="fontColor"
                            name="fontColor"
                            value={formData.fontColor}
                            onChange={handleInputChange}
                            className="w-10 h-10 rounded border border-gray-200 cursor-pointer"
                          />
                          <input
                            type="text"
                            value={formData.fontColor}
                            onChange={handleInputChange}
                            name="fontColor"
                            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg"
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* 步骤二的内容 */}
              {activeStep === 2 && (
                <div className="space-y-6">
                  <div className="mb-6">
                    <h2 className="text-xl font-semibold">文本内容设置</h2>
                    <p className="mt-2 text-gray-600">输入日语单词（如 寿司），点击生成按钮，系统将自动生成相关的单词，罗马音及翻译等内容</p>
                  </div>
                  {/* 输入和生成区域 */}
                  <div className="flex gap-4">
                    {/* 添加模型选择 */}
                    <select
                      value={textModel}
                      onChange={(e) => setTextModel(e.target.value)}
                      className="input-primary"
                    >
                      {textModels.map(model => (
                        <option key={model.id} value={model.id}>
                          {model.name}
                        </option>
                      ))}
                    </select>

                    <input
                      type="text"
                      value={vocabInput}
                      onChange={(e) => setVocabInput(e.target.value)}
                      placeholder="请输入日语单词"
                      className="flex-1 px-4 py-2.5 bg-white border-2 border-[var(--primary)] rounded-lg shadow-sm hover:shadow-md transition-all duration-200"
                    />
                    <button
                      onClick={handleGenerate}
                      disabled={generating || !vocabInput.trim()}
                      className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed min-w-[100px]"
                    >
                      {generating ? '生成中...' : '生成'}
                    </button>
                  </div>

                  {/* 修改生成结果展示区域 */}
                  <div className="mt-6">
                    <h3 className="text-sm font-medium text-gray-700 mb-2">生成结果</h3>
                    <div className="card p-4">
                      {vocabData ? (
                        <div className="space-y-4">
                          {/* 中心词编辑 */}
                          <div className="space-y-2">
                            <h4 className="text-sm font-medium text-gray-700">中心词</h4>
                            <div className="grid grid-cols-3 gap-4">
                              <div>
                                <input
                                  type="text"
                                  value={vocabData.center_word}
                                  onChange={(e) => handleVocabDataChange({
                                    ...vocabData,
                                    center_word: e.target.value
                                  })}
                                  className="w-full px-4 py-2.5 bg-white border-2 border-[var(--primary)] rounded-lg shadow-sm hover:shadow-md transition-all duration-200"
                                  placeholder="日语"
                                />
                              </div>
                              <div>
                                <input
                                  type="text"
                                  value={vocabData.center_word_romaji}
                                  onChange={(e) => handleVocabDataChange({
                                    ...vocabData,
                                    center_word_romaji: e.target.value
                                  })}
                                  className="w-full px-4 py-2.5 bg-white border-2 border-[var(--primary)] rounded-lg shadow-sm hover:shadow-md transition-all duration-200"
                                  placeholder="罗马音"
                                />
                              </div>
                              <div>
                                <input
                                  type="text"
                                  value={vocabData.center_word_translation}
                                  onChange={(e) => handleVocabDataChange({
                                    ...vocabData,
                                    center_word_translation: e.target.value
                                  })}
                                  className="w-full px-4 py-2.5 bg-white border-2 border-[var(--primary)] rounded-lg shadow-sm hover:shadow-md transition-all duration-200"
                                  placeholder="翻译"
                                />
                              </div>
                            </div>
                          </div>

                          {/* 相关词编辑 */}
                          <div className="space-y-2">
                            <div className="flex justify-between items-center">
                              <h4 className="text-sm font-medium text-gray-700">相关词</h4>
                              <button
                                onClick={() => {
                                  handleVocabDataChange({
                                    ...vocabData,
                                    surrounding_words: [...vocabData.surrounding_words, ""],
                                    surrounding_words_romaji: [...vocabData.surrounding_words_romaji, ""],
                                    surrounding_words_translation: [...vocabData.surrounding_words_translation, ""]
                                  })
                                }}
                                className="text-sm text-[#FF3366] hover:text-[#FF4775]"
                              >
                                添加词条
                              </button>
                            </div>
                            
                            {vocabData.surrounding_words.map((word: string, index: number) => (
                              <div key={index} className="grid grid-cols-3 gap-4 mt-2">
                                <div>
                                  <input
                                    type="text"
                                    value={word}
                                    onChange={(e) => {
                                      const newWords = [...vocabData.surrounding_words]
                                      newWords[index] = e.target.value
                                      handleVocabDataChange({
                                        ...vocabData,
                                        surrounding_words: newWords
                                      })
                                    }}
                                    className="w-full px-4 py-2.5 bg-white border-2 border-[var(--primary)] rounded-lg shadow-sm hover:shadow-md transition-all duration-200"
                                    placeholder="日语"
                                  />
                                </div>
                                <div>
                                  <input
                                    type="text"
                                    value={vocabData.surrounding_words_romaji[index]}
                                    onChange={(e) => {
                                      const newRomaji = [...vocabData.surrounding_words_romaji]
                                      newRomaji[index] = e.target.value
                                      handleVocabDataChange({
                                        ...vocabData,
                                        surrounding_words_romaji: newRomaji
                                      })
                                    }}
                                    className="w-full px-4 py-2.5 bg-white border-2 border-[var(--primary)] rounded-lg shadow-sm hover:shadow-md transition-all duration-200"
                                    placeholder="罗马音"
                                  />
                                </div>
                                <div className="flex gap-2">
                                  <input
                                    type="text"
                                    value={vocabData.surrounding_words_translation[index]}
                                    onChange={(e) => {
                                      const newTranslations = [...vocabData.surrounding_words_translation]
                                      newTranslations[index] = e.target.value
                                      handleVocabDataChange({
                                        ...vocabData,
                                        surrounding_words_translation: newTranslations
                                      })
                                    }}
                                    className="flex-1 px-4 py-2.5 bg-white border-2 border-[var(--primary)] rounded-lg shadow-sm hover:shadow-md transition-all duration-200"
                                    placeholder="翻译"
                                  />
                                  <button
                                    onClick={() => {
                                      const newData = {
                                        ...vocabData,
                                        surrounding_words: vocabData.surrounding_words.filter((_: string, i: number) => i !== index),
                                        surrounding_words_romaji: vocabData.surrounding_words_romaji.filter((_: string, i: number) => i !== index),
                                        surrounding_words_translation: vocabData.surrounding_words_translation.filter((_: string, i: number) => i !== index)
                                      }
                                      handleVocabDataChange(newData)
                                    }}
                                    className="px-2 py-2 text-gray-500 hover:text-red-500"
                                  >
                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                    </svg>
                                  </button>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      ) : (
                        <div className="text-gray-500">
                          生成内容将显示在这里...
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* 步骤三的内容 */}
              {activeStep === 3 && (
                <div className="space-y-6">
                  <div className="mb-6">
                    <h2 className="text-xl font-semibold">背景图片设置</h2>
                    <p className="mt-2 text-gray-600">设置视频的基本参数，选择AI生成（点击AI生成景按钮生成图片）或上传自定义背景图片，让视频更加生动</p>
                  </div>
                  <div className="flex gap-8">
                    {/* 左侧参数置 */}
                    <div className="w-1/3 space-y-4">
                      <div className="space-y-2">
                        <label className="block text-sm font-medium text-gray-700">分辨率</label>
                        <select
                          value={videoParams.resolution}
                          onChange={(e) => setVideoParams({...videoParams, resolution: e.target.value})}
                          className="input-primary"
                        >
                          <option value="480p">480p</option>
                          <option value="720p">720p</option>
                          <option value="1080p">1080p</option>
                        </select>
                      </div>

                      <div className="space-y-2">
                        <label className="block text-sm font-medium text-gray-700">宽高比</label>
                        <select
                          value={videoParams.aspectRatio}
                          onChange={(e) => setVideoParams({...videoParams, aspectRatio: e.target.value})}
                          className="input-primary"
                        >
                          <option value="16:9">16:9</option>
                          <option value="4:3">4:3</option>
                          <option value="1:1">1:1</option>
                        </select>
                      </div>

                      <div className="space-y-2">
                        <label className="block text-sm font-medium text-gray-700">方向</label>
                        <select
                          value={videoParams.orientation}
                          onChange={(e) => setVideoParams({...videoParams, orientation: e.target.value})}
                          className="input-primary"
                        >
                          <option value="portrait">竖向</option>
                          <option value="landscape">横向</option>
                        </select>
                      </div>

                      {/* 帧率设置 */}
                      <div className="space-y-2">
                        <label className="block text-sm font-medium text-gray-700">帧率</label>
                        <select
                          value={videoParams.frameRate}
                          onChange={(e) => setVideoParams({...videoParams, frameRate: Number(e.target.value)})}
                          className="input-primary"
                        >
                          <option value={24}>24 fps</option>
                          <option value={25}>25 fps</option>
                          <option value={30}>30 fps</option>
                          <option value={60}>60 fps</option>
                        </select>
                      </div>
                    </div>

                    {/* 右侧背景设置 */}
                    <div className="flex-1 space-y-4">
                      {/* 选 - 只保留AI生成和用户上传 */}
                      <div className="flex gap-2 mb-6">
                        {[
                          { id: 'ai', label: 'AI生成' },
                          { id: 'upload', label: '用户上传' }
                        ].map((tab) => (
                          <button
                            key={tab.id}
                            onClick={() => setBgMode(tab.id as 'ai' | 'upload')}
                            className={`btn-secondary ${bgMode === tab.id ? 'active' : ''}`}
                          >
                            {tab.label}
                          </button>
                        ))}
                      </div>

                      {/* 景操作区域 */}
                      <div className="p-6 border-2 border-dashed border-gray-200 rounded-lg">
                        {bgMode === 'ai' ? (
                          <div className="flex gap-4 items-center">
                            {/* 添加模型选择 */}
                            <select
                              value={bgModel}
                              onChange={(e) => setBgModel(e.target.value)}
                              className="input-primary"
                            >
                              {bgModels.map(model => (
                                <option key={model.id} value={model.id}>
                                  {model.name}
                                </option>
                              ))}
                            </select>

                            <button
                              onClick={handleGenerateBackground}
                              disabled={isGeneratingBg}
                              className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed min-w-[100px]"
                            >
                              {isGeneratingBg ? '生成中...' : 'AI生成背景'}
                            </button>
                          </div>
                        ) : (
                          <div className="text-center">
                            <div className="btn-primary cursor-pointer">
                              选择文件
                            </div>
                          </div>
                        )}
                      </div>

                      {/* 预览区 */}
                      {backgroundImage && (
                        <div className="mt-6">
                          <h3 className="text-sm font-medium text-gray-700 mb-3">背景预览</h3>
                          <div className="relative w-full h-64 bg-gray-100 rounded-lg overflow-hidden">
                            <img
                              src={backgroundImage ? getFullResourceUrl(backgroundImage) : ''}
                              alt="背景预览"
                              className="w-full h-full object-contain"
                              onError={(e) => {
                                console.error('Image load error:', e);
                                console.log('Failed URL:', e.currentTarget.src);
                              }}
                            />
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* 步骤四的内容 */}
              {activeStep === 4 && (
                <div className="space-y-6">
                  <div className="mb-6">
                    <h2 className="text-xl font-semibold">背景音乐设置</h2>
                    <p className="mt-2 text-gray-600">选择随机生成背景音乐或上传己有音乐文件，为视频添加合适的氛围</p>
                  </div>
                  {/* 音乐模式选择 */}
                  <div className="grid grid-cols-2 gap-4">
                    <button
                      onClick={() => setMusicMode('random')}
                      className={`btn-secondary ${musicMode === 'random' ? 'active' : ''}`}
                    >
                      <div className="text-2xl mb-2">🎲</div>
                      <div className="font-medium">随机生成</div>
                    </button>
                    
                    <button
                      onClick={() => setMusicMode('upload')}
                      className={`btn-secondary ${musicMode === 'upload' ? 'active' : ''}`}
                    >
                      <div className="text-2xl mb-2">📤</div>
                      <div className="font-medium">上传MP3</div>
                    </button>
                  </div>

                  {/* 乐操作区域 */}
                  <div className="mt-8 p-6 border-2 border-dashed border-gray-200 rounded-lg">
                    {musicMode === 'random' ? (
                      <div className="text-center">
                        <button
                          onClick={handleGenerateRandomMusic}
                          disabled={isGeneratingMusic}
                          className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          {isGeneratingMusic ? '生成中...' : '随机生成音乐'}
                        </button>
                      </div>
                    ) : (
                      <div className="text-center">
                        <div className="btn-primary cursor-pointer">
                          选择文件
                        </div>
                      </div>
                    )}
                  </div>

                  {/* 音乐预览 */}
                  {musicFile && (
                    <div className="mt-6">
                      <h3 className="text-sm font-medium text-gray-700 mb-3">音乐预览</h3>
                      <audio 
                        ref={audioRef}
                        controls 
                        className="w-full"
                        src={musicFile ? getFullResourceUrl(musicFile) : ''}
                      >
                        您的浏览器不支持音频播放
                      </audio>
                    </div>
                  )}
                </div>
              )}

              {/* 步骤五的内容 */}
              {activeStep === 5 && (
                <div className="space-y-6">
                  <div className="mb-6">
                    <h2 className="text-xl font-semibold">人物音频合成</h2>
                    <p className="mt-2 text-gray-600">选择合适的语音模型，点击生成按钮，生成清晰自的日语发音</p>
                  </div>
                  
                  {/* 模型选择和生成按钮 */}
                  <div className="flex gap-4 items-center">
                    <div className="flex-1">
                      <select
                        value={selectedModel}
                        onChange={(e) => setSelectedModel(e.target.value)}
                        className="input-primary"
                      >
                        {voiceModels.map(model => (
                          <option key={model.id} value={model.id}>
                            {model.name}
                          </option>
                        ))}
                      </select>
                    </div>
                    
                    <button
                      onClick={handleGenerateVoice}
                      disabled={isGeneratingVoice}
                      className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed min-w-[100px]"
                    >
                      {isGeneratingVoice ? '生成中...' : '生成'}
                    </button>
                  </div>

                  {/* 生成结果区域 */}
                  <div className="mt-6">
                    <div className="flex justify-between items-center mb-2">
                      <h3 className="text-sm font-medium text-gray-700">生成结果</h3>
                      {voiceGenerationResult && (
                        <button
                          onClick={() => setShowVoiceResult(!showVoiceResult)}
                          className="text-sm text-[#FF3366] hover:text-[#FF4775] transition-colors"
                        >
                          {showVoiceResult ? '收起详情' : '查看详情'}
                        </button>
                      )}
                    </div>
                    
                    <div className="card p-4">
                      {voiceGenerationResult ? (
                        <div className="space-y-2">
                          {/* 成功提示 */}
                          <div className="flex items-center text-green-600 gap-2">
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                            </svg>
                            <span>音频生成成功！</span>
                          </div>
                          
                          {/* 详结果（可折叠） */}
                          {showVoiceResult && (
                            <pre className="mt-4 whitespace-pre-wrap text-sm text-gray-600">
                              {JSON.stringify(voiceGenerationResult, null, 2)}
                            </pre>
                          )}
                        </div>
                      ) : (
                        <div className="text-gray-500">
                          生成的内容将显示在这里...
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* 步骤六的内容 */}
              {activeStep === 6 && (
                <div className="space-y-6">
                  <div className="mb-6">
                    <h2 className="text-xl font-semibold">视频生成</h2>
                    <p className="mt-2 text-gray-600">点击生成按钮，预计30s左右即可生成最终视频</p>
                  </div>

                  {/* 修改视频预览部分 */}
                  <div className="mt-8">
                    <div className="flex justify-between items-center mb-3">
                      <h3 className="text-sm font-medium text-gray-700">视频预览</h3>
                      {generatedVideoUrl && (
                        <button
                          onClick={handleDownload}
                          disabled={loading}
                          className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          {loading ? (
                            <>
                              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                              </svg>
                              <span>下载中...</span>
                            </>
                          ) : (
                            <>
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                              </svg>
                              <span>下载视频</span>
                            </>
                          )}
                        </button>
                      )}
                    </div>
                    <div className="aspect-video bg-gray-100 rounded-lg overflow-hidden">
                      {generatedVideoUrl ? (
                        <video 
                          controls 
                          className="w-full h-full"
                          src={generatedVideoUrl ? getFullResourceUrl(generatedVideoUrl) : ''}
                          controlsList="nodownload" // 禁用浏览器默认下载按钮
                        >
                          您的浏览器不支持视频播放
                        </video>
                      ) : (
                        <div className="flex items-center justify-center h-full text-gray-500">
                          <p>视频将在这里显示</p>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* 进度条 */}
                  {loading && (
                    <div className="mt-8">
                      <div className="flex justify-between mb-2">
                        <span className="text-sm font-medium text-gray-700">生成进度</span>
                        <span className="text-sm font-medium text-gray-700">{progress}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2.5">
                        <div 
                          className="bg-gradient-to-r from-[var(--primary)] to-[var(--secondary)] h-2.5 rounded-full transition-all duration-300"
                          style={{ width: `${progress}%` }}
                        ></div>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* 底部按钮区域 - 优化样式 */}
              <div className="flex justify-between mt-8 pt-6 border-t">
                <button
                  onClick={() => setActiveStep(Math.max(1, activeStep - 1))}
                  disabled={activeStep === 1}
                  className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  上一步
                </button>
                
                {activeStep < 6 ? (
                  <button
                    onClick={() => setActiveStep(Math.min(6, activeStep + 1))}
                    className="btn-primary"
                  >
                    下一步
                  </button>
                ) : (
                  <button
                    onClick={handleFinalGenerate}
                    disabled={loading}
                    className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {loading ? '生成中...' : '开始生成'}
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 