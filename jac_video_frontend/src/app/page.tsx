'use client';

import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();

  const features = [
    {
      title: "智能生成",
      description: "基于AI技术,一键生成专业短视频内容",
      icon: "🎯"
    },
    {
      title: "多场景模板",
      description: "涵盖教育、娱乐、营销等多种场景模板",
      icon: "📚"
    },
    {
      title: "高效创作",
      description: "显著提升内容创作效率,让创作更轻松",
      icon: "⚡"
    },
    {
      title: "质量保证",
      description: "确保生成内容的专业性和准确性",
      icon: "✨"
    }
  ];

  const useCases = [
    {
      title: "教育培训",
      description: "快速生成知识点讲解、语言学习等教育视频",
      image: "/images/education.jpg" // 需要添加相应图片
    },
    {
      title: "营销推广",
      description: "制作产品介绍、品牌宣传等营销视频",
      image: "/images/marketing.jpg"
    },
    {
      title: "内容创作",
      description: "生成短视频、Vlog等各类创意内容",
      image: "/images/content.jpg"
    }
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <div className="pt-32 pb-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="main-title">
              Express Your Videos
            </h1>
            <p className="sub-title max-w-2xl mx-auto">
              让AI为您的内容创作加速，将情感和创意转化为精彩视频
            </p>
            <div className="mt-10">
              <button
                onClick={() => router.push('/products')}
                className="btn-primary text-lg px-10 py-4"
              >
                立即体验
              </button>
            </div>

            {/* 装饰图案 */}
            <div className="mt-16 relative">
              <div className="w-[600px] h-[200px] mx-auto rounded-3xl bg-white shadow-sm overflow-hidden p-6 flex flex-col justify-center">
                <p className="text-gray-500 text-center mb-4">如何使用 AI 短视频生成器？</p>
                <div className="flex justify-center items-center space-x-8">
                  <div className="flex flex-col items-center">
                    <div className="w-10 h-10 rounded-full bg-[#F0E9FF] flex items-center justify-center mb-2">
                      <span className="text-[#8778E5]">1</span>
                    </div>
                    <span className="text-sm text-gray-600">描述内容</span>
                  </div>
                  <div className="w-8 h-[2px] bg-gray-200"></div>
                  <div className="flex flex-col items-center">
                    <div className="w-10 h-10 rounded-full bg-[#F0E9FF] flex items-center justify-center mb-2">
                      <span className="text-[#8778E5]">2</span>
                    </div>
                    <span className="text-sm text-gray-600">设置参数</span>
                  </div>
                  <div className="w-8 h-[2px] bg-gray-200"></div>
                  <div className="flex flex-col items-center">
                    <div className="w-10 h-10 rounded-full bg-[#F0E9FF] flex items-center justify-center mb-2">
                      <span className="text-[#8778E5]">3</span>
                    </div>
                    <span className="text-sm text-gray-600">生成视频</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center mb-3 gradient-text">核心优势</h2>
          <p className="text-center text-gray-600 mb-12 max-w-2xl mx-auto">
            我们的AI视频创作工具提供多种强大功能，满足您的各种创作需求
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="bg-white p-8 rounded-2xl shadow-sm hover:shadow-md transition-shadow">
                <div className="w-14 h-14 rounded-full bg-[#F0E9FF] flex items-center justify-center mb-5 text-2xl">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-semibold mb-3">{feature.title}</h3>
                <p className="text-gray-600">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Use Cases Section */}
      <div className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center mb-3 gradient-text">应用场景</h2>
          <p className="text-center text-gray-600 mb-12 max-w-2xl mx-auto">
            探索我们的AI视频工具在不同场景下的应用，为您的需求找到最佳解决方案
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {useCases.map((useCase, index) => (
              <div key={index} className="bg-white rounded-2xl overflow-hidden shadow-sm hover:shadow-md transition-shadow">
                <div className="h-48 bg-[#F0E9FF] flex items-center justify-center">
                  <div className="text-5xl">{index === 0 ? '📚' : index === 1 ? '📱' : '🎬'}</div>
                </div>
                <div className="p-6">
                  <h3 className="text-xl font-semibold mb-2">{useCase.title}</h3>
                  <p className="text-gray-600">{useCase.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="py-24">
        <div className="max-w-3xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <div className="bg-white rounded-3xl p-12 shadow-sm">
            <h2 className="text-3xl font-bold mb-4 gradient-text">开始您的创作之旅</h2>
            <p className="text-gray-600 mb-8 max-w-md mx-auto">
              立即体验AI驱动的视频创作工具,让创作更轻松、更高效
            </p>
            <button
              onClick={() => router.push('/products')}
              className="btn-primary px-10 py-4 text-lg"
            >
              免费使用
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
