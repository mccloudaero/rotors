import math

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
 cd = cd*1.1 # Drag Factor
 
 return cl,cd

pi = math.pi

# Rotor Inputs (metric)
diameter = 0.9144	# meters
blades = 2.0		# number of blades
root_chord = 0.1143	# meters
tip_chord = 0.1016	# meters
root_theta = 20.0	# degrees
tip_theta = 6.0		# degrees
RPMs = [2200,2310,2420,2640,2820,3080,3300,3410,3520,3740,3960]		# rotor speed in RPM

# Atmospheric Inputs
# Note: rho = 1.225 (kg/m3) standard sea level atmosphere density @ 70 F
rho = 1.1644	# Sea level pressure, 30 C

# Initial Calculations
tip_radius = diameter/2
root_radius = 0.1*tip_radius
area = pi*diameter*diameter/4
avg_chord = (root_chord + tip_chord)/2
sigma=2*avg_chord/2/pi/tip_radius			# solidity

# Blade Element Calculation
elements = 20
r_inc = (tip_radius-root_radius)/(elements-1)
theta_inc = (tip_theta-root_theta)/(elements-1)
chord_inc = (tip_chord-root_chord)/(elements-1)

# Initialize lists
radius = []
theta = []
theta_rad = []
alpha_rad = []
chord = []
thrust = []
drag =[]
torque = []

# Populate radii and theta lists
for i in range(elements):
 radius.append(root_radius+i*r_inc)
 chord.append(root_chord+chord_inc)
 theta.append(root_theta+i*theta_inc)
 theta_rad.append(theta[i]/180*pi)
 alpha_rad.append(0)

# Print Data Header
print 'RPM\tT(N)\tP(kW)\tT(lbf)\tP(Hp)\tFM'
  
for RPM in RPMs:
 # Initial Calcs at RPM
 n = RPM/60					# RPS
 omega = n*2*pi				# angular velocity
 V_tip = omega*tip_radius	# tip velocity

 # Initialize/Clear Lists
 thrust = []
 drag =[]
 torque = []

 for i in range(elements):
  # Guess at initial values of inflow and swirl factor
  # Note: swirl currently isn't used
  v_inflow = 1
  #v_swirl = 0.1
    
  # Iterate at Each Blade Element
  iter = 0
  finished = False
  while( finished == False):
   v_axial = v_inflow					# axial velocity
   #v_radial = omega*radius[i] - v_swirl	# disk plane velocity
   v_radial = omega*radius[i]	# disk plane velocity
   phi_rad = math.atan2(v_axial,v_radial)	# flow angle (radians)
   alpha_rad[i] = theta_rad[i]- phi_rad		# blade angle of attack
   cl,cd = airfoil_coef(alpha_rad[i])
   
   v_mag = pow((v_axial*v_axial+v_radial*v_radial),0.5)	# local velocity at blade (Resultant of Induced & Radial)
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
   if ( math.fabs(v_inflow_new-v_inflow)< 0.005):
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

 # Convert radians to degrees
 for i in range(elements):
  theta[i] = theta[i]*180/pi
  alpha_rad[i] = alpha_rad[i]*180/pi
 
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
 print RPM,'\t',round(T,2),'\t',round(P,2),'\t',round(T_imp,2),'\t',round(P_imp,2),'\t',round(FM,3)