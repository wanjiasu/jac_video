'use client';

import Link from 'next/link';

interface ProductCard {
  id: string;
  title: string;
  description: string;
  icon: string;
  status: 'active' | 'coming';
  link: string;
}

export default function ProductsPage() {
  const products: ProductCard[] = [
    {
      id: 'japanese-vocab',
      title: '日语单词学习短视频生成器',
      description: '快速生成日语单词学习短视频，支持发音、例句和记忆技巧',
      icon: '📚',
      status: 'active',
      link: '/products/japanese-vocab'
    },
    {
      id: 'coming-1',
      title: '新功能开发中',
      description: '更多智能视频生成工具正在开发中...',
      icon: '🚧',
      status: 'coming',
      link: '#'
    },
    {
      id: 'coming-2',
      title: '新功能开发中',
      description: '更多智能视频生成工具正在开发中...',
      icon: '🚧',
      status: 'coming',
      link: '#'
    },
    {
      id: 'coming-3',
      title: '新功能开发中',
      description: '更多智能视频生成工具正在开发中...',
      icon: '🚧',
      status: 'coming',
      link: '#'
    }
  ];

  return (
    <div className="page-container">
      <div className="text-center mb-16">
        <h1 className="main-title">
          智能视频生成工具
        </h1>
        <p className="sub-title max-w-2xl mx-auto">
          选择下方工具，快速生成专业的短视频内容
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {products.map((product) => (
          <Link
            key={product.id}
            href={product.link}
            className={`group relative overflow-hidden rounded-2xl bg-white hover:shadow-lg 
              transition-all duration-300 
              ${product.status === 'coming' ? 'cursor-not-allowed opacity-80' : 'hover:-translate-y-1'}`}
            onClick={(e) => product.status === 'coming' && e.preventDefault()}
          >
            {/* 卡片内容 */}
            <div className="flex flex-col h-full p-8">
              {/* 图标 */}
              <div className="w-16 h-16 rounded-full bg-[#F0E9FF] flex items-center justify-center mb-6 text-3xl">
                {product.icon}
              </div>

              {/* 标题和描述 */}
              <div className="flex-grow">
                <h3 className="text-xl font-semibold mb-3 text-gray-900">
                  {product.title}
                </h3>
                <p className="text-gray-600 mb-6">
                  {product.description}
                </p>
              </div>

              {/* 状态标签 */}
              <div className="mt-4">
                {product.status === 'active' ? (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-[#E9FFF6] text-[#00C48C]">
                    可用
                  </span>
                ) : (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-[#F0E9FF] text-[#8778E5]">
                    开发中
                  </span>
                )}
              </div>

              {/* 悬浮效果 - 仅对可用的功能显示 */}
              {product.status === 'active' && (
                <div className="absolute inset-0 bg-gradient-to-r from-[#8778E5] to-[#EF6DA0] 
                  opacity-0 group-hover:opacity-5 transition-opacity duration-300"/>
              )}
            </div>
          </Link>
        ))}
      </div>

      {/* 底部提示 */}
      <div className="mt-16 bg-white rounded-2xl p-8 shadow-sm text-center max-w-2xl mx-auto">
        <h3 className="text-xl font-semibold mb-4 gradient-text">想要更多功能？</h3>
        <p className="text-gray-600 mb-6">
          我们正在努力开发更多智能视频生成工具，敬请期待！
        </p>
        <button className="btn-secondary">
          提交功能建议
        </button>
      </div>
    </div>
  );
} 