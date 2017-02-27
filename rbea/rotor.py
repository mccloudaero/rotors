import sys
import math
import numpy as np
import scipy.interpolate

# Rotor Blade Element Analysis
# Python Script for determining Rotor Performance using Blade Element Theory

# Definitions
# theta - The physical angle the airfoil is rotated from the plane of rotation
# phi	- The change in flow angle due to the induced airflow.  Makes the angle of attack smaller
# alpha_rad	- The effective angle of attack the airfoil experiences
# alpha_rad + phi = theta

pi = math.pi

# Read inputs file
execfile('inputs.txt')

# Determine airfoil method
try:
 airfoil_name
except:
 # airfoil_name is not defined, see if tip & root airfoil names exist
 try:
  tip_airfoil_name
 except NameError:
  print 'Neither airfoil_name nor tip_airfoil_name in inputs file'
  print 'Exiting!'
  sys.exit(1)
 else:
  # tip_airfoil_name exists, see if root_airfoil_name exists
  try:
   root_airfoil_name
  except:
   print 'root_airfoil_name is not defined in the inputs file'
   print 'Exiting!'
   sys.exit(1)
  else:
   airfoil_type = 'blended' 
else:
 airfoil_type = 'single' 

# Read airfoil data
if airfoil_type == 'single':
 airfoil = np.loadtxt('./airfoils/'+airfoil_name+'.dat',skiprows=1,delimiter=',')
 # Create splines
 mach_data = airfoil[:,0]
 alpha_data = airfoil[:,1]
 cd_data = airfoil[:,2]
 cl_data = airfoil[:,3]
 # Determine Mach Range
 if min(mach_data) == max(mach_data):
  # Single Mach Number present, Create 1D splines
  airfoil_data_type = '1D'
  cd_spline = scipy.interpolate.splrep(alpha_data,cd_data)
  cl_spline = scipy.interpolate.splrep(alpha_data,cl_data)
 else:
  # Multiple Mach Numbers present, Create 2D splines
  airfoil_data_type = '2D'
  cd_spline = scipy.interpolate.bisplrep(mach_data,alpha_data,cd_data)
  cl_spline = scipy.interpolate.bisplrep(mach_data,alpha_data,cl_data)
else:
 # Tip
 airfoil = np.loadtxt('./airfoils/'+tip_airfoil_name+'.dat',skiprows=1,delimiter=',')
 # Create splines
 mach_data = airfoil[:,0]
 alpha_data = airfoil[:,1]
 cd_data = airfoil[:,2]
 cl_data = airfoil[:,3]
 # Determine Mach Range
 if min(mach_data) == max(mach_data):
  # Single Mach Number present, Create 1D splines
  tip_airfoil_data_type = '1D'
  tip_cd_spline = scipy.interpolate.splrep(alpha_data,cd_data)
  tip_cl_spline = scipy.interpolate.splrep(alpha_data,cl_data)
 else:
  # Multiple Mach Numbers present, Create 2D splines
  tip_airfoil_data_type = '2D'
  tip_cd_spline = scipy.interpolate.bisplrep(mach_data,alpha_data,cd_data)
  tip_cl_spline = scipy.interpolate.bisplrep(mach_data,alpha_data,cl_data)

 # Root 
 airfoil = np.loadtxt('./airfoils/'+root_airfoil_name+'.dat',skiprows=1,delimiter=',')
 # Create splines
 mach_data = airfoil[:,0]
 alpha_data = airfoil[:,1]
 cd_data = airfoil[:,2]
 cl_data = airfoil[:,3]
 # Determine Mach Range
 if min(mach_data) == max(mach_data):
  # Single Mach Number present, Create 1D splines
  root_airfoil_data_type = '1D'
  root_cd_spline = scipy.interpolate.splrep(alpha_data,cd_data)
  root_cl_spline = scipy.interpolate.splrep(alpha_data,cl_data)
 else:
  # Multiple Mach Numbers present, Create 2D splines
  root_airfoil_data_type = '2D'
  root_cd_spline = scipy.interpolate.bisplrep(mach_data,alpha_data,cd_data)
  root_cl_spline = scipy.interpolate.bisplrep(mach_data,alpha_data,cl_data)


