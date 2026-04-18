import json
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

# Load data from the benchmark script
with open('benchmark_results.json', 'r') as f:
    data = json.load(f)

# Extract unique depths and breadths
depths = sorted(list(set(d['depth'] for d in data)))
breadths = sorted(list(set(d['breadth'] for d in data)))

# Create grids for plotting
X, Y = np.meshgrid(depths, breadths)
Z_custom = np.zeros(X.shape)
Z_builtin = np.zeros(X.shape)

# Fill the Z grids
for entry in data:
    d_idx = depths.index(entry['depth'])
    b_idx = breadths.index(entry['breadth'])
    Z_custom[b_idx, d_idx] = entry['custom_time']
    Z_builtin[b_idx, d_idx] = entry['builtin_time']

# Create the figure
fig = plt.figure(figsize=(14, 7))

# Subplot 1: Custom Parser (3D)
ax1 = fig.add_subplot(121, projection='3d')
surf1 = ax1.plot_surface(X, Y, Z_custom, cmap='viridis', edgecolor='none')
ax1.set_title('Custom Parser Performance')
ax1.set_xlabel('Depth')
ax1.set_ylabel('Breadth')
ax1.set_zlabel('Time (s)')
fig.colorbar(surf1, ax=ax1, shrink=0.5, aspect=5)

# Subplot 2: Built-in Parser (3D)
ax2 = fig.add_subplot(122, projection='3d')
surf2 = ax2.plot_surface(X, Y, Z_builtin, cmap='plasma', edgecolor='none')
ax2.set_title('Built-in Parser Performance')
ax2.set_xlabel('Depth')
ax2.set_ylabel('Breadth')
ax2.set_zlabel('Time (s)')
fig.colorbar(surf2, ax=ax2, shrink=0.5, aspect=5)

plt.tight_layout()
plt.savefig('performance_scaling.png')
print("Visualization saved as 'performance_scaling.png'.")
plt.show()
