# Adaptive Mamba Neural Operators

- **作者 (Authors)**: Zeyuan Song, Zheyu Jiang
- **来源 (Source)**: Arxiv (math.AP)
- **日期 (Date)**: 2026-07-20
- **原文链接 (Link)**: [查看原始论文](https://arxiv.org/abs/2607.18043v1)

## 中文摘要

准确求解任意几何形状和各种网格上的偏微分方程（PDE）是科学和工程应用中的一项重要任务。在本文中，我们提出了自适应曼巴神经算子（AMO），它集成了状态空间模型（SSM）的再现内核，而不是 SSM 的内核积分公式。这是通过为偏微分方程构建 Takenaka-Malmquist 系统来实现的。 AMO 提供了与自适应傅立叶分解 (AFD) 理论非常一致的新表示形式，并且可以在各种几何形状和网格上近似偏微分方程的解流形。在流体物理、固体物理和金融领域的点云、结构化网格、规则网格和不规则域上的几个具有挑战性的基准偏微分方程问题中，AMO 在相对 $L^2$ 误差方面始终优于最先进的求解器。总的来说，这项工作为设计可解释的神经算子框架提供了一种新的范例。

---

## 英文摘要

Accurately solving partial differential equations (PDEs) on arbitrary geometries and a variety of meshes is an important task in science and engineering applications. In this paper, we propose Adaptive Mamba Neural Operators (AMO), which integrates reproducing kernels for state-space models (SSMs) rather than the kernel integral formulation of SSMs. This is achieved by constructing Takenaka-Malmquist systems for the PDEs. AMO offers new representations that align well with the adaptive Fourier decomposition (AFD) theory and can approximate the solution manifold of PDEs on a wide range of geometries and meshes. In several challenging benchmark PDE problems in the fields of fluid physics, solid physics, and finance on point clouds, structured meshes, regular grids, and irregular domains, AMO consistently outperforms state-of-the-art solvers in terms of relative $L^2$ error. Overall, this work presents a new paradigm for designing explainable neural operator frameworks.
