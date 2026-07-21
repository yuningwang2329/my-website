# Phase-Field Models, Sharp Interface Limits, and Numerical Schemes for Contact Line Dynamics

- **作者 (Authors)**: Guosheng Fu, Yuan Gao, Jian-Guo Liu
- **来源 (Source)**: Arxiv (math.AP)
- **日期 (Date)**: 2026-07-19
- **原文链接 (Link)**: [查看原始论文](https://arxiv.org/abs/2607.17410v1)

## 中文摘要

我们在统一的变分框架内研究固体基底上液滴接触线动力学的相场和锐界面模型。由于无滑移流体动力学的经典应力奇异性，液、气、固相交汇处的接触线的运动给连续介质建模带来了根本性的困难。相场模型通过引入厚度薄的过渡层并通过由基底上的壁能量增强的金兹堡-朗道自由能编码界面效应来规范这种奇点。从总自由能 $E = E_b + E_w$ 出发，我们分析两个相场模型：Allen-Cahn 方程和 Cahn-Hilliard 方程。使用匹配的渐近展开式$δ\to 0$，我们恢复了它们相应的尖锐界面限制。在 Allen-Cahn 情况下，极限产生平均曲率运动，接触线定律由动态接触角与杨氏角的偏差驱动。在 Cahn-Hilliard 案例中，该极限导致具有相同形式的接触线动力学的 Mullins-Sekerka 问题。这项工作的核心成果是识别了两个模型中一致的梯度流结构。 Allen-Cahn 动力学对应于 $L^2$ 梯度流，而 Cahn-Hilliard 动力学对应于 $H^{-1}$ 梯度流，并且两者都收敛到保留相同能量耗散结构的锐界面演化。这提供了对接触线运动作为单一变分原理的结果的统一解释。最后，我们基于最小化运动原理开发了能量稳定的数值方案，并建立了完全离散问题的离散能量耗散和适定性。数值例子证实，两种方案都松弛到相同的稳态尖锐界面解，而它们的动力学反映了不同的耗散机制。

---

## 英文摘要

We study phase-field and sharp-interface models for contact line dynamics of a liquid droplet on a solid substrate within a unified variational framework. The motion of the contact line, where liquid, gas, and solid phases meet, poses a fundamental difficulty in continuum modeling due to the classical stress singularity of no-slip hydrodynamics. Phase-field models regularize this singularity by introducing a thin transition layer of thickness and encoding interfacial effects through a Ginzburg-Landau free energy augmented by a wall energy on the substrate. Starting from the total free energy $E = E_b + E_w$, we analyze two phase-field models: the Allen-Cahn equation and the Cahn-Hilliard equation. Using matched asymptotic expansions as $δ\to 0$, we recover their corresponding sharp interface limits. In the Allen-Cahn case, the limit yields motion by mean curvature with a contact line law driven by deviations of the dynamic contact angle from Young's angle. In the Cahn-Hilliard case, the limit leads to a Mullins-Sekerka problem with the same form of contact line dynamics. A central result of this work is the identification of consistent gradient-flow structures across both models. The Allen-Cahn dynamics correspond to an $L^2$-gradient flow, while the Cahn-Hilliard dynamics correspond to an $H^{-1}$-gradient flow, and both converge to sharp-interface evolutions that preserve the same energy-dissipation structure. This provides a unified interpretation of contact line motion as a consequence of a single variational principle. Finally, we develop energy-stable numerical schemes based on the minimizing movement principle and establish discrete energy dissipation and well-posedness of the fully discrete problem. Numerical examples confirm that both schemes relax toward the same stationary sharp interface solution while their dynamics reflect the different dissipation mechanisms.
