import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const { word } = await request.json();
    
    // 模拟API响应
    const mockResponse = {
      word: word,
      reading: "たんご",
      meaning: "单词",
      example: {
        japanese: "新しい単語を覚えます。",
        reading: "あたらしいたんごをおぼえます。",
        meaning: "记住新单词。"
      },
      tags: ["N5", "名词"],
      created_at: new Date().toISOString()
    };

    // 模拟API延迟
    await new Promise(resolve => setTimeout(resolve, 1000));

    return NextResponse.json(mockResponse);
  } catch (error) {
    return NextResponse.json(
      { error: '生成失败' },
      { status: 500 }
    );
  }
} 