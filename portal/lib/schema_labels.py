"""
Human-friendly labels for schemas, tables, columns.

Why: raw Postgres names like `tt_gmvmax_creative_daily` or
`sku_subtotal_after_discount` are opaque to POCs. The Browse Data
dropdowns now show a friendly label first, with the technical name
preserved alongside in the value attribute and audit trail.

How to maintain:
  - Add entries to SCHEMA_LABELS / TABLE_LABELS as you discover better
    names. Anything not in the mapping falls back to a generic
    snake_case → Title Case transform with known acronyms preserved.
  - If you're unsure what a name means, leave it to fall through — the
    auto-formatter usually produces something readable enough.
"""

from __future__ import annotations

# Per-schema friendly names. Add aggressively — POCs see these.
# Names describe what the data IS, not what the schema is called.
SCHEMA_LABELS: dict[str, str] = {
    "acq_dashboard": "Creator acquisition pipeline",
    "creator_dashboard": "Creator master list",
    "rootlabs_core": "Products, SKUs & team",
    "tiktok_raw_data": "TikTok performance (videos, lives, orders)",
    "tt_creator_relations_raw_data": "Creator deals & contacts",
    "tejas_sync": "CSV upload sessions (Tejas)",
    "wp_convo": "WhatsApp / Periskope chats",
    "public": "System (unused)",
}

# Per-table friendly names, keyed by (schema, table).
# Names describe content: the verb/object a POC would search for.
TABLE_LABELS: dict[tuple[str, str], str] = {
    # TikTok performance — the high-traffic schema
    ("tiktok_raw_data", "tt_video"): "Videos posted by creators",
    ("tiktok_raw_data", "tiktok_orders"): "Orders (every purchase)",
    ("tiktok_raw_data", "tiktok_affiliate_orders"): "Orders attributed to a creator",
    ("tiktok_raw_data", "live_campaign_performance"): "Livestream sales performance",
    ("tiktok_raw_data", "product_campaign_performance"): "Product ad-campaign performance",
    ("tiktok_raw_data", "rootlabs_brand_usernames"): "Our official TikTok handles",
    ("tiktok_raw_data", "tiktok_fbt_inventory"): "Inventory in TikTok warehouses (FBT)",
    ("tiktok_raw_data", "tt_gmvmax_creative_daily"): "GMV Max ad creatives — daily metrics",
    ("tiktok_raw_data", "tt_video_enrichments"): "Video metadata enrichments (hashtags, music)",
    # Creator pipeline
    ("acq_dashboard", "creators"): "Creators being onboarded",
    ("acq_dashboard", "daily_snapshots"): "Daily onboarding stage snapshots",
    ("acq_dashboard", "creator_snapshots"): "Per-creator onboarding history",
    # Master list
    ("creator_dashboard", "creators"): "All creators (master list)",
    ("creator_dashboard", "creator_audit_log"): "Edits / changes to creator records",
    ("creator_dashboard", "creator_daily_metrics"): "Per-creator daily metrics",
    # Products & team
    ("rootlabs_core", "rootlabs_products"): "Our products (HGR, MagAshwa, Alpha, …)",
    ("rootlabs_core", "rootlabs_sku_listings"): "Product listings on TikTok (SKU links)",
    ("rootlabs_core", "rootlabs_team_members"): "Rootlabs team members",
    ("rootlabs_core", "rootlabs_communication_channels"): "Comms channels (Slack, email, etc.)",
    ("rootlabs_core", "team_member_phones"): "Team member phone numbers",
    # Creator deals & contacts (Airtable mirror)
    ("tt_creator_relations_raw_data", "creator_collab_master"): "Creator contacts (Airtable mirror)",
    ("tt_creator_relations_raw_data", "creator_deals_expenses"): "Creator deals & expenses log",
    # Tejas uploads
    ("tejas_sync", "upload_sessions"): "Uploaded CSV file history",
    ("tejas_sync", "sync_sources"): "Configured data sources",
    # WhatsApp / Periskope
    ("wp_convo", "conversations"): "Chats with creators",
    ("wp_convo", "messages"): "Every chat message sent / received",
    ("wp_convo", "attachments"): "Images & files in chats",
    ("wp_convo", "webhook_events"): "Raw events from Periskope webhook",
}

# Per-column friendly names — optional, keyed by (schema, table, column).
# Sparse: only fill in when a column name is genuinely confusing.
COLUMN_LABELS: dict[tuple[str, str, str], str] = {
    ("tiktok_raw_data", "tiktok_orders", "sku_subtotal_after_discount"): "Subtotal after discount",
    ("tiktok_raw_data", "tiktok_orders", "sku_platform_discount"): "Platform discount",
    ("tiktok_raw_data", "tiktok_orders", "cancellation_return_type"): "Cancellation / return type",
    ("tiktok_raw_data", "tiktok_orders", "normal_or_preorder"): "Order kind (normal / preorder)",
    ("tiktok_raw_data", "tiktok_orders", "created_time"): "Created at (UTC)",
}

