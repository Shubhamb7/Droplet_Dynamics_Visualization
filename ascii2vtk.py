"""---------------------------------------------------------------------------

Notes:
    This script requires the pyevtk library, currently hoster here:
    https://pypi.org/project/pyevtk/#description

    # add pyevtk to python environment:
    > pip install pyevtk

    # for help:
    > python ascii2vtk.py -h

    # usage:
    > python ${input_directory} ${output_directory} <-n ${stride}>

    Stride arg is optional; subsets the data every n steps

========================================================================== """
from __future__ import division, absolute_import, print_function
import os
import argparse
import numpy as np
from pyevtk.hl import pointsToVTK

# ----------------------------------------------------------------------------

def _config():
    # a helper function to set up command line arguments
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'input_directory',
        help='the input directory containing ascii files')
    parser.add_argument(
        'output_directory',
        help='the output directory for vtk files;' +\
        ' cannot be the same dir as input dir')
    parser.add_argument(
        '-n', '--stride',
        help='subset the data by every n steps',
        type=int,
        default=1)

    args = parser.parse_args()
    kwargs = vars(args)

    return kwargs

# ----------------------------------------------------------------------------

def main(input_directory, output_directory, stride):

    stride_name = '' if stride == 1 else '_stride_{}'.format(stride)
    if not output_directory.endswith(stride_name):
        output_directory += stride_name

    # ensure directories are different so original files are not overwritten    
    if input_directory == output_directory:                                     
        raise ValueError("input and output directories must be different")      
         
    # make output_directory if it doesn't exist yet                             
    try:                                                                        
        os.mkdir(output_directory)                                              
    except FileExistsError:                                                     
        pass                                                                    
                                         
    # get list of netcdf files in directory  
    infiles = [f for f in sorted(os.listdir(input_directory)) if
                f.endswith('.txt')]


    # get number of columns
    with open(os.path.join(input_directory, infiles[0])) as f:
        ncols = len(f.readline().split())


    ## for inname in infiles[start:stop]:
    for inname in infiles:
        # determine file names
        infile = os.path.join(input_directory, inname)
        outname = os.path.splitext(inname)[0]
        outfile = os.path.join(output_directory, outname)

        if os.path.isfile(outfile + '.vtu'):
            print(outname + '.vtu exists') # info
            continue

        print('{} =>\n{}.vtu\n'.format(inname, outname))

        data = np.fromfile(infile, dtype=np.float32, sep=" ")
        data = data.reshape(round(data.size / ncols), ncols)

        # subset if stride > 1
        subdata = data[::stride,:]

        if subdata.size > 0:
            idn, x, y, z, r = [subdata[:,n].flatten() for n in range(ncols)]
            r*=10000
            x, y, z = [n * 10 for n in (x, y, z)]
            pointsToVTK(outfile, x, y, z, data={'radius': r, 'ID': idn})
        else:
            print('no data in range in', outfile) # info

# ----------------------------------------------------------------------------  

if __name__ == '__main__':
    main(**_config())