# Initial Calculations
tip_radius = diameter/2
area = pi*diameter*diameter/4
avg_chord = (root_chord + tip_chord)/2
sigma=2*avg_chord/2/pi/tip_radius			# solidity

# Blade Element Calculation
r_inc = (tip_radius-root_radius)/(num_elements-1)
theta_inc = (tip_theta-root_theta)/(num_elements-1)
chord_inc = (tip_chord-root_chord)/(num_elements-1)

# Initialize lists
radius = []
theta = []
theta_rad = []
alpha_rad = []
chord = []
thrust = []
drag =[]
torque = []

# Initialize total_output file
total_output = open('./output.txt','w')
# Print Data Header
total_output.write('RPM\tT(N)\tP(kW)\tT(lbf)\tP(Hp)\tFM\tM_tip\tv_induced\n')
  
# Initialize total_output file
radial_output = open('./radial_output.txt','w')
# Print Data Header
radial_output.write('i\\RPM\t')
for i in range(num_elements):
 radial_output.write(str(i)+'\t')
radial_output.write('\n')

# Populate radii and theta lists
for i in range(num_elements):
 radius.append(root_radius+i*r_inc)
 chord.append(root_chord+chord_inc)
 theta.append(root_theta+i*theta_inc)
 theta_rad.append(theta[i]/180*pi)
 alpha_rad.append(0)

# Specified Theta
#theta = [18.00, 17.34, 16.68, 16.03, 15.37, 14.71, 14.05, 13.39, 12.74, 12.08, 11.42, 10.76, 10.10, 9.44, 8.79, 8.13, 7.47, 6.82, 6.16, 5.50]
#for i in range(num_elements):
# theta_rad[i] = (theta[i]/180*pi)
#print theta

