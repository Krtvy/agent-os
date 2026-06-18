# Cruva — Platform Knowledge for Hanuman

> **Imported 2026-05-13 04:18 IST** from `/Users/mosaic/creator-intel/platforms/cruva.com-api.md` (mapped 2026-04-29 live from `cruva.com/dashboard/api`).
>
> **Product URL:** https://cruva.com
> **API base:** https://api.cruva.com
> **MCP server:** https://mcp.cruva.com/sse?api_key=<KEY>
> **Plan in use at Rootlabs:** Scale ($599/mo) — confirmed via `_audit/PROJECT-STORY` context (provenance: `/Users/mosaic/creator-intel/PROJECT-STORY.md`).
>
> The full content below is the **canonical Cruva API specification** as captured live from the product. This is the authoritative reference Hanuman uses for any Cruva-touching task.
>
> Vidura's third-party research **integrated 2026-05-13 04:33 IST** (see appendix at end of file — 13 tier-tagged sources B1–B13 covering founder info, market positioning, and competitive comparisons vs Grin/Aspire/Brevo). The canonical API spec below remains the operational ground truth; the appendix adds context, not authority.
>
> Companion files: [`apify.md`](apify.md) · [`kalodata.md`](kalodata.md) · [`README.md`](README.md). For the operational story of how Hanuman would actually use these endpoints (including known Kalodata anti-abuse gotchas), see `/Users/mosaic/creator-intel/PROJECT-STORY.md`.

---

# Cruva API — JSON Reference

**Base URL:** `https://api.cruva.com`
**Source:** rendered from https://cruva.com/dashboard/api on 2026-04-29
**Account:** Pranav @ Root Labs · Plan: **Scale** · Cruva Shop ID: `68b5a03bba91e6252be52373`
**API key:** redacted in this file. Read live from `cruva.com/dashboard/api → API Key & Access` (eye/copy icons). The same key is also embedded in the MCP URL at `cruva.com/dashboard/api → Claude MCP`.

> **Safety:** treat the key as a bearer credential. Don't commit it. Cruva offers a "Rotate Key" button on the same modal if it leaks.

## Auth

All requests need:

```
Content-Type: application/json
x-api-key:   <YOUR_API_KEY>
x-shop-id:   <YOUR_CRUVA_SHOP_ID>
```

The `x-shop-id` is **Cruva's internal id**, not the TikTok shop id. Get it from `cruva.com/dashboard/my-shops → ⋯ → View Info`. One subscription is account-wide; `x-shop-id` selects which shop you're querying. The only endpoint that doesn't need `x-shop-id` is `GET /v1/account/shops` (used to discover shop ids).

## Rate limits

- 3 requests / second
- 50,000 requests / day

## Plan tiers

The endpoints below are split into **Standard API** (available on Basic / Growth / Scale) and **Enterprise API** (locked, requires custom plan). Root Labs is on Scale, so Standard endpoints work today; Enterprise endpoints return an "enterprise required" error until the plan is upgraded.

## Cruva also publishes an MCP server

```
https://mcp.cruva.com/sse?api_key=<YOUR_API_KEY>
```

Add it at `claude.ai/settings/connectors → Add custom connector`, name "Cruva". Gives Claude full access to the same endpoints below from chat.

---

# Endpoint catalogue

