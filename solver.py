import numpy as np
import numpy.linalg as la
import mesh
import pandas as pd
import matplotlib.pyplot as plt

def compdN(e,n):
    dNde = 0.25*np.array([n-1, 1-n, n+1, -n-1])
    dNdn = 0.25*np.array([e-1, -e-1, e+1, 1-e])
    return [dNde, dNdn]

def Jacobian(dN,x,y):
    J = np.array([[dN[0]@np.transpose(x),  dN[0]@np.transpose(y)],[dN[1]@np.transpose(x),  dN[1]@np.transpose(y)]])

    return J


def computeKe(x,y):
    '''
    A function to calculate the elemental stiffness matrix

    Input: Coordinates of the element

    Output: Local elemental matrix 

    Works for Linear Quadrilateral elements
    '''
    K = np.zeros((4,4))
    zeta = eta = [-1/np.sqrt(3), 1/np.sqrt(3)]
    for e in zeta:
        for n in eta:
            dN = compdN(e,n)
            J = Jacobian(dN,x,y)
            B = la.inv(J) @ dN
            K = K + la.det(J)*(np.transpose(B) @ B)
    
    return K

def computeV(x,y,psi):
    V = np.zeros((4,4))
    zeta = eta = [-1, 1]
    count = 0
    for e in zeta:
        for n in eta:
            dN = compdN(e,n)
            J = Jacobian(dN,x,y)
            B = la.inv(J) @ dN
            V[count,0:2] = np.transpose(B @ psi)
            V[count,2] = np.sqrt(V[count,0]**2 + V[count,1]**2)
            V[count,3] = 0.5*(1 - V[count,2]**2)
            count+=1
    return V

def plotQOI(x,y,qoi,text):
    '''
    plots the nodal value of qoi.
    '''

    l = max(x) - min(x) + 2 
    h = max(y) - min(y)
    meshfig = plt.figure(figsize=[l,h])
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.xlim([min(x),max(x)])
    plt.ylim([min(y),max(y)])
    plt.scatter(x, y, c=qoi, cmap='turbo', s=5)
    plt.colorbar(label=text)
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.savefig(f'n100/{text}.png', bbox_inches='tight', dpi=300)

def solver(m):
    
    '''
    Function to solve the potential flow laplace eqn.

    Input: Mesh object m

    Output: Velocity and Pressure at each node

    Procedure:
    1. Assemble the Global Stiffness Matrix
    2. Assemblying the RHS
    3. Find the active nodes
    4. Find the value of potential function
    5. Compute velocity from potential function
    6. Compute pressure from velocity

    B.C.
    1--> Inlet
    2--> Outlet
    3--> Top
    4--> Bottom
    5--> Cylinder
    6--> Fluid
    '''

    K = np.zeros((m.nNodes,m.nNodes))
    Nodes = set(m.nodes.index)
    
    inlet = m.elements[np.logical_and(m.elements["PhyGrp"] == 1,m.elements["Type"] == 1)]
    outlet = m.elements[np.logical_and(m.elements["PhyGrp"] == 2,m.elements["Type"] == 1)]
    quads = m.elements[m.elements["Type"] == 3]
    nQuads = len(quads.index)

    # Step 1 
    for i in range(nQuads):
        nodes = mesh.nodeList(quads.iloc[i,3])
        n = m.nodes.iloc[nodes-1,:]
        Ke = computeKe(n.x,n.y)
        K[np.ix_(nodes-1, nodes-1)] += Ke

    #Step 2
    RHS = np.zeros((m.nNodes,1))
    for i in range(len(outlet.index)):
        n = mesh.nodeList(outlet.iloc[i,3])
        l = np.abs(m.nodes.iloc[n[0]-1,1]-m.nodes.iloc[n[1]-1,1])
        RHS[n[0]-1] += l/2
        RHS[n[1]-1] += l/2

    #Step 3 (At inlet, phi=Ux)
    PD = set()
    for i in range(len(inlet.index)):
        n = mesh.nodeList(inlet.iloc[i,3])
        PD.update(list(n))
    
    AD = Nodes - PD
    PD = np.array(list(PD), dtype=int)
    AD = np.array(list(AD), dtype=int)

    #Step 4
    psi = np.zeros((m.nNodes,1))
    #psi[PD-1] = np.mean(m.nodes.iloc[PD-1,0])
    psi[AD-1] = la.solve(K[np.ix_(AD-1, AD-1)], RHS[AD-1])

    #Step 5 and 6
    sol = pd.DataFrame(np.zeros((m.nNodes,4)), columns=['u','v','Vel','p'])
    for i in range(nQuads):
        nodes = mesh.nodeList(quads.iloc[i,3])
        n = m.nodes.iloc[nodes-1,:]
        ps = psi[nodes-1]
        sol.loc[nodes-1,:] = computeV(n.x,n.y,ps) 
    return psi, sol