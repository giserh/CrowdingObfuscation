#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Schei008
#
# Created:     04/09/2018
# Copyright:   (c) Schei008 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import shapely
from shapely import geometry
from shapely.geometry import Point
import matplotlib.pyplot as plt
import random
import time
import math
from random import randint
import Queue as Q

import georasters as gr
#see https://github.com/ozak/georasters
import pyproj
#see https://github.com/jswhit/pyproj
from shapely.ops import transform
from shapely.geometry import shape


from scipy import stats


fig, ax = plt.subplots()

# set aspect to equal. This is done automatically
# when using *geopandas* plot on it's own, but not when
# working with pyplot directly.
ax.set_aspect('equal')


"""Functions for rasterization"""

def Rasterize(track,m):
    print('Size of original track:'+str(track.size))
    lookup = track.apply(lambda p: (np.round(p.x/m)*m, np.round(p.y/m)*m) )
    rt = pd.DataFrame({'points': lookup.unique()})
    print("lookup table:")
    lookup = lookup.apply(lambda (x,y): Point(x, y) )
    print lookup

    rt['geom'] = rt['points'].apply(Point)

    rastertrack = gpd.GeoDataFrame(rt, geometry='geom')['geom']
    #Point(np.round(p.x/m)*m, np.round(p.y/m)*m)

    print("rasterized track:")
    print rastertrack
    return lookup,rastertrack



"""Functions for mimicking track extension"""

#Spatial vector operations
def Vminus(p1, p2):
    return Point(p1.x - p2.x, p1.y - p2.y)

def Vplus(p1, p2):
    return Point(p1.x + p2.x, p1.y + p2.y)

def Vmult(m, p):
    return Point(p.x*m, p.y*m)

#Generating differences vector list and set in track sequence
def getV(track):
    #Get the vector difference between all pairs of points in the track
     V = [ Vminus(track[i[0]+1], p) for i,p in np.ndenumerate(track.values) if i[0]+1 < track.values.size]
     Vset =[]
     for v in V:
        count = 0
        insert = True
        for vv in Vset:
            if not v.equals(vv):
                insert = True
            else:
                insert = False
                break
        if insert:
            Vset.append(v)
     return  V, Vset

#Genereating distance list for track
def getDistances(track):
    #Returns an array of distances in a sequence of point geometries in the track
   return [x.distance(track[i[0]+1]) for i,x in np.ndenumerate(track.values) if i[0]+1 < track.values.size]
    #print pd.rolling_apply(track, 2,  lambda x: Point(x[0]["X"],x[0]['Y']).distance(Point(x[1]['X'],x[1]['Y'])))


#Computing movement and location probablity
def probability(v,end, V):
    return moveProb(v, V) #* locProb(v,end)


def moveProb(v, V):
    c = 0
    #Count the number of occurrences of this movement in the track
    for vi in V:
        if vi.equals(v):
        #if (vi.x == v.x) & (vi.y == v.y):
            c+=1
    return  float(c)/float(len(V))


"""A function for looking up Raster cell row/colum projected in RD_new, based on a WGS84 coordinate pair as input as well as a Geo raster tile"""
project = lambda x, y: pyproj.transform(pyproj.Proj(init='EPSG:4326'), pyproj.Proj(init='EPSG:28992'), x, y)
def lookupWGS84(x,y,GeoT):
    pass
##    p = shapely.geometry.point.Point(x,y)
##    print(str(p))
##    pn = transform(project, p)
##    print(str(pn))
##    try:
##        # Find location of point (x,y) on raster, e.g. to extract info at that location
##        col, row = gr.map_pixel(pn.x,pn.y,GeoT[1],GeoT[-1], GeoT[0],GeoT[3])
##        #value = gr.map_pixel(pn.x,pn.y, )
##    except:
##        print "Coordinates out of bounds!"
##        return 'NN','NN'
##    return row, col

def locProb(v,end):
    return 0.5
##    BBG2012_Publicatiebestand = 'data\\BBG2012_Publicatiebestand.tif'
##    NDV, xsize, ysize, GeoT, Projection, DataType = gr.get_geo_info(BBG2012_Publicatiebestand)
##    data = gr.load_tiff(BBG2012_Publicatiebestand)
##    s = data.shape
##    rows = s[0]
##    cols = s[1]
##    #load raster data once
##    row, col = lookupWGS84(x, y, GeoT)
##    if row != 'NN' and (row < rows and col < cols):
##                    pass
##    else:
##                    print("Coordinates out of bounds!")



def similarity(track, test):
    return moveSim(track, test)

def moveSim(track, test):
    Vtrack, vsettrack = getV(track)
    #print [str(v) for v in Vtrack]
    Vtest, vsettest = getV(test)
    #print  [str(v) for v in Vtest]

    contingencytable = []
    for v in vsettest:
        #print (str(v)+""+str(moveProb(v, Vtest)) +""+ str(moveProb(v, Vtrack)))
        contingencytable.append([moveProb(v, Vtest) , moveProb(v, Vtrack)])
        #psum += math.pow((moveProb(v, Vtrack) - p2),2)/p2
    #chi = psum * track.size
    print  np.array(contingencytable)
    chi2_stat, p_val, dof, ex = stats.chi2_contingency(np.array(contingencytable))
    print "p_val:"+str(p_val)
    return p_val

