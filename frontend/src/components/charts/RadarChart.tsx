'use client'

import {
  RadarChart as RechartsRadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  Tooltip,
} from 'recharts'
import { cn } from '@/lib/utils'

interface RadarDataPoint {
  subject: string
  value: number
  fullMark: number
}

interface RadarChartProps {
  data: RadarDataPoint[]
  className?: string
  showTooltip?: boolean
  fillColor?: string
  strokeColor?: string
}

export function RadarChart({
  data,
  className,
  showTooltip = true,
  fillColor = 'rgba(59, 130, 246, 0.3)',
  strokeColor = '#3b82f6',
}: RadarChartProps) {
  return (
    <div className={cn('w-full h-64', className)}>
      <ResponsiveContainer width="100%" height="100%">
        <RechartsRadarChart data={data} cx="50%" cy="50%" outerRadius="70%">
          <PolarGrid
            gridType="polygon"
            stroke="rgba(100, 116, 139, 0.2)"
          />
          <PolarAngleAxis
            dataKey="subject"
            tick={{
              fill: '#94a3b8',
              fontSize: 11,
            }}
            tickLine={false}
          />
          <PolarRadiusAxis
            angle={90}
            domain={[0, 10]}
            tick={{
              fill: '#64748b',
              fontSize: 10,
            }}
            tickCount={6}
            axisLine={false}
          />
          <Radar
            name="评分"
            dataKey="value"
            stroke={strokeColor}
            fill={fillColor}
            strokeWidth={2}
            dot={{
              r: 4,
              fill: strokeColor,
              strokeWidth: 0,
            }}
            activeDot={{
              r: 6,
              fill: strokeColor,
              stroke: '#fff',
              strokeWidth: 2,
            }}
          />
          {showTooltip && (
            <Tooltip
              contentStyle={{
                backgroundColor: '#1e293b',
                border: '1px solid #334155',
                borderRadius: '8px',
                boxShadow: '0 4px 6px rgba(0, 0, 0, 0.3)',
              }}
              labelStyle={{
                color: '#f8fafc',
                fontWeight: 500,
              }}
              itemStyle={{
                color: '#cbd5e1',
              }}
              formatter={(value: number) => [`${value.toFixed(1)} 分`, '']}
            />
          )}
        </RechartsRadarChart>
      </ResponsiveContainer>
    </div>
  )
}

// 预设的分析维度雷达图
interface AnalysisRadarChartProps {
  scores: {
    maturity_score?: number
    positioning_clarity?: number
    pain_point_sharpness?: number
    pricing_clarity?: number
    conversion_friendliness?: number
    individual_replicability?: number
  }
  className?: string
}

export function AnalysisRadarChart({ scores, className }: AnalysisRadarChartProps) {
  const data: RadarDataPoint[] = [
    {
      subject: '产品成熟度',
      value: scores.maturity_score ?? 0,
      fullMark: 10,
    },
    {
      subject: '定位清晰度',
      value: scores.positioning_clarity ?? 0,
      fullMark: 10,
    },
    {
      subject: '痛点锋利度',
      value: scores.pain_point_sharpness ?? 0,
      fullMark: 10,
    },
    {
      subject: '定价清晰度',
      value: scores.pricing_clarity ?? 0,
      fullMark: 10,
    },
    {
      subject: '转化友好度',
      value: scores.conversion_friendliness ?? 0,
      fullMark: 10,
    },
    {
      subject: '可复制性',
      value: scores.individual_replicability ?? 0,
      fullMark: 10,
    },
  ]

  return <RadarChart data={data} className={className} />
}

// 市场分析雷达图
interface MarketRadarChartProps {
  metrics: {
    total_projects: number
    median_revenue: number
    top10_revenue_share: number
    gini_coefficient: number
  }
  className?: string
}

export function MarketRadarChart({ metrics, className }: MarketRadarChartProps) {
  // 归一化数据到 0-10 范围
  const normalize = (value: number, max: number) => Math.min(10, (value / max) * 10)

  const data: RadarDataPoint[] = [
    {
      subject: '市场规模',
      value: normalize(metrics.total_projects, 100),
      fullMark: 10,
    },
    {
      subject: '收入潜力',
      value: normalize(metrics.median_revenue, 10000),
      fullMark: 10,
    },
    {
      subject: '竞争度',
      value: 10 - normalize(metrics.top10_revenue_share, 100), // 反向：集中度越低越好
      fullMark: 10,
    },
    {
      subject: '公平性',
      value: 10 - metrics.gini_coefficient * 10, // 反向：基尼系数越低越公平
      fullMark: 10,
    },
  ]

  return (
    <RadarChart
      data={data}
      className={className}
      fillColor="rgba(6, 182, 212, 0.3)"
      strokeColor="#06b6d4"
    />
  )
}
