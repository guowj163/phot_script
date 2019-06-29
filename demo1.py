# @Author: zhixiang zhang <zzx>
# @Date:   24-Aug-2017
# @Email:  zhangzx@ihep.ac.cn
# @Filename: demo1.py
# @Last modified by:   zzx
# @Last modified time: 24-Aug-2017


import os
import sys
import glob
import alipy


def save_lst(list_name,contents):
    f=open(list_name,'w')
    contents.sort()
    for content in contents:
        f.write(content+'\n')
    f.close()

namelst = glob.glob("images/*.fits")

if len(namelst) == 0:
    print 'no image will be aligned'
    sys.exit(1)

if os.path.isfile('updatelst'):
    updatefile=open('updatelst','r')
    updatelst=updatefile.readlines()
    updatefile.close()
    save_lst('updatelst',namelst)
    for i in updatelst:
        namelst.remove(i.split()[0])
    images_to_align = sorted(namelst)    
else:
    print 'make a updatelst'
    save_lst('updatelst',namelst)
    images_to_align = sorted(namelst)

ref_image = "ref.fits"

identifications = alipy.ident.run(ref_image, images_to_align, visu=False)
# That's it !
# Put visu=True to get visualizations in form of png files (nice but much slower)
# On multi-extension data, you will want to specify the hdu (see API doc).
# The output is a list of Identification objects, which contain the transforms :
for id in identifications:  # list of the same length as images_to_align.
    if id.ok == True:  # i.e., if it worked
        print "%20s : %20s, flux ratio %.2f" % (id.ukn.name, id.trans, id.medfluxratio)
        # id.trans is a alipy.star.SimpleTransform object. Instead of printing it out as a string,
        # you can directly access its parameters :
        # print id.trans.v # the raw data, [r*cos(theta)  r*sin(theta)  r*shift_x  r*shift_y]
        # print id.trans.matrixform()
        # print id.trans.inverse() # this returns a new SimpleTransform object
    else:
        print "%20s : no transformation found !" % (id.ukn.name)


# Minimal example of how to align images :
outputshape = alipy.align.shape(ref_image)

# This is simply a tuple (width, height)... you could specify any other shape.
for id in identifications:
    if id.ok == True:
        # Variant 1, using only scipy and the simple affine transorm :
        # alipy.align.affineremap(id.ukn.filepath, id.trans, shape=outputshape, makepng=True)

        # Variant 2, using geomap/gregister, correcting also for distortions :
        alipy.align.irafalign(id.ukn.filepath, id.uknmatchstars,
                              id.refmatchstars, shape=outputshape, makepng=True)
        # id.uknmatchstars and id.refmatchstars are simply lists of corresponding Star objects.

        # By default, the aligned images are written into a directory "alipy_out".

# To be continued ...

sys.exit(0)





