'use client'

import { Card, CardHeader } from '@/components/ui/Card'
import { MarketTypeBadge } from '@/components/ui/Badge'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import {
  faLightbulb,
  faChartLine,
  faCode,
  faRocket,
} from '@fortawesome/free-solid-svg-icons'
import type { MarketType } from '@/types'

export default function AboutPage() {
  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* 标题 */}
      <div className="text-center">
        <h1 className="text-3xl font-display font-bold text-content-primary mb-4">
          分析说明
        </h1>
        <p className="text-content-secondary max-w-2xl mx-auto">
          了解我们如何分析 SaaS 产品，以及各项指标的含义
        </p>
      </div>

      {/* 分析维度 */}
      <Card>
        <CardHeader
          title="📊 六维评分体系"
          subtitle="从多个角度评估产品的可复制性和市场机会"
        />
        <div className="grid md:grid-cols-2 gap-4">
          {[
            {
              name: '产品成熟度',
              score: 'maturity_score',
              desc: '评估产品的完成度、功能完整性和用户体验。成熟的产品意味着已验证的需求。',
              icon: faRocket,
            },
            {
              name: '定位清晰度',
              score: 'positioning_clarity',
              desc: '目标用户是否明确，价值主张是否清晰。好的定位让用户一眼就知道产品能解决什么问题。',
              icon: faLightbulb,
            },
            {
              name: '痛点锋利度',
              score: 'pain_point_sharpness',
              desc: '解决的问题是否足够痛，用户是否有强烈的付费意愿。锋利的痛点意味着更高的转化率。',
              icon: faChartLine,
            },
            {
              name: '定价清晰度',
              score: 'pricing_clarity',
              desc: '价格体系是否清晰合理，用户是否容易理解和接受。清晰的定价减少决策摩擦。',
              icon: faChartLine,
            },
            {
              name: '转化友好度',
              score: 'conversion_friendliness',
              desc: '用户从了解到付费的路径是否顺畅，有无免费试用、清晰的CTA等。',
              icon: faChartLine,
            },
            {
              name: '可复制性',
              score: 'individual_replicability',
              desc: '独立开发者复制这个产品的难度如何，技术门槛、资源需求、时间成本等。',
              icon: faCode,
            },
          ].map((item) => (
            <div key={item.name} className="p-4 rounded-lg bg-background-secondary/50">
              <div className="flex items-center gap-2 mb-2">
                <FontAwesomeIcon icon={item.icon} className="h-4 w-4 text-accent-primary" />
                <span className="font-medium text-content-primary">{item.name}</span>
              </div>
              <p className="text-sm text-content-muted">{item.desc}</p>
            </div>
          ))}
        </div>
      </Card>

      {/* 市场类型 */}
      <Card>
        <CardHeader
          title="🏷️ 市场类型说明"
          subtitle="基于竞争程度和收入分布的市场分类"
        />
        <div className="space-y-4">
          {[
            {
              type: 'blue_ocean' as MarketType,
              desc: '项目少但收入高，中位数收入表现优秀。竞争较少，大部分产品都能盈利，适合进入。',
              advice: '建议：优先考虑，但要思考为什么竞争少',
            },
            {
              type: 'emerging' as MarketType,
              desc: '新兴市场，项目数量少但已有收入验证。可能是早期机会窗口。',
              advice: '建议：快速验证，抢占先机',
            },
            {
              type: 'moderate' as MarketType,
              desc: '竞争适中，有一定市场空间。需要差异化竞争策略。',
              advice: '建议：找到细分定位，差异化切入',
            },
            {
              type: 'concentrated' as MarketType,
              desc: '头部集中，TOP10 产品占据大部分收入。赢者通吃的格局。',
              advice: '建议：除非有独特优势，否则建议避开',
            },
            {
              type: 'red_ocean' as MarketType,
              desc: '项目多但中位数收入低，说明大部分产品赚不到钱。竞争激烈，内卷严重。',
              advice: '建议：建议避开，除非有颠覆性创新',
            },
            {
              type: 'weak_demand' as MarketType,
              desc: '市场总收入很低，可能是伪需求或过度细分的市场。',
              advice: '建议：建议避开',
            },
          ].map((item) => (
            <div key={item.type} className="flex items-start gap-4 p-4 rounded-lg bg-background-secondary/50">
              <MarketTypeBadge type={item.type} className="flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-content-secondary mb-2">{item.desc}</p>
                <p className="text-sm text-accent-primary">{item.advice}</p>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* 组合筛选 */}
      <Card>
        <CardHeader
          title="🎯 组合筛选逻辑"
          subtitle="多条件组合找出最适合独立开发者的产品"
        />
        <div className="space-y-4">
          <div className="p-4 rounded-lg border border-accent-success/30 bg-accent-success/5">
            <h4 className="font-medium text-content-primary mb-2">组合1：黄金机会</h4>
            <p className="text-sm text-content-secondary mb-2">
              低粉丝 (≤1000) + 高收入 (≥$1000) + 技术简单 (低复杂度) + 年轻产品 (≤2年)
            </p>
            <p className="text-xs text-content-muted">
              说明：不依赖个人IP，收入已验证，技术门槛低，还有成长空间
            </p>
          </div>

          <div className="p-4 rounded-lg border border-accent-primary/30 bg-accent-primary/5">
            <h4 className="font-medium text-content-primary mb-2">组合2：小工具机会</h4>
            <p className="text-sm text-content-secondary mb-2">
              简短描述 (≤30词) + 中等收入 (≥$500) + 低复杂度
            </p>
            <p className="text-xs text-content-muted">
              说明：功能聚焦的小工具，容易理解和开发
            </p>
          </div>

          <div className="p-4 rounded-lg border border-accent-secondary/30 bg-accent-secondary/5">
            <h4 className="font-medium text-content-primary mb-2">组合3：验证需求</h4>
            <p className="text-sm text-content-secondary mb-2">
              小而美产品 + 有收入 (≥$100) + 低复杂度
            </p>
            <p className="text-xs text-content-muted">
              说明：需求已验证，功能精简，适合快速复制
            </p>
          </div>
        </div>
      </Card>

      {/* 数据来源 */}
      <Card>
        <CardHeader
          title="📦 数据来源"
          subtitle="分析数据的采集和处理说明"
        />
        <div className="prose prose-sm prose-invert max-w-none text-content-secondary">
          <ul className="space-y-2">
            <li>产品数据来源于 TrustMRR 公开数据</li>
            <li>Landing Page 分析通过 AI 自动抓取和评估</li>
            <li>收入数据为产品方自行披露，仅供参考</li>
            <li>分析结论基于算法模型，不构成投资建议</li>
            <li>数据每日自动更新</li>
          </ul>
        </div>
      </Card>

      {/* 免责声明 */}
      <div className="text-center text-sm text-content-muted py-8">
        <p>本工具仅供学习研究使用，分析结论仅供参考</p>
        <p className="mt-1">Built for Indie Hackers with ❤️</p>
      </div>
    </div>
  )
}
