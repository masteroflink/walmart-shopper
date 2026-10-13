---
name: cart-fill
description: Fill the walmart.com cart from the Apple Reminders "Grocery" list. Use when the user says "fill the cart", "run the shopper", or the daily scheduled task fires.
---

# /cart-fill

Project root: `/Users/bruce/Documents/projects/walmart_buyer`. Never use `cd`; use absolute paths. Use Claude in Chrome (`mcp__claude-in-chrome__*`, the user's logged-in Chrome), NOT the built-in browser. Load the Chrome tools with one ToolSearch call:

```
select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__computer,mcp__claude-in-chrome__find,mcp__claude-in-chrome__get_page_text,mcp__claude-in-chrome__browser_batch,mcp__claude-in-chrome__javascript_tool,mcp__claude-in-chrome__tabs_close_mcp
```

Also load `PushNotification` via ToolSearch.

## 1. Read inputs

- Items: run `/Users/bruce/Documents/projects/walmart_buyer/scripts/get_list.sh` (one open Reminders "Grocery" item per line). If empty, write a short run log saying "list empty, nothing done" and stop. Do not ping.
- Rules: read `/Users/bruce/Documents/projects/walmart_buyer/rules.md` and follow it exactly (Delivery from local store only, cheapest unit price, single pack, size cap, qty 1, plain meaning, skip-and-report when unclear).
- Pins: for each item run `python3 /Users/bruce/Documents/projects/walmart_buyer/scripts/pins.py lookup "<item>"`. Exit 0 means pinned: use the `url` field and skip search. Exit 1 means unpinned: search.

## 2. Record cart before

Open a Chrome tab on `https://www.walmart.com/search?q=bread` (any page) and use `find` for "cart button in header showing item count and total". Record items and $ total.

## 3. For each item

**Pinned:** navigate to the pin's `url`, wait 3s, confirm the page shows "Delivery" available (not shipping-only, not out of stock). If out of stock or shipping-only, skip and report; do not substitute. Click "Add to cart" by coordinate (take a screenshot first).

**Unpinned:** navigate to `https://www.walmart.com/search?q=<item>`, wait 3s, `get_page_text`. Every card exposes name, price, unit price, and a fulfillment line ("Delivery as soon as ..." vs "Free shipping, arrives ..." / "Separate delivery"). Rank per rules.md and pick. Then:

1. `find` the product TITLE LINK for the pick (not the Add button; Add-button refs scroll to the wrong row).
2. `scroll_to` that link ref, wait 1s, screenshot.
3. Click the Add button for that card BY COORDINATE from the screenshot. Ref-clicks on Add silently fail.
4. Wait 3s. Verify: the header cart count went up by 1 and the card now shows a quantity stepper reading 1. If not verified, retry the coordinate click once. If still not verified, report as failed, do not mark complete.
5. Get the item ID with `javascript_tool`. Return ONLY the trailing numeric ID, never a full href (hrefs with query strings get blocked):
   ```js
   [...document.querySelectorAll('a[href*="/ip/"]')].map(a=>a.getAttribute('href').split('?')[0]).find(h=>/<loose slug fragment>/i.test(h))?.split('/').pop()
   ```
6. On verified add only: run `/Users/bruce/Documents/projects/walmart_buyer/scripts/complete_item.sh "<exact item text from get_list.sh>"`.

## 4. Record cart after

Re-read the header cart button. Record items and $ total.

## 5. Log

Write `/Users/bruce/Documents/projects/walmart_buyer/runs/<YYYY-MM-DD>-daily.md` (append a numbered suffix if it exists). Run logs are local-only and gitignored. Format:

- Title line with date and "daily".
- "Cart before: N items / $X. After: N items / $Y."
- `## Picks` table with columns: Item | Pinned? | Picked | ID | Unit price | Runner-up / skipped
- `## Reminders`: which items were marked completed.
- `## What broke`: anything that failed or needed a retry, or "Nothing failed."
- `## Cart total`: final $ and whether the $45 threshold was exceeded.

Do not write the store address into the log.

## 6. Ping rule

If the cart total after the run is OVER $45.00, call `PushNotification` (status "proactive") with one line: `Walmart cart $<total>, <n> items. Added: <comma list>. Skipped: <comma list or none>.` If the total is $45.00 or under, send no notification at all.

## 7. Cleanup

Close the Chrome tab you opened. Never check out, never change delivery address or store, never add anything not on the list, never add quantity > 1 unless the list item says so.
