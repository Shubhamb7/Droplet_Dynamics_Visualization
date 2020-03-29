import xarray as xr
from collections import OrderedDict
import os

#give pathways for the directories
eulrdir = "/lus/dal/hpcs_rnd/RAIT_IITM/Data_Visualization/DNS_Data_Visualization/Data/1m_data/Eul_data/"
destdir = "/lus/dal/hpcs_rnd/RAIT_IITM/Data_Visualization/DNS_Data_Visualization/Data/1m_data/Eul_MixingRatio_data/"

#get list of all the netcdf files
files = sorted([x for x in os.listdir(eulrdir) if x.endswith('.nc')])

#start and stop depending on which file to begin and end
start = 0
stop = len(files)
stride = 2

for i in range(start,stop):

  eulrfile = os.path.join(eulrdir,files[i])
  destfile = os.path.join(destdir,files[i])
  
  data = xr.open_dataset(eulrfile)
  
  zindices, yindices, xindices = [data[dim].astype(int)[::stride] for dim in ('z', 'y', 'x')]
  
  coords = OrderedDict([('z', zindices),('y', yindices),('x', xindices)])
  
  newdata = xr.Dataset(coords=coords)
      
  dims = ['z', 'y', 'x']
  
  #Extract mixing ratio
  variables = [v for v in data.variables if v in ('mixing_ratio')]
  
  for variable in variables:
      tempdata = data[variable][::stride,::stride,::stride]
      newdataarray = xr.DataArray(tempdata.astype('float64'),
              dims=dims, coords=coords)
  
      newdata.update({variable: newdataarray})
      newdata[variable].encoding['_FillValue'] = False
  
      print(variable,newdata[variable].shape, newdata[variable].dtype) ##info
  
  newdata.x.encoding['_FillValue'] = False
  newdata.y.encoding['_FillValue'] = False
  newdata.z.encoding['_FillValue'] = False
  
  print(newdata, '\n\n')
  
  # write netcdf file
  newdata.to_netcdf(path=destfile,format='NETCDF4_CLASSIC')