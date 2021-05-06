# ShrinkRepair
Shrinkwrapping repair for solid models in obj or poly or CityGML format
# Folder description
- RepairShrink the repair source code
    - TetgenDLL the compiled dll of Tetgen 1.5+ for tetrahedralization
    - TriangleDLL the compiled dll of Triangle for triangulation
    - TriangleIntersection the compiled dll for fast detection of intersecting triangles
    - iglDLL the compiled dll for estimate mesh curvature
    - RepairShrink the source code
- CityGML2SPoly  utility for converting CityGML solids to semantic-enabled poly files
- obj2poly  utility for converting and tesselating .obj file to .poly file 
- SPolys2CityGML utility for converting repaired semantic-enabled poly files to a CityGML .xml file 

# Usage
Please refer to CallRepair.py
Sorry the code is out of maitainance and tons of debugging and experimental code exist. 
But it should run after some tuning...