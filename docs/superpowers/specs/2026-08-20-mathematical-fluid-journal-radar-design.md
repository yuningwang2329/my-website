# 数学流体期刊雷达设计

## 目标

把现有的“流体论文库”从仅依赖少量分析/PDE 期刊，扩展为面向数学流体的高信号订阅雷达：既持续捕获数学流体与非线性 PDE 的常规新论文，也不会漏掉顶级综合数学期刊中的低频重要文章。

## 范围

- 保留已有来源、去重、AI/关键词筛选、翻译、Markdown 详情页和 90 天首页数据窗口。
- 新增 18 个经验证的期刊来源，并把所有来源归入三个稳定的内部组标识：
  - `math-fluid-pde`：数学流体与非线性 PDE；包括既有来源，以及 Journal of Mathematical Fluid Mechanics、Annales de l’Institut Henri Poincaré C – Analyse non linéaire、Analysis & PDE、Nonlinearity。
  - `top-general-math`：顶级综合数学；Annals of Mathematics、Acta Mathematica、Inventiones mathematicae、Journal of the American Mathematical Society、Publications Mathématiques de l’IHÉS。
  - `high-general-math`：综合数学高刊；Proceedings/Journal of the London Mathematical Society、Duke Mathematical Journal、Journal of the European Mathematical Society、Annales scientifiques de l’École Normale Supérieure、Advances in Mathematics、Crelle’s Journal、Selecta Mathematica、Forum of Mathematics, Pi。
- 首页新增“期刊组”筛选。它显示三组、各自近 90 天的论文数，并能与专题、单一期刊、月份和收藏筛选取交集。
- 顶级综合数学在界面中作为一个入口出现，但每篇论文继续显示其真实期刊名和 DOI 链接。

## 不在本次范围

- 不加载超过 90 天的归档数据到首页；历史期刊浏览需要独立的按需归档加载方案。
- 不改变当前“同标题只保留一个记录”的去重逻辑；因此先收录 arXiv 版本时，后续期刊版本不会另行出现。这是已有行为，留作后续单独改进。
- 不增加物理/工程流体期刊，也不重做页面视觉设计。

## 数据与更新设计

每个 `FEEDS` 条目增加 `source_group`。更新器把它写入新论文的 `fluids.json`；Markdown 详情页继续只保存并显示真实期刊来源。已有的 90 天记录在首页通过来源名称映射到相同分组，因此新旧记录的筛选行为一致。

所有适合的数学期刊使用 Crossref 的期刊 works API，查询明确限定 `type:journal-article`，避免把 issue 或 future issue 元数据误写成论文。Advances in Mathematics 使用其官方 Elsevier RSS，因为其电子 ISSN 的 Crossref 记录为空。PLMS 和 JLMS 使用官方 Wiley RSS，其余经验证有正常 Crossref 期刊 works 返回的期刊使用 Crossref。

关键词兜底筛选补足 `non-Newtonian`、`viscoelastic`、`multiphase`、`porous media` 等数学流体术语，确保 LLM 服务临时不可用时仍不会系统性漏掉相关论文。

## 页面行为

`source` 永远表示真实期刊名；`source_group` 只用于组筛选。新组筛选使用单独的 `filterSourceGroup` 状态，与现有 `filterJournal` 和 `filterMonth` 并列。论文卡片与详情页不显示内部组 ID。

期刊组是静态的三项导航，即便当期组内数为零也保留入口。首页仍只请求 `fluids.json`，不增加额外首屏网络请求或 JavaScript 依赖。

## 验收标准

- 配置中的每个来源都有合法的 `source_group`，并且四大刊与 PMIHÉS 位于 `top-general-math`。
- Crossref 请求只请求 `journal-article`，不会把空标题 issue 记录写入数据。
- 新写入论文保留真实 `source` 与 `source_group`；关键词兜底可识别新增的数学流体术语。
- 首页存在三个期刊组入口；选择组后只显示该组文章，并可与单一期刊/月筛选叠加。
- 论文卡片仍直接显示 `p.source`，不会显示或以分组名替代真实期刊。
- 现有首页性能、移动筛选、论文详情页渲染与自动更新流程保持可用。
