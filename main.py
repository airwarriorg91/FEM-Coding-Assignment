import reader

mesh = reader.Mesh(2)

mesh.read('mesh.msh')
mesh.plotMesh()