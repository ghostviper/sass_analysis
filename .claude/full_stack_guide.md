# FullStack claude code 工作流

# 技术选型

## 前端

- 前端框架：nextjs
- UI框架：shadcn
- 样式框架：tailwindcss3
- 图标规范：lucide-react icon
- 认证框架：better-auth
- AI对话框架：vercel-ai-sdk
- AI对话markdown框架：streamdown
- 可视化图表框架:echarts
- 数据库：supabase
- 头像图标库：unavartar.io, the ultimate avatar service that offers everything you need to easily retrieve user avatars
- 动效库：framer-motion
- 国际化：next-intl
- 主题切换：next-themes

## 后端

- python版本：python3.10
- python虚拟环境：venv
- 接口：FastAPI
- 进程管理：gunicorn
- AI Agent框架：claude-agent-sdk-python
- 数据库ORM：sqlalchemy

# 总体设计原则和惯例

## 前端

landing Page（落地页），通常包含下列区块，根据各类产品定位不同而不同：

- hero：引人注目的页面标题（务实而吸引人）
- features、：突出您产品的关键功能和特性（结合当前项目和产品定位痛点）
- CTA (Call-To-Action)：鼓励用户行动（结合当前项目和产品定位痛点）
- 推荐：显示客户评价和推荐
- logo云：显示合作伙伴或客户logo
- pricing：展示您的价格计划（例如：免费计划、按积分定价（1-2个档次）、企业套餐（联系））
- 试用：支持首次使用体验，（例如：支持非注册首张照片的处理，但是带水印，下载需要登录）
- 集成：展示第三方集成
- 统计：显示重要指标和统计数据
- contact：比较不同的产品功能或计划
- 页脚：带有链接和信息的页脚
- 比较器：比较不同的产品功能或计划
- 常见问题：回答常见问题

login/register（登录注册/认证）

- 整体页面左右布局，左边主体显示背景、平台logo和广告语相关、文案信息等
- 右侧显示登录和注册页面、支持登录和注册切换
- 注册支持邮箱（用户名）、密码注册、邮箱验证码
- 三方登录：默认支持谷歌登录
- 支持密码找回
- 框架约束：主要使用better-auth进行实现，前端可以根据选型和要求进行调整和优化

navigation（导航栏）

- 设计约束：顶部导航栏通常和左侧菜单栏的logo和标题区域等高对齐
- 布局：导航左侧显示当前主体页面标题文字和欢迎语、右侧显示搜索栏、语言切换、主题切换

slidebar （左侧菜单）

- 整体布局：上中下三块布局，从上到下依次为logo和标题区域、菜单区域、用户状态和设置区域
- logo和标题区域：位于左侧菜单顶部，通常显示产品的logo和名称，左侧logo，右侧标题
- 菜单区域：一级菜单和二级菜单，不超过二级菜单，左侧图标，右侧菜单名称，默认一级菜单
- 用户状态和设置区域：位于左侧菜单底部，左侧用户头像，右侧昵称+状态（会员状态/在线状态）
- 交互设计惯例：可以支持菜单展开和收缩，使用lucide-react的PanelLeftClose和PanelLeft图标实现
- 响应式：支持web端和移动端响应适配
- 其他：用户状态和设置区域点击可以弹出和菜单等宽并且和信息栏顶部对齐的弹出菜单，菜单项通常包括：用户状态信息（头像、昵称）、升级（用户会员）、个性化、设置、帮助、退出登录

MainPage（主体页面）

- 导航栏左侧菜单为公共组件、主体页面和菜单项页面对应
- 主体页面和顶部导航、左侧菜单等距离留白对齐
- 主体页面为多个页面组件组成，具体根据业务需求设计

前端工程化：

- 默认使用.env文件，生产环境使用.env.production,测试环境为.env.development,本地环境为.env.local
- README.md文件描述前端功能使用和调试步骤
- 文件夹默认为frontend

## 后端

- 架构设计原则：分层设计原则（至少要求数据访问层、业务逻辑层、接口路由分离）
- 缓存和高并发：使用redis作为消息队列或者缓存层
- API接口：使用fastapi框架，符合rest api设计规范
- 配置文件：默认使用.env文件，生产环境使用.env.production,测试环境为.env.development,本地环境为.env.local
- 文件夹规范：文件夹默认为backend
- README.md文件描述后端功能使用和调试步骤

# 产品设计原则

- 主要突出的特点：简单、易用、快速、实现效果好
- 不要过多暴露技术细节只需要站在用户角度进行宣传和描述
- 遵循现代UI设计和sass主流产品设计方法和原则
- 注重产品交互和用户体验，实用主义、避免过度设计和炫技

# UI/UX设计原则

- 使用主流应用使用的字体、字号、字体颜色
- 避免多种配色方案，统一样式配置惯例
- 输出高保真的web UI设计，确保用于商业化场景。
- 用户体验分析：先分析项目的主要功能和用户需求，确定核心交互逻辑。
- 产品界面规划：作为产品经理，定义关键界面，确保信息架构合理。
- 高保真 UI 设计：作为 UI 设计师，设计贴近真实、现代web 工具类sass规范、 设计规范的界面，使用现代化的 UI 元素，使其具有良好的视觉体验。
- 移动端响应适配
- 真实感增强： 使用真实的 UI 图片，而非占位符图片（可从 Unsplash、Pexels、Apple 官方 UI 资源中选择）。

# 配色和主题方案参考

# 外部工具调用和支持

- context7 mcp：可以实现对各类开源软件包和文档进行在线查阅，当你对某个软件或者包的具体原理和功能不了解请使用context7 mcp进行文档查阅和参考，其次才是Web Fetch
- Figma desktop mcp：当用户提供Figma设计稿的selection link时，请务必使用Figma mcp进行设计稿code获取并复现

# 项目规范

- gitignore文件：需考虑前后端
- docs目录：主要存放项目相关的文档和档案材料
- CI/CD：根据项目有dockerfile和docker compose文件
- README.md：项目描述文件，需要清晰描述项目运行、部署步骤说明

# 运行环境约束

- 没有明确要求的情况下避免npm/pnpm build前端项目
- python执行环境目录为backend/venv下
- 当前项目运行环境为Windows、powershell，避免使用linux常用命令和工具造成无效执行