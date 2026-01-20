# Database Schema Reference

## Overview

This document describes the database tables and fields available for template filter rules. All tables are defined in `backend/database/models.py`.

## Core Tables

### startups

Primary product information table.

**Available fields for filtering**:
- `id` (int): Primary key
- `name` (str): Product name
- `slug` (str): URL-friendly identifier
- `tagline` (str): Short description
- `description` (text): Full description
- `website` (str): Product website URL
- `logo_url` (str): Logo image URL
- `category` (str): Product category
- `revenue_30d` (int): 30-day revenue in USD
- `revenue_all_time` (int): All-time revenue
- `founder_id` (int): Founder ID
- `founder_name` (str): Founder name
- `founder_followers` (int): Founder's follower count
- `team_size` (int): Team size
- `launch_date` (date): Product launch date
- `created_at` (datetime): Record creation time
- `updated_at` (datetime): Last update time

**Common filter patterns**:
``python
"startup": {
    "revenue_30d": {"min": 5000, "max": 50000},
    "founder_followers": {"max": 1000},
    "team_size": {"max": 2},
    "category": {"contains": ["developer", "api"]}
}
``

### product_selection_analysis

Product analysis focusing on growth drivers and technical characteristics.

**Available fields for filtering**:
- `startup_id` (int): Foreign key to startups
- `growth_driver` (str): Main growth driver (product_driven, ip_driven, content_driven, channel_driven)
- `is_product_driven` (bool): Whether product-driven
- `ip_dependency_score` (float): IP dependency score (0-10)
- `follower_revenue_ratio` (float): Follower to revenue ratio
- `tech_complexity_level` (str): Technical complexity (low, medium, high)
- `feature_complexity` (str): Feature complexity (simple, moderate, complex)
- `ai_dependency_level` (str): AI dependency (none, light, moderate, heavy)
- `startup_cost_level` (str): Startup cost (low, medium, high)
- `market_scope` (str): Market scope (horizontal, vertical)
- `target_customer` (str): Target customer type (b2c, b2b_smb, b2b_enterprise, b2d)
- `requires_realtime` (bool): Requires real-time processing
- `requires_large_data` (bool): Requires large datasets
- `requires_compliance` (bool): Requires regulatory compliance

See full documentation in file for more details.
