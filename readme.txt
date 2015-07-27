Rotor Design and Build Repository
McCloud Aero Corporation

This repository contains the rotor designs and rotor analysis software created by McCloud Aero Corporation. The specific rotor designs contained in this repository were intended for use with the Goliath gas powered quadcopter, but the rotors could be used for other applications.  Goliath uses four rotors with two rotating clockwise (CW) and two counter-clockwise (CCW).  Any use of the data contained in this repository is without warranty.

==Repository Contents==
 Documentation (this readme.txt file)
 Rotor Blade Element Analysis (RBEA) software (/rbea)
 Alpha Rotor Design and Build Files (/alpha)
  Counter-Clockwise Version (/CCW)
  Clockwise Version (/CW)
 Beta Rotor Design and Build Files  (/beta)
  Counter-Clockwise Version (/CCW)
  Clockwise Version (/CW)
 Crush Plate Designa and Build Files (/common)

== Alpha Rotor ==
The Alpha rotor was the original rotor design used for the Goliath quadcopter. This rotor has been tested approximatly 20 times and experienced thrust loads up to 50 lbs. This rotor has not seen long term testing. The pitch was found to be too large and required too much power at the proper RPM for Goliath. It could be applied to other vehicles.

== Beta Rotor ==
A redesign of the alpha rotor, with the pitch at the tip reduced.  Has not been tested.
 
==Design Files==
Each rotor contains the following Design Files:
 *.AD_PRT		- CAD file, Cubify Design Native CAD format (The software used to design the rotors)
 *.stp			- CAD file, STEP format
 *.igs			- CAD file, IGES format
 *_final.stl		- STL file of the final rotor shape
 *_mill_shape.stl	- STL file of the shape to be milled
 *.png			- Image of the rotor design
 
==Design Process==
The CAD was built using Cubify Design. The STL file was generated using the folowing settings:
 Units: Inches
 Format: ASCII
 Normal Deviation: 2.0 deg
 Surface Deviation: 0.02
 Maximum Cell Size: 0.5

To create the mill shape in the CAD file:
1) Unsuppress the Machine Supports 
2) Unsuppress the Hub Support
3) Unsuppress the Hub Support Mirror
4) Suppress the Mounting Holes
5) Suppress the Center Hole
6) Suppress the Trim Tip

==Toolpath Generation==
The toolpaths contained in this repository were generated using MeshCam (http://www.grzsoftware.com/). The rough steps used to create the toolpaths are below.  Feed Rates and plunge rates were driven by the need to go slower though the birch stiffness present in the propeller blanks.

1) Load mill shape
2) Choose 2-Sided Maching
3) Define Stock Size 38" x 10" x 1.75"
4) Create Top & Bottom Rough Tool Paths with 0.25" diameter tool
 A) Depth per Pass 0.25"
 B) Stepover 0.125"
 C) Feed Rate 60 in/min 
 D) Plunge Rate 10 in/min
 E) Stock to leave 0.05"
5) Create Top and Bottom Finish X Only Tool Paths with 0.25" diameter tool
 A) Stepover 0.0.0833"
 B) Feed Rate 60 in/min 
 C) Plunge Rate 10 in/min
6) Create Top and Bottom Finish X Only Tool Paths with 0.25" diameter tool
 A) Stepover 0.0.0833"
 B) Feed Rate 60 in/min 
 C) Plunge Rate 10 in/min

==Build Process==
For each rotor there are two STL files, one is the milled shape and the second is the final rotor shape. Each rotor is machined out of a 38" x 10" x 1.75" foam block.  The machining region is 36" x 8" x 1.75", leaving an inch extra on each of the side and no extra on the top and bottom. To machine the part double sided accurately, alignment pins are helpful.  To use the pins, the same alignment holes drilled into rotor need to be drilled into the spoil board (if possible).  Dowel rods (1/4" diameter) are used as alignment pins.

Tool bits needed are:
1/4" End Mill  (>=1.75" Long) for the Finishing Passes

==Machining Steps==
1) Machine the Top
 A) Roughing pass: Start with the 1/2" End Mill and run rotor_XXX_top_rough
 B) Finishing pass (X direction): Switch to 1/4" End Mill and run rotor_XXX_top_finish_x_only
 C) Finishing pass (Y direction): Run rotor_XXX_top_finish_y_only
 D) Drill the Alignment Holes: Run rotor_XXX_top_drill_holes
2) Flip the block over and re-mount using the alignment holes and pins
3) Machine the Bottom
 A) Roughing pass: Run rotor_XXX_bottom_rough (Note: roughing stays with 1/4" bit because of the fragile part)
 B) Finishing pass (X direction): Run rotor_XXX_bottom_finish_x_only
 C) Finishing pass (Y direction): Run rotor_XXX_bottom_finish_y_only
