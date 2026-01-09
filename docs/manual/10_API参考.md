# API 参考

本章节提供 mlp-train 主要类和函数的 API 参考。

## 核心类

### System

表示一个完整的系统，包含分子和可能的周期性边界条件。

```python
mlt.System(molecule, box=None)
```

**参数**：
- `molecule` (Molecule)：分子对象
- `box` (Box, optional)：周期性盒子

**方法**：
- `random_configuration()`：生成随机构型
- `configuration()`：生成特定构型

### Molecule

表示一个分子。

```python
mlt.Molecule(filename, charge=0, mult=1)
```

**参数**：
- `filename` (str)：XYZ 文件路径
- `charge` (int)：电荷
- `mult` (int)：自旋多重度

### Configuration

表示系统在某一时刻的构型。

```python
mlt.Configuration(atoms=None, charge=0, mult=1, box=None)
```

**属性**：
- `atoms`：原子列表
- `energy`：能量对象（Energy）
- `forces`：力对象（Forces）
- `box`：周期性盒子
- `charge`：电荷
- `mult`：自旋多重度

**方法**：
- `save_xyz(filename)`：保存为 XYZ 格式
- `single_point(method_name)`：单点计算

### ConfigurationSet

构型集合，用于管理训练数据。

```python
mlt.ConfigurationSet(configurations=None)
```

**方法**：
- `save_xyz(filename)`：保存所有构型
- `remove_above_e(threshold)`：移除高能构型
- `has_a_none_energy`：检查是否有未计算能量的构型

### Trajectory

分子动力学轨迹，继承自 ConfigurationSet。

```python
mlt.Trajectory(configurations=None)
```

**方法**：
- `save(filename)`：保存轨迹
- `compare(mlp, method_name)`：比较预测与真实值
- `plot()`：绘制轨迹

### Box

周期性边界条件的盒子。

```python
mlt.Box(size)
```

**参数**：
- `size` (list)：盒子尺寸 [x, y, z]（Å）

## 机器学习势能

### MLPotential（基类）

所有 MLP 模型的基类。

**属性**：
- `name`：势能名称
- `system`：关联的系统
- `training_data`：训练数据集

**方法**：
- `al_train(...)`：主动学习训练
- `train(configurations)`：使用给定数据集训练
- `predict(configuration)`：预测能量和力
- `save()`：保存模型
- `load()`：加载模型

### GAP

Gaussian Approximation Potential。

```python
mlt.potentials.GAP(name, system)
```

### ACE

Atomic Cluster Expansion。

```python
mlt.potentials.ACE(name, system)
```

### MACE

Multi-ACE。

```python
mlt.potentials.MACE(name, system)
```

## 主动学习

### al_train

主动学习训练函数。

```python
mlp.al_train(
    method_name,              # 参考方法名称
    selection_method=None,    # 选择方法
    max_active_time=1000,     # 最大时间（fs）
    n_configs_iter=10,       # 每次迭代的构型数
    temp=300.0,              # 温度（K）
    max_e_threshold=None,    # 最大能量阈值
    max_active_iters=50,     # 最大迭代次数
    n_init_configs=10,      # 初始构型数
    init_configs=None,      # 预定义初始构型
    fix_init_config=False,   # 固定初始构型
    bias=None,               # 偏置势
    constraints=None,        # 约束
    md_program='ASE',        # MD 程序
    pbc=False,               # 周期性边界条件
    box_size=None,           # 盒子尺寸
)
```

## 分子动力学

### run_mlp_md

使用 ASE 运行 MD 模拟。

```python
mlt.md.run_mlp_md(
    configuration,           # 起始构型
    mlp,                    # MLP 模型
    temp,                   # 温度（K）
    dt,                     # 时间步长（fs）
    interval,               # 保存间隔（步数）
    pressure=None,          # 压力（bar，NPT）
    compress=None,          # 压缩率（bar⁻¹，NPT）
    init_temp=None,         # 初始温度（K）
    bias=None,              # 偏置势
    constraints=None,       # 约束
    restart_files=None,      # 重启文件
    fs=None,                # 模拟时间（fs）
    ps=None,                # 模拟时间（ps）
    ns=None,                # 模拟时间（ns）
    save_fs=None,           # 保存间隔（fs）
    save_ps=None,           # 保存间隔（ps）
    save_ns=None,           # 保存间隔（ns）
)
```