## elements = [1.1, 2.2, 3.3]
##probabilities = [0.2, 0.5, 0.3]
##np.random.choice(elements, 10, p=probabilities)


def ExtendMimic(track,p):
    endindex = track.size-1#int(round(float(randint(0,track.size))/float(track.size))*(track.size-1))
    end = track[endindex]
    V, Vset = getV(track)
    faketrack = track
    for i in range(0,randint(1,int(0.7*track.size))):
        #q = Q.PriorityQueue()
        #for v in Vset:
            #print "prob:"+str(probability(v,end, V))
            #q.put((probability(v,end, V)-1,Vplus(end,v)))

        probdist = [probability(v,end, V) for v in Vset]
        #print probdist
        #print Vset
        #while not q.empty():
        for i in range(1,len(Vset)):
            #candidate = q.get()[1]
            #This generates a new point candidate bas on random choice over movement probability
            candidate =  Vplus(end,Vset[np.random.choice(np.arange(len(Vset)), None, p=list(probdist))])
            print candidate
            test = faketrack.copy()
            test.loc[endindex+1] = candidate  # adding a row at the end of the dataframe
            test = test.reset_index(drop=True)  # sorting by index
            if (similarity(track, test) > p) & (candidate not in faketrack):
                print("Extend track with:"+str(candidate))
                faketrack = test
                end = candidate
                endindex =test.size-1
                error = False
                break
            else:
                error = True
        if error:
            print "Error: no sufficnetly similar candidate found!"
    return faketrack



"""Functions for template masking"""

def vNTemplate(r):
    template = []
    for x in range(-r,r+1):
        for y in range(-r,r+1):
            if abs(x) + abs(y) <= r:
                template.append(Point(x,y))
    print [str(p) for p in template]
    return template

def rdmshift(template):
    #This random selection prefers center points sitting at the periphery of the template
    templatedistances = [float(max(abs(p.x),abs(p.y))+1) for p in template]
    templateprobabilities = [d/sum(templatedistances) for d in templatedistances]
    v0 = template[np.random.choice(np.arange(len(template)), None, p=templateprobabilities)]
    template = [Vminus(v, v0) for v in template]
    #print [str(p) for p in template]
    return  template

def apply(vgeo, template,m):
    template = [Vplus(vgeo, Vmult(m,v)) for v in template]
    #print [str(p) for p in template]
    return  template


def Masking(track, m, r, k, d):
    out = []
    Pred = []
    vntemplate = vNTemplate(r)
    for v in track:
        print("Now masking point: "+str(v) )
        #Randomly shift template
        temp = apply(v, rdmshift(vntemplate),m)
        #print temp
        candidates = [vk for vk in temp if vk not in Pred]

        #Mask
        candidates.append(v)
        print [str(p) for p in candidates]
        mask = candidates


        out.extend(mask)
        Pred = mask

    print(str(len(out))+" masked points from originally "+str(track.size))
    outgdf = pointlist2GDF(out)
    return outgdf


def pointlist2GDF(pointlist):
        rt = pd.DataFrame({'points': pointlist})
        outputframe = gpd.GeoDataFrame(rt, geometry='points')['points']
        return outputframe


"""Main crowding function"""
def Crowd(track='data\\301756.csv', k=10, p = 0.02) :
    track['points'] = list(zip(track.X, track.Y))
    track['points']  = track['points'].apply(Point)
    trackgdf = gpd.GeoDataFrame(track, geometry='points')
    trackgdf.crs = {"init": 'epsg:4326'}
    trackgdf = trackgdf.to_crs({"init": 'epsg:28992'})
    trackgdf.to_file(driver = 'ESRI Shapefile', filename = 'track.shp')
    #print trackgdf

    #Maximum distance parameter
    distances = getDistances(trackgdf['points'])
    d = 1.3* max(distances)
    print('the distance parameter is '+str(d))

    #Rounding increment
    m = math.floor(d/(math.sqrt(2 * k/math.pi)))
    print('the rounding increment is '+str(m))

    #Template radius
    r = int(math.ceil((-1 + math.sqrt(1+4*k))/2))
    print('the template radius is '+str(r))


    #Start of the programming logic
    lookup,rastertrack = Rasterize(trackgdf['points'],m)
    #rastertrack.plot(marker='*', color='blue', markersize=5)
    rastertrack.to_file(driver = 'ESRI Shapefile', filename = 'rastertrack.shp')


    faketrack = ExtendMimic(rastertrack,p)
    print faketrack
    #faketrack.plot(marker='*', color='green', markersize=5)
    #plt.show();
    faketrack.to_file(driver = 'ESRI Shapefile', filename = 'faketrack.shp')

    maskedtrack = Masking(faketrack,m, r, k, d)
    maskedtrack.to_file(driver = 'ESRI Shapefile', filename = 'maskedtrack.shp')






    #print df










def main():
##    track='data\\2420.csv'
##    df = pd.read_csv(track)
##    for track, trackdf in df.groupby("track"):
##        trackdf.to_csv('data\\'+str(track)+".csv")
    df = pd.read_csv('data\\332541.csv')
    track = df[['X','Y']]
    Crowd(track)




if __name__ == '__main__':
    main()
