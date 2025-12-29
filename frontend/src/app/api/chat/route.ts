import { NextRequest, NextResponse } from 'next/server'

// 模拟 AI 响应 - 后续可以替换为真实的 AI 调用
const mockResponses: Record<string, string> = {
  product: `## 产品分析报告

### 核心洞察
1. **市场定位**：该产品定位于中小企业市场
2. **竞争优势**：简洁的用户体验是主要差异化因素
3. **增长潜力**：MRR 增长率显示健康的产品-市场契合度

### 建议
- 可以考虑在垂直细分领域进行差异化
- 关注用户留存率的优化`,

  trend: `## 行业趋势分析

### 市场动态
1. **AI 工具赛道**持续火热，但竞争加剧
2. **开发者工具**领域出现整合趋势
3. **垂直 SaaS** 展现更好的生存空间

### 机会识别
| 领域 | 机会评级 | 竞争强度 |
|-----|---------|---------|
| AI 写作助手 | ⭐⭐⭐ | 高 |
| 开发者工具 | ⭐⭐⭐⭐ | 中 |
| 垂直行业SaaS | ⭐⭐⭐⭐⭐ | 低 |`,

  career: `## 个人开发者机会探索

### 推荐方向
**🎯 高推荐**
- 小工具类产品（低复杂度、快速验证）
- 细分领域的效率工具
- 内容创作者工具

### 下一步建议
1. 从个人痛点出发，列出 3-5 个潜在方向
2. 在产品库中搜索类似产品，学习成功案例
3. 用 MVP 快速验证`,
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { message, mode } = body

    // 模拟延迟
    await new Promise(resolve => setTimeout(resolve, 1000))

    // 根据模式返回不同响应
    let response = mockResponses[mode] || mockResponses.product

    // 可以在这里添加更复杂的逻辑
    if (message.includes('产品')) {
      response = mockResponses.product
    } else if (message.includes('趋势') || message.includes('行业')) {
      response = mockResponses.trend
    } else if (message.includes('开发者') || message.includes('职业')) {
      response = mockResponses.career
    }

    return NextResponse.json({
      success: true,
      message: response,
    })
  } catch (error) {
    console.error('Chat API error:', error)
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    )
  }
}

// 支持流式响应的版本（供将来使用）
export async function GET() {
  return NextResponse.json({
    status: 'ok',
    message: 'Chat API is running. Use POST to send messages.',
  })
}