| #   | Method | Path                                      | Tier           | What it does                                                                                                                                                            |
| --- | ------ | ----------------------------------------- | -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | GET    | `/v1/account/shops`                       | Standard       | List shops on your account (also returns each shop's plan)                                                                                                              |
| 2   | POST   | `/v1/shop/products`                       | Standard       | List products in the current shop, fuzzy search supported                                                                                                               |
| 3   | POST   | `/v1/affiliate/crm/list`                  | Standard       | **Affiliates who have already worked with your store** (videos / sample requests / showcases)                                                                           |
| 4   | POST   | `/v1/affiliate/videos/list`               | Standard       | Affiliate videos for your shop with performance metrics                                                                                                                 |
| 5   | POST   | `/v1/affiliate/lives/list`                | Standard       | Affiliate live streams for your shop with per-product splits                                                                                                            |
| 6   | POST   | `/v1/affiliate/samples/list`              | Standard       | Sample requests received                                                                                                                                                |
| 7   | POST   | `/v1/affiliate/samples/approve`           | Standard       | Bulk approve sample requests by `apply_id`                                                                                                                              |
| 8   | POST   | `/v1/affiliate/samples/reject`            | Standard       | Bulk reject sample requests by `apply_id`                                                                                                                               |
| 9   | POST   | `/v1/shop/stats`                          | Standard       | Aggregated shop analytics with optional daily breakdowns (28+ stat keys, see below)                                                                                     |
| 10  | GET    | `/v1/shop/sps`                            | Standard       | Shop Performance Score 0–5. Below 3.5 = Cruva blocks outbound DMs.                                                                                                      |
| 11  | POST   | `/v1/timeseries/affiliates`               | Standard       | CRM affiliates ranked by performance over a date range                                                                                                                  |
| 12  | POST   | `/v1/timeseries/videos`                   | Standard       | Affiliate videos ranked by performance over a date range                                                                                                                |
| 13  | POST   | `/v1/affiliate/message/dm`                | Standard       | Send a direct TikTok DM to a creator (US/UK only)                                                                                                                       |
| 14  | POST   | `/v1/affiliate/message/list`              | Standard       | Last 20 messages exchanged with a given creator                                                                                                                         |
| 15  | POST   | `/v1/affiliate/marketplace/search`        | **Enterprise** | **Full creator profile by handle** — demographics, follower breakdown, brand-collab count, language, race, body type, age band, tone, etc. (THE creator-intel endpoint) |
| 16  | POST   | `/v1/intelligence/brands/search`          | **Enterprise** | Search any brand on TikTok Shop, returns GMV / views / video count / creator count                                                                                      |
| 17  | POST   | `/v1/intelligence/products/search`        | **Enterprise** | Search any product on TikTok Shop, returns GMV / units sold / views / creator count                                                                                     |
| 18  | POST   | `/v1/intelligence/brands/creators/list`   | **Enterprise** | Given a `brand_id`, list every creator driving GMV for that brand with full profiles                                                                                    |
| 19  | POST   | `/v1/intelligence/products/creators/list` | **Enterprise** | Given a `product_id`, list every creator driving GMV for that product                                                                                                   |
| 20  | POST   | `/v1/intelligence/creators/brands/list`   | **Enterprise** | Given a `creator_id`, which brands they've driven revenue for                                                                                                           |
| 21  | POST   | `/v1/intelligence/creators/products/list` | **Enterprise** | Given a `creator_id`, which products they've driven revenue for                                                                                                         |

---

# Standard endpoints — full schemas

## 1. List Shops

```http
GET /v1/account/shops
```

No body. Only header needed: `x-api-key`.

```json
{
  "path": "/v1/account/shops",
  "data": [
    {
      "shop_id": "a1b2c3d4e5f6g7h8i9j0k1l2",
      "shop_name": "Example Shop One",
      "is_active": true,
      "created_at": "2024-06-29",
      "plan": "growth"
    },
    {
      "shop_id": "m3n4o5p6q7r8s9t0u1v2w3x4",
      "shop_name": "Example Shop Two",
      "is_active": true,
      "created_at": "2025-06-10",
      "plan": "scale"
    }
  ]
}
```

## 2. List Shop Products

```http
POST /v1/shop/products
```

```json
{
  "search": "",
  "is_open_plan": null
}
```

`search` is fuzzy on product name. `is_open_plan` — `true` for open-plan only, `false` for non-open-plan only, `null` for all.

```json
{
  "path": "/v1/shop/products",
  "data": [
    {
      "product_id": "1800291847362058192",
      "product_name": "Glow Radiance Serum SPF30 – Hydrating Sun Shield",
      "status": 1,
      "is_open_plan": true,
      "price": 850.0,
      "units_sold": 4312
    }
  ]
}
```

## 3. CRM Search — affiliates already working with your store

```http
POST /v1/affiliate/crm/list
```

```json
{
  "page_size": 20,
  "page_number": 1,
  "sort_by": "gmv",
  "sort_direction": "desc",
  "filters": {
    "handle": "example_creator",
    "min_gmv": 0,
    "min_units_sold": 0,
    "min_videos": 0
  }
}
```

```json
{
  "path": "/v1/affiliate/crm/list",
  "data": {
    "results": [
      {
        "shop_id": "your_shop_id_here",
        "handle": "example_creator",
        "creator_oecuid": "7171717171717171717",
        "nickname": "Example Creator",
        "showcasing": true,
        "units_sold": 9081,
        "video_count": 80,
        "gmv": 271487.8,
        "last_post": null,
        "email": null,
        "phone_number": null,
        "video_gmv": 271447.81,
        "live_gmv": 0.0,
        "live_count": 0,
        "commission": 1234.5,
        "status": "Posted",
        "sampled_product": "product_id_123",
        "med_gmv_revenue": 107199,
        "follower_cnt": 84227,
        "post_rate": 1293,
        "tags": []
      }
    ],
    "has_more": false,
    "page_size": 20,
    "page_offset": 0
  }
}
```

> `med_gmv_revenue` = total GMV the creator earned across the platform in the last 30 days.

## 4. Videos Search

```http
POST /v1/affiliate/videos/list
```

```json
{
  "sort_by": "gmv",
  "sort_direction": "desc",
  "filters": {
    "handle": "example_creator",
    "min_gmv": 100,
    "min_view_count": 1000,
    "product_filter": "product_id_123",
    "time_from": "2025-02-01",
    "time_to": "2025-03-15"
  }
}
```

```json
{
  "path": "/v1/affiliate/videos/list",
  "data": {
    "videos": [
      {
        "shop_id": "your_shop_id_here",
        "video_id": "12345678",
        "handle": "example_creator",
        "gmv": 130931.64,
        "post_time": "02/26/2025",
        "view_count": 3417702,
        "units_sold": 3419,
        "ctr": 1.6,
        "like_count": 6382,
        "comment_count": 169,
        "title": "4 for 1 deal ends soon!",
        "campaign_id": null,
        "products": ["product_id_123"],
        "product": "product_id_123"
      }
    ],
    "has_more": false,
    "page_size": 20,
    "page_offset": 0
  }
}
```

## 5. LIVE Stream Search

```http
POST /v1/affiliate/lives/list
```

```json
{
  "sort_by": "gmv",
  "sort_direction": "desc",
  "page_size": 100,
  "page_offset": 0,
  "filters": {
    "handle": "example_creator",
    "min_gmv": 100,
    "min_view_count": 1000,
    "product_filter": "product_id_123",
    "time_from": "2025-02-01",
    "time_to": "2025-03-15"
  }
}
```

```json
{
  "path": "/v1/affiliate/lives/list",
  "data": {
    "videos": [
      {
        "shop_id": "your_shop_id_here",
        "campaign_id": null,
        "live_id": "7610921877288061726",
        "handle": "example_creator",
        "title": "Product Demo LIVE",
        "start_time": "02/25/2025",
        "duration": 14869,
        "units_sold": 22,
        "gmv": 701.2,
        "views": 87473,
        "likes": 1539,
        "comments": 133,
        "ctr": 0.05,
        "products": ["product_id_123", "product_id_456"],
        "products_stats": [
          {
            "product_id": "product_id_123",
            "gmv": 564.15,
            "units_sold": 19,
            "impressions": 13963
          },
          {
            "product_id": "product_id_456",
            "gmv": 137.05,
            "units_sold": 3,
            "impressions": 2567
          }
        ]
      }
    ],
    "page_size": 100,
    "page_offset": 0,
    "sort_by": "gmv",
    "sort_direction": "DESC",
    "has_more": false
  }
}
```

## 6. Sample Request Search

```http
POST /v1/affiliate/samples/list
```

```json
{
  "page_size": 50,
  "page_number": 1,
  "sort_by": "timestamp",
  "sort_direction": "desc",
  "filters": {
    "sample_status": ["To Review", "Ready to Ship"],
    "handle": "example_creator",
    "product_filter": "product_id_123",
    "time_from": "2025-09-09",
    "time_to": "2025-10-15"
  }
}
```

```json
{
  "path": "/v1/affiliate/samples/list",
  "data": {
    "results": [
      {
        "shop_id": "your_shop_id_here",
        "creator_oecuid": "7171717171717171717",
        "sampled_product": "product_id_123",
        "status": "To Review",
        "campaign_id": null,
        "timestamp": "2025-09-10T01:00:57.815932",
        "sample_received": null,
        "apply_id": "9191919191919191919",
        "handle": "example_creator",
        "follower_cnt": 4413,
        "post_rate": "N/A",
        "med_gmv_revenue": 0,
        "med_gmv_revenue_range": 1
      }
    ],
    "page": 1,
    "page_size": 50,
    "has_more": false
  }
}
```

## 7. Approve Sample Requests

```http
POST /v1/affiliate/samples/approve
```

```json
{ "apply_ids": ["9191919191919191919", "9191919191919191920"] }
```

```json
{
  "path": "/v1/affiliate/samples/approve",
  "data": {
    "message": "Successfully approved 2 sample requests",
    "success_count": 2
  }
}
```

## 8. Reject Sample Requests

```http
POST /v1/affiliate/samples/reject
```

Same shape as Approve.

## 9. Shop Stats

```http
POST /v1/shop/stats
```

```json
{
  "date_range": { "from": "2026-03-01", "to": "2026-04-01" },
  "include_charts": true,
  "stats": ["affiliate_gmv", "videos_posted", "emv"],
  "product_id": "1234567890",
  "cpm": 5
}
```

`product_id` and `cpm` are optional. `cpm` defaults to 5 and only affects `emv`.

### Available stat keys

| Key                        | Daily series? | Description                             |
| -------------------------- | ------------- | --------------------------------------- |
| `affiliate_gmv`            | ✅            | Affiliate GMV driven by brand           |
| `total_gmv`                | ✅            | Affiliate + ads + organic               |
| `affiliate_units_sold`     | ✅            |                                         |
| `total_units_sold`         | ✅            |                                         |
| `videos_posted`            | ✅            | Affiliate + brand                       |
| `affiliate_videos_posted`  | ✅            |                                         |
| `video_views`              | ✅            |                                         |
| `likes`                    | ✅            |                                         |
| `comments`                 | ✅            |                                         |
| `gpm`                      | ✅            | GMV per 1,000 views                     |
| `emv`                      | ✅            | Earned media value = (views/1000) × cpm |
| `commission`               | ✅            | Affiliate commission paid               |
| `distinct_creators`        | ✅            | Unique creators who posted              |
| `first_time_posters`       | ✅            | Affiliates with their first ever post   |
| `daily_active_affiliates`  | ✅            | Affiliates with non-zero GMV that day   |
| `dms_sent`                 | ✅            | DMs sent from Cruva                     |
| `replies`                  | ✅            | Creator replies received                |
| `tc_invites_sent`          | ✅            | Target Collaboration invites sent       |
| `sample_requests`          | ✅            |                                         |
| `samples_approved`         | ✅            |                                         |
| `samples_delivered`        | ✅            |                                         |
| `gmv_per_sample_delivered` | ✅            |                                         |
| `live_gmv`                 | ✅            |                                         |
| `lives_posted`             | ✅            |                                         |
| `avg_videos_per_creator`   | ❌            | Total only                              |
| `avg_gmv_per_video`        | ❌            | Total only                              |
| `sample_ratio`             | ❌            | sample_requests / tc_invites_sent       |
| `reply_ratio`              | ❌            | replies / dms_sent                      |

```json
{
  "path": "/v1/shop/stats",
  "data": [
    {
      "key": "affiliate_gmv",
      "title": "Affiliate GMV",
      "total_count": 188444.1,
      "daily_counts": [
        { "date": "2026-03-28", "count": 37140.0 },
        { "date": "2026-03-29", "count": 37791.58 }
      ],
      "percent_change": -8.1
    }
  ]
}
```

## 10. Shop Performance Score

```http
GET /v1/shop/sps
```

```json
{ "path": "/v1/shop/sps", "data": { "sps": 4.5 } }
```

Drops below 3.5 → outbound DMs are blocked by Cruva.

## 11. CRM Timeseries — affiliates ranked over a date range

```http
POST /v1/timeseries/affiliates
```

```json
{
  "page_size": 10,
  "page_number": 1,
  "search_params": {
    "date_range": { "from": "2026-04-01", "to": "2026-04-07" },
    "sort_by": "gmv",
    "sort_direction": "DESC",
    "handle": "example_creator"
  }
}
```

```json
{
  "path": "/v1/timeseries/affiliates",
  "data": [
    {
      "handle": "example_creator",
      "nickname": "Example Creator",
      "gmv": 4360.58,
      "commission": 186.88,
      "views": 554296,
      "likes": 4070,
      "comments": 50,
      "units_sold": 167,
      "video_count": 10,
      "engagement_rate": 0.74,
      "conversion_rate": 0.0301,
      "avg_gmv_per_view": 0.0079,
      "avg_order_value": 26.11
    }
  ]
}
```

## 12. Video Timeseries

```http
POST /v1/timeseries/videos
```

Same envelope as #11; per-video records with `video_id`, `title`, `post_time`, `product_id`, `gmv`, `commission`, `views`, `likes`, `comments`, `units_sold`, `engagement_rate`, `conversion_rate`, `avg_gmv_per_view`, `avg_order_value`.

## 13. Send DM (US / UK only)

```http
POST /v1/affiliate/message/dm
```

```json
{ "handle": "example_creator", "message": "Hello, collab with us!" }
```

```json
{
  "path": "/v1/affiliate/message/dm",
  "data": {
    "success": true,
    "data": { "message_id": "123456789" },
    "message": "Success"
  }
}
```

## 14. List Messages (last 20)

```http
POST /v1/affiliate/message/list
```

```json
{ "handle": "example_creator" }
```

```json
{
  "path": "/v1/affiliate/message/list",
  "data": {
    "success": true,
    "data": {
      "messages": [
        {
          "content": "",
          "type": "TARGET_COLLABORATION_CARD",
          "sender": "brand",
          "send_time": "Apr 08, 2026 10:20 PM UTC"
        },
        {
          "content": "Hi example_creator! Thanks for reaching out about a potential collaboration. Feel free to browse our products and request a sample. We'll review your request shortly!",
          "type": "TEXT",
          "sender": "brand",
          "send_time": "Feb 27, 2026 02:33 PM UTC"
        },
        {
          "content": "How can we work together",
          "type": "TEXT",
          "sender": "creator",
          "send_time": "Feb 27, 2026 02:33 PM UTC"
        }
      ],
      "has_more": true
    },
    "message": "success"
  }
}
```

---

# Enterprise endpoints (locked on Scale plan)

These are gated behind a custom-priced Enterprise plan. Useful when you need to find / vet creators **outside** your existing affiliate base.

## 15. Creator Data — full profile by handle ⭐ (the creator-intel endpoint)

```http
POST /v1/affiliate/marketplace/search
```

```json
{ "handle": "thysamus" }
```

> Handle must match exactly — Cruva disabled fuzzy matching here to prevent scraping.

```json
{
  "path": "/v1/affiliate/marketplace/search",
  "data": {
    "creator_id": "7171717171717171717",
    "category": [
      "Menswear & Underwear",
      "Phones & Electronics",
      "Beauty & Personal Care"
    ],
    "top_follower_ages": ["18-24", "25-34"],
    "handle": "thysamus",
    "nickname": "sam",
    "email": null,
    "follower_cnt": 16983,
    "is_fast_growing": false,
    "med_gmv_revenue_range": 1,
    "units_sold_range": 1,
    "top_follower_gender": "Female",
    "video_avg_view_cnt": 0,
    "video_engagement": 0,
    "spanish": false,
    "post_rate": 33.02,
    "gender": "male",
    "med_gmv_revenue": 0,
    "brand_collaborations": 0,
    "gmv_range": 0,
    "race": "none",
    "body_type": "average",
    "economic_status": "none",
    "age": "teen",
    "face_visibility": "frequently",
    "tone": "humorous",
    "embedding_attempts": 2,
    "bio": null,
    "language": "english",
    "live_gmv_30d": 0,
    "pps": null,
    "msg_name": "Sam"
  }
}
```

This is the richest single payload — Cruva infers `gender`, `race`, `body_type`, `economic_status`, `age` (band), `face_visibility`, `tone`, language, plus follower demographics and brand-collaboration count. Useful for persona matching but **note the inferred attributes are AI-derived** and should be sanity-checked before any production decision.

## 16. Brand Search

```http
POST /v1/intelligence/brands/search
```

```json
{
  "region": "us",
  "params": {
    "page": 1,
    "page_size": 10,
    "search": "Shark",
    "category": null,
    "sort": "gmv",
    "ts_start": "2026-03-07",
    "ts_end": "2026-04-06"
  }
}
```

```json
{
  "path": "/v1/intelligence/brands/search",
  "data": [
    {
      "brand_id": "7496047005540322107",
      "brand_name": "Shark",
      "creator_count": 4737,
      "top_category": "Household Appliances",
      "region": "us",
      "gmv": 3026883.79,
      "views": 149453235.52,
      "video_count": 12789,
      "shop_name": "Shark UK"
    }
  ]
}
```

## 17. Product Search

```http
POST /v1/intelligence/products/search
```

```json
{
  "region": "us",
  "params": {
    "page": 1,
    "page_size": 10,
    "search": "Whitening Strips",
    "category": null,
    "sort": "gmv",
    "ts_start": "2026-03-07",
    "ts_end": "2026-04-06"
  }
}
```

```json
{
  "path": "/v1/intelligence/products/search",
  "data": [
    {
      "product_id": "1729635919293618333",
      "product_name": "DRDENT Purple Teeth Whitening Strips",
      "price_value": 13.71,
      "creator_count": 3597,
      "shop_name": "DR.DENT - shop",
      "gmv": 400820.59,
      "units_sold": 29237,
      "views": 54625344,
      "video_count": 2704,
      "brand_id": "7495899075622504605"
    }
  ]
}
```

## 18. Brand's Creators — who's driving GMV for any brand

```http
POST /v1/intelligence/brands/creators/list
```

```json
{
  "region": "us",
  "params": {
    "brand_id": "7495899075622504605",
    "page": 1,
    "page_size": 10,
    "sort": "gmv",
    "ts_start": "2026-03-07",
    "ts_end": "2026-04-06"
  }
}
```

Returns a list of creators with `handle`, `nickname`, `bio`, `follower_cnt`, `category[]`, `top_follower_ages[]`, `top_follower_gender`, `video_avg_view_cnt`, `video_engagement`, `brand_collaborations`, `med_gmv_revenue` (last-30d platform-wide GMV), `category_splits` (% per category), `follower_gender_breakdown` (key/value), `follower_age_breakdown`, `regional_geography`, `email`, `gender`, `age`, `language`, `shop_gmv`, `video_count`, `creator_id`, plus `has_more` for pagination.

## 19. Product's Creators — same shape, scoped to one product

```http
POST /v1/intelligence/products/creators/list
```

Same as #18 but takes `product_id` instead of `brand_id`, and the result has `product_gmv` instead of `shop_gmv`.

## 20. Creator's Brands — reverse lookup

```http
POST /v1/intelligence/creators/brands/list
```

```json
{
  "region": "us",
  "params": {
    "creator_id": "7493993245181314497",
    "page": 1,
    "page_size": 10,
    "sort": "gmv",
    "ts_start": "2026-03-07",
    "ts_end": "2026-04-06"
  }
}
```

```json
{
  "path": "/v1/intelligence/creators/brands/list",
  "data": {
    "creator_oecuid": "7493993245181314497",
    "region": "us",
    "ts_start": "2026-03-07",
    "ts_end": "2026-04-06",
    "page": 1,
    "page_size": 10,
    "has_more": true,
    "results": [
      {
        "gmv": 24595.22,
        "views": 1600249.31,
        "videos": 4,
        "brand_name": "Color Wow UK",
        "brand_id": "7494530868351044030"
      },
      {
        "gmv": 20236.33,
        "views": 1347692.71,
        "videos": 2,
        "brand_name": "DR.DENT - shop",
        "brand_id": "7495899075622504605"
      }
    ]
  }
}
```

## 21. Creator's Products

```http
POST /v1/intelligence/creators/products/list
```

Same shape as #20 but returns `product_id`, `product_name`, `price_value`, `brand_id`.

---

# Quick recipes

### Pull every affiliate who's posted for Root Labs in the last 7 days

```python
import requests, os
HEADERS = {
    "Content-Type": "application/json",
    "x-api-key":   os.environ["CRUVA_API_KEY"],
    "x-shop-id":   "68b5a03bba91e6252be52373",
}
r = requests.post(
    "https://api.cruva.com/v1/timeseries/affiliates",
    headers=HEADERS,
    json={
        "page_size": 100, "page_number": 1,
        "search_params": {
            "date_range": {"from": "2026-04-22", "to": "2026-04-28"},
            "sort_by": "gmv",
            "sort_direction": "DESC"
        }
    },
).json()
for a in r["data"]:
    print(a["handle"], a["gmv"], a["video_count"])
```

### Find a single creator by handle (Enterprise only)

```python
requests.post(
    "https://api.cruva.com/v1/affiliate/marketplace/search",
    headers=HEADERS,
    json={"handle": "thysamus"}
).json()
```

### Daily Affiliate GMV chart for a date range

```python
requests.post(
    "https://api.cruva.com/v1/shop/stats",
    headers=HEADERS,
    json={
        "date_range": {"from": "2026-04-01", "to": "2026-04-28"},
        "include_charts": True,
        "stats": ["affiliate_gmv", "videos_posted", "first_time_posters"]
    }
).json()
```

---

# Scope warning — what the Standard tier can vs cannot answer

| Question                                                          | Standard tier                                                                         | Enterprise tier                                                               |
| ----------------------------------------------------------------- | ------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| "How are MY current affiliates doing?"                            | ✅ `/v1/affiliate/crm/list`, `/v1/timeseries/affiliates`, `/v1/affiliate/videos/list` | ✅                                                                            |
| "What's the full demographic profile of `@some_random_handle`?"   | ❌                                                                                    | ✅ `/v1/affiliate/marketplace/search`                                         |
| "Which creators are driving the most GMV for competitor brand X?" | ❌                                                                                    | ✅ `/v1/intelligence/brands/search` → `/v1/intelligence/brands/creators/list` |
| "Which other brands does my best affiliate already work with?"    | ❌                                                                                    | ✅ `/v1/intelligence/creators/brands/list`                                    |
| "Send a DM"                                                       | ✅ (US/UK only)                                                                       | ✅                                                                            |
| "Approve a sample"                                                | ✅                                                                                    | ✅                                                                            |

For the creator-discovery use case (finding new creators by handle, persona, or competitor brand), the Enterprise endpoints are the only ones that work — Cruva calls these the "Enterprise API" and gates them behind a custom-priced plan.

---

# Appendix: Third-Party Research (Vidura, 2026-05-13)

> Everything below is sourced from public internet research -- blog reviews, comparison articles, press releases, YouTube, LinkedIn, and news coverage. It complements the API spec above with company background, market positioning, competitive context, community sentiment, and gaps the API spec cannot answer.

## Company background

- **Product URL:** https://cruva.com (confirmed operational; the initial `.ai` / `.io` / `hq.com` / `getcruva.com` domains do not resolve to the product)
- **Previous name:** UpTk. Rebranded to Cruva on **October 23, 2025** [B2, T3] [B3, T4]
- **Founders:**
  - **Sebastian Nelson** -- CEO and co-founder. Based in Santa Barbara, CA. Started in e-commerce (Amazon) in 2018, pivoted to TikTok Shop at launch. Built Cruva to solve the manual pain of managing hundreds of affiliate creators [B1, T3] [B7, T3].
  - **Samuel Strong** -- CTO and co-founder. UCLA CS graduate. Background in large-scale systems design, data automation, AI infrastructure. Previously worked on ML initiatives with NASA JPL [B4, T4].
  - **Bryan Rangel** -- Head of Partnerships [B4, T4].
- **Headquarters:** Los Angeles, California (some sources say Santa Barbara for the CEO specifically) [B7, T3]
- **Founded:** UpTk launch date not precisely published; the TikTok Shop US launch was September 2023, and UpTk was described as being built "when TikTok Shop launched" [B7, T3]. Rebrand to Cruva in October 2025.
- **Scale claims:** 400+ brands served, partners collectively generating $10M/month on TikTok Shop, $47M cumulative GMV managed, 233% YoY growth [B2, T3] [B7, T3].
- **Official TikTok Shop Partner** -- automation tools reviewed and endorsed by TikTok [B2, T3].
- **Funding:** Not publicly disclosed [B7, T3].
- **LinkedIn:** linkedin.com/company/cruva [B4, T4]

## What this platform is (third-party perspective)

**One-liner:** AI-powered TikTok Shop affiliate management platform -- creator discovery, automated outreach (email + DM), sample tracking, CRM, community building, competitor intelligence, and GMV attribution.

**What KIND of data lives here (vs Kalodata vs Apify):**

Cruva is the **CRM and outreach engine** for your TikTok Shop affiliate program. It answers:

- "Which creators should I recruit?" -- AI-powered discovery across 3M+ verified TikTok Shop affiliates
- "How do I reach them at scale?" -- Automated outreach via TikTok DM + email, 3,000+ messages/day
- "Where are my samples?" -- Full sample lifecycle tracking (request > approval > shipment > creator post)
- "Which affiliates are actually driving GMV?" -- Performance attribution per creator, per video, per product
- "What are my competitors doing?" -- Competitor brand/creator/product intelligence (Enterprise tier)

**Distinctly vs Kalodata:** Kalodata shows you the whole TikTok Shop market (any product, any creator, any shop). Cruva manages YOUR creator relationships. Kalodata is reconnaissance; Cruva is operations.

**Distinctly vs Apify:** Apify scrapes raw public data. Cruva has CRM-layer data: outreach history, sample status, DM threads, GMV per creator for YOUR shop. Apify doesn't know your affiliates; Cruva does.

## Feature summary from third-party sources

### Core features (confirmed across multiple sources)

1. **AI Creator Search / Magic Search** [B5, T3] [B6, T4]
   - Natural language queries: "Show me Latinx women who review skincare products with over 1k followers", "Show me affiliates with over 10k GMV who post cooking content"
   - Filters: follower count, GMV, engagement rate, average views, posting frequency, brand collaboration history
   - Also filters by physical/demographic attributes: race, gender, age range, language, body type, economic status, facial features (beard, etc.) -- AI-inferred [B5, T3]
   - Database: 3M+ verified TikTok Shop affiliates [B6, T4]
   - Competitor overlap: find creators already selling for competitors [B8, T4]

2. **Automated Outreach Bot** [B2, T3] [B6, T4]
   - Dual-channel: TikTok DM + email
   - 3,000+ messages per day capacity
   - AI-powered personalization using creator and brand context
   - Automated follow-ups based on triggers (sample shipped, no response after X days, etc.)
   - AI-powered auto-replies
   - Claims: 12% creator response rate vs 2% industry average [B2, T3]

3. **Sample Tracking** [B2, T3] [B9, T4]
   - Full lifecycle: request > approval > shipment > delivery > first post
   - Automated sample approvals with quality filters
   - Claims: 65% sample-to-sale conversion vs 40% with manual processes [B2, T3]

4. **Affiliate CRM** [API spec above is authoritative]
   - Creator pipeline management
   - Tags, stages, notes
   - Messaging history
   - GMV/video/live attribution per creator
   - CRM automations triggered by conditions (sample shipped, GMV milestone, video posted)

5. **Creator Community / Gamification** [B2, T3]
   - Private creator communities
   - Contests and rewards
   - Re-activation campaigns for top performers
   - Claims: 76% GMV increase for brands using gamification, 133% increase in creator posting frequency [B2, T3]

6. **Social Intelligence / Competitor Spy** [B8, T4]
   - Track competitors' top affiliates, trending content, best-performing products
   - Build outreach lists based on competitors' creator earnings
   - Segment by brand, product, or creator level
   - Export competitor data
   - (Enterprise tier only via API endpoints #16-#21; likely available in UI for all tiers in some form)

7. **Performance Tracking** [B9, T4]
   - GMV attribution per creator, video, product, campaign
   - Real-time dashboards
   - 28+ stat keys available via API (see API spec above)

### Multi-platform expansion (announced, status unclear) [B2, T3]

- Instagram Shopping
- YouTube Shopping
- Amazon Influencer programs
- Announced at rebrand (Oct 2025). No third-party confirmation of live multi-platform features as of 2026-05.

## Pricing (third-party perspective)

**Cruva does not publicly list pricing.** Key signals:

- The API spec header confirms Rootlabs is on the **Scale plan at $599/month**.
- Cruva's pricing page (cruva.com/pricing) directs users to "book a demo" -- no self-serve pricing visible [B6, T4].
- "Most customers start on an annual plan after a paid pilot" [B6, T4].
- "White-glove onboarding -- your CSM helps configure outreach, import lists, and run your first cohort" [B6, T4].
- Competitive context: Grin starts at ~$2,500/month, Aspire at ~$2,300/month [B10, T3]. Cruva's pricing is significantly below these enterprise platforms.
- One comparison article notes "many sellers, agencies and brands pay $199 or more per month for tools that cover only one part of the workflow" -- implying Cruva is in or above this range [B6, T4].

_Synthesis:_ Cruva appears to have tiered plans (the API spec mentions Basic / Growth / Scale / Enterprise). The Scale plan at $599/month is confirmed for Rootlabs. Entry-level pricing is not publicly known but likely starts lower.

## Competitive positioning

### vs Grin ($2,500+/month) [B10, T3]

- Grin is end-to-end creator management for e-commerce (deep Shopify/WooCommerce integrations, product seeding, affiliate tracking)
- Grin's discovery is opt-in creators only; Cruva searches all 3M+ TikTok Shop affiliates
- Grin is 4-5x more expensive
- Grin is platform-agnostic; Cruva is TikTok Shop-native
- Choose Grin for multi-platform e-commerce with deep fulfillment integration; choose Cruva for TikTok Shop-specific affiliate scaling

### vs Aspire ($2,300+/month) [B10, T3]

- Aspire excels at inbound talent sourcing (1.2M+ vetted creators, branded application pages)
- Aspire has first-party data integrations (Meta, TikTok, Pinterest)
- Aspire is 3-4x more expensive
- Choose Aspire for UGC-to-paid-ad workflows; choose Cruva for TikTok Shop affiliate outreach automation

### vs Colaba ($59+/month) [B11, T3]

- Colaba positions as "all-in-one" (outreach + tracking + performance in one platform)
- Cruva is described as "primarily outreach-focused" and "lacks full system integration for analytics and workflow management" [B11, T3]
- Cruva users "require additional tools" for a complete workflow
- _Note:_ This critique comes from a Colaba-authored comparison article [B11, T3] -- treat with bias awareness. The API spec above shows Cruva has substantial analytics capabilities (28+ stat keys, video/live/timeseries endpoints), which contradicts the "outreach-only" framing.

### vs Kalodata

- Different tool categories entirely. Kalodata = market intelligence. Cruva = affiliate CRM.
- Complementary, not competitive. Use Kalodata to identify trending products and top creators in a category. Use Cruva to recruit and manage those creators for your brand.
- The Enterprise tier endpoints (#15-#21) give Cruva some of the same competitive intelligence capabilities as Kalodata (brand search, product search, creator lookup by handle). If Rootlabs upgrades to Enterprise, some Kalodata lookups could be done in Cruva instead.

## Case studies (vendor-authored but with specific numbers) [B9, T4 -- vendor]

| Brand           | Before Cruva       | After Cruva             | Key metrics                                                     |
| --------------- | ------------------ | ----------------------- | --------------------------------------------------------------- |
| **SEEQ Supply** | $138,780 GMV       | $693,950 GMV            | 89% from affiliate sales, 3,313 videos, 7,170 samples processed |
| **Hiccaway**    | New to TikTok Shop | $71,448 GMV in 4 months | 82% from affiliate sales, 2,219 videos, 5,419 samples           |

_Note:_ These are vendor-published case studies [B9, T4 -- vendor]. Specific numbers are plausible given the platform's scale claims but are not independently verified.

## Community sentiment

### Positive signals

- Official TikTok Shop Partner status adds credibility [B2, T3]
- 400+ brands served claim [B7, T3]
- Specific performance metrics (12% response rate, 65% sample-to-sale) are cited across multiple press releases [B2, T3]
- YouTube reviews exist (e.g., "Cruva Full Demo" walkthrough, Sebastian Nelson interview) [B12, T4]

### Negative signals / gaps

- **No G2 or Capterra reviews found.** The platform is too new (rebranded Oct 2025) to have accumulated review-site presence.
- **No Reddit threads found** discussing Cruva or UpTk specifically.
- **One cautionary YouTube review** titled "Cruva Review - Is This TIKTOK SHOP AFFILIATE Platform Only Relevant To Me? See? (Do not Use Yet)" [B12, T4] -- suggests at least one reviewer had reservations, though the video content was not accessible for analysis.
- **"Lacks full system integration"** per Colaba comparison [B11, T3] -- but this is a competitor's characterization and may be outdated given the API spec shows substantial analytics.
- **No public API documentation** -- the API spec in this file was captured from a live session, not from public docs. Third-party developers cannot evaluate the API without an account.

### Dissent

The main disagreement in the evidence is whether Cruva is "outreach-only" (Colaba's framing [B11, T3]) or a comprehensive affiliate management platform (Cruva's own positioning and the API spec). The API spec above settles this: Cruva has outreach, CRM, analytics, sample management, messaging, and competitive intelligence. But the Enterprise endpoints (creator profiles, brand/product search) are gated, so on the Standard/Scale plan, the analytics are limited to YOUR OWN affiliates.

## Integration and API access (third-party perspective)

- **API:** RESTful, JSON, documented in the spec above. Base URL `https://api.cruva.com`. Headers: `x-api-key` + `x-shop-id`.
- **MCP server:** `https://mcp.cruva.com/sse?api_key=<KEY>` -- confirmed in the API spec. This is the integration path for Hanuman.
- **TikTok DM integration:** US/UK only (endpoint #13). DMs are sent through Cruva's official TikTok Shop Partner integration.
- **No Apify Actor wraps Cruva.** No third-party scraper or automation exists.
- **PromoteKit:** `affiliate.cruva.com` hosts a PromoteKit affiliate program page -- this is Cruva's own referral program, not a product feature [B4, T4].
- **Fulfillment integrations:** "Specific fulfillment integrations and limitations are covered during onboarding" [B6, T4] -- not publicly documented.
- **No public webhook documentation found.**

## Appendix sources

```
[B1]  "Sebastian Nelson" -- Coruzant profile, undated -- [T3]
      https://coruzant.com/profiles/sebastian-nelson/
      Why: Founder background, company origin story, Santa Barbara location, 400+ brands claim.

[B2]  "TikTok Shop Automation Leader UPTK Rebrands to CRUVA" -- OpenPR press release, 2025-10-23 -- [T3]
      https://www.openpr.com/news/4236851/tiktok-shop-automation-leader-uptk-rebrands-to-cruva-expands
      Why: Official rebrand announcement with metrics ($47M GMV, 233% YoY, performance claims).
      Also syndicated: markets.financialcontent.com, index.businessinsurance.com, kotaradio.com

[B3]  "From TikTok-Shop Specialist to Social Commerce Powerhouse" -- US Business News, 2025-11-03 -- [T3]
      https://usbusinessnews.com/from-tiktok-shop-specialist-to-social-commerce-powerhouse-uptk-is-now-cruva/
      Why: Rebrand coverage with feature overview, multi-platform expansion announcement.

[B4]  LinkedIn profiles (Sebastian Nelson, Samuel Strong, Bryan Rangel, Cruva company page) -- [T4]
      Why: Confirms team, roles, location, CTO background (UCLA CS, NASA JPL).

[B5]  "AI Creator Search in Cruva: Revolutionizing How Brands Find TikTok Shop Affiliates" -- US Insider, undated -- [T3]
      https://usinsider.com/ai-creator-search-in-cruva-revolutionizing-how-brands-find-tiktok-shop-affiliates/
      Why: Detailed AI search feature description including demographic/physical attribute filters.
      Note: Likely vendor-influenced content but provides specific feature details.

[B6]  "Cruva: TikTok Shop Affiliate Outreach Tool" -- AI Just Better, undated -- [T4]
      https://aijustbetter.com/item/cruva-tiktok-shop-affiliate-outreach-tool
      Why: Feature summary, target users, "saves 20+ hours weekly" claim. No pricing disclosed.

[B7]  "Sebastian Nelson: CEO of Cruva (formerly UpTK)" -- YouTube interview (#17), undated -- [T4]
      https://www.youtube.com/watch?v=3iGXySzAnH0
      Why: CEO interview with company background. (Audio/video not analyzed; metadata only.)

[B8]  "Cruva Social Intelligence: How to Spy on Competitors" -- YouTube, undated -- [T4]
      https://www.youtube.com/watch?v=Ab3iHFuGvKQ
      Why: Competitor spy feature walkthrough. (Audio/video not analyzed; metadata only.)

[B9]  Cruva case studies page -- [T4 -- vendor]
      https://cruva.com/case-studies
      Why: SEEQ Supply ($693,950 GMV) and Hiccaway ($71,448 GMV) case studies with specific numbers.

[B10] "Best Influencer Marketing Tool 2026: TikTok Software Comparison" -- Colaba Blog, 2026 -- [T3]
      https://www.colaba.us/blogs/best-influencer-marketing-tool-2026-tiktok-software-comparison
      Why: Comparison of Cruva vs Colaba vs Euka. Notes Cruva as "outreach-focused."
      Note: Published by a competitor (Colaba) -- treat positioning claims with bias awareness.

[B11] Colaba comparison (same as B10) -- [T3, competitor-authored]
      Why: The "lacks full system integration" critique originates here.

[B12] YouTube reviews of Cruva -- [T4]
      "Cruva Review- Is This TIKTOK SHOP AFFILIATE Platform Only Relevant To Me?" -- https://www.youtube.com/watch?v=Yzz1xeswiDo
      "Cruva Full Demo: How to Scale TikTok Shop Sales with Affiliate Automation" -- https://www.youtube.com/watch?v=nZkQu7hqbsw
      "How to manage affiliate relationships in Cruva" -- https://www.youtube.com/watch?v=e2dcl6a16WE
      Why: Video walkthroughs exist but were not audio-analyzed in this research pass.

[B13] "Cruva" -- SaaS Browser listing -- [T4]
      https://saasbrowser.com/en/saas/1137449/cruva
      Why: Feature listing (returned 403 at fetch time).
```

## What the third-party research adds that the API spec doesn't cover

1. **Company background:** Founded by Sebastian Nelson (CEO, Santa Barbara) and Samuel Strong (CTO, UCLA CS / NASA JPL). Previously UpTk, rebranded Oct 2025.
2. **Scale context:** 400+ brands, $10M/month collective partner sales, $47M cumulative GMV, 233% YoY growth. Vendor claims, not independently verified.
3. **Competitive positioning:** Significantly cheaper than Grin ($2,500+) and Aspire ($2,300+). Competes with Colaba ($59+) on features. TikTok Shop-native vs platform-agnostic competitors.
4. **AI search capabilities:** Natural language queries with demographic/physical attribute filters not visible in the API spec (these may be UI-only features or may map to the Enterprise endpoint #15).
5. **Case study results:** SEEQ Supply and Hiccaway numbers provide reference points for what Cruva-powered programs can achieve.
6. **Multi-platform roadmap:** Instagram Shopping, YouTube Shopping, Amazon Influencer announced but not confirmed live.
7. **Community gap:** No G2/Capterra reviews, no Reddit threads. Platform is too new for independent review aggregation.

## Remaining gaps (manual walkthrough or Kartavya escalation needed)

1. **Cruva plan tiers and pricing.** The API spec confirms Basic / Growth / Scale / Enterprise exist. Rootlabs is on Scale ($599/mo). But no third-party source lists all plans with prices. A sales conversation or pricing page walkthrough would close this.
2. **Enterprise plan pricing.** Custom-priced. What would it cost Rootlabs to unlock endpoints #15-#21? This is a business decision with significant intelligence value.
3. **UI feature coverage vs API.** The API spec covers 21 endpoints. The UI likely has additional features (AI Magic Search, community tools, gamification, social intelligence dashboard) not exposed via API. A UI walkthrough would map these.
4. **Multi-platform status.** Instagram/YouTube/Amazon Shopping integrations were announced Oct 2025. Are they live? Which features work cross-platform? No third-party confirmation.
5. **YouTube video content.** Three+ YouTube walkthroughs exist [B12, T4] but their audio/video content was not analyzed. A watch-through would yield UI screenshots and workflow details.
6. **Fulfillment integrations.** "Covered during onboarding" -- which shipping/logistics platforms does Cruva integrate with for sample fulfillment?
7. **Webhook/event system.** Does Cruva support webhooks for real-time event notifications (new sample request, creator posted video, etc.)? Not in the API spec, not in third-party sources.
8. **Colaba's "outreach-only" critique.** Is this still accurate post-rebrand? The API spec suggests no, but the UI-side analytics capabilities should be confirmed with a walkthrough.
