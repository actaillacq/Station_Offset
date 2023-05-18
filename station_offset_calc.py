def calcDistance(x1, y1, x2, y2):
    return math.sqrt((x2-x1)**2+(y2-y1)**2)

def projectPoint(verticies, pointGeometry, maxOffset):
    n=len(verticies)
    minOffset = maxOffset + 1 #A number greater than the maximum distance
    xInt = 0 #picked this because it should be far from any real coordinates
    yInt = 0 #picked 0 because it should be far from any real coordinates
    segment = 0 #This is one based counting (see i)
        
    for i in range(1,n):
        StX = verticies[i-1].x()
        StY = verticies[i-1].y()
        EdX = verticies[i].x()
        EdY = verticies[i].y()
        if (EdX-StX) == 0:
            #Vertical line perpendicular line is horizontal
            x0 = EdX
            y0 = pointGeometry.y()
        elif (EdY-StY) == 0:
            #Horizontal line perpendicular line is verticle
            x0 = pointGeometry.x()
            y0 = EdY
        else:
            slope1 = (EdY-StY)/(EdX-StX)
            slope2 = (EdX-StX)/(EdY-StY)
            
            a1 = slope1
            b1 = -1 #because of the simplification
            c1 = -1*slope1*StX+StY
            
            a2 = slope2
            b2 = -1 #becasue of the simplification
            c2 = -1*slope2*pointGeometry.x()+pointGeometry.y()
                    
            x0 = (b1*c2-b2*c1)/(a1*b2-a2*b1)
            y0 = (c1*a2-c2*a1)/(a1*b2-a2*b1)

        minX = min(StX, EdX)
        maxX = max(StX, EdX)
        minY = min(StY, EdY)
        maxY = max(StY, EdY)
        #This checks the points in the middle - it will not check the end points.
        if ((minX > x0) or (x0 > maxX) or (minY > y0) or (y0 > maxY)):
            if(i<(n-1)):
                offset = calcDistance(EdX,EdY,pointGeometry.x(), pointGeometry.y())
                if(offset < minOffset):
                    minOffset = offset
                    xInt = EdX
                    yInt = EdY
                    segment = i #this assignment will let us easily grab the correct segment for angle calculations
            continue #the perpendicular intesection is not on this line
                
        offset = calcDistance(x0,y0, pointGeometry.x(), pointGeometry.y())
        print("offset" + str(offset))
        if(offset < minOffset):
            minOffset = offset
            xInt = x0
            yInt = y0
            segment = i #this assignment will let us easily grab the correct segment for angle calculations
    if(minOffset > maxOffset):
        return(None, 0, 0, 0)
    print("Returning a value")
    return(minOffset, xInt, yInt, segment)
