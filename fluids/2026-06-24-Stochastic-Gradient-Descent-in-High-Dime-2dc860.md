# Stochastic Gradient Descent in High Dimensions for Multi‐Spiked Tensor PCA

- **作者 (Authors)**: Gérard Ben Arous, Cédric Gerbelot, Vanessa Piccolo
- **来源 (Source)**: Commun. Pure Appl. Math.
- **日期 (Date)**: 2026-06-24
- **原文链接 (Link)**: [查看原始论文](https://onlinelibrary.wiley.com/doi/10.1002/cpa.70056?af=R)

## 中文摘要

摘要
                  我们研究多尖峰张量模型的在线随机梯度下降（SGD）的高维动力学。这种多指标模型源于具有多个尖峰的张量主成分分析（PCA）问题，其目标是通过来自张量的噪声观测的最大似然估计来估计维单位球内的未知信号向量。我们确定从自然随机初始化中有效恢复未知尖峰所需的样本数量和信噪比（SNR）条件。我们表明，如果样本缩放数量为 ，与排名一情况下确定的算法阈值相匹配，则可以完全恢复所有尖峰。我们的结果是通过对低维系统的详细分析获得的，该系统描述了估计量和尖峰之间相关性的演变，同时严格控制动态中的噪声。我们发现尖峰在我们称之为“顺序消除”的过程中顺序恢复：一旦相关性超过临界阈值，共享行或列索引的所有相关性就会变得足够小，从而允许下一个相关性增长并变得宏观。相关性变得宏观的顺序取决于它们的初始值和相应的 SNR，从而导致尖峰排列的精确恢复或恢复。在矩阵情况下，当 时，如果 SNR 充分分离，我们可以实现尖峰的精确恢复，而相等的 SNR 则可以恢复它们所跨越的子空间。

---

## 英文摘要

ABSTRACT
                  We study the high‐dimensional dynamics of online stochastic gradient descent (SGD) for the multi‐spiked tensor model. This multi‐index model arises from the tensor principal component analysis (PCA) problem with multiple spikes, where the goal is to estimate the unknown signal vectors within the ‐dimensional unit sphere through maximum likelihood estimation from noisy observations of a ‐tensor. We determine the number of samples and the conditions on the signal‐to‐noise ratios (SNRs) required to efficiently recover the unknown spikes from natural random initializations. We show that full recovery of all spikes is possible provided a number of sample scaling as , matching the algorithmic threshold identified in the rank‐one case. Our results are obtained through a detailed analysis of a low‐dimensional system that describes the evolution of the correlations between the estimators and the spikes, while sharply controlling the noise in the dynamics. We find the spikes are recovered sequentially in a process we term “sequential elimination”: once a correlation exceeds a critical threshold, all correlations sharing a row or column index become sufficiently small, allowing the next correlation to grow and become macroscopic. The order in which correlations become macroscopic depends on their initial values and the corresponding SNRs, leading to either exact recovery or recovery of a permutation of the spikes. In the matrix case, when , if the SNRs are sufficiently separated, we achieve exact recovery of the spikes, whereas equal SNRs lead to recovery of the subspace spanned by them.
