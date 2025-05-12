"""
WIPERRtube drop and flight model

Created on Thu Mar 27 19:25:28 2025

@author: graham.mackintosh@nasa.gov

NOTE: This model uses several simplifications, particularly for calculating the terminal velocity
and the dynamics during venting (e.g. neglecting aerodynamic drag during thrust). Results are estimates.
"""

import math
import matplotlib.pyplot as plt

# PHYSICAL AND ENVIRONMENTAL PARAMETERS
water_density = 1000  # kg /m3
g = 9.80665  # m/sec2
pi = math.pi
air_density = 1.0582 # kg/m3 - Typical air density at 5000 feet
temperature = 15  # degrees Celsius
R_specific_air = 287.05  # J/(kg*K)
standard_atmospheric_pressure_pa = 101325  # Pascals
temperature_kelvin = 273.15 + 15 # assumes temp = 15C= 59F
pressure_pa = air_density * R_specific_air * temperature_kelvin
pressure_atm = pressure_pa / standard_atmospheric_pressure_pa

# DESIGN AND OPERATIONAL PARAMETERS
tube_diameter = 0.75  # meters
tube_height = 1.75  # meters
pressure_tube_diameter = 0.5  # meters
pressure_tube_headspace = 0.5  # meters
head_space_pressure = 2600000  # Pascals
dry_mass = 68  # kg  ~ 150 lbs
paddle_width = 0.4  # meters
paddle_length = 0.6  # meters
number_of_paddles = 4
vent_nozzle_diameter = 0.02  # meters
number_of_vents = 6
drop_altitude = 3048  # meters ~10,000 ft
venting_altitude = 340  # meters 

# CALCULATED PARAMETERS
head_space_volume = pi * (pressure_tube_diameter/2)**2 * pressure_tube_headspace    # m^3 cylinder volume of pressurized gas
tube_volume = pi * (tube_diameter/2)**2 * tube_height  # m^3 total volume within the flexible WIPERRtube
water_volume = tube_volume - head_space_volume  # m^3
water_mass = water_volume * water_density  # kg
wet_mass = dry_mass + water_mass  # kg (Total mass at start of drop)
paddle_area = paddle_width * paddle_length * number_of_paddles  # m2 ... downward facing area assuming paddles remain close to horizontal
# simplified terminal velocity assumes constant air density with a value that would be typical at 5000 feet
# and that the WIPERRtube is falling close to vertically 
# and the drag area is calculated be the paddles in a horizontal position plus the bottom surface of the WIPERRtube cylinder
drag_coefficient_area = paddle_area + pi * (tube_diameter / 2)**2 # m2
drag_coefficient = 1.0 # Assume a drag coefficient of 1 for a flat-ish shape
terminal_velocity = math.sqrt((2 * wet_mass * g) / (air_density * drag_coefficient * drag_coefficient_area)) # m/s

# water_exit_velocity: Using Bernoulli's principle P = 0.5 * rho * v^2
# v = sqrt(2 * P_gauge / rho_water)
# Assumes headspace gas pressure is constant and flow is ideal
water_exit_velocity = math.sqrt(2 * head_space_pressure / water_density)  # m/s   
water_mass_ejection_rate = pi * (vent_nozzle_diameter/2)**2 * water_exit_velocity * water_density  # kg / sec (per vent)
total_water_mass_ejection_rate = water_mass_ejection_rate * number_of_vents  # kg / sec (total)
thrust_per_vent = water_mass_ejection_rate * water_exit_velocity  # Newtons (per vent)
total_thrust = thrust_per_vent * number_of_vents  # Newtons (total)

# --- Deceleration Flight Dynamics Calculations ---
# This simplified model neglects aerodynamic drag during the the water venting phase.
# time_to_hover is calculated based on an increasing deceleration during water venting
# due to water venting at the constant rate of total_water_mass_ejection_rate calculated above
time_to_venting = (drop_altitude - venting_altitude) / (0.5 * terminal_velocity) # seconds simplied using constant acceleration to terminal velocity
t = 0
dt = 0.1  # Reduced timestep for better accuracy
current_velocity = terminal_velocity
current_altitude = venting_altitude

