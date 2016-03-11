# pyBinaryReader

## Usage

```
import pybinaryreader as br

# Get the model where the first argument is the path to the mdl and the second the path to BinaryReader.
# If you only have the jar, "java -jar /path/to/jar/BinaryReader-assembly-0.1.0.jar" can be use.
model = br.Model("/path/to/your/model/tcn01_a11_01.mdl", "/usr/bin/binaryreader")

# Get a specific node
node = model.getNode("Object1226")

# Get faces from the mesh
faces = node['mesh']['faces']
```