### run_mlp_md_openmm

使用 OpenMM 运行 MD 模拟。

```python
mlt.md_openmm.run_mlp_md_openmm(
    configuration,           # 起始构型
    mlp,                     # MLP 模型
    temp,                    # 温度（K）
    dt,                      # 时间步长（fs）
    interval,                # 保存间隔（步数）
    init_temp=None,          # 初始温度（K）
    bias=None,               # 偏置势
    restart_files=None,      # 重启文件
    platform=None,           # OpenMM 平台
    fs=None,                 # 模拟时间（fs）
    ps=None,                 # 模拟时间（ps）
    ns=None,                 # 模拟时间（ns）
    save_fs=None,            # 保存间隔（fs）
    save_ps=None,            # 保存间隔（ps）
    save_ns=None,            # 保存间隔（ns）
)
```

## 选择方法

### AbsDiffE

基于能量绝对误差的选择方法。

```python
mlt.selection.AbsDiffE(e_thresh=0.1)
```

**参数**：
- `e_thresh` (float)：能量阈值（eV）

### AtomicEnvSimilarity

基于原子环境相似性的选择方法。

```python
mlt.selection.AtomicEnvSimilarity(descriptor, threshold=0.999)
```

**参数**：
- `descriptor`：描述符对象（如 SoapDescriptor）
- `threshold` (float)：相似性阈值

### AtomicEnvDistance

基于局部异常因子的选择方法。

```python
mlt.selection.AtomicEnvDistance(
    descriptor,
    pca=False,
    distance_metric='euclidean',
    n_neighbors=15
)
```

## 高级采样

### Metadynamics

元动力学类。

```python
mlt.Metadynamics(cvs, bias=None, temp=None)
```

**方法**：
- `run_mlp_md(...)`：运行元动力学 MD
- `estimate_width(...)`：估计高斯宽度
- `compute_free_energy(...)`：计算自由能

### UmbrellaSampling

伞形采样类。

```python
mlt.UmbrellaSampling(cvs, temp)
```

**方法**：
- `run(...)`：运行伞形采样
- `compute_free_energy(method='wham')`：计算自由能
- `plot_free_energy()`：绘制自由能曲线

## 反应坐标

### AverageDistance

平均距离反应坐标。

```python
mlt.AverageDistance(atom_idxs)
```

### DifferenceDistance

距离差反应坐标。

```python
mlt.DifferenceDistance(atom_idxs1, atom_idxs2)
```

## PLUMED 集体变量

### PlumedAverageCV

PLUMED 平均距离 CV。

```python
mlt.PlumedAverageCV(atom_idxs)
```

### PlumedDifferenceCV

PLUMED 距离差 CV。

```python
mlt.PlumedDifferenceCV(atom_idxs1, atom_idxs2)
```

### PlumedCNCV

PLUMED 配位数 CV。

```python
mlt.PlumedCNCV(atom_idxs, r_0, n, m)
```

### PlumedCustomCV

自定义 PLUMED CV。

```python
mlt.PlumedCustomCV(plumed_cv_string)
```

## 偏置

### Bias

简单偏置势。

```python
mlt.Bias(cv, kappa, ref)
```

**参数**：
- `cv`：反应坐标
- `kappa` (float)：弹簧常数（eV/单位²）
- `ref` (float)：参考值

### PlumedBias

PLUMED 偏置势。

```python
mlt.PlumedBias(cvs, from_file=False)
```

## 配置

### Config

全局配置类。

**属性**：
- `n_cores` (int)：并行核心数
- `orca_keywords` (list)：ORCA 关键词
- `gaussian_keywords` (list)：Gaussian 关键词
- `gap_default_params` (dict)：GAP 默认参数
- `ace_params` (dict)：ACE 参数
- `mace_params` (dict)：MACE 参数

## 工具函数

### convert_ase_time

转换 ASE 时间单位。

```python
mlt.convert_ase_time(value, from_unit, to_unit)
```

### convert_ase_energy

转换 ASE 能量单位。

```python
mlt.convert_ase_energy(value, from_unit, to_unit)
```

## 下一步

- 查看 [常见问题](11_常见问题.md) 解决使用中的问题
- 参考 [最佳实践](12_最佳实践.md) 优化您的使用
