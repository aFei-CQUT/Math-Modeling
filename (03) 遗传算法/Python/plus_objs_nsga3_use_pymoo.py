import numpy as np
import matplotlib.pyplot as plt
from pymoo.core.problem import Problem
from pymoo.algorithms.moo.nsga3 import NSGA3
from pymoo.util.ref_dirs import get_reference_directions
from pymoo.optimize import minimize
from sklearn.decomposition import PCA

# 定义多目标优化问题（4个目标函数）
class MyProblemND(Problem):
    def __init__(self, n_obj=4):
        super().__init__(n_var=10, n_obj=n_obj, n_constr=0, xl=np.array([-5]*10), xu=np.array([5]*10))

    def _evaluate(self, x, out, *args, **kwargs):
        f1 = np.sum(x**2, axis=1)
        f2 = np.sum((x - 1)**2, axis=1)
        f3 = np.sum((x + 1)**2, axis=1)
        f4 = np.sum((x - 0.5)**2, axis=1)  # 新增的目标函数
        out["F"] = np.column_stack([f1, f2, f3, f4])

# 创建问题实例，指定目标数量
problem = MyProblemND(n_obj=4)

# 获取参考方向
ref_dirs = get_reference_directions("das-dennis", 4, n_partitions=12)

# 定义 NSGA-III 算法
algorithm = NSGA3(pop_size=100, ref_dirs=ref_dirs)

# 执行优化
res = minimize(problem,
               algorithm,
               termination=('n_gen', 200),
               seed=1,
               verbose=True,
               save_history=True)  # 保存历史记录

# 处理优化结果中的无效值
def clean_results(res):
    f_values = res.F
    valid_indices = ~np.isnan(f_values).any(axis=1) & ~np.isinf(f_values).any(axis=1)
    valid_f_values = f_values[valid_indices]
    return valid_f_values

# 获取清理后的结果
valid_f_values = clean_results(res)

# PCA 降维
n_components = min(valid_f_values.shape[1], 2)  # 确保最多降维到2维
pca = PCA(n_components=n_components)
valid_f_values_2d = pca.fit_transform(valid_f_values)

# 设置全局样式
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体字体
plt.rcParams['axes.unicode_minus'] = False  # 正常显示负号
plt.style.use('seaborn-v0_8-deep')  # 使用 Seaborn 样式风格
plt.rcParams['text.usetex'] = True  # 启用 LaTeX 渲染

# 绘制 PCA 投影，使用适应度值作为颜色映射
plt.figure(figsize=(10, 5))
scatter = plt.scatter(valid_f_values_2d[:, 0], valid_f_values_2d[:, 1], 
                      c=np.linalg.norm(valid_f_values, axis=1), cmap='viridis')
plt.colorbar(scatter, label='Fitness Value')  # 添加颜色条，表示适应度值
plt.title("PCA Projection of Optimization Results")
plt.xlabel("First Principal Component")
plt.ylabel("Second Principal Component")
plt.grid(True)
plt.show()

# 绘制最优粒子位置随迭代变化
history = res.history
best_fitness = [h.pop.get("F").min(axis=0) for h in history]

# 迭代次数
iterations = range(len(best_fitness))

plt.figure(figsize=(9.33, 5))
for i in range(best_fitness[0].shape[0]):
    plt.plot(iterations, [bf[i] for bf in best_fitness], label=f'Objective {i+1}')

plt.title('Best Fitness Over Iterations')
plt.xlabel('Iterations')
plt.ylabel('Fitness Value')
plt.grid(True)
plt.legend()
plt.show()