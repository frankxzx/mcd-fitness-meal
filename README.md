<h1 align="center">🍔💪 麦门健身餐 · mcd-fitness-meal</h1>

<p align="center"><b>健身期也想吃麦当劳？告诉它你的热量和蛋白质目标，它帮你算出最省钱的那一顿。</b></p>

<p align="center">
  <img src="https://img.shields.io/badge/McDonald's-MCP-FFC72C?logo=mcdonalds&logoColor=DA291C" />
  <img src="https://img.shields.io/badge/Skill-Claude%20Code%20%7C%20Cursor%20%7C%20WorkBuddy-blue" />
  <img src="https://img.shields.io/badge/python-3.8%2B-3776AB?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/依赖-0%20个-brightgreen" />
  <img src="https://img.shields.io/badge/license-MIT-green" />
</p>

---

## ✨ 它能做什么

> 「≤600 大卡，蛋白质 ≥40g，最便宜怎么点？」

- 🥩 **按营养目标点餐**：减脂 / 增肌 / 高蛋白 / 均衡四种预设，也能自定义热量、蛋白质、脂肪、碳水、钠的上下限
- 💰 **算出最便宜组合**：用门店**实时价格**做精确搜索（分支定界，非拍脑袋），不是"推荐个板烧就完事"
- 📊 **三大营养素拆解**：每个方案给出热量、蛋白质、脂肪、碳水、钠，以及供能比
- 📍 **按城市/门店定价**：先找附近门店，再用 `calculate-price` 二次校验实时价
- 🔌 **离线也能跑**：内置官方营养库快照 + 示例门店价格，没 Token 也能体验
- 🧩 **一份 SKILL.md 走天下**：Claude Code / Cursor / WorkBuddy 都能直接用

## 🖥️ 真实运行效果

以下为 2026-10-14 调用麦当劳官方 MCP 的真实输出（上海人民广场附近门店）：

```text
$ python -m mcd_fitness --goal 高蛋白 --city 上海 --keyword 人民广场 --verify
🍔 麦门健身餐 | 数据: 实时 MCP | 门店: 麦当劳上海黄浦华旭国际大厦餐厅
目标: ≤650kcal, 蛋白≥40g

方案 1  ¥30.0
  - 那么大鸡排（椒盐风味）  ¥14.0  385kcal  蛋白24g
  - 薄皮焦香V翅  ¥16.0  192kcal  蛋白17g
  合计: 577 kcal | 蛋白质 41g | 脂肪 32g | 碳水 30g | 钠 1590mg
  供能比: 蛋白 28% · 脂肪 50% · 碳水 21%

方案 2  ¥39.0
  - 双层吉士汉堡  ¥23.0  429kcal  蛋白27g
  - 薄皮焦香V翅  ¥16.0  192kcal  蛋白17g
  合计: 621 kcal | 蛋白质 44g | 脂肪 33g | 碳水 37g | 钠 1611mg
  供能比: 蛋白 28% · 脂肪 48% · 碳水 24%

方案 3  ¥39.5
  - 薄皮焦香V翅  ¥16.0  192kcal  蛋白17g
  - 板烧鸡腿堡  ¥23.5  391kcal  蛋白23g
  合计: 583 kcal | 蛋白质 40g | 脂肪 28g | 碳水 41g | 钠 1635mg
  供能比: 蛋白 27% · 脂肪 43% · 碳水 28%

✅ calculate-price 实时校验方案 1: ¥30.00（原价 ¥30.00）
```

减脂模式（≤550kcal、蛋白 ≥30g、脂肪 ≤22g）：

```text
$ python -m mcd_fitness --goal 减脂 --offline --top 2
方案 1  ¥32.0
  - 薄皮焦香V翅 ×2  ¥16.0  192kcal  蛋白17g
  合计: 384 kcal | 蛋白质 34g | 脂肪 22g | 碳水 12g | 钠 1188mg
方案 2  ¥37.0
  - 双层深海鳕鱼堡  ¥24.0  485kcal  蛋白28g
  - 玉米杯（默认:小杯玉米杯）  ¥13.0  53kcal  蛋白2g
  合计: 538 kcal | 蛋白质 30g | 脂肪 22g | 碳水 53g | 钠 918mg
```

