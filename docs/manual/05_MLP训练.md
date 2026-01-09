# MLP 训练

mlp-train 的核心功能是使用主动学习（Active Learning）方法训练机器学习势能。本章节详细介绍训练过程和各种选项。

## 主动学习概述

主动学习是一个迭代过程，通过以下循环自动生成训练数据：

```
生成构型 → 训练 MLP → 运行 MLP-MD → 选择构型 → 计算真实值 → 添加到训练集
     ↑                                                                      |
     |______________________________________________________________________|
```

### 主动学习的优势

- **自动化**：无需手动准备训练数据
- **高效**：只计算对训练有用的构型
- **自适应**：自动探索构型空间

## 基本训练

最简单的训练方式：

```python
import mlptrain as mlt

mlt.Config.n_cores = 10
system = mlt.System(mlt.Molecule('water.xyz'), box=None)

# 创建 MLP
gap = mlt.potentials.GAP('water', system=system)

# 主动学习训练
gap.al_train(method_name='orca', temp=1000)
```

### 参数说明

- `method_name`：参考方法（'orca', 'xtb', 'gaussian', 'gpaw' 等）
- `temp`：主动学习时的温度（K），较高温度有助于探索更多构型空间

## 训练参数详解

### 基本参数

```python
gap.al_train(
    method_name='orca',
    temp=1000,                    # 温度（K）
    max_active_iters=50,          # 最大迭代次数
    max_active_time=1000,         # 每次迭代最大时间（fs）
    n_configs_iter=10,           # 每次迭代生成的构型数
    n_init_configs=10,            # 初始构型数
)
```

### 选择方法（Selection Method）

选择方法决定哪些构型应该被添加到训练集。

#### 1. AbsDiffE（默认）

基于能量绝对误差的选择方法：

```python
from mlptrain.training.selection import AbsDiffE

selector = AbsDiffE(e_thresh=0.1)  # 能量阈值（eV）
gap.al_train(method_name='orca', selection_method=selector, temp=1000)
```

**工作原理**：
- 如果 `E_T < |E_predicted - E_true| < 10*E_T`，则选择该构型
- 如果 `|E_predicted - E_true| > 10*E_T`，则回溯并重新搜索

#### 2. AtomicEnvSimilarity

基于原子环境相似性的选择方法：

```python
from mlptrain.training.selection import AtomicEnvSimilarity
from mlptrain.descriptor import SoapDescriptor

# 定义 SOAP 描述符
descriptor = SoapDescriptor(
    average='outer',
    r_cut=6.0,      # 截断半径（Å）
    n_max=6,        # 径向基函数数
    l_max=6,        # 角动量量子数
)

# 创建选择器
selector = AtomicEnvSimilarity(
    descriptor=descriptor,
    threshold=0.9995  # 相似性阈值
)

gap.al_train(method_name='xtb', selection_method=selector, temp=500)
```

**工作原理**：
- 计算新构型与训练集中所有构型的 SOAP 核相似性
- 如果最大相似性在阈值范围内，则选择该构型

#### 3. AtomicEnvDistance

基于局部异常因子（LOF）的选择方法：

```python
from mlptrain.training.selection import AtomicEnvDistance

selector = AtomicEnvDistance(
    descriptor=descriptor,
    pca=False,              # 是否使用 PCA 降维
    distance_metric='euclidean',  # 距离度量
    n_neighbors=15,         # 邻居数
)

gap.al_train(method_name='orca', selection_method=selector, temp=1000)
```

### 能量阈值

限制添加到训练集的构型能量：

```python
gap.al_train(
    method_name='orca',
    temp=1000,
    max_e_threshold=5.0  # 最大相对能量（eV），高于此值的构型将被移除
)
```

### 初始构型

#### 使用随机初始构型

```python
gap.al_train(
    method_name='orca',
    temp=1000,
    n_init_configs=20  # 生成 20 个随机初始构型
)
```

#### 使用预定义初始构型

```python
# 准备初始构型集
init_configs = mlt.ConfigurationSet()
init_configs += config1
init_configs += config2

gap.al_train(
    method_name='orca',
    temp=1000,
    init_configs=init_configs  # 使用预定义的初始构型
)
```

#### 固定初始构型

```python
gap.al_train(
    method_name='orca',
    temp=1000,
    fix_init_config=True  # 每次迭代都从同一个初始构型开始
)
```

