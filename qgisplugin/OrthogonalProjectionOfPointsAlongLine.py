from qgis.core import QgsProcessingParameterFeatureSource
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessing
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameters
from qgis.core import QgsProcessingParameterField
from qgis.core import QgsProcessingParameterFileDestination
from qgis.core import QgsProcessingParameterNumber
from qgis.core import QgsGeometryUtils
from qgis.core import QgsPoint
from qgis.core import QgsPointXY
from qgis.core import QgsGeometry

import math

import processing
from console import console

        
def calcDistance(x1, y1, x2, y2):
    """
    Pathgorean formula applied to two x-y point pairs.
    """
    return math.sqrt((x2-x1)**2+(y2-y1)**2)

def projectPoint(verticies, pointGeometry, maxOffset):
    """
    This algorithm takes a list of verticies, a point, and a maximum offset. The function itterates through all the segments defined by the verticies and finds the closest orthogonal location.
    Interior verticies are also checked for distance and used if the distance, no matter the angle, is closer to the vertex. If the distance is less than the maxOffset the function returns the offset,
    closest point on the geometry, and the segement that point is located.
    
    param: verticies is a list that contains the verticies from the line geometry
    param: pointGeometry is a QgsPoint geometry for the point of interest
    param: maxOffset is the maximum offset to return data for.
    """
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

class OrthogonalProjectionOfPointsAlongLine(QgsProcessingAlgorithm):

        
    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSource('AlignmentLines', 'Alignment Lines', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterField('LineName','Attribute with Alignment Name', defaultValue=None, parentLayerParameterName='AlignmentLines',type=QgsProcessingParameterField.String,allowMultiple=False))
        self.addParameter(QgsProcessingParameterFeatureSource('SurveyPoints', 'Survey Points', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterField('Description','Attribute with Point Description', defaultValue=None, parentLayerParameterName='SurveyPoints',type=QgsProcessingParameterField.String,allowMultiple=False))
        self.addParameter(QgsProcessingParameterField('PN','Attribute with Point Number', defaultValue=None, parentLayerParameterName='SurveyPoints',type=QgsProcessingParameterField.Numeric,allowMultiple=False))
        self.addParameter(QgsProcessingParameterField('Ele','Attribute with Elevation', defaultValue=None, parentLayerParameterName='SurveyPoints',type=QgsProcessingParameterField.Numeric,allowMultiple=False))
        self.addParameter(QgsProcessingParameterNumber('MaxOffset', 'Maximum offset', defaultValue=99999, type=QgsProcessingParameterNumber.Double, minValue=0))
        self.addParameter(QgsProcessingParameterFileDestination(name='outfile', description='Output Filename', createByDefault=True))
        
    
    def processAlgorithm(self, parameters, context, model_feedback):
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        pointLayer = self.parameterAsVectorLayer(parameters,'SurveyPoints',context)
        
        
        lineLayer = self.parameterAsVectorLayer(parameters,'AlignmentLines',context)
        lineFeatures = lineLayer.getFeatures()
        
        nameAttributeField= self.parameterAsString(parameters, 'LineName',context)
        descriptionAttributeField= self.parameterAsString(parameters, 'Description',context)
        pnAttributeField = self.parameterAsString(parameters, 'PN',context)
        eleAttributeField = self.parameterAsString(parameters, 'Ele', context)
        
        outfileName = self.parameterAsString(parameters, 'outfile', context)
        maxOffset = self.parameterAsDouble(parameters, 'MaxOffset', context)
        #get the name for the output file.
        #console.show_console()
        try:
            outfile = open(outfileName,"w")
        except OSError:
            print("Could not open outfile", outfile)
            return {}
        outfile.write("Alignment, Point Number, Station, Offset, Elevation, Description \n")
        for lineFeature in lineFeatures:
            lineGeom = QgsGeometry(lineFeature.geometry())
            lineName = lineFeature.attribute(nameAttributeField)
            if(lineGeom.isMultipart()):
                verticies = lineGeom.asMultiPolyline()[0]
                #model_feedback.pushInfo("Multipart geometry detected using first part in multipart geometry. Additional parts will be ignored")
            else:
                verticies = lineGeom.asPolyline()
            vertex_m = [] #Create an empty list for this
            n = len(verticies)
            print("vertex count " + str(n))
            vertex_m.append(0) #Add the first virtex
            if(n<2):
                continue
            i = 1
            for i in range(1,n):
                StX = verticies[i-1].x()
                StY = verticies[i-1].y()
                EdX = verticies[i].x()
                EdY = verticies[i].y()
                distance = math.sqrt((EdX-StX)**2+(EdY-StY)**2)
                vertex_m.append(vertex_m[i-1] + distance)
            pointFeatures = pointLayer.getFeatures()
            for pointFeature in pointFeatures:
                pointDescription = pointFeature.attribute(descriptionAttributeField)
                pn = pointFeature.attribute(pnAttributeField)
                elevation = pointFeature.attribute(eleAttributeField)
                #Calulate the distance
                pointGeometry = pointFeature.geometry().asPoint()
                offset, xInt, yInt, segment = projectPoint(verticies, pointGeometry, maxOffset)
                
                #point, vertex index before, vertex index after, sqrDistance
                if offset is None:
                    outfile.write(lineName + ", " + str(pn) + ", " + "Out of Range" + ", " + "Out of Range" + ", " + str(elevation) + ", " + pointDescription + "\n")
                else:
                    dist = calcDistance(verticies[segment-1].x(), verticies[segment-1].y(),xInt, yInt)
                    station = vertex_m[segment-1] + dist
                    outfile.write(lineName + ", " + str(pn) + ", " + str(station) + ", " + str(offset) + ", " + str(elevation) + ", " + pointDescription + "\n")
            verticies.clear()
            vertex_m.clear()
            n = 0
            
        outfile.close()
        return {}

    
    def name(self):
        return 'OrthogonalProjectionOfPointsAlongLine'

    def displayName(self):
        return 'Orthogonal Projection Of Points Along Line'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return OrthogonalProjectionOfPointsAlongLine()
