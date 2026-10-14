"""麦门健身餐 CLI: python -m mcd_fitness --goal 减脂 --city 上海 --keyword 人民广场"""
import argparse, json, os, sys, time
from concurrent.futures import ThreadPoolExecutor

from .data import parse_nutrition, nutrition_index, match, is_combo
from .optimizer import Goal, PRESETS, optimize

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), "data")
NUT_CACHE = os.path.join(DATA, "nutrition.json")
MENU_CACHE = os.path.join(DATA, "menu_snapshot.json")


def build_menu(client, store_code, nut):
    """Join query-meals prices with list-nutrition-foods macros. Generic items resolved via query-meal-detail."""
    idx = nutrition_index(nut)
    meals = client.call("query-meals", {"storeCode": store_code, "orderType": 1, "beType": 1})["data"]["meals"]
    out, unresolved = [], []
    for code, m in meals.items():
        n = match(m["name"], idx)
        if n:
            out.append(dict(n, code=code, menuName=m["name"], price=float(m["currentPrice"])))
        elif not is_combo(m["name"]) and "套餐" not in m["name"]:
            unresolved.append((code, m))

    def detail(cm):
        code, m = cm
        try:
            d = client.call("query-meal-detail", {"storeCode": store_code, "orderType": 1, "beType": 1, "code": code})
            name = d["data"]["name"]
        except Exception:
            return None
        n = match(name, idx)
        return dict(n, code=code, menuName=f"{m['name']}（默认:{name}）", price=float(m["currentPrice"])) if n else None

    with ThreadPoolExecutor(6) as ex:
        out += [r for r in ex.map(detail, unresolved) if r]
    seen, uniq = set(), []
    for it in out:
        if it["code"] not in seen:
            seen.add(it["code"]); uniq.append(it)
    return uniq


