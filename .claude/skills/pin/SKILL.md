---
name: pin
description: Pin a Walmart product to a grocery list name so the cart filler always picks that exact item. Use when the user gives a walmart.com/ip link (or item ID) and wants it pinned, or says "pin this", "always buy this for X".
argument-hint: <walmart-url-or-id> [list name] [aliases...]
---

# /pin

Add a Walmart item to `pins.json` so the cart filler skips search for that list name.

Input: `$ARGUMENTS` = a walmart.com `/ip/...` URL or bare numeric ID, optionally followed by the list name and aliases.

## Steps

1. Parse the arguments. The first token is the URL or ID. Anything after it is the list name, and comma-separated extras are aliases. If the list name is missing, derive it from the URL slug: the plain grocery word a person would say to Siri ("milk", "egg", "peanut butter"), not the brand or size.
2. Derive aliases from the slug when the user gave none. Include the natural variants someone might say: for `Great-Value-Milk-2-Reduced-Fat-Half-Gallon-64-fl-oz-Jug` use `2% milk`, `2 percent milk`, `reduced fat milk`, `half gallon milk`. Do not include the brand name as an alias unless the user asked for it (the brand is the pick, not the list word).
3. Run, from the project root, without `cd`:
   ```bash
   python3 scripts/pins.py add "<url-or-id>" --key "<list name>" --alias "<alias1>" --alias "<alias2>" ...
   ```
   The script normalizes key and aliases (lowercase, punctuation stripped, quantity words dropped, last word singularized) and stores them. It refuses an alias that already belongs to another pin.
4. Confirm with one `lookup` per alias plus the key to prove each resolves:
   ```bash
   python3 scripts/pins.py lookup "<alias>"
   ```
5. Reply with the stored entry (key, id, aliases) in one short block. If the derived key or an alias looks ambiguous (e.g. "chicken" for breasts vs thighs), say so in one line and pick the narrower word.

## Notes

- Lookup is exact-match after normalization. "Eggs", "egg", "2 dozen eggs" all hit the key `egg`. "egg whites" does not.
- Keys that already exist are overwritten by `add`. Mention it if the key existed.
- The cart filler checks `scripts/pins.py lookup "<item>"` before searching.
