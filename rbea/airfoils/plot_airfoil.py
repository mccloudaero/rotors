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
cm_data = airfoil[:,4]

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
 fig, axes_array = plt.subplots(3,sharex=True)
 axes_array[0].plot(alpha_data,cd_data,'o-',label='drag')
 axes_array[0].set_title('Drag')
 axes_array[1].plot(alpha_data,cl_data,'o-',label='lift')
 axes_array[1].set_title('Lift')
 axes_array[2].plot(alpha_data,lift2drag_data,'o-',label='lift to_drag')
 axes_array[2].set_title('Lift to Drag')
 plt.show()
 
 # CM
 torque_fig = plt.figure()
 axes = torque_fig.add_subplot(111)
 sc = axes.scatter(alpha_data,cm_data,c=mach_data,vmin=0.3,vmax=0.5)
 torque_fig.colorbar(sc)
 axes.grid(True)
 axes.set_xlabel('Alpha (deg)')
 axes.set_ylabel('Pitch Coefficient')
 axes.set_ylim(-0.1,0.1)
 # Title
 torque_fig.text(0.2,0.8, airfoil_name, fontsize=20)
 plt.show()


else:
 # Multiple Mach Numbers prsent, Create 2D splines
 airfoil_data_type = '2D'
 cd_spline = scipy.interpolate.bisplrep(mach_data,alpha_data,cd_data)
 cl_spline = scipy.interpolate.bisplrep(mach_data,alpha_data,cl_data)

 # Plot 3D Data
 drag_fig = plt.figure()
 axes = drag_fig.add_subplot(111, projection='3d')
 axes.scatter(mach_data,alpha_data,cd_data)
 plt.show()

 lift_fig = plt.figure()
 axes = lift_fig.add_subplot(111, projection='3d')
 axes.scatter(mach_data,alpha_data,cl_data)
 plt.show()

 lift2drag_fig = plt.figure()
 axes = lift2drag_fig.add_subplot(111, projection='3d')
 axes.scatter(mach_data,alpha_data,lift2drag_data)
 plt.show()

 # CM
 torque_fig = plt.figure()
 axes = torque_fig.add_subplot(111)
 sc = axes.scatter(alpha_data,cm_data,c=mach_data,vmin=0.3,vmax=0.5)
 cbar = torque_fig.colorbar(sc)
 cbar.ax.set_ylabel('Mach')
 axes.grid(True)
 axes.set_xlabel('Alpha (deg)')
 axes.set_ylabel('Moment Coefficient')
 axes.set_ylim(-0.02,0.02)
 # Title
 torque_fig.text(0.2,0.8, airfoil_name, fontsize=20)
 plt.show()

 