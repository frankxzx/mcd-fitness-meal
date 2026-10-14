import json, os, unittest
from mcd_fitness.data import parse_nutrition, nutrition_index, match
from mcd_fitness.optimizer import Goal, optimize
from mcd_fitness.cli import main

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ITEMS = [
    dict(name="A", price=10, energyKcal=300, protein=20, fat=10, carbohydrate=30, sodium=500),
    dict(name="B", price=8, energyKcal=200, protein=15, fat=8, carbohydrate=10, sodium=400),
    dict(name="C", price=20, energyKcal=500, protein=40, fat=20, carbohydrate=40, sodium=900),
    dict(name="Cola", price=5, energyKcal=150, protein=0, fat=0, carbohydrate=36, sodium=0),
]


class T(unittest.TestCase):
    def test_parse_toon(self):
        raw = "[2]{productName,nutritionDescription,energyKj,energyKcal,protein,fat,carbohydrate,sodium,calcium}:\n  巨无霸,null,2146,513,27,26,42,961,171\n  纯悦,能量约清水1杯,0,0,0,0,0,0,0"
        n = parse_nutrition({"data": raw})
        self.assertEqual(n[0]["name"], "巨无霸"); self.assertEqual(n[0]["protein"], 27)
        self.assertEqual(len(n), 2)

    def test_match_aliases(self):
        idx = nutrition_index([{"name": "麦辣鸡翅-2块"}, {"name": "牛气满满"}, {"name": "那么大鸡排"}, {"name": "可乐中杯"}])
        self.assertTrue(match("麦辣鸡翅2块", idx))
        self.assertTrue(match("牛气满满套餐", idx))
        self.assertTrue(match("那么大鸡排（椒盐风味）", idx))
        self.assertTrue(match("可乐", idx))
        self.assertIsNone(match("麦当劳奶昔", idx))

    def test_cheapest(self):
        p = optimize(ITEMS, Goal(max_kcal=600, min_protein=35), top=3)
        self.assertEqual(p[0]["total"]["price"], 18)  # A+B (35g, 500kcal) beats C (20)
        for plan in p:
            self.assertGreaterEqual(plan["total"]["protein"], 35)
            self.assertLessEqual(plan["total"]["energyKcal"], 600)

    def test_brute_force_agrees(self):
        import itertools
        g = Goal(max_kcal=700, min_protein=40, max_items=3)
        best = min((sum(i["price"] for i in c) for k in range(1, 4) for c in itertools.combinations_with_replacement(ITEMS, k)
                    if sum(i["protein"] for i in c) >= 40 and sum(i["energyKcal"] for i in c) <= 700
                    and all(c.count(x) <= 2 for x in c)), default=None)
        self.assertEqual(optimize(ITEMS, g)[0]["total"]["price"], best)

    def test_infeasible(self):
        self.assertEqual(optimize(ITEMS, Goal(max_kcal=100, min_protein=50)), [])

    def test_budget(self):
        self.assertEqual(optimize(ITEMS, Goal(max_kcal=600, min_protein=35, budget=15)), [])

    def test_offline_cli(self):
        self.assertEqual(main(["--goal", "减脂", "--offline", "--json"]), 0)

    def test_no_secret_in_repo(self):
        for d, _, fs in os.walk(ROOT):
            if ".git" in d:
                continue
            for f in fs:
                if f.endswith((".py", ".md", ".json")):
                    txt = open(os.path.join(d, f), encoding="utf-8", errors="ignore").read()
                    self.assertNotRegex(txt, r"Bearer [A-Za-z0-9]{20,}")


if __name__ == "__main__":
    unittest.main()
