# import the simple module from the paraview
from paraview.simple import *

import os
import math

# disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

#-----------------------------------------------------------------------------

# Variables #

# index to start reading files
start = 0
# number of files
nfiles = 80
# calculate index to stop reading files
stop = start + nfiles

# should existing files be overwritten?
overwrite = False

#---------------------------------------------------------------------------------

# transfer function (color and opacity map)
eulr_transfer_fn_name = 'eulr_gray.8'
lagr_transfer_fn_name = 'Warm to Cool'
# color map ranges
radius_start = 0.
radius_end = 18.
mixing_ratio_start = 0.
mixing_ratio_end = 0.0012

# rotation in degrees per frame (leave None to disable rotaion)
rotation = 1

# set pathways and camera based on domain size
eulrdir = "D:/new_data/eul/"
lagrdir = "D:/new_data/lag/"
imagedir = "D:/new_data/img/"
gaussian_radius = 1.3
camera_start_pos = (-1000, 1300, 3000)
camera_focalpt = (512, 400, 512)

#--------------------------------------------------------------------------------

# get lists of files
eulrfiles = sorted([f for f in os.listdir(eulrdir) if f.endswith('.nc')]) 
lagrfiles = sorted([f for f in os.listdir(lagrdir) if f.endswith('.vtu')]) 

#--------------------------------------------------------------------------------

# Setup #
# get active view
renderView1 = GetActiveViewOrCreate('RenderView')
renderView1.ViewSize = [2555, 1376]

# set up camera
camera = GetActiveCamera()
camera.SetFocalPoint(*camera_focalpt)
camera.SetPosition(*camera_start_pos)
camera.SetViewUp(0, 1, 0)
#-----------------------------------------------------------------------------

# Camera #

rotation_rad = rotation * math.pi / 180.

xfocus, yfocus, zfocus = camera_focalpt
xstart, ystart, zstart = camera_start_pos

xtranslation = xstart - xfocus
ztranslation = zstart - zfocus

start_angle = math.atan2(xtranslation, ztranslation)
camera_radius = (ztranslation**2 + xtranslation**2)**.5

def point(angle, camera_radius):
    # returns z, x
    return (camera_radius * math.cos(angle) + zfocus,
            camera_radius * math.sin(angle) + xfocus)

#-----------------------------------------------------------------------------

# Load Files #

