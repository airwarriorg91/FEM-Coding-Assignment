import mesh, solver
import numpy as np
import matplotlib.pyplot as plt
import scienceplots

plt.style.use(['science','ieee'])

m = mesh.Mesh(2)
m.read('mesh.msh')
m.plotMesh()

psi, sol = solver.solver(m)
solver.plotQOI(m.nodes.x,m.nodes.y,psi,'Potential')
solver.plotQOI(m.nodes.x,m.nodes.y,sol.Vel,'Velocity')
solver.plotQOI(m.nodes.x,m.nodes.y,sol.p,'Pressure')


cylwall = m.elements[np.logical_and(m.elements["PhyGrp"] == 5,m.elements["Type"] == 1)]

cylNodes = set()
for i in range(len(cylwall.index)):
    n = mesh.nodeList(cylwall.iloc[i,3])
    cylNodes.update(list(n))

cylNodes = np.array(list(cylNodes))
x = np.array(m.nodes.iloc[cylNodes-1,0])
y = np.array(m.nodes.iloc[cylNodes-1,1])
t = np.atan2(y,x)
idx = np.argsort(t)
cylNodes = cylNodes[idx]

theta = np.arange(-0.01,np.pi+0.01,0.01)
cp_theory = 1 - 4*np.sin(theta)**2
cp = 2*sol.p[cylNodes-1]

plt.figure(figsize=[4,4])
plt.plot(theta,cp_theory)
plt.plot(t[idx], cp)
plt.legend(['Theory', 'FEM'])
plt.xlabel('$\\theta$')
plt.ylabel('$c_p$')
plt.savefig('n100/cp.png', bbox_inches='tight', dpi=300)