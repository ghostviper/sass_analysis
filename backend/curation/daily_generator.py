"""
每日策展生成器

基于模板定义，从数据库筛选匹配的产品，生成 DailyCuration 记录。
"""

import logging
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_, or_, not_
from sqlalchemy.orm import Session

from database.models import (
    Startup,
    ProductSelectionAnalysis,
    LandingPageAnalysis,
    MotherThemeJudgment,
    DailyCuration,
    CurationProduct,
)
from .daily_templates import CurationTemplate, ALL_TEMPLATES, get_template

logger = logging.getLogger(__name__)


class DailyCurationGenerator:
    """每日策展生成器"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_curation(
        self,
        template: CurationTemplate,
        curation_date: date,
        force_regenerate: bool = False
    ) -> Optional[DailyCuration]:
        """
        根据模板生成一条策展记录
        
        Args:
            template: 策展模板
            curation_date: 策展日期
            force_regenerate: 是否强制重新生成（会删除已有记录）
        
        Returns:
            生成的 DailyCuration 对象，如果产品数量不足则返回 None
        """
        curation_key = f"{template.key}_{curation_date.isoformat()}"
        
        # 检查是否已存在
        existing = self.db.query(DailyCuration).filter(
            DailyCuration.curation_key == curation_key
        ).first()
        
        if existing:
            if force_regenerate:
                self.db.delete(existing)
                self.db.flush()
            else:
                logger.info(f"策展已存在: {curation_key}")
                return existing
        
        # 筛选匹配的产品
        products = self._filter_products(template.filter_rules)
        
        if len(products) < template.min_products:
            logger.warning(
                f"模板 {template.key} 匹配产品不足: "
                f"需要 {template.min_products}，实际 {len(products)}"
            )
            return None
        
        # 限制产品数量
        products = products[:template.max_products]
        
        # 创建策展记录
        curation = DailyCuration(
            curation_key=curation_key,
            title=template.title_zh,
            title_zh=template.title_zh,
            title_en=template.title_en,
            description=template.description_zh,
            description_zh=template.description_zh,
            description_en=template.description_en,
            insight=template.insight_zh,
            insight_zh=template.insight_zh,
            insight_en=template.insight_en,
            tag=template.tag_zh,
            tag_zh=template.tag_zh,
            tag_en=template.tag_en,
            tag_color=template.tag_color,
            curation_type=template.curation_type,
            filter_rules=template.filter_rules,
            conflict_dimensions=template.conflict_dimensions,
            curation_date=curation_date,
            is_active=True,
            ai_generated=True,
        )
        self.db.add(curation)
        self.db.flush()
        
        # 添加产品关联
        for i, (startup, highlight_zh, highlight_en) in enumerate(products):
            cp = CurationProduct(
                curation_id=curation.id,
                startup_id=startup.id,
                highlight_zh=highlight_zh,
                highlight_en=highlight_en,
                display_order=i,
            )
            self.db.add(cp)
        
        self.db.commit()
        logger.info(f"生成策展: {curation_key}，包含 {len(products)} 个产品")
        
        return curation
    
    def _filter_products(
        self, 
        filter_rules: Dict[str, Any]
    ) -> List[Tuple[Startup, str, str]]:
        """
        根据筛选规则查询匹配的产品
        
        Returns:
            List of (Startup, highlight_zh, highlight_en) tuples
        """
        # 基础查询
        query = self.db.query(Startup).filter(
            Startup.revenue_30d.isnot(None),
            Startup.revenue_30d > 0
        )
        
        # 应用 startup 层面的筛选
        startup_rules = filter_rules.get("startup", {})
        query = self._apply_startup_filters(query, startup_rules)
        
        # 获取候选产品
        candidates = query.all()
        
        # 应用需要 join 的筛选（母题判断、选品分析、落地页分析）
        results = []
        for startup in candidates:
            if self._matches_advanced_filters(startup, filter_rules):
                highlight_zh, highlight_en = self._generate_highlight(startup, filter_rules)
                results.append((startup, highlight_zh, highlight_en))
        
        # 按收入排序
        results.sort(key=lambda x: x[0].revenue_30d or 0, reverse=True)
        
        return results
    
    def _apply_startup_filters(self, query, rules: Dict[str, Any]):
        """应用 Startup 表的筛选条件"""
        for field, condition in rules.items():
            if field == "revenue_30d":
                if "min" in condition:
                    query = query.filter(Startup.revenue_30d >= condition["min"])
                if "max" in condition:
                    query = query.filter(Startup.revenue_30d <= condition["max"])
            
            elif field == "founder_followers":
                if "min" in condition:
                    query = query.filter(Startup.founder_followers >= condition["min"])
                if "max" in condition:
                    query = query.filter(Startup.founder_followers <= condition["max"])
            
            elif field == "team_size":
                if "max" in condition:
                    query = query.filter(
                        or_(
                            Startup.team_size.is_(None),
                            Startup.team_size <= condition["max"]
                        )
                    )
            
            elif field == "category":
                if "contains" in condition:
                    # 类别包含任一关键词
                    category_filters = [
                        Startup.category.ilike(f"%{kw}%") 
                        for kw in condition["contains"]
                    ]
                    query = query.filter(or_(*category_filters))
        
        return query
    
    def _matches_advanced_filters(
        self, 
        startup: Startup, 
        filter_rules: Dict[str, Any]
    ) -> bool:
        """检查产品是否匹配高级筛选条件（母题、选品分析等）"""
        
        # 母题判断筛选
        mother_theme_rules = filter_rules.get("mother_theme", {})
        if mother_theme_rules:
            judgments = self.db.query(MotherThemeJudgment).filter(
                MotherThemeJudgment.startup_id == startup.id
            ).all()
            judgment_map = {j.theme_key: j.judgment for j in judgments}
            
            for theme_key, expected_values in mother_theme_rules.items():
                actual = judgment_map.get(theme_key)
                
                # 处理 "not" 条件
                if isinstance(expected_values, dict) and "not" in expected_values:
                    if actual in expected_values["not"]:
                        return False
                # 处理正向匹配
                elif isinstance(expected_values, list):
                    if actual not in expected_values:
                        return False
        
        # 选品分析筛选
        selection_rules = filter_rules.get("selection", {})
        if selection_rules:
            selection = self.db.query(ProductSelectionAnalysis).filter(
                ProductSelectionAnalysis.startup_id == startup.id
            ).first()
            
            if not selection:
                return False
            
            for field, expected_values in selection_rules.items():
                actual = getattr(selection, field, None)
                if isinstance(expected_values, list):
                    if actual not in expected_values:
                        return False
        
        # 落地页分析筛选
        landing_rules = filter_rules.get("landing_page", {})
        if landing_rules:
            landing = self.db.query(LandingPageAnalysis).filter(
                LandingPageAnalysis.startup_id == startup.id
            ).first()
            
            if not landing:
                return False
            
            for field, condition in landing_rules.items():
                actual = getattr(landing, field, None)
                if actual is None:
                    return False
                if "max" in condition and actual > condition["max"]:
                    return False
                if "min" in condition and actual < condition["min"]:
                    return False
        
        return True
    
    def _generate_highlight(
        self, 
        startup: Startup, 
        filter_rules: Dict[str, Any]
    ) -> Tuple[str, str]:
        """为产品生成亮点文案"""
        revenue = startup.revenue_30d or 0
        followers = startup.founder_followers or 0
        
        # 根据冲突维度生成亮点
        conflict_dims = filter_rules.get("conflict_dimensions", [])
        
        # 低粉丝高收入
        if "founder_followers" in str(filter_rules) and followers < 1000 and revenue > 5000:
            return (
                f"粉丝{followers}，月入${revenue:,.0f}",
                f"{followers} followers, ${revenue:,.0f}/mo"
            )
        
        # 功能简单
        if "feature_complexity" in str(filter_rules):
            return (
                f"功能极简，月入${revenue:,.0f}",
                f"Minimal features, ${revenue:,.0f}/mo"
            )
        
        # 默认亮点
        return (
            f"月入${revenue:,.0f}",
            f"${revenue:,.0f}/mo"
        )
    
    def generate_all_for_date(
        self, 
        curation_date: date,
        template_keys: Optional[List[str]] = None,
        force_regenerate: bool = False
    ) -> List[DailyCuration]:
        """
        为指定日期生成所有策展
        
        Args:
            curation_date: 策展日期
            template_keys: 要生成的模板key列表，None表示全部
            force_regenerate: 是否强制重新生成
        
        Returns:
            成功生成的策展列表
        """
        templates = ALL_TEMPLATES
        if template_keys:
            templates = [t for t in templates if t.key in template_keys]
        
        results = []
        for template in templates:
            try:
                curation = self.generate_curation(
                    template, 
                    curation_date, 
                    force_regenerate
                )
                if curation:
                    results.append(curation)
            except Exception as e:
                logger.error(f"生成策展失败 {template.key}: {e}")
        
        return results
    
    def preview_template(self, template_key: str) -> Dict[str, Any]:
        """
        预览模板匹配的产品（不写入数据库）
        
        Returns:
            包含模板信息和匹配产品的字典
        """
        template = get_template(template_key)
        if not template:
            return {"error": f"模板不存在: {template_key}"}
        
        products = self._filter_products(template.filter_rules)
        
        return {
            "template": {
                "key": template.key,
                "title_zh": template.title_zh,
                "title_en": template.title_en,
                "description_zh": template.description_zh,
                "curation_type": template.curation_type,
                "filter_rules": template.filter_rules,
            },
            "matched_count": len(products),
            "min_required": template.min_products,
            "is_viable": len(products) >= template.min_products,
            "products": [
                {
                    "id": p[0].id,
                    "name": p[0].name,
                    "revenue_30d": p[0].revenue_30d,
                    "founder_followers": p[0].founder_followers,
                    "highlight_zh": p[1],
                    "highlight_en": p[2],
                }
                for p in products[:10]  # 最多显示10个
            ]
        }