在 AI 助手里直接说人话即可：

> 我在杭州西湖附近，今晚练腿，想吃 800 大卡以内、蛋白质 50g 以上，40 块钱以内，不吃鱼。

## 🚀 安装

### 1. 拿到麦当劳 MCP Token
登录 [open.mcd.cn/mcp](https://open.mcd.cn/mcp) → 控制台 → 激活 → 复制 Token，然后：

```bash
export MCD_MCP_TOKEN=你的token   # 不要提交到 Git！
```

### 2. 配置 MCP（三选一）

<details open><summary><b>Claude Code</b></summary>

```bash
claude mcp add --transport http mcd-mcp https://mcp.mcd.cn --header "Authorization: Bearer $MCD_MCP_TOKEN"
git clone https://github.com/<你的用户名>/mcd-fitness-meal ~/.claude/skills/mcd-fitness-meal
```
</details>

<details><summary><b>Cursor</b></summary>

把 [`mcp-config.example.json`](./mcp-config.example.json) 的内容合并到 `~/.cursor/mcp.json`（`${MCD_MCP_TOKEN}` 会读取环境变量），再把本仓库克隆到项目里，或把 `SKILL.md` 放进 `.cursor/rules/`。
</details>

<details><summary><b>WorkBuddy</b></summary>

【专家·技能·连接器】→【连接器】→【自定义连接器】→【配置MCP】，粘贴 `mcp-config.example.json` 并替换 Token；然后在【技能】里导入本仓库的 `SKILL.md`。
</details>

### 3. 命令行（可选，零依赖）

```bash
git clone https://github.com/<你的用户名>/mcd-fitness-meal && cd mcd-fitness-meal
python -m mcd_fitness --goal 减脂 --offline                          # 离线体验
python -m mcd_fitness --goal 增肌 --city 北京 --keyword 国贸 --verify  # 实时价格
python -m mcd_fitness --max-kcal 600 --min-protein 40 --budget 35 --exclude 鱼,咖啡 --json
```

| 参数 | 说明 |
|---|---|
| `--goal` | 减脂 / 增肌 / 高蛋白 / 均衡 |
| `--max-kcal` `--min-kcal` `--min-protein` | 热量与蛋白质约束 |
| `--max-fat` `--max-carb` `--max-sodium` | 可选上限 |
| `--budget` | 预算（元） |
| `--city` `--keyword` / `--store` | 定位门店，使用实时价格 |
| `--exclude` | 忌口关键词 |
| `--verify` | 用 `calculate-price` 校验最优方案 |
| `--offline` | 只用 `data/` 下的缓存 |

## 👥 适合谁

- 🏋️ 健身党、减脂期、增肌期的打工人：想吃得爽也想守住宏量
- 🧑‍💻 加班的程序员：没空算卡路里，一句话出方案
- 🎓 学生党：预算有限，每一块钱都要换成蛋白质
- 🥗 控盐、控脂人群：用 `--max-sodium` / `--max-fat` 约束

## 🧠 原理

1. `list-nutrition-foods` 拉官方营养表（160 个单品）
2. `query-nearby-stores` → `query-meals` 拿门店菜单与实时价
3. 名称归一化 + `query-meal-detail` 解析默认规格，把菜单和营养表对齐
4. 分支定界精确搜索：最小化总价，满足热量/蛋白/脂肪/碳水/钠/预算约束（单测中与暴力枚举结果一致）
5. `calculate-price` 校验最终价格

详见 [MCP_INTEGRATION.md](./MCP_INTEGRATION.md)。

## ✅ 测试

```bash
python -m unittest discover -s tests -t .
```

## ⚠️ 声明

本项目为麦当劳程序员创意开发大赛参赛作品，由参赛者独立开发，非麦当劳官方产品。营养数据来自麦当劳官方 MCP，仅供参考，不构成医疗或营养建议；餐品、价格及供应状态以麦当劳官方渠道实时结果为准。详见 [CONTEST_DECLARATION.md](./CONTEST_DECLARATION.md)。

如果它帮你省了钱、守住了宏量，欢迎点个 ⭐！

License: [MIT](./LICENSE)
