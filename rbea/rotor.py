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

# Airfoil Aerodynamic Coefs
# If using an Airfoil other than the NACA 2412, simply replace this function one tailored to the
# new airfoil
def airfoil_coef(alpha):
 # Linear Behaviour
 cl=0.25 + 5.93*alpha  	# lift coefficient NACA 2412
 # Non-Linear Behaviour
 if(cl > 1.43):
   cl = 5612.93*pow(alpha,4)-5694.98*pow(alpha,3) + 2077.74*pow(alpha,2) - 321.77*alpha + 19.19  
 #if(cl < -0.8):
 #  cl = -9822.62*pow(alpha,4)-9110.65*pow(alpha,3) - 3065.66*pow(alpha,2) - 441.54*alpha - 23.8  
 #cd = 0.010 - 0.003*cl + 0.01*cl*cl	# drag coefficient NACA 2412
 cd = 0.001538*pow(cl,4) - 0.0009347*pow(cl,3) + 0.002775*pow(cl,2) - 0.000882*cl + 0.00608	# drag coefficient NACA 2412
 cd = cd*1.2 # Drag Factor
 
 return cl,cd

'''
# 63-212
# Mach 0.4 curves
def airfoil_coef(alpha):
 # Linear Behaviour
 # dCl/dalpha = 0.115 deg = 
 cl=0.15 + 6.589*alpha  	# lift coefficient NACA 2412
 # Non-Linear Behaviour
 if cl > 0.98:
  cl = 0.98
 cd = 0.02
 cd = cd*1.2 # Drag Factor
 
 return cl,cd
'''

pi = math.pi

# Read inputs file
execfile('inputs.txt')

# Read airfoil data
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
 # Multiple Mach Numbers prsent, Create 2D splines
 airfoil_data_type = '2D'
 cd_spline = scipy.interpolate.bisplrep(mach_data,alpha_data,cd_data)
 cl_spline = scipy.interpolate.bisplrep(mach_data,alpha_data,cl_data)

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
total_output.write('RPM\tT(N)\tP(kW)\tT(lbf)\tP(Hp)\tFM\tM_tip\n')
  
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
   if airfoil_data_type == '1D':
    cd = scipy.interpolate.splev(alpha,cd_spline) 
    cl = scipy.interpolate.splev(alpha,cl_spline) 
   elif airfoil_data_type == '2D':
    cd = scipy.interpolate.bisplev(mach,alpha,cd_spline) 
    cl = scipy.interpolate.bisplev(mach,alpha,cl_spline) 
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
   # check to see if iteration stuck
   elif(iter>2000):
    finished=True
  
   # Updates Values
   v_inflow = v_inflow + 0.5*(v_inflow_new-v_inflow)
   #v_swirl = v_inflow + 0.5*(v_swirl_new-v_swirl)    
  
  phi = phi_rad*180/pi
  alpha = alpha_rad[i]*180/pi 
  thrust.append(DtDr*r_inc)
  drag.append(DdDr*r_inc)
  torque.append(DqDr*r_inc)

  #print RPM,i,iter

 # Convert radians to degrees
 radial_output.write('{:d}\t'.format(RPM))
 for i in range(num_elements):
  theta[i] = theta[i]*180/pi
  alpha_rad[i] = alpha_rad[i]*180/pi
  radial_output.write('{:5.3f}\t'.format(alpha_rad[i]))
 radial_output.write('\n')
 
 # Totals
 T = sum(thrust)			# total thrust (N) 
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
 total_output.write('{:d}\t{:5.2f}\t{:5.2f}\t{:5.2f}\t{:5.2f}\t{:5.3f}\t{:5.3f}\n'.format(RPM,T,P,T_imp,P_imp,FM,M_tip))


# Close total_output
total_output.close()
radial_output.close()
