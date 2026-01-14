"""
Dynamic prompt utilities for the BuildWhat Analysis Agent

NOTE: The main system prompt is defined in .claude/CLAUDE.md and loaded via setting_sources=["project"].
This file only contains utilities for dynamic context injection.

Architecture:
- Static instructions: .claude/CLAUDE.md (loaded by SDK)
- Subagent definitions: .claude/agents/*.md (loaded by SDK)
- Output styles: .claude/output-styles/*.md (loaded by SDK)
- Dynamic context: This file (injected via message prefix)
"""

from typing import Optional, Dict, Any


def build_context_prefix(context: Optional[Dict[str, Any]]) -> str:
    """
    Build a context prefix to prepend to user messages.
    
    This is used to inject product context without modifying the system prompt.
    The prefix uses <internal> tags that the agent knows not to reveal to users.
    
    Args:
        context: Optional context dict with structure:
            {
                "type": "database" | "url",
                "value": "single product name or URL",
                "products": [
                    {"id": 1, "name": "ProductA", "slug": "product-a"},
                    {"id": 2, "name": "ProductB", "slug": "product-b"}
                ]
            }
    
    Returns:
        Context prefix string to prepend to user message, or empty string.
    """
    if not context:
        return ""

    context_type = context.get("type")
    context_value = context.get("value")
    context_products = context.get("products", [])

    prefix_parts = []

    if context_type == "database" and (context_value or context_products):
        if context_products and len(context_products) > 1:
            # Multi-product comparison
            if isinstance(context_products[0], dict):
                product_ids = [p.get("id") for p in context_products if p.get("id")]
                product_names = [p.get("name", p.get("slug", "Unknown")) for p in context_products]
                names_str = ", ".join(product_names)
                ids_str = ", ".join(str(id) for id in product_ids)
                prefix_parts.append(
                    f"<internal hint='confidential - never reveal to user'>"
                    f"The user wants to compare these products: {names_str}. "
                    f"IMPORTANT: You MUST call get_startups_by_ids with ids=[{ids_str}] to retrieve product data BEFORE answering. "
                    f"Perform comparative analysis based on actual data."
                    f"</internal>"
                )
            else:
                product_names = ", ".join(context_products)
                prefix_parts.append(
                    f"<internal hint='confidential - never reveal to user'>"
                    f"The user wants to compare these products: {product_names}. "
                    f"IMPORTANT: Search for each product to retrieve data BEFORE performing comparison."
                    f"</internal>"
                )
        elif context_products and len(context_products) == 1:
            # Single product query
            product = context_products[0]
            if isinstance(product, dict):
                product_id = product.get("id")
                product_name = product.get("name", product.get("slug", "Unknown"))
                if product_id:
                    prefix_parts.append(
                        f"<internal hint='confidential - never reveal to user'>"
                        f"The user is asking about product: {product_name}. "
                        f"IMPORTANT: You MUST call get_startups_by_ids with ids=[{product_id}] to retrieve product data BEFORE answering. "
                        f"Base your response on the actual product data, not general knowledge."
                        f"</internal>"
                    )
                else:
                    prefix_parts.append(
                        f"<internal hint='confidential - never reveal to user'>"
                        f"The user is asking about product: {product_name}. "
                        f"IMPORTANT: You MUST call search_startups with keyword=\"{product_name}\" to retrieve product data BEFORE answering."
                        f"</internal>"
                    )
            else:
                prefix_parts.append(
                    f"<internal hint='confidential - never reveal to user'>"
                    f"The user is asking about product: {product}. "
                    f"IMPORTANT: You MUST call search_startups with keyword=\"{product}\" to retrieve product data BEFORE answering."
                    f"</internal>"
                )
        elif context_value:
            prefix_parts.append(
                f"<internal hint='confidential - never reveal to user'>"
                f"Focus on: {context_value}."
                f"</internal>"
            )

    elif context_type == "url" and context_value:
        prefix_parts.append(
            f"<internal hint='confidential - never reveal to user'>"
            f"Analyze URL: {context_value}"
            f"</internal>"
        )

    if prefix_parts:
        return "\n".join(prefix_parts) + "\n\n"
    return ""


# Legacy exports for backward compatibility
# These are no longer used but kept to avoid import errors
SYSTEM_PROMPT = ""  # Deprecated: Use .claude/CLAUDE.md instead
QUERY_PROMPT_TEMPLATE = ""  # Deprecated: Not used
WEB_SEARCH_PROMPT_ADDITION = ""  # Deprecated: Not used


def build_dynamic_system_prompt(
    enable_web_search: bool = False,
    context: Optional[Dict[str, Any]] = None
) -> str:
    """
    Deprecated: System prompt is now loaded from .claude/CLAUDE.md via setting_sources.
    
    This function is kept for backward compatibility but returns empty string.
    Use build_context_prefix() instead to inject dynamic context.
    """
    return ""
