'use client'

import { useLocale } from '@/contexts/LocaleContext'
import { Card } from '@/components/ui/Card'
import { Sparkles, ArrowRight, MessageCircle, Heart, Zap } from 'lucide-react'
import Link from 'next/link'

// 模拟数据 - 为你推荐
const mockRecommendations = [
  {
    id: 1,
    direction: 'API 工具类产品',
    description: '技术门槛适中，市场需求稳定，适合有后端经验的开发者',
    whyForYou: '你之前浏览过多个 API 相关产品，这个方向可能适合你',
    examples: ['Screenshot API', 'PDF Generation API', 'Email Validation API'],
    difficulty: '中等',
    potential: '高',
    gradient: 'from-blue-500/10 to-cyan-500/5',
    accentColor: 'blue',
  },
  {
    id: 2,
    direction: '开发者效率工具',
    description: '面向开发者的小工具，用户付费意愿强，口碑传播效果好',
    whyForYou: '基于你对 DevUtils 和 Xnapper 的关注',
    examples: ['代码片段管理', 'API 测试工具', '本地开发环境'],
    difficulty: '低',
    potential: '中高',
    gradient: 'from-violet-500/10 to-purple-500/5',
    accentColor: 'violet',
  },
  {
    id: 3,
    direction: '内容创作者工具',
    description: '帮助内容创作者提高效率的工具，市场正在快速增长',
    whyForYou: '你关注了多位内容创作者转型的案例',
    examples: ['社交媒体排程', '视频字幕生成', '内容分析工具'],
    difficulty: '中等',
    potential: '高',
    gradient: 'from-rose-500/10 to-pink-500/5',
    accentColor: 'rose',
  },
]

export function ForYouSection() {
  const { t } = useLocale()

  return (
    <section>
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-pink-500 to-rose-500 flex items-center justify-center shadow-lg shadow-pink-500/20">
            <Heart className="h-5 w-5 text-white" />
          </div>
          <div>
            <h2 className="text-lg font-display font-bold text-content-primary tracking-tight">
              {t('discover.forYou.title')}
            </h2>
            <p className="text-xs text-content-muted">{t('discover.forYou.subtitle')}</p>
          </div>
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        {mockRecommendations.map((rec) => (
          <Card
            key={rec.id}
            hover
            className={`group bg-gradient-to-br ${rec.gradient}`}
          >
            {/* 方向标题 */}
            <div className="flex items-start gap-2 mb-3">
              <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0
                ${rec.accentColor === 'blue' ? 'bg-blue-500/20 text-blue-500' : ''}
                ${rec.accentColor === 'violet' ? 'bg-violet-500/20 text-violet-500' : ''}
                ${rec.accentColor === 'rose' ? 'bg-rose-500/20 text-rose-500' : ''}
              `}>
                <Zap className="h-4 w-4" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-content-primary group-hover:text-brand-600 dark:group-hover:text-brand-400 transition-colors">
                  {rec.direction}
                </h3>
              </div>
            </div>

            {/* 描述 */}
            <p className="text-xs text-content-tertiary mb-3 line-clamp-2">
              {rec.description}
            </p>

            {/* 为什么适合你 */}
            <div className={`p-2.5 rounded-lg mb-3 text-xs
              ${rec.accentColor === 'blue' ? 'bg-blue-500/10 text-blue-700 dark:text-blue-300' : ''}
              ${rec.accentColor === 'violet' ? 'bg-violet-500/10 text-violet-700 dark:text-violet-300' : ''}
              ${rec.accentColor === 'rose' ? 'bg-rose-500/10 text-rose-700 dark:text-rose-300' : ''}
            `}>
              <div className="flex items-center gap-1.5 mb-1 font-medium">
                <Sparkles className="h-3 w-3" />
                {t('discover.forYou.whyForYou')}
              </div>
              <p className="text-content-secondary">{rec.whyForYou}</p>
            </div>

            {/* 示例产品 */}
            <div className="mb-3">
              <div className="text-[10px] text-content-muted mb-1.5">参考方向</div>
              <div className="flex flex-wrap gap-1.5">
                {rec.examples.map((example, idx) => (
                  <span
                    key={idx}
                    className="text-[10px] px-2 py-0.5 rounded bg-surface border border-surface-border/50 text-content-secondary"
                  >
                    {example}
                  </span>
                ))}
              </div>
            </div>

            {/* 难度和潜力 */}
            <div className="flex items-center gap-4 mb-3 text-xs">
              <div>
                <span className="text-content-muted">难度：</span>
                <span className="text-content-secondary font-medium">{rec.difficulty}</span>
              </div>
              <div>
                <span className="text-content-muted">潜力：</span>
                <span className={`font-medium
                  ${rec.potential === '高' ? 'text-emerald-600 dark:text-emerald-400' : ''}
                  ${rec.potential === '中高' ? 'text-amber-600 dark:text-amber-400' : ''}
                `}>
                  {rec.potential}
                </span>
              </div>
            </div>

            {/* CTA */}
            <div className="flex gap-2">
              <Link
                href="/assistant"
                className="flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg bg-brand-500/10 text-brand-600 dark:text-brand-400 text-xs font-medium hover:bg-brand-500/20 transition-colors"
              >
                <MessageCircle className="h-3.5 w-3.5" />
                {t('discover.forYou.explore')}
              </Link>
              <Link
                href={`/products?direction=${rec.id}`}
                className="flex items-center justify-center gap-1 px-3 py-2 rounded-lg bg-surface border border-surface-border text-xs font-medium text-content-secondary hover:text-content-primary hover:border-brand-500/30 transition-colors"
              >
                {t('discover.cta.findSimilar')}
                <ArrowRight className="h-3 w-3" />
              </Link>
            </div>
          </Card>
        ))}
      </div>

      {/* 底部提示 */}
      <div className="mt-6 p-4 rounded-xl bg-gradient-to-r from-brand-500/5 via-violet-500/5 to-amber-500/5 border border-brand-500/10 text-center">
        <p className="text-sm text-content-secondary mb-2">
          想要更精准的推荐？告诉 AI 你的背景和兴趣
        </p>
        <Link
          href="/assistant"
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-brand-500 text-white text-sm font-medium hover:bg-brand-600 transition-colors shadow-lg shadow-brand-500/20"
        >
          <MessageCircle className="h-4 w-4" />
          开始对话，获取个性化建议
        </Link>
      </div>
    </section>
  )
}