def fmt_plan(i, p, priced=True):
    t = p["total"]
    lines = [f"方案 {i}" + (f"  ¥{t['price']:.1f}" if priced else "")]
    for it in p["items"]:
        q = f" ×{it['quantity']}" if it["quantity"] > 1 else ""
        pr = f"¥{it['price']:.1f}  " if priced else ""
        lines.append(f"  - {it.get('menuName', it['name'])}{q}  {pr}{it['energyKcal']:.0f}kcal  蛋白{it['protein']:.0f}g")
    lines.append(f"  合计: {t['energyKcal']:.0f} kcal | 蛋白质 {t['protein']:.0f}g | 脂肪 {t['fat']:.0f}g | 碳水 {t['carbohydrate']:.0f}g | 钠 {t['sodium']:.0f}mg")
    kc = max(t["energyKcal"], 1)
    lines.append(f"  供能比: 蛋白 {t['protein']*4/kc*100:.0f}% · 脂肪 {t['fat']*9/kc*100:.0f}% · 碳水 {t['carbohydrate']*4/kc*100:.0f}%")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="mcd-fitness-meal", description="麦门健身餐：按热量/蛋白质目标找最便宜的麦当劳组合")
    ap.add_argument("--goal", choices=list(PRESETS), help="预设目标")
    ap.add_argument("--max-kcal", type=float); ap.add_argument("--min-kcal", type=float)
    ap.add_argument("--min-protein", type=float); ap.add_argument("--max-fat", type=float)
    ap.add_argument("--max-carb", type=float); ap.add_argument("--max-sodium", type=float)
    ap.add_argument("--budget", type=float, help="预算上限（元）")
    ap.add_argument("--max-items", type=int, default=4)
    ap.add_argument("--exclude", default="", help="排除关键词，逗号分隔，如 鱼,咖啡")
    ap.add_argument("--city"); ap.add_argument("--keyword", help="门店位置关键词")
    ap.add_argument("--store", help="门店编码 storeCode")
    ap.add_argument("--offline", action="store_true", help="只用本地缓存数据")
    ap.add_argument("--verify", action="store_true", help="用 calculate-price 校验最优方案实时价格")
    ap.add_argument("--save-snapshot", action="store_true")
    ap.add_argument("--top", type=int, default=3); ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    g = Goal(max_items=a.max_items, exclude=[x for x in a.exclude.split(",") if x])
    for k, v in PRESETS.get(a.goal, {}).items():
        setattr(g, k, v)
    for k in ("max_kcal", "min_kcal", "min_protein", "max_fat", "max_carb", "max_sodium", "budget"):
        if getattr(a, k) is not None:
            setattr(g, k, getattr(a, k))

    online = not a.offline and (a.store or a.city)
    client, store = None, None
    if online:
        from .mcp_client import MCPClient
        client = MCPClient(); client.initialize()
        nut = parse_nutrition(client.call("list-nutrition-foods"))
        if a.store:
            store = {"storeCode": a.store, "storeName": a.store}
        else:
            st = client.call("query-nearby-stores", {"beType": 1, "searchType": 2, "city": a.city, "keyword": a.keyword or a.city})
            stores = [s for s in st.get("data") or [] if s.get("businessStatus", True)]
            if not stores:
                sys.exit("没有找到营业中的门店，换个关键词试试")
            store = stores[0]
        items = build_menu(client, store["storeCode"], nut)
        if a.save_snapshot:
            json.dump(nut, open(NUT_CACHE, "w"), ensure_ascii=False, indent=1)
            json.dump({"store": {k: store.get(k) for k in ("storeCode", "storeName", "address")},
                       "fetchedAt": time.strftime("%Y-%m-%d %H:%M"), "items": items},
                      open(MENU_CACHE, "w"), ensure_ascii=False, indent=1)
        priced = True
    elif os.path.exists(MENU_CACHE):
        snap = json.load(open(MENU_CACHE)); items, store, priced = snap["items"], dict(snap["store"], fetchedAt=snap["fetchedAt"]), True
    else:
        items, priced = json.load(open(NUT_CACHE)), False
        for i in items:
            i["price"] = 0.0

    plans = optimize(items, g, top=a.top, objective="price" if priced else "protein")
    verify = None
    if a.verify and client and plans:
        r = client.call("calculate-price", {"storeCode": store["storeCode"], "orderType": 1, "beType": 1,
                                             "items": [{"productCode": it["code"], "quantity": it["quantity"]} for it in plans[0]["items"]]})
        d = r.get("data") or {}
        verify = {"price": d.get("price", 0) / 100, "originalPrice": d.get("originalPrice", 0) / 100}

    if a.json:
        print(json.dumps({"goal": g.__dict__, "store": store, "plans": plans, "verify": verify}, ensure_ascii=False, indent=1))
        return 0
    src = "实时 MCP" if online else ("本地快照 " + store.get("fetchedAt", "") if priced else "离线营养库（无价格，按蛋白质最高排序）")
    print(f"🍔 麦门健身餐 | 数据: {src}" + (f" | 门店: {store.get('storeName')}" if store else ""))
    tgt = f"目标: ≤{g.max_kcal:.0f}kcal, 蛋白≥{g.min_protein:.0f}g"
    if g.budget < 1e8: tgt += f", 预算≤¥{g.budget:.0f}"
    if g.max_fat < 1e8: tgt += f", 脂肪≤{g.max_fat:.0f}g"
    print(tgt + "\n")
    if not plans:
        print("😢 没找到满足条件的组合，试试放宽热量或蛋白质目标。")
        return 1
    for i, p in enumerate(plans, 1):
        print(fmt_plan(i, p, priced) + "\n")
    if verify:
        print(f"✅ calculate-price 实时校验方案 1: ¥{verify['price']:.2f}（原价 ¥{verify['originalPrice']:.2f}）")
    print("ℹ️ 营养数据来自麦当劳官方 MCP，仅供参考，不构成医疗或营养建议；价格以下单页为准。")
    return 0