默认情况下，每次迭代会选择能量最低的构型作为起始点。

### 约束和偏置

#### 添加约束

```python
from ase.constraints import FixBondLength

# 固定键长
constraint = FixBondLength(0, 1)  # 固定原子 0 和 1 之间的键长

gap.al_train(
    method_name='orca',
    temp=1000,
    constraints=[constraint]
)
```

#### 添加偏置势

```python
from mlptrain.sampling import Bias
from mlptrain.sampling.reaction_coord import AverageDistance

# 定义反应坐标
cv = AverageDistance(atom_idxs=[0, 1])

# 创建偏置
bias = Bias(cv, kappa=0.1, ref=2.0)  # 弹簧常数 0.1 eV/Å²，参考值 2.0 Å

gap.al_train(
    method_name='orca',
    temp=1000,
    bias=bias,
    bias_start_iter=5  # 从第 5 次迭代开始应用偏置
)
```

### 键断裂/形成能量

在特定键方向添加额外能量，促进反应：

```python
# 键断裂能量
bbond_energy = {(0, 1): 0.1}  # 在原子 0 和 1 之间添加 0.1 eV 的断裂能量

# 键形成能量
fbond_energy = {(2, 3): 0.1}  # 在原子 2 和 3 之间添加 0.1 eV 的形成能量

gap.al_train(
    method_name='orca',
    temp=1000,
    bbond_energy=bbond_energy,
    fbond_energy=fbond_energy
)
```

### 使用 OpenMM

MACE 模型支持使用 OpenMM 进行 MD 模拟：

```python
mace = mlt.potentials.MACE('water', system=system)

mace.al_train(
    method_name='xtb',
    temp=500,
    md_program='OpenMM',  # 使用 OpenMM 而不是 ASE
)
```

### 周期性边界条件

对于溶液相系统：

```python
box = mlt.Box([20.0, 20.0, 20.0])
system = mlt.System(mlt.Molecule('water.xyz'), box=box)

gap.al_train(
    method_name='orca',
    temp=1000,
    pbc=True,              # 启用周期性边界条件
    box_size=[20.0, 20.0, 20.0]
)
```

## 训练过程监控

训练过程中会输出以下信息：

- 当前迭代次数
- 已添加的构型数
- 训练数据集大小
- 能量误差统计

## 训练结果

训练完成后：

- **训练数据**：保存在 `mlp.training_data` 中
- **模型文件**：根据模型类型保存（如 `water_gap.xml`）
- **日志信息**：显示在控制台

### 访问训练数据

```python
# 训练数据集大小
print(f"训练数据点数: {gap.n_train}")

# 访问训练数据
for config in gap.training_data:
    print(f"能量: {config.energy.true} eV")
```

### 保存和加载

```python
# 保存（通常在训练时自动保存）
gap.save()

# 加载已训练的模型
gap.load()
```

## 高级选项

### 重启训练

从特定迭代重新开始：

```python
gap.al_train(
    method_name='orca',
    temp=1000,
    restart_iter=10  # 从第 10 次迭代重新开始
)
```

### 继承元动力学偏置

在主动学习中继承之前的元动力学偏置：

```python
gap.al_train(
    method_name='orca',
    temp=1000,
    inherit_metad_bias=True  # 继承元动力学偏置
)
```

### 保存 AL 轨迹

保存主动学习过程中生成的轨迹：

```python
gap.al_train(
    method_name='orca',
    temp=1000,
    keep_al_trajs=True  # 保存 AL 轨迹到单独文件夹
)
```

## 最佳实践

1. **选择合适的温度**：
   - 较低温度（300-500 K）：适合稳定结构
   - 较高温度（1000-2000 K）：适合探索反应路径

2. **调整选择方法**：
   - 简单系统：使用 `AbsDiffE`
   - 复杂系统：使用 `AtomicEnvSimilarity`

3. **监控训练过程**：
   - 观察添加的构型数
   - 检查能量误差是否收敛

4. **验证训练结果**：
   - 使用 `trajectory.compare()` 比较预测与真实值
   - 检查能量和力的误差分布

## 下一步

- 学习如何运行 [分子动力学模拟](06_分子动力学.md)
- 了解 [高级采样方法](07_高级采样.md)
