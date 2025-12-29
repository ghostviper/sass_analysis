## 一款依托对网站 https://trustmrr.com/ 进行数据获取的Sass Agent分析工具

### 技术选型
#### 后端
- 爬虫：playwright对网站进行数据抓取和分类存储
- Agent框架:Google AgentDevelopmentKit 构建分析Agent
- 数据库:数据使用本地Sqllite进行存储
- 接口：FastAPI
- 语言：Python
#### 前端
- 语言
- nextjs 15
- tailwindcss 3
- vercel AI SDK
- shadcn ui

### 需求清单
- 需要使用playwright模拟浏览器打开页面分析页面然后获取指定的数据存储到本地数据库，然后使用ADK构建sass产品分析类agent
#### 爬虫内容
- trustmrr 网站 https://trustmrr.com/acquire 页面列表数据
- trustmrr 网站 主页 Leaderboard 列表
#### Agent内容
- AI问数：可以对存储的数据进行多轮问答
- 每日趋势分析：按类别sass趋势分析、排行榜分析、toB和toC产品趋势分析

### 实现步骤
- 爬虫和数据存储
- 后端
- 前端