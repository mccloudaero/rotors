# Code to optimize G-code Files for Rotor Blades
input_filename = 'input.nc'
output_filename = 'output.nc'

# Read input file
print 'Reading:',input_filename
input_file = open(input_filename,'r')
input_code = []
for line in input_file:
 input_code.append(line.strip())
input_file.close()
lines = len(input_code)
print 'Total Number of Lines in Input File:',lines

# Process input code
print 'Processing Input Code'
i = 0
count = 0
while i < lines:
 line = input_code[i]
 if line == 'X0.0000':
  # Check Line Before
  last_line = input_code[i-1]
  last_z = float(last_line.split('Z')[1])
  if last_z == -1.7508:
   # Tool Bit on Floor, Check line after
   line_after = input_code[i+1]
   if 'Y' in line_after:
	input_code[i] = input_code[i+2]
	input_code.pop(i+2)
	count += 1
 elif line == 'X36.0000':
  # Check Line Before
  last_line = input_code[i-1]
  last_z = float(last_line.split('Z')[1])
  if last_z == -1.7508:
   # Tool Bit on Floor, Check line after
   line_after = input_code[i+1]
   if 'Y' in line_after:
	input_code[i] = input_code[i+2]
	input_code.pop(i+2)
	count += 1
 lines = len(input_code)
 i += 1
print 'lines removed',count
 
# Output Cleaned File
print 'Writing Optimized Code'
output_file =  open(output_filename,'w')
for line in input_code:
 output_file.write(line+'\n')
output_file.close()