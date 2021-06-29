''' https://core.ac.uk/download/pdf/82483792.pdf  
approximates an Euler spiral (clothoid) by a series of circular arcs with linearly in/de-creasing curvatures
To retain 2nd order accuracy the first and last arcs are half-length
As there is no equality constraint in sketcher for arcs, we make the corresponding chords equal.  This creates additional O((A/N)^2) errors.
A is the angle (in degrees) between the entry and exit points on the spiral
R1 is the initial radius
R2 is the final radius
N is the number of arc-segments
The spiral turns counter-clockwise from entry to exit.
The A, N and the R2/R1 remains fixed whenever the sketch is manipulated.
useA = True  #   to use A, else use curveLength as Input.
The sketch has one remaing degrees of freedom:
    Rotating around the origin
Deactivating the "EulerOrigin"" constraint allow the curve to be translated
Deactivating the "EulerR1/2'" radius constraint allows the curve to be rescaled keeping R1/R2 fixed.
Make R large for a straight entry or exit.   Radius ratios more than 1000- 10000 can give weird solver problems'''
    

import math
from FreeCAD import Vector
import FreeCAD as App

### edit these input parameters
useA = False    # Use total angle as input, otherwise use curveLength
A = 90
curveLength = 10*math.pi
R1 = 10
R2 = 1e4
N = 20


sketchName = 'Sketch'
####

def newarc(vertex_x, vertex_y, beta, d, alpha):
    new_radius = (d/2)/math.sin(alpha/2)
    center_x = vertex_x - new_radius* math.cos(beta)
    center_y = vertex_y - new_radius * math.sin(beta)
    new_vertex_x = vertex_x - d * math.sin(beta + alpha/2)
    new_vertex_y = vertex_y + d * math.cos(beta + alpha/2)
    mid_x = center_x + new_radius * math.cos(beta + alpha/2)
    mid_y = center_y + new_radius * math.sin(beta + alpha/2)
    new_beta = beta + alpha
    return (center_x, center_y, new_vertex_x, new_vertex_y, mid_x, mid_y, new_beta)


def addArc(center_x, center_y, v1_x, v1_y, v12_x, v12_y, v2_x, v2_y, construction):
    global arcN, arcLength
    #print(f'Arc {arcN} {center_x}, {center_y} | {v1_x}, {v1_y} | {v2_x} {v2_y}')
    if construction:
        geomListConArc.append(Part.Arc(Vector(v1_x, v1_y, 0.), Vector(v12_x, v12_y, 0.), Vector(v2_x, v2_y, 0.)))
    else:
        geomListArc.append(Part.Arc(Vector(v1_x, v1_y, 0.), Vector(v12_x, v12_y, 0.), Vector(v2_x, v2_y, 0.)))
        arc= geomListArc[-1].length()
        arcLength += arc
        #print(f'Arc {arc}')
    arcN += 1
    
def addLine(v1_x, v1_y, v2_x, v2_y, construction):
    global lineN
    #print(f'Line {lineN}  {v1_x}, {v1_y} | {v2_x}, {v2_y}')
    geomListLine.append(Part.LineSegment(Vector(v1_x, v1_y, 0.), Vector(v2_x, v2_y, 0.)))
    lineN += 1

geomListLine =[]
geomListConArc =[]
geomListArc = []
conList = []

arcN = 0
lineN = 0
arcLength = 0.
lineLength = 0.
sketch = App.ActiveDocument.getObject(sketchName)
noOfExistingConstraints =len(sketch.Constraints) 
if useA:
    A_rad = A * math.pi/180
else:
    A_rad = curveLength*(1/R1 + 1/R2)/2

alphas = [((1-i/N)/R1 + (i/N)/R2)/(1/R1 + 1/R2) * 2* A_rad/N for i in range(N+1)]
d = 2 * R1 * math.sin(alphas[0]/2) #chord lengths
v1_x = R1 * math.cos(alphas[0]/2)
v1_y = R1 * math.sin(alphas[0]/2)
v12_x = R1 * math.cos(alphas[0]/4)
v12_y = R1 * math.sin(alphas[0]/4)
#beginning half-arcs
addArc(0. , 0., v1_x, -v1_y, v12_x , -v12_y, R1 , 0, True)
addArc(0. , 0., R1 , 0, v12_x , v12_y, v1_x , v1_y, False)
#first construction line
addLine(v1_x, -v1_y, v1_x, v1_y, True)
lineLength += geomListLine[-1].length()/2.
beta = alphas[0]/2  #cumulative angle from x-axis of radii
#middle arcs and construction lines
for i in range(1, N):
    center_x, center_y, v2_x, v2_y, v12_x, v12_y, new_beta = newarc(v1_x, v1_y, beta, d, alphas[i])
    addLine(v1_x, v1_y, v2_x, v2_y, True)
    lineLength += geomListLine[-1].length()
    addArc(center_x, center_y, v1_x, v1_y, v12_x, v12_y, v2_x, v2_y, False)
    v1_x = v2_x
    v1_y = v2_y
    beta = new_beta