# Acronyms that should keep their casing rather than being title-cased.
_ACRONYMS: dict[str, str] = {
    "tt": "TikTok",
    "gmv": "GMV",
    "fbt": "FBT",
    "hgr": "HGR",
    "sku": "SKU",
    "id": "ID",
    "url": "URL",
    "ist": "IST",
    "utc": "UTC",
    "mtd": "MTD",
    "ymd": "YMD",
    "wp": "WP",
}


def nice_label(name: str) -> str:
    """Generic snake_case → Title Case with acronym preservation.

    Used as fallback when no explicit mapping exists.
    """
    if not name:
        return name
    parts = name.split("_")
    out: list[str] = []
    for p in parts:
        if p.lower() in _ACRONYMS:
            out.append(_ACRONYMS[p.lower()])
        elif p.isupper():
            out.append(p)
        else:
            out.append(p.capitalize())
    return " ".join(out)


def schema_label(name: str) -> str:
    return SCHEMA_LABELS.get(name, nice_label(name))


def table_label(schema: str, table: str) -> str:
    return TABLE_LABELS.get((schema, table), nice_label(table))


def column_label(schema: str, table: str, column: str) -> str:
    return COLUMN_LABELS.get((schema, table, column), nice_label(column))


# ────────────────────────────────────────────────────────────────────
# Column priority — what POCs actually pick first in dropdowns.
# Per-table explicit list takes precedence; generic patterns fall back.
# ────────────────────────────────────────────────────────────────────

COLUMN_PRIORITY: dict[tuple[str, str], list[str]] = {
    ("tiktok_raw_data", "tt_video"): [
        "handle", "video_id", "post_time", "product",
    ],
    ("tiktok_raw_data", "tiktok_affiliate_orders"): [
        "creator_username", "content_type", "content_id",
        "time_created", "order_id", "sku_id", "rate", "commission_paid",
    ],
    ("tiktok_raw_data", "tiktok_orders"): [
        "order_status", "order_substatus", "created_time",
        "sku_subtotal_after_discount", "sku_platform_discount",
        "quantity", "cancellation_return_type", "normal_or_preorder",
        "order_id", "sku_id", "seller_sku",
    ],
    ("tiktok_raw_data", "live_campaign_performance"): [
        "creator_username", "campaign_id", "live_date",
        "gmv", "viewers", "duration",
    ],
    ("tiktok_raw_data", "product_campaign_performance"): [
        "product_name", "campaign_id", "campaign_date",
        "gmv", "impressions", "clicks",
    ],
}

# Generic heuristic — used when no per-table list applies, or for columns
# the per-table list didn't include. Lower weight = higher priority.
_PRIORITY_PATTERNS: list[tuple[str, int]] = [
    (r"^(handle|creator_username|creator)$", 10),
    (r"_username$|_handle$", 15),
    (r"^(product|sku_name|variation|product_name)$", 20),
    (r"^(order_status|content_type|status|state|order_substatus)$", 25),
    (r"^(post_time|created_time|time_created|date|live_date|campaign_date)$", 30),
    (r"_time$|^time_|_date$", 35),
    (r"^(video_id|content_id|campaign_id|order_id)$", 40),
    (r"^(quantity|gmv|amount|count|revenue|price|impressions|clicks|viewers)$", 45),
    (r"^sku_", 50),
    (r"_id$", 60),  # generic _id columns less interesting than business IDs
    (r"^last_synced|^ingested|^etl_", 90),  # housekeeping at the bottom
]


def column_sort_key(schema: str, table: str, column: str) -> tuple[int, int, str]:
    """Lower tuple = appears earlier in dropdowns."""
    priority_list = COLUMN_PRIORITY.get((schema, table), [])
    if column in priority_list:
        return (0, priority_list.index(column), column)
    import re
    for pattern, weight in _PRIORITY_PATTERNS:
        if re.search(pattern, column):
            return (1, weight, column)
    return (2, 0, column)


def sort_columns(schema: str, table: str, columns: list) -> list:
    """Sort ColumnInfo (or dicts with `.name`) by POC-priority. Returns a new list."""
    def keyfn(c):
        name = c["name"] if isinstance(c, dict) else c.name
        return column_sort_key(schema, table, name)
    return sorted(columns, key=keyfn)


# Per-table creator column — used by the POC scope filter.
CREATOR_COLUMN: dict[tuple[str, str], str] = {
    ("tiktok_raw_data", "tt_video"): "handle",
    ("tiktok_raw_data", "tiktok_affiliate_orders"): "creator_username",
    ("tiktok_raw_data", "live_campaign_performance"): "creator_username",
    ("tiktok_raw_data", "product_campaign_performance"): "creator_username",
}


def creator_column_for(schema: str, table: str) -> str | None:
    """Return the column name that holds the creator handle for this table,
    or None if the table has no creator concept."""
    return CREATOR_COLUMN.get((schema, table))
