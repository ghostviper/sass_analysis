#!/usr/bin/env python3
"""
Template Validation Script

Validates CurationTemplate objects for correctness and quality.
"""

import sys
import ast
import argparse
from pathlib import Path
from typing import List, Dict, Any

# Valid field names by table
VALID_FIELDS = {
    "startup": ["revenue_30d", "founder_followers", "team_size", "category"],
    "selection": [
        "growth_driver", "feature_complexity", "startup_cost_level",
        "ai_dependency_level", "target_customer", "market_scope",
        "tech_complexity_level", "requires_realtime", "requires_large_data"
    ],
    "mother_theme": [
        "success_driver", "demand_type", "entry_barrier", "mvp_clarity",
        "solo_feasibility", "primary_risk", "opportunity_validity",
        "positioning_insight", "differentiation_point"
    ],
    "landing_page": [
        "feature_count", "has_instant_value_demo", "conversion_friendliness_score",
        "pain_point_sharpness", "positioning_clarity_score"
    ]
}

# Valid enum values
VALID_ENUMS = {
    "growth_driver": ["product_driven", "ip_driven", "content_driven", "channel_driven"],
    "feature_complexity": ["simple", "moderate", "complex"],
    "startup_cost_level": ["low", "medium", "high"],
    "ai_dependency_level": ["none", "light", "moderate", "heavy"],
    "target_customer": ["b2c", "b2b_smb", "b2b_enterprise", "b2d"],
    "market_scope": ["horizontal", "vertical"],
    "tech_complexity_level": ["low", "medium", "high"],
    "curation_type": ["contrast", "cognitive", "action", "niche"],
}

# Tailwind colors
VALID_COLORS = [
    "amber", "emerald", "blue", "purple", "slate", "teal",
    "orange", "green", "indigo", "cyan", "red", "yellow", "gray"
]


def validate_template(template_dict: Dict[str, Any]) -> List[str]:
    """Validate a single template, return list of errors"""
    errors = []
    
    # Check required fields
    required_fields = [
        "key", "title_zh", "title_en", "description_zh", "description_en",
        "insight_zh", "insight_en", "tag_zh", "tag_en", "tag_color",
        "curation_type", "filter_rules", "conflict_dimensions"
    ]
    
    for field in required_fields:
        if field not in template_dict:
            errors.append(f"Missing required field: {field}")
    
    # Validate key format
    if "key" in template_dict:
        key = template_dict["key"]
        if not key.islower() or " " in key:
            errors.append(f"Invalid key format: {key} (should be snake_case)")
    
    # Validate curation_type
    if "curation_type" in template_dict:
        ctype = template_dict["curation_type"]
        if ctype not in VALID_ENUMS["curation_type"]:
            errors.append(f"Invalid curation_type: {ctype}")
    
    # Validate tag_color
    if "tag_color" in template_dict:
        color = template_dict["tag_color"]
        if color not in VALID_COLORS:
            errors.append(f"Invalid tag_color: {color}")

    
    # Validate filter_rules
    if "filter_rules" in template_dict:
        filter_rules = template_dict["filter_rules"]
        
        for table, rules in filter_rules.items():
            if table not in VALID_FIELDS:
                errors.append(f"Invalid table in filter_rules: {table}")
                continue
            
            for field, value in rules.items():
                if field not in VALID_FIELDS[table]:
                    errors.append(f"Invalid field {table}.{field}")
                
                # Check enum values
                if field in VALID_ENUMS and isinstance(value, list):
                    for v in value:
                        if v not in VALID_ENUMS[field]:
                            errors.append(f"Invalid enum value for {field}: {v}")
    
    # Validate priority
    if "priority" in template_dict:
        priority = template_dict["priority"]
        if not (1 <= priority <= 10):
            errors.append(f"Priority out of range: {priority} (should be 1-10)")
    
    # Validate product counts
    if "min_products" in template_dict and "max_products" in template_dict:
        if template_dict["min_products"] > template_dict["max_products"]:
            errors.append("min_products > max_products")
    
    # Check bilingual completeness
    for lang_pair in [("title_zh", "title_en"), ("description_zh", "description_en"), 
                      ("insight_zh", "insight_en"), ("tag_zh", "tag_en")]:
        zh, en = lang_pair
        if zh in template_dict and en in template_dict:
            if bool(template_dict[zh]) != bool(template_dict[en]):
                errors.append(f"Incomplete bilingual pair: {zh}/{en}")
    
    return errors


def main():
    parser = argparse.ArgumentParser(description="Validate curation templates")
    parser.add_argument("--template-file", "-f", required=True, help="Template file to validate")
    
    args = parser.parse_args()
    
    template_file = Path(args.template_file)
    if not template_file.exists():
        print(f"❌ File not found: {template_file}")
        sys.exit(1)
    
    print(f"🔍 Validating templates in: {template_file}")
    print()
    
    # Read and parse file
    content = template_file.read_text(encoding="utf-8")
    
    # Simple validation: check if it contains CurationTemplate
    if "CurationTemplate" not in content:
        print("❌ File does not contain CurationTemplate definitions")
        sys.exit(1)
    
    print("✅ File structure looks valid")
    print()
    print("⚠️  Note: Full validation requires running the templates in Python context")
    print("   Suggested next step: Import templates and test with preview script")


if __name__ == "__main__":
    main()
