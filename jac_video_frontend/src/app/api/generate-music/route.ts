import { NextResponse } from 'next/server';

export async function POST() {
  try {
    // 这里返回测试音频文件的URL
    return NextResponse.json({
      musicUrl: '/test.MP3'  // 假设test.MP3放在public文件夹下
    });
  } catch (error) {
    return NextResponse.json(
      { error: '音乐生成失败' },
      { status: 500 }
    );
  }
} 