for n in range(start, stop):
    eulrfile = eulrfiles[n]
    lagrfile = lagrfiles[n]
    print('Time Step: {}, Eulerian File: {}, Lagrangian File: {}'.format(
        n, eulrfile, lagrfile))

    eulrfilepath = os.path.join(eulrdir, eulrfile)
    lagrfilepath = os.path.join(lagrdir, lagrfile)
    
    imagefile = 'img.{}.png'.format(
        int(round(float(os.path.splitext(lagrfile)[0].split('.')[1]) / 100.)))
    imagefilepath = os.path.join(imagedir, imagefile)

    if not os.path.exists(eulrfilepath) or not os.path.exists(lagrfilepath):
        print('Eulerian file and/or Lagrangian file not found')
        continue

    # info
    print('Image File: ' + imagefilepath)

    if not overwrite and os.path.exists(imagefilepath):
        print('Image already exists; skipping')
        continue

    #-------------------------------------------------------------------------

    # Load Eulerian Netcdf File #

    # create a new 'NetCDF Reader'
    eulrreader = NetCDFReader(FileName=[eulrfilepath])

    eulrreader.Dimensions = '(z, y, x)'

    # set active source
    SetActiveSource(eulrreader)

    # show data in view
    eulrreaderDisplay = Show(eulrreader, renderView1)

    # change representation type
    eulrreaderDisplay.SetRepresentationType('NVIDIA IndeX')
    eulrreaderDisplay.SetRepresentationType('Volume')

    # set scalar coloring
    ColorBy(eulrreaderDisplay, ('POINTS', 'mixing_ratio'))

    #-------------------------------------------------------------------------

    # Load Lagrangian Vtk File #

    # create a new 'XML Unstructured Grid Reader'
    lagrreader = XMLUnstructuredGridReader(FileName=[lagrfilepath])
    lagrreader.CellArrayStatus = []
    lagrreader.PointArrayStatus = ['radius', 'ID']

    # set active source
    SetActiveSource(lagrreader)

    # show data in view
    lagrreaderDisplay = Show(lagrreader, renderView1)

    # set scalar coloring
    ColorBy(lagrreaderDisplay, ('POINTS', 'radius'))

    # change representation type
    lagrreaderDisplay.SetRepresentationType('Point Gaussian')
    lagrreaderDisplay.GaussianRadius = gaussian_radius
    lagrreaderDisplay.ShaderPreset = 'Plain circle'

    #-------------------------------------------------------------------------

    # Camera And Colorbar Settings #

    # get color transfer function/color maps
    mixing_ratioLUT = GetColorTransferFunction('mixing_ratio')
    radiusLUT = GetColorTransferFunction('radius')

    # get opacity transfer function/opacity maps
    mixing_ratioPWF = GetOpacityTransferFunction('mixing_ratio')
    radiusPWF = GetOpacityTransferFunction('radius')

    # Apply a preset using its name.
    mixing_ratioLUT.ApplyPreset(eulr_transfer_fn_name, True)
    radiusLUT.ApplyPreset(lagr_transfer_fn_name, True)

    # Apply a preset using its name.
    mixing_ratioPWF.ApplyPreset(eulr_transfer_fn_name, True)
    radiusPWF.ApplyPreset(lagr_transfer_fn_name, True)

    # Rescale transfer function
    mixing_ratioLUT.RescaleTransferFunction(mixing_ratio_start, mixing_ratio_end)
    radiusLUT.RescaleTransferFunction(radius_start, radius_end)

    # Rescale transfer function
    mixing_ratioPWF.RescaleTransferFunction(mixing_ratio_start, mixing_ratio_end)
    radiusPWF.RescaleTransferFunction(radius_start, radius_end)

    # get color legend/bar for mixing_ratioLUT in view renderView1
    mixing_ratioLUTColorBar = GetScalarBar(mixing_ratioLUT, renderView1)
    radiusLUTColorBar = GetScalarBar(radiusLUT, renderView1)

    # show color bar/color legend
    eulrreaderDisplay.SetScalarBarVisibility(renderView1, True)
    lagrreaderDisplay.SetScalarBarVisibility(renderView1, True)

    # Properties modified
    mixing_ratioLUTColorBar.LabelFontFamily = 'Courier'
    radiusLUTColorBar.LabelFontFamily = 'Courier'

    mixing_ratioLUTColorBar.Title = 'Mixing Ratio'
    mixing_ratioLUTColorBar.TitleFontFamily = 'Arial'
    radiusLUTColorBar.Title = 'Radius (μm)'
    radiusLUTColorBar.TitleFontFamily = 'Arial'

    mixing_ratioLUTColorBar.TitleFontSize = 12
    radiusLUTColorBar.TitleFontSize = 12

    mixing_ratioLUTColorBar.LabelFontSize = 10
    radiusLUTColorBar.LabelFontSize = 10

    mixing_ratioLUTColorBar.RangeLabelFormat = '%-#7.4'
    radiusLUTColorBar.RangeLabelFormat = '%-#7.4'

    mixing_ratioLUTColorBar.AddRangeAnnotations = 0
    radiusLUTColorBar.AddRangeAnnotations = 0
    #-------------------------------------------------------------------------

    # Rotation #

    if rotation is not None:
        new_angle = start_angle + n * rotation_rad
        print(n, new_angle) ##d
        znew, xnew = point(new_angle, camera_radius)
        print(xnew, ystart, znew) ##d
        camera.SetPosition(xnew, ystart, znew)
    #-------------------------------------------------------------------------

    # Render Image #

    # save screenshot
    SaveScreenshot(imagefilepath, renderView1)

    # delete object after rendering
    # destroy lagrreader
    SetActiveSource(lagrreader)
    Delete(lagrreader)
    del lagrreader
    # destroy eulrreader
    SetActiveSource(eulrreader)
    Delete(eulrreader)
    del eulrreader

    #-------------------------------------------------------------------------


