import sys
import math
import numpy as np
import scipy.interpolate
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D 

# Airfoil Plot Script 
airfoil_name = 'rc5-10'
#airfoil_name = 'rc6-08'
#airfoil_name = 'naca_2412'

# Read airfoil data
airfoil = np.loadtxt('./'+airfoil_name+'.dat',skiprows=1,delimiter=',')
# Create splines
mach_data = airfoil[:,0]
alpha_data = airfoil[:,1]
cd_data = airfoil[:,2]
cl_data = airfoil[:,3]

lift2drag_data = []
num_values = len(cd_data)
for i in range(num_values):
 lift2drag_data.append(cl_data[i]/cd_data[i])

# Determine Mach Range
mach_values = set(mach_data)

if len(mach_values) == 1:
 # Single Mach Number present, Create 1D splines
 airfoil_data_type = '1D'
 cd_spline = scipy.interpolate.splrep(alpha_data,cd_data)
 cl_spline = scipy.interpolate.splrep(alpha_data,cl_data)

 # Plot Data 
 fig, axis_array = plt.subplots(3,sharex=True)
 axis_array[0].plot(alpha_data,cd_data,'o-',label='drag')
 axis_array[0].set_title('Drag')
 axis_array[1].plot(alpha_data,cl_data,'o-',label='lift')
 axis_array[1].set_title('Lift')
 axis_array[2].plot(alpha_data,lift2drag_data,'o-',label='lift to_drag')
 axis_array[2].set_title('Lift to Drag')
 plt.show() 


else:
 # Multiple Mach Numbers prsent, Create 2D splines
 airfoil_data_type = '2D'
 cd_spline = scipy.interpolate.bisplrep(mach_data,alpha_data,cd_data)
 cl_spline = scipy.interpolate.bisplrep(mach_data,alpha_data,cl_data)

 # Plot 3D Data
 drag_fig = plt.figure()
 axis = drag_fig.add_subplot(111, projection='3d')
 axis.scatter(mach_data,alpha_data,cd_data)
 plt.show()

 lift_fig = plt.figure()
 axis = lift_fig.add_subplot(111, projection='3d')
 axis.scatter(mach_data,alpha_data,cl_data)
 plt.show()

 lift2drag_fig = plt.figure()
 axis = lift2drag_fig.add_subplot(111, projection='3d')
 axis.scatter(mach_data,alpha_data,lift2drag_data)
 plt.show()
