import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class Mesh:

    '''
    A Mesh class definition to hold the handle meshes for the purpose.
    '''

    #Properties
    dimension = 2
    nNodes = 0
    nPhyGrp = 0
    nElem = 0
    nodes = []
    elements = []
    phyGrps = {}
    Connection = []

    #Constructor
    def __init__(self, dim):
        self.dimension = dim


    #Methods

    def read(self,filename):
        
        '''
        A function to read the GMSH exported mesh files.

        Supported Mesh Format is ASCII Version 2.0

        $MeshFormat
        2.0 0 8
        $EndMeshFormat

        $PhysicalNames
        Number of Physical Entities
        Dimension Number Name
        $EndPhysicalNames

        $Nodes
        #Number of Nodes
        Node X Y Z
        $EndNodes

        $Elements
        #Number of Elements                      
        ElementNumber ElementType 2 Physical Elementary Nodes
        $EndElements
        '''
        #Read the line
        with open(filename, 'r') as f:
            lines = np.array(f.readlines())


        format = lines[1].split()

        # Check the correct file format
        if lines[0] != "$MeshFormat\n":
            raise Exception("Incorrect File type !")
        elif not (format[0] == '2.2' and format[1] =='0'):
            raise Exception("Incorrect format of MSH file. Only Version 2.0 ASCII is supported.")

        # List out the physical groups
        phygrpIdx = np.where(lines=="$PhysicalNames\n")[0]
        self.nPhyGrp = int(lines[phygrpIdx+1])
        for i in range(self.nPhyGrp):
            l = lines[phygrpIdx+2+i][0].split()
            self.phyGrps[l[2].replace('"',"")] = int(l[1])

        # List out the nodes
        nodesIdx = np.where(lines=="$Nodes\n")[0]
        self.nNodes = int(lines[nodesIdx+1])

        #Create a Nodes dataframe
        self.nodes = pd.DataFrame({'ID':np.zeros(self.nNodes), 'x':np.zeros(self.nNodes), 'y':np.zeros(self.nNodes), 'z':np.zeros(self.nNodes)})

        #Set values of nodes
        for i in range(self.nNodes):
            l = lines[nodesIdx+2+i][0].split()
            self.nodes.loc[i,"ID"] = int(l[0])
            self.nodes.loc[i,"x"] = float(l[1])
            self.nodes.loc[i,"y"] = float(l[2])
            self.nodes.loc[i,"z"] = float(l[3])

        #Set ID column as row_index
        self.nodes=self.nodes.set_index('ID')

        # List out the elements
        elemIdx = np.where(lines=="$Elements\n")[0]
        self.nElem = int(lines[elemIdx+1])

        # Create an Elements dataframe
        self.elements = pd.DataFrame({'ID':np.zeros(self.nElem), 'Type':np.zeros(self.nElem), 'PhyGrp':np.zeros(self.nElem), 'Nodes':self.nElem*["0"]})

        # Set values of elements
        for i in range(self.nElem):
            l = lines[elemIdx+2+i][0].split()
            nN = len(l) - 5
            self.elements.loc[i, "ID"] = int(l[0])
            self.elements.loc[i, "Type"] = int(l[1])
            self.elements.loc[i, "PhyGrp"] = int(l[3])
            localNodes = []

            for j in range(nN):  
                localNodes.append(int(l[5 + j]))
            localNodes = self.sortCCW(np.array(localNodes))
            self.elements.loc[i, "Nodes"] = str(localNodes)
    
    def sortCCW(self,nL):
        '''
        Sorts the nodes in CCW order for easier computation
        '''
        n = self.nodes.iloc[nL-1,:]
        centX = np.mean(n.x)
        centY = np.mean(n.y)
        angle = np.atan2(n.y-centY, n.x-centX)
        return nL[np.argsort(angle)]

    def checkPair(self, pair):
    
        '''
        A method to check if a node pair exists in the
        connection set.
        '''
        if sorted(pair) not in self.Connection:
            return True
        else:
            return False
    
    def buildConnection(self):
        '''
        Method to create a set of connections between the
        various nodes which comprise the elements.

        Working:
        1. Initialize an empty set
        2. Start with first elements and start pairing nodes i.e. ith node with (i+1)th node.
        3. Check if (N1, N2) or (N2, N1) already exists in the connection set, if not add it.
        4. Continue for all the elements. 
        '''
        Con = []

        #Iterate over elements
        for i in range(self.nElem):
            nL = nodeList(self.elements.loc[i,'Nodes'])
            pairs = polygon_edges(nL)
            for pair in pairs:
                if self.checkPair(pair):
                    Con.append(sorted(pair))
        
        self.Connection = np.array(Con)
        
    def plotMesh(self):

        '''
        Method to plot the mesh elements.

        Working:
        1. BuildConnection.
        2. Plot lines of same color between the nodes.
        3. Save the figure
        '''
        
        #build the connection 
        if self.Connection==[]:
            self.buildConnection()

        #plot the lines between the nodes
        l = max(self.nodes.x) - min(self.nodes.x)
        h = max(self.nodes.y) - min(self.nodes.y)
        meshfig = plt.figure(figsize=[l,h])
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.xlim([min(self.nodes.x),max(self.nodes.x)])
        plt.ylim([min(self.nodes.y),max(self.nodes.y)])

        for pair in self.Connection:
            xl = [self.nodes.loc[pair[0], 'x'], self.nodes.loc[pair[1], 'x']]

            yl = [self.nodes.loc[pair[0], 'y'], self.nodes.loc[pair[1], 'y']]

            plt.plot(xl,yl,color='k',linewidth=0.5)

        plt.savefig('mesh.png', bbox_inches='tight', dpi=300)

def nodeList(st):
    '''
    A method to obtain and clean a list of nodes from the element dataframe.
    '''

    st = st.replace('[','')
    st = st.replace(']','')
    st = st.replace(',','')
    st = st.split()
    return np.array([int(x) for x in st])

def polygon_edges(corners):
        # Create consecutive pairs using zip and add the closing pair (last to first corner)
        edges = [[corners[i], corners[i+1]] for i in range(len(corners)-1)]
        edges.append([corners[-1], corners[0]])
        return edges