# Values for plotting
time_values = []
altitude_values = []
velocity_values = []
water_remaining_values = []
acceleration_values = []

while current_altitude > 0:
    t += dt
    current_mass = wet_mass - total_water_mass_ejection_rate * t
    if current_mass <= dry_mass:
        break  # ran out of water
    
    net_force = total_thrust - current_mass * g
    acceleration = net_force / current_mass
    current_velocity -= acceleration * dt
    current_altitude -= current_velocity * dt
    
    if current_velocity <= 0:  # hover achieved
        break
    
    time_values.append(t)
    altitude_values.append(current_altitude / 10)  # x 10 meters for plot scale normalizing
    velocity_values.append(current_velocity)
    water_remaining_values.append(max(0, current_mass - dry_mass) / 10)  # 10s of kg for plot scale normalizing
    acceleration_values.append(acceleration)
        
water_remaining = (max(0, current_mass - dry_mass))
hover = (current_altitude >= 0 and water_remaining)


# REPORT ON FLIGHT OUTCOME
print(f">>> WIPERRtube DROP - SIMULATION OUTCOME: {"SUCCESS" if hover else "FAIL"}\n")
print(f"WIPERRtube reservoir dimensions :  {tube_diameter:.2f} meters inner diameter, {tube_height:.2f} meters high.")
print(f"\t containing {water_volume:.1f} cubic meters of water ({water_volume * 264.2:.1f} gallons) weighing {water_mass/1000:.1f} metric tons.")
print(f"Freefall flight controlled with {number_of_paddles} paddles measuring {paddle_width} x {paddle_length} meters each.")
print(f"\t for a terminal velocity of {terminal_velocity:.0f} m/s ({terminal_velocity * 2.237:.1f} mph) with air density of {air_density:.2f} kg/m3 ({pressure_atm:.2f} atm)")
print(f"WIPERRtube was dropped at an altitude of {drop_altitude} meters ({drop_altitude * 3.28084:.0f} feet)")
print(f"\t and fell for {time_to_venting:.0f} seconds to an altitude of {venting_altitude} meters ({venting_altitude * 3.28084:.0f} feet) before venting for retrothrust")
print(f"Resevoir headspace pressure maintained at {head_space_pressure/1000} kPa ({head_space_pressure* 0.000145038:.0f} psi) throughout venting phase")
print(f"\t causing a water ejection velocity of {water_exit_velocity:.1f} m/s ({water_exit_velocity * 2.237:.1f} mph) through each venting nozzle of diameter {vent_nozzle_diameter * 100:.1f} cm ({vent_nozzle_diameter * 39.37:.1f} inches)")
print(f"\t ejecting water at a rate of {total_water_mass_ejection_rate:.1f} kg/sec ({total_water_mass_ejection_rate * 0.26:.1f} gallons / sec) in total across all {number_of_vents} vent nozzles")
print(f"\t producing a total deceleration thrust of {total_thrust:.2f} N ( {total_thrust/ 4.44822:.2f} pound-force)")
print(f"\t resulting in a peak deceleration of {acceleration / g:.1f} g.")

if hover:
    print(f"\nWIPERRtube will hover at an altitude of {current_altitude:.2f} meters.")
else:
    print(f"\nWIPERRtube will impact at a velocity of {current_velocity:.2f} m/s. ({current_velocity * 2.237:.1f} mph)")
if water_remaining:
    print(f"\t with {water_remaining:.1f} kg ({water_remaining/ 3.7854:.1f} gallons) of water remaining in the reservoir\n")
else:
    print(f"\t because the water was depleted at an altitude of {current_altitude:.1f} meters({current_altitude * 3.28084:.0f} feet)")
    
# PLOT RESULTS
plt.figure(figsize=(10, 6))
plt.plot(time_values, altitude_values, label="Altitude (x10 m)")
plt.plot(time_values, velocity_values, label="Velocity (m/s)")
plt.plot(time_values, water_remaining_values, label="Water Remaining (x10 kg)")
plt.plot(time_values, acceleration_values, label="Deceleration (m/s²)")
plt.xlabel("Time (s)")
plt.ylabel("Values")
plt.title("WIPERRtube Flight Dynamics")
plt.legend()
plt.grid()
plt.show()