#final half-arcs and last construction line    
'''center_x, center_y, v2_x, v2_y, v12_x, v12_y, beta = newarc(v1_x, v1_y, beta, d, alphas[N]/2)
addArc(center_x, center_y, v1_x, v1_y, v12_x, v12_y, v2_x, v2_y, False)
center_x, center_y, v3_x, v3_y, v23_x, v23_y, beta = newarc(v2_x, v2_y, beta, d, alphas[N]/2)
addArc(center_x, center_y, v2_x, v2_y, v23_x, v23_y, v3_x, v3_y, True)
addLine(v1_x, v1_y, v3_x, v3_y, True)'''
center_x, center_y, v3_x, v3_y, v2_x, v2_y, betajunk = newarc(v1_x, v1_y, beta, d, alphas[N])
rad = math.sqrt((v1_x-center_x)**2 +(v1_y -center_y)**2)
#print(f'rad= {rad}')
v12_x = center_x + rad*math.cos(beta  + alphas[N]/4)
v12_y = center_y + rad*math.sin(beta  + alphas[N]/4)
v23_x = center_x + rad*math.cos(beta  + 3*alphas[N]/4)
v23_y = center_y + rad*math.sin(beta  + 3*alphas[N]/4)
addArc(center_x, center_y, v1_x, v1_y, v12_x, v12_y, v2_x, v2_y, False)
addArc(center_x, center_y, v2_x, v2_y, v23_x, v23_y, v3_x, v3_y, True)
addLine(v1_x, v1_y, v3_x, v3_y, True)
lineLength += geomListLine[-1].length()/2.
#set up constraints
geoIndicesLine = sketch.addGeometry(geomListLine,True)
geoIndicesConArc =sketch.addGeometry(geomListConArc,True)
geoIndicesArc = sketch.addGeometry(geomListArc,False)
alphadeg = [x*180/math.pi for x in alphas]
#print(f'angles {alphadeg}')
#construction chords equal  (arcs become equal as N-> infty)
for i in range(1,N+1):
    conList.append(Sketcher.Constraint('Equal',geoIndicesLine[0],geoIndicesLine[i]))
for i in range(0,N):
    conList.append(Sketcher.Constraint(
                'Coincident', geoIndicesLine[i],2, geoIndicesLine[i+1],1))
#arcs all tangent
conList.append(Sketcher.Constraint('Tangent', geoIndicesConArc[0],2, geoIndicesArc[0],1))
for i in range(0, N):
    conList.append(Sketcher.Constraint(
                'Tangent', geoIndicesArc[i],2, geoIndicesArc[i+1],1)) 
conList.append(Sketcher.Constraint('Tangent', geoIndicesArc[N],2, geoIndicesConArc[1],1))  
#lines all coincident
conList.append(Sketcher.Constraint('Coincident',geoIndicesLine[0],1,geoIndicesConArc[0],1))
for i in range(0,N):
    conList.append(Sketcher.Constraint('Coincident', geoIndicesLine[i], 2, geoIndicesArc[i],2))
conList.append(Sketcher.Constraint('Coincident',geoIndicesLine[N],2,geoIndicesConArc[1],2))
#set arc angles
conList.append(Sketcher.Constraint('Angle', geoIndicesConArc[0],alphas[0]/2))
conList.append(Sketcher.Constraint('Angle', geoIndicesArc[0],alphas[0]/2))
for i in range(1,N):
    conList.append(Sketcher.Constraint('Angle', geoIndicesArc[i],alphas[i]))
conList.append(Sketcher.Constraint('Angle', geoIndicesArc[N],alphas[N]/2))
conList.append(Sketcher.Constraint('Angle', geoIndicesConArc[1],alphas[N]/2))
#half-arcs equal radii
conList.append(Sketcher.Constraint('Equal', geoIndicesConArc[0], geoIndicesArc[0]))
conList.append(Sketcher.Constraint('Equal', geoIndicesConArc[1], geoIndicesArc[N]))
#set radius constraint smaller of R1 and R2
if R1 < R2:
    conList.append(Sketcher.Constraint('Radius',geoIndicesConArc[0], App.Units.Quantity(str(R1) + 'mm')))
else:
    conList.append(Sketcher.Constraint('Radius',geoIndicesConArc[1], App.Units.Quantity(str(R2) + 'mm')))
sketch.addConstraint(conList)
if R1 < R2:
    sketch.renameConstraint(len(sketch.Constraints)-1,str(len(sketch.Constraints))+ ' EulerR1')
else:
    sketch.renameConstraint(len(sketch.Constraints)-1,str(len(sketch.Constraints))+ ' EulerR2')
for i in range(noOfExistingConstraints, noOfExistingConstraints + len(conList)-1):
    sketch.setVirtualSpace(i, True)
#sketch.toggleActive(noOfExistingConstraints + len(conList) - 1)
#start curve at origin
sketch.addConstraint(Sketcher.Constraint('Coincident', -1, 1, geoIndicesArc[0],1))
sketch.renameConstraint(len(sketch.Constraints)-1, str(len(sketch.Constraints))+' EulerOrigin')
print(f'Actual arcLength= {arcLength} Desired = {2*A_rad/(1/R1 + 1/R2)}  Total Chord Length = {lineLength}')
