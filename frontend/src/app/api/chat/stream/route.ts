import { NextRequest } from 'next/server'

export const runtime = 'edge'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    // 代理到后端的流式端点
    const backendUrl = process.env.BACKEND_URL || 'http://127.0.0.1:8001'
    
    const response = await fetch(`${backendUrl}/api/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
      },
      body: JSON.stringify(body),
      // @ts-expect-error - Cloudflare Workers / Edge Runtime 支持
      cf: { cacheTtl: 0 },
    })

    if (!response.ok) {
      const errorText = await response.text().catch(() => 'Unknown error')
      return new Response(
        JSON.stringify({ error: `Backend error: ${response.status}`, detail: errorText }),
        {
          status: response.status,
          headers: { 'Content-Type': 'application/json' },
        }
      )
    }

    if (!response.body) {
      return new Response(
        JSON.stringify({ error: 'No response body from backend' }),
        {
          status: 500,
          headers: { 'Content-Type': 'application/json' },
        }
      )
    }

    // 创建一个新的 ReadableStream，手动控制数据传输
    // 这样可以确保每个 chunk 立即被发送，不会被缓冲
    const stream = new ReadableStream({
      async start(controller) {
        const reader = response.body!.getReader()
        
        try {
          while (true) {
            const { done, value } = await reader.read()
            
            if (done) {
              controller.close()
              break
            }
            
            // 立即将数据推送到流中
            controller.enqueue(value)
          }
        } catch (error) {
          console.error('Stream read error:', error)
          controller.error(error)
        }
      },
    })

    return new Response(stream, {
      headers: {
        'Content-Type': 'text/event-stream; charset=utf-8',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Connection': 'keep-alive',
        'X-Accel-Buffering': 'no',
        'Transfer-Encoding': 'chunked',
      },
    })
  } catch (error) {
    console.error('Stream proxy error:', error)
    return new Response(
      JSON.stringify({ error: 'Internal server error', detail: String(error) }),
      {
        status: 500,
        headers: { 'Content-Type': 'application/json' },
      }
    )
  }
}
