// Gmsh script to generate a mesh around a cylinder

// Variables

R = 0.5; //Radius of Cylinder
DH = 6;  //Domain Height
DL = 8;  //Domain Length
nc = 20; //Number of points of cylinder surface
nh = 20; //Number of points on the length boundary
nl = 20; //Number of points on the height boundary
np = 30; //Number of points on the progression boundaries

//Points
Point(100) = {0,0,0};
Point(1) = {R,0,0};
Point(2) = {R/Sqrt(2),R/Sqrt(2),0};
Point(3) = {-R/Sqrt(2),R/Sqrt(2),0};
Point(4) = {-R,0,0};
Point(5) = {-DL,0,0};
Point(6) = {-DL,DH,0};
Point(7) = {DL,DH,0};
Point(8) = {DL,0,0};


//Lines
Circle(1) = {1,100,2};
Circle(2) = {2,100,3};
Circle(3) = {3,100,4};
Line(4) = {4,5};
Line(5) = {5,6};
Line(6) = {6,7};
Line(7) = {7,8};
Line(8) = {8,1};
Line(9) = {2,7};
Line(10) = {3,6};

Transfinite Curve {1,2,3} = nc Using Progression 1.0;
Transfinite Curve {6} = nl Using Progression 1.0;
Transfinite Curve {5,7} = nh Using Progression 1.0;
Transfinite Curve {-4,8,-9,-10} = np Using Progression 0.95;
Transfinite Surface {1,2};

// Surfaces
Curve Loop(1) = {8, 1, 9, 7};
Plane Surface(1) = {1};
Curve Loop(2) = {9, -6, -10, -2};
Plane Surface(2) = {2};
Curve Loop(3) = {10, -5, -4, -3};
Plane Surface(3) = {3};

Transfinite Surface{1,2,3};
Recombine Surface {:};

Mesh 1;
Mesh 2;

//Physical Curves and Surfaces
Physical Curve("Inlet", 1) = {7};
Physical Curve("Outlet", 2) = {5};
Physical Curve("Top", 3) = {6};
Physical Curve("Bottom", 4) = {4,8};
Physical Curve("Cylinder",5) = {1,2,3};
Physical Surface("Fluid", 6) = {1,2,3};