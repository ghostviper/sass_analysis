'use client'

import { useState } from 'react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faCheck, faRobot, faUser } from '@fortawesome/free-solid-svg-icons'
import { cn } from '@/lib/utils'

// 字体方案配置
const fontSchemes = [
  {
    id: 'current',
    name: '当前方案',
    description: 'Inter + Noto Sans SC，偏小的字号',
    fonts: {
      sans: '"Inter", "Noto Sans SC", system-ui, sans-serif',
      display: '"Inter", "Noto Sans SC", system-ui, sans-serif',
    },
    sizes: {
      chatBody: '0.875rem',    // 14px
      chatLineHeight: '1.5',
      heading: '1rem',
    },
    weights: {
      normal: 400,
      medium: 500,
      bold: 600,
    },
  },
  {
    id: 'scheme-a',
    name: '方案 A：清晰阅读',
    description: 'Inter + 思源黑体，加大字号，增强层次感',
    fonts: {
      sans: '"Inter", "Noto Sans SC", system-ui, sans-serif',
      display: '"Inter", "Noto Sans SC", system-ui, sans-serif',
    },
    sizes: {
      chatBody: '0.9375rem',   // 15px
      chatLineHeight: '1.7',
      heading: '1.0625rem',    // 17px
    },
    weights: {
      normal: 400,
      medium: 500,
      bold: 600,
    },
  },
  {
    id: 'scheme-b',
    name: '方案 B：舒适大字',
    description: '更大的正文字号，宽松行高，适合长时间阅读',
    fonts: {
      sans: '"Inter", "Noto Sans SC", system-ui, sans-serif',
      display: '"Inter", "Noto Sans SC", system-ui, sans-serif',
    },
    sizes: {
      chatBody: '1rem',        // 16px
      chatLineHeight: '1.75',
      heading: '1.125rem',     // 18px
    },
    weights: {
      normal: 400,
      medium: 500,
      bold: 600,
    },
  },
  {
    id: 'scheme-c',
    name: '方案 C：系统原生',
    description: '使用系统字体，中文显示更自然',
    fonts: {
      sans: 'system-ui, -apple-system, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif',
      display: 'system-ui, -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif',
    },
    sizes: {
      chatBody: '0.9375rem',   // 15px
      chatLineHeight: '1.7',
      heading: '1.0625rem',
    },
    weights: {
      normal: 400,
      medium: 500,
      bold: 600,
    },
  },
  {
    id: 'scheme-d',
    name: '方案 D：优雅衬线',
    description: 'Merriweather + 思源宋体，适合内容型产品',
    fonts: {
      sans: '"Merriweather", "Noto Serif SC", "Source Han Serif SC", Georgia, serif',
      display: '"Inter", "Noto Sans SC", system-ui, sans-serif',
    },
    sizes: {
      chatBody: '1rem',        // 16px
      chatLineHeight: '1.8',
      heading: '1.125rem',
    },
    weights: {
      normal: 400,
      medium: 500,
      bold: 700,
    },
  },
  {
    id: 'scheme-e',
    name: '方案 E：现代简约',
    description: 'DM Sans + 思源黑体，现代感强，字重对比明显',
    fonts: {
      sans: '"DM Sans", "Noto Sans SC", system-ui, sans-serif',
      display: '"DM Sans", "Noto Sans SC", system-ui, sans-serif',
    },
    sizes: {
      chatBody: '0.9375rem',   // 15px
      chatLineHeight: '1.65',
      heading: '1.0625rem',
    },
    weights: {
      normal: 400,
      medium: 500,
      bold: 700,
    },
  },
  {
    id: 'scheme-f',
    name: '方案 F：专业商务',
    description: 'IBM Plex Sans + 思源黑体，专业稳重',
    fonts: {
      sans: '"IBM Plex Sans", "Noto Sans SC", system-ui, sans-serif',
      display: '"IBM Plex Sans", "Noto Sans SC", system-ui, sans-serif',
    },
    sizes: {
      chatBody: '0.9375rem',   // 15px
      chatLineHeight: '1.7',
      heading: '1.0625rem',
    },
    weights: {
      normal: 400,
      medium: 500,
      bold: 600,
    },
  },
]

// 示例对话内容
const sampleMessages = [
  {
    role: 'user' as const,
    content: '分析一下月收入超过 $5000 的 SaaS 产品有什么共同特点？',
  },
  {
    role: 'assistant' as const,
    content: `根据数据库中的分析，月收入超过 $5000 的 SaaS 产品通常具有以下共同特点：

## 1. 明确的价值主张

这些产品都能清晰地解决一个具体问题，用户能在 **30 秒内** 理解产品价值。例如：
- **Notion** - 一体化工作空间
- **Linear** - 现代化项目管理
- **Figma** - 协作设计工具

## 2. 定价策略

成功的产品通常采用以下定价模式：
- 免费试用 + 付费升级
- 按座位/用量计费
- 年付优惠 (通常 20% 折扣)

## 3. 技术特点

| 特点 | 占比 |
|------|------|
| 响应式设计 | 95% |
| API 支持 | 78% |
| 多语言 | 65% |

> 值得注意的是，这些产品的技术复杂度并不一定很高，关键在于 **解决真实痛点**。

需要我进一步分析某个具体方向吗？`,
  },
]

export default function FontPreviewPage() {
  const [selectedScheme, setSelectedScheme] = useState<string | null>(null)

  return (
    <div className="min-h-screen p-8">
      {/* 加载额外字体 */}
      <link
        href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=IBM+Plex+Sans:wght@400;500;600&family=Merriweather:wght@400;700&family=Noto+Serif+SC:wght@400;700&display=swap"
        rel="stylesheet"
      />

      {/* 页面标题 */}
      <div className="max-w-6xl mx-auto mb-8">
        <h1 className="text-2xl font-bold text-content-primary mb-2">
          字体方案预览
        </h1>
        <p className="text-content-secondary">
          选择一个你喜欢的字体方案，点击卡片查看详细效果。选定后我会应用到全局。
        </p>
      </div>

      {/* 方案网格 */}
      <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-6">
        {fontSchemes.map((scheme) => {
          const isSelected = selectedScheme === scheme.id
          return (
            <div
              key={scheme.id}
              onClick={() => setSelectedScheme(scheme.id)}
              className={cn(
                'relative rounded-2xl border-2 transition-all duration-300 cursor-pointer overflow-hidden',
                isSelected
                  ? 'border-accent-primary shadow-lg shadow-accent-primary/10'
                  : 'border-surface-border hover:border-accent-primary/40 hover:shadow-md'
              )}
            >
              {/* 选中标记 */}
              {isSelected && (
                <div className="absolute top-4 right-4 w-6 h-6 rounded-full bg-accent-primary flex items-center justify-center z-10">
                  <FontAwesomeIcon icon={faCheck} className="h-3 w-3 text-white" />
                </div>
              )}

              {/* 方案标题 */}
              <div className="p-4 border-b border-surface-border bg-surface/50">
                <h3 className="font-semibold text-content-primary">{scheme.name}</h3>
                <p className="text-sm text-content-secondary mt-1">{scheme.description}</p>
                <div className="flex gap-4 mt-2 text-xs text-content-muted">
                  <span>正文: {scheme.sizes.chatBody}</span>
                  <span>行高: {scheme.sizes.chatLineHeight}</span>
                </div>
              </div>

              {/* 聊天预览 */}
              <div
                className="p-4 space-y-4 bg-background"
                style={{ fontFamily: scheme.fonts.sans }}
              >
                {sampleMessages.map((msg, idx) => (
                  <div
                    key={idx}
                    className={cn(
                      'flex gap-3',
                      msg.role === 'user' ? 'justify-end' : 'justify-start'
                    )}
                  >
                    {msg.role === 'assistant' && (
                      <div className="w-8 h-8 rounded-full bg-accent-primary/10 flex items-center justify-center flex-shrink-0">
                        <FontAwesomeIcon icon={faRobot} className="h-4 w-4 text-accent-primary" />
                      </div>
                    )}
                    <div
                      className={cn(
                        'rounded-2xl px-4 py-3 max-w-[85%]',
                        msg.role === 'user'
                          ? 'bg-accent-primary text-white rounded-tr-sm'
                          : 'bg-surface border border-surface-border rounded-tl-sm'
                      )}
                      style={{
                        fontSize: scheme.sizes.chatBody,
                        lineHeight: scheme.sizes.chatLineHeight,
                      }}
                    >
                      {msg.role === 'assistant' ? (
                        <div className="prose-preview">
                          <AssistantContent content={msg.content} scheme={scheme} />
                        </div>
                      ) : (
                        <span>{msg.content}</span>
                      )}
                    </div>
                    {msg.role === 'user' && (
                      <div className="w-8 h-8 rounded-full bg-accent-secondary/10 flex items-center justify-center flex-shrink-0">
                        <FontAwesomeIcon icon={faUser} className="h-4 w-4 text-accent-secondary" />
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )
        })}
      </div>

      {/* 选中提示 */}
      {selectedScheme && (
        <div className="fixed bottom-8 left-1/2 -translate-x-1/2 bg-surface border border-surface-border rounded-2xl shadow-xl px-6 py-4 flex items-center gap-4 z-50">
          <div>
            <p className="font-medium text-content-primary">
              已选择: {fontSchemes.find(s => s.id === selectedScheme)?.name}
            </p>
            <p className="text-sm text-content-secondary">
              确认后请告诉我，我会将此方案应用到全局
            </p>
          </div>
          <button
            onClick={() => setSelectedScheme(null)}
            className="px-4 py-2 text-sm text-content-secondary hover:text-content-primary transition-colors"
          >
            取消
          </button>
        </div>
      )}
    </div>
  )
}

// 简单的 Markdown 渲染组件
function AssistantContent({ content, scheme }: { content: string; scheme: typeof fontSchemes[0] }) {
  // 简单解析 markdown
  const lines = content.split('\n')
  const elements: JSX.Element[] = []
  let inTable = false
  let tableRows: string[] = []

  lines.forEach((line, idx) => {
    // 标题
    if (line.startsWith('## ')) {
      elements.push(
        <h3
          key={idx}
          className="font-semibold text-content-primary mt-4 mb-2"
          style={{
            fontSize: scheme.sizes.heading,
            fontWeight: scheme.weights.bold,
          }}
        >
          {line.replace('## ', '')}
        </h3>
      )
      return
    }

    // 表格
    if (line.startsWith('|')) {
      if (!inTable) {
        inTable = true
        tableRows = []
      }
      tableRows.push(line)
      return
    } else if (inTable) {
      // 表格结束
      elements.push(
        <table key={`table-${idx}`} className="w-full my-3 text-sm border-collapse">
          <tbody>
            {tableRows.map((row, rowIdx) => {
              if (row.includes('---')) return null
              const cells = row.split('|').filter(c => c.trim())
              const isHeader = rowIdx === 0
              return (
                <tr key={rowIdx} className={isHeader ? 'border-b border-surface-border' : ''}>
                  {cells.map((cell, cellIdx) => (
                    isHeader ? (
                      <th key={cellIdx} className="text-left py-2 px-3 font-medium text-content-secondary">
                        {cell.trim()}
                      </th>
                    ) : (
                      <td key={cellIdx} className="py-2 px-3 text-content-primary">
                        {cell.trim()}
                      </td>
                    )
                  ))}
                </tr>
              )
            })}
          </tbody>
        </table>
      )
      inTable = false
      tableRows = []
    }

    // 引用
    if (line.startsWith('> ')) {
      elements.push(
        <blockquote
          key={idx}
          className="border-l-2 border-accent-primary/40 pl-3 my-2 text-content-tertiary italic"
        >
          {parseInlineStyles(line.replace('> ', ''))}
        </blockquote>
      )
      return
    }

    // 列表项
    if (line.startsWith('- ')) {
      elements.push(
        <li key={idx} className="ml-4 my-1 text-content-primary list-disc">
          {parseInlineStyles(line.replace('- ', ''))}
        </li>
      )
      return
    }

    // 普通段落
    if (line.trim()) {
      elements.push(
        <p key={idx} className="my-2 text-content-primary">
          {parseInlineStyles(line)}
        </p>
      )
    }
  })

  return <>{elements}</>
}

// 解析行内样式
function parseInlineStyles(text: string): JSX.Element {
  // 简单处理 **bold** 和 `code`
  const parts = text.split(/(\*\*[^*]+\*\*|`[^`]+`)/g)
  return (
    <>
      {parts.map((part, idx) => {
        if (part.startsWith('**') && part.endsWith('**')) {
          return <strong key={idx} className="font-semibold">{part.slice(2, -2)}</strong>
        }
        if (part.startsWith('`') && part.endsWith('`')) {
          return (
            <code key={idx} className="px-1.5 py-0.5 bg-surface rounded text-accent-primary text-[0.85em] font-mono">
              {part.slice(1, -1)}
            </code>
          )
        }
        return <span key={idx}>{part}</span>
      })}
    </>
  )
}
