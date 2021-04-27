import cv2
import math

boundary_zone = []
MAX_DISTANCE_TO_ENEMY = 730
# MAX_DISTANCE_TO_ENEMY = 600
MAX_CENTER_DISTANCE = 300
# MAX_CENTER_DISTANCE = 730
DISTANCE_BUFFER = 200
MAX_MAGNITUDE = 50


def distance_eq(coord1, coord2):
    distance = math.sqrt(((coord1[0] - coord2[0]) ** 2) + ((coord1[1] - coord2[1]) ** 2))
    return distance

# Returns the speed and direction caused by the center force
def center_forcev2(curr_coord, center_coord, max_magnitude):
    speed_mag = 0
    dir = 0
    U = 0
    V = 0

    x_bot = curr_coord[0]
    y_bot = curr_coord[1]
    x_center = center_coord[0]
    y_center = center_coord[1]

    y_diff = y_center - y_bot
    x_diff = x_center - x_bot

    if(x_diff == 0):
        dir = 0
    else:
        dir = math.atan(abs(y_diff) / abs(x_diff))

    dir_degrees = math.degrees(dir)
    if(x_diff >= 0 and y_diff >= 0): # Quad 2 # good
        dir_degrees
        # print("QUad 2")
    elif(x_diff > 0 and y_diff < 0): # Quad 3 #good
        dir_degrees *= -1
        # print("QUad 3")
    elif (x_diff < 0 and y_diff < 0): # Quad 4 # good
        dir_degrees += 180
        # print("QUad 4")
    elif (x_diff < 0 and y_diff > 0): # Quad 1
        dir_degrees *= -1
        dir_degrees += 180
        # print("QUad 1")

    print(dir_degrees)
    dir = math.radians(dir_degrees)

    # Chenge this to change the speed mag
    # Changed from 100
    distance_to_center = distance_eq(curr_coord, center_coord)
    if(distance_to_center < DISTANCE_BUFFER):
        speed_mag = 0
    elif (distance_to_center > DISTANCE_BUFFER and distance_to_center < MAX_CENTER_DISTANCE):
        speed_mag = (distance_to_center - DISTANCE_BUFFER) * (max_magnitude / (MAX_CENTER_DISTANCE - DISTANCE_BUFFER))
    else:
        speed_mag = max_magnitude

    # return speed and direction
    return (speed_mag,dir)

# Returns the speed and direction caused by the enemy force(s)
def enemy_forcev2(curr_coord, enemy_coord, max_magnitude):
    speed_mag = 0
    dir = 0
    U = 0
    V = 0

    x_bot = curr_coord[0]
    y_bot = curr_coord[1]
    x_enemy_center = enemy_coord[0]
    y_enemy_center = enemy_coord[1]

    y_diff = y_enemy_center - y_bot
    x_diff = x_enemy_center - x_bot

    if(x_diff == 0):
        dir = 0
    else:
        dir = math.atan(abs(y_diff) / abs(x_diff))

    dir_degrees = math.degrees(dir)
    if(x_diff >= 0 and y_diff >= 0): # Quad 2 # good
        dir_degrees += 180
    elif(x_diff > 0 and y_diff < 0): # Quad 3 #good
        dir_degrees *= -1
        dir_degrees += 180
    elif (x_diff < 0 and y_diff < 0): # Quad 4 # good
        dir_degrees
    elif (x_diff < 0 and y_diff > 0): # Quad 1
        dir_degrees *= -1

    dir = math.radians(dir_degrees)

    distance_to_enemy = distance_eq(curr_coord, enemy_coord)

    # Chenge this to change the speed mag
    # Changed from 100
    if(distance_to_enemy < DISTANCE_BUFFER):
        speed_mag = max_magnitude
    elif(distance_to_enemy >= DISTANCE_BUFFER and distance_to_enemy < MAX_DISTANCE_TO_ENEMY):
        speed_mag = max_magnitude + (distance_to_enemy - DISTANCE_BUFFER) * (-1 * (max_magnitude / (MAX_DISTANCE_TO_ENEMY - DISTANCE_BUFFER)))
    else:
        speed_mag = 0

    speed_mag = abs(speed_mag)
    # return speed and direction
    return (speed_mag,dir)

# Function used to move towards the current boundary coord
def boundary_forcev2(curr_coord, boundary_coord, max_magnitude):
    speed_mag = 0
    dir = 0
    U = 0
    V = 0

    x_bot = curr_coord[0]
    y_bot = curr_coord[1]
    x_center = boundary_coord[0]
    y_center = boundary_coord[1]

    y_diff = y_center - y_bot
    x_diff = x_center - x_bot

    if(x_diff == 0):
        dir = 0
    else:
        dir = math.atan(abs(y_diff) / abs(x_diff))

    dir_degrees = math.degrees(dir)
    if(x_diff >= 0 and y_diff >= 0): # Quad 2 # good
        dir_degrees
        # print("QUad 2")
    elif(x_diff > 0 and y_diff < 0): # Quad 3 #good
        dir_degrees *= -1
        # print("QUad 3")
    elif (x_diff < 0 and y_diff < 0): # Quad 4 # good
        dir_degrees += 180
        # print("QUad 4")
    elif (x_diff < 0 and y_diff > 0): # Quad 1
        dir_degrees *= -1
        dir_degrees += 180
        # print("QUad 1")

    # print(dir_degrees)
    dir = math.radians(dir_degrees)

    # Chenge this to change the speed mag
    # Changed from 100
    distance_to_center = distance_eq(curr_coord, boundary_coord)
    if(distance_to_center < DISTANCE_BUFFER):
        speed_mag = 0
    elif (distance_to_center > DISTANCE_BUFFER and distance_to_center < MAX_CENTER_DISTANCE):
        speed_mag = (distance_to_center - DISTANCE_BUFFER) * (max_magnitude / (MAX_CENTER_DISTANCE - DISTANCE_BUFFER))
    else:
        speed_mag = max_magnitude


    # return speed and direction
    return (speed_mag,dir)