for RPM in RPMs:
 # Initial Calcs at RPM
 n = RPM/60			# RPS
 omega = n*2*pi			# angular velocity
 V_tip = omega*tip_radius	# tip velocity

 # Initialize/Clear Lists
 thrust = []
 drag =[]
 torque = []

 for i in range(num_elements):
  # Guess at initial values of inflow and swirl factor
  # Note: swirl currently isn't used
  v_inflow = 10
  #v_swirl = 0.1
    
  # Iterate at Each Blade Element
  iter = 0
  finished = False
  while( finished == False):
   v_axial = v_inflow				# axial velocity
   v_radial = omega*radius[i]			# disk plane velocity
   #v_radial = omega*radius[i] - v_swirl	# disk plane velocity
   v_mag = pow((v_axial*v_axial+v_radial*v_radial),0.5)	# local velocity at blade (Resultant of Induced & Radial)
   mach = v_mag/a
   phi_rad = math.atan2(v_axial,v_radial)	# flow angle (radians)
   alpha_rad[i] = theta_rad[i]- phi_rad		# blade angle of attack
   #cl,cd = airfoil_coef(alpha_rad[i])
   alpha = alpha_rad[i]*180/pi
   alpha = min(alpha,12)

   # Find section coefficients
   if airfoil_type == 'single':
    if airfoil_data_type == '1D':
     cd = scipy.interpolate.splev(alpha,cd_spline) 
     cl = scipy.interpolate.splev(alpha,cl_spline) 
    elif airfoil_data_type == '2D':
     cd = scipy.interpolate.bisplev(mach,alpha,cd_spline) 
     cl = scipy.interpolate.bisplev(mach,alpha,cl_spline) 
   else:
    # Tip
    if tip_airfoil_data_type == '1D':
     tip_cd = scipy.interpolate.splev(alpha,tip_cd_spline) 
     tip_cl = scipy.interpolate.splev(alpha,tip_cl_spline) 
    elif tip_airfoil_data_type == '2D':
     tip_cd = scipy.interpolate.bisplev(mach,alpha,tip_cd_spline) 
     tip_cl = scipy.interpolate.bisplev(mach,alpha,tip_cl_spline) 
    # Root
    if root_airfoil_data_type == '1D':
     root_cd = scipy.interpolate.splev(alpha,root_cd_spline) 
     root_cl = scipy.interpolate.splev(alpha,root_cl_spline) 
    elif root_airfoil_data_type == '2D':
     root_cd = scipy.interpolate.bisplev(mach,alpha,root_cd_spline) 
     root_cl = scipy.interpolate.bisplev(mach,alpha,root_cl_spline) 
    # Interpolate cd and cl
    tip_portion = float(i)/(num_elements-1)
    root_portion = float(num_elements-1-i)/(num_elements-1)
    cd = tip_portion*tip_cd + root_portion*root_cd
    cl = tip_portion*tip_cl + root_portion*root_cl

    
   # Appply drag factor
   cd = cd*drag_factor   
   
   q = 0.5*rho*pow(v_mag,2)								# local dynamic pressure
   DtDr = q*blades*chord[i]*(cl*math.cos(phi_rad)-cd*math.sin(phi_rad))			# thrust grading
   DdDr = q*blades*chord[i]*(cd*math.cos(phi_rad)+cl*math.sin(phi_rad))			# drag grading
   DqDr = q*blades*chord[i]*radius[i]*(cd*math.cos(phi_rad)+cl*math.sin(phi_rad))	# torque grading
   
   # momentum check on inflow and swirl factors
   v_inflow_new = DtDr/(4*pi*radius[i]*rho*v_axial)
   #v_swirl_new = DqDr/(4*pi*pow(radius[i],3)*rho*v_axial*omega)
          
   # increment iteration count
   iter += 1
  
   # check for convergence
   if ( math.fabs(v_inflow_new-v_inflow)< 0.001):
    finished = True
   # check to see if iterations are stuck
   elif(iter>maximum_iterations):
    finished=True
    print 'RPM:',RPM,'element:',i,'exceed maximum number of iterations (',maximum_iterations,')'
  
   # Updates Values
   v_inflow = v_inflow + relaxation_factor*(v_inflow_new-v_inflow)
   #v_swirl = v_inflow + 0.5*(v_swirl_new-v_swirl)    
  
  phi = phi_rad*180/pi
  alpha = alpha_rad[i]*180/pi 
  thrust.append(DtDr*r_inc)
  drag.append(DdDr*r_inc)
  torque.append(DqDr*r_inc)

  #print RPM,i,v_inflow

 # Convert radians to degrees
 radial_output.write('{:d}\t'.format(RPM))
 for i in range(num_elements):
  theta[i] = theta[i]*180/pi
  alpha_rad[i] = alpha_rad[i]*180/pi
  radial_output.write('{:5.3f}\t'.format(alpha_rad[i]))
 radial_output.write('\n')
 
 # Totals
 T = sum(thrust)		# total thrust (N) 
 P = sum(torque)*omega/1000	# total power (kW)
 
 # Ideals
 v_ideal = pow((T/(2*rho*pi*pow(tip_radius,2))),0.5) # Ideal Induced Velocity (m/s)
 P_ideal = T*v_ideal/1000 # Ideal Power (kW)
 
 # Compute Coefficients
 ct = T/(rho*n*n*pow(diameter,4))
 cq = sum(torque)/(rho*n*n*pow(diameter,5))

 # Adjust for Tip Loss using Empirical Equations
 B = 1 - pow(2*ct,2)/2
 P = P_ideal/B + (P - P_ideal)
 
 T_imp = T*0.224808943		# N to lbf
 P_imp = P*0.00134102209*1000	# kW to Hp
 
 FM = P_ideal/P
 M_tip = v_mag/a
 total_output.write('{:d}\t{:5.2f}\t{:5.2f}\t{:5.2f}\t{:5.2f}\t{:5.3f}\t{:5.3f}\t{:5.3f}\n'.format(RPM,T,P,T_imp,P_imp,FM,M_tip,v_ideal))

# Close total_output
total_output.close()
radial_output.close()
