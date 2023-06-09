import math
from qgis.core import (QgsProcessingFeedback,
					   QgsPoint)

def calcDistance(p1, p2):
	#Simple distance calculator
	return math.sqrt((p2.x()-p1.x())**2+(p2.y()-p1.y())**2)

def computeAngle(V):
	"""Computes the angle from a vector assuming if x is positive the value is between -pi/2 and pi/2 and if x is negative then add pi"""
	if(V[0] != 0):
		theta = math.atan(V[1]/V[0])#this gives us a value between -Pi/2 and Pi/2
	else:
		if(V[1] >0):
			theta = math.pi/2
		else:
			theta = 3*math.pi/2
		if(V[0] < 0):
			theta = theta + math.pi
		if(theta < 0):
			theta = theta + 2* math.pi
	return theta

def isInteriorPoint(point, p1, pmid, p3):
	"""Checks to see if the vector from the midpoint to the point falls between the other two vectors """
	magV1 = calcDistance(pmid, p1)
	magV2 = calcDistance(pmid, p3)
	magVp = calcDistance(pmid, point)
	#Calculate the unit vectors for the lines so the magnitude of each vector is 1
	V1 = [(p1.x()-pmid.x())/magV1, (p1.y()-pmid.y())/magV2]
	V2 = [(p3.x()-pmid.x())/magV2, (p3.y()-pmid.y())/magV2]
	VP = [(point.x()-pmid.x())/magVp, (point.y()-pmid.y())/magVp]
	#Calculate the negative vector
	V1minus = [-1*V1[0], -1*V1[1]]
	V2minus = [-1*V2[0], -1*V2[1]]

	ang1 = computeAngle(V1)
	ang2 = computeAngle(V2)
	angP = computeAngle(VP)

	firstAng = min(ang1, ang2)
	secondAng = max(ang2, ang1)

	if(firstAng-secondAng > math.pi):
		#Then we need to look the other direction
		if(angP < firstAng or angP > secondAng):
			return True
	if(angP>firstAng and angP < secondAng):
		return True
	return False

def projectPoint(verticies, pointGeometry, maxOffset, feedback):
	"""This function itterates through the verticies in a polyline and finds the point nearest to the given point  """
	n=len(verticies)
	minOffset = maxOffset + 1 #A number greater than the maximum distance
	p = QgsPoint(0,0) #picked this because it should be far from any real coordinateses
	segment = 0 #This is one based counting (see i)
		
	for i in range(1,n):
		offset = maxOffset + 1
		St = verticies[i-1]
		Ed = verticies[i]

		if (Ed.x()-St.x()) == 0:
			#Vertical line perpendicular line is horizontal
			x0 = Ed.x()
			y0 = pointGeometry.y()
		elif (Ed.y()-St.y()) == 0:
			#Horizontal line perpendicular line is verticle
			x0 = pointGeometry.x()
			y0 = Ed.y()
		else:
			slope1 = (Ed.y()-St.y())/(Ed.x()-St.x())
			slope2 = (Ed.x()-St.x())/(Ed.y()-St.y())
			
			a1 = slope1
			b1 = -1 #because of the simplification
			c1 = -1*slope1*St.x()+St.y()
			
			a2 = slope2
			b2 = -1 #because of the simplification
			c2 = -1*slope2*pointGeometry.x()+pointGeometry.y()
					
			x0 = (b1*c2-b2*c1)/(a1*b2-a2*b1)
			y0 = (c1*a2-c2*a1)/(a1*b2-a2*b1)
		feedback.pushDebugInfo("x0 " +  str(x0) + " y0 " + str(y0))
		minX = min(St.x(), Ed.x())
		maxX = max(St.x(), Ed.x())
		minY = min(St.y(), Ed.y())
		maxY = max(St.y(), Ed.y())
		#If the point doesn't fall in the perpendicular offset check the end points
		#This checks the points in the middle - it will not check the end points.
		if ((minX > x0) or (x0 > maxX) or (minY > y0) or (y0 > maxY)):
			continue #the perpendicular intesection is not on this line     
		else:
			testP = QgsPoint(x0,y0)
			offset = calcDistance(testP, pointGeometry)
			print("offset" + str(offset))
			if(offset < minOffset):
				minOffset = offset
				p.setX(x0)
				p.setY(y0)
				segment = i-1 #this assignment will let us easily grab the correct segment for staiton calculation
		#check the endpoints
	for j in range(1,n-1):
		Ed = verticies[j]
		St = verticies[j-1]
		offset = calcDistance(Ed,pointGeometry)
		#Check the distance first - simple calculation
		if(offset >= minOffset):
			continue
		if(isInteriorPoint(pointGeometry,St, Ed, verticies[j+1])):
			feedback.pushDebugInfo("Is interior point")
			minOffset = offset
			p.setX(Ed.x())
			p.setY(Ed.y())
			segment = j-1 #this assignment will let us easily grab the correct segment for angle calculations
	if(minOffset >= maxOffset):
		return(None, QgsPoint(0,0), 0)

	feedback.pushDebugInfo("returning point")
	return(minOffset, p, segment)