# Function to find the center point of a set of boundary coordinates
def find_center_point(boundary_points):
    size = len(boundary_points)
    sum_x = 0
    sum_y = 0
    i = 0
    for i in range(size):
        sum_x += boundary_points[i][0]
        sum_y += boundary_points[i][1]

    center_x = sum_x / size
    center_y = sum_y / size
    return (center_x, center_y)

# Calculate the total forces based on where the TAG Bot is and where the enemy is
def getForces(curr_coord, enemy_coords, boundary, image, max_magnitude):
    net_enemy_force_x = 0
    net_enemy_force_y = 0
    x_bot = curr_coord[0]
    y_bot = curr_coord[1]
    center_direction = 0
    enemy_directions = 0
    total_direction = 0
    count_enemies = 0
    center_force_used = 0

    magnitude = 0
    direction = 0

    total_forces = []

    # Find the center point
    if(len(boundary) > 0):
        center_force_used = 1
        center_x, center_y = find_center_point(boundary)
        center_coord = (int(center_x), int(center_y))

        x_center = center_coord[0]
        y_center = center_coord[1]

        cv2.circle(image, center_coord, 10, (0, 0, 255), -1)

        # Draw an arrow towards the center
        if (distance_eq(center_coord, curr_coord) > 50):
            (magnitude, direction) = center_forcev2(curr_coord, center_coord, max_magnitude)
            total_forces.append((magnitude, direction))
            if (math.degrees(center_direction) < 0):
                center_direction += 2 * math.pi
            # total_direction += center_direction
            end_point_offset = (int(magnitude * math.cos(direction)), int(magnitude * math.sin(direction)))
            end_point = (curr_coord[0] + end_point_offset[0], curr_coord[1] + end_point_offset[1])
            cv2.arrowedLine(image, curr_coord, end_point, (0, 0, 255), 5)

    x_enemies = 0
    y_enemies = 0
    for enemy_coord in enemy_coords:
        x_enemy = curr_coord[0]
        y_enemy = curr_coord[1]

        # Draw an arrow away from the enemy
        if (distance_eq(enemy_coord, curr_coord) < 10000):
            (magnitude, direction) = enemy_forcev2(curr_coord, enemy_coord, max_magnitude)
            if(math.degrees(direction) < 0):
                #enemy_direction =  math.radians(math.degrees(enemy_direction) + 360)
                direction += 2 * math.pi
            # total_direction += direction
            # enemy_directions += direction
            total_forces.append((magnitude, direction))

            count_enemies += 1
            end_point_offset = (int(magnitude * math.cos(direction)), int(magnitude * math.sin(direction)))
            end_point = (curr_coord[0] + end_point_offset[0], curr_coord[1] + end_point_offset[1])
            cv2.arrowedLine(image, curr_coord, end_point, (0, 255, 0), 5)

    net_x_force = 0
    net_y_force = 0
    for force in total_forces:
        mag = force[0]
        dir = force[1]
        x_force = mag * math.cos(dir)
        y_force = mag * math.sin(dir)

        net_x_force += x_force
        net_y_force += y_force

    net_magnitude = math.sqrt(net_x_force ** 2 + net_y_force ** 2)
    if(net_x_force != 0):
        net_direction = math.atan(abs(net_y_force) / abs(net_x_force))

        if(net_x_force > 0 and net_y_force > 0): # Quad 2
            net_direction
        elif(net_x_force < 0 and net_y_force > 0): # Quad 1
            net_direction *= -1
            net_direction += 3*math.pi
        elif (net_x_force < 0 and net_y_force < 0): # Quad 4
            net_direction += math.pi
        elif (net_x_force > 0 and net_y_force < 0): # Quad 3
            net_direction *= -1
            net_direction += 2*math.pi
    else:
        net_direction = 0

    end_point_offset = (int(net_magnitude * math.cos(net_direction)), int(net_magnitude * math.sin(net_direction)))
    end_point = (curr_coord[0] + end_point_offset[0], curr_coord[1] + end_point_offset[1])
    cv2.arrowedLine(image, curr_coord, end_point, (255,0,0), 5)
    print("Center Direction: " + str(math.degrees(center_direction)))
    # print("FOD Direction: " + str(math.degrees(net_enemy_direction)))
    print("Total Direction: " + str(math.degrees(total_direction)))

    return (net_magnitude, net_direction)

### TO DO 3/12
    # Need to change the weights or have a dynamic weight change
    # Maybe weigh avoiding the enemy more than the center force
        # Maybe up to a certain distance then switch back?