"""Fluid Sim Using Smoothed Particle Hydrodynamics"""

import pygame


NUM_PARTICLES = 70
GRAVITY = 0.01
PARTICLE_SIZE = 5
SMOOTHING_RADIUS = 30
PRESSURE_FORCE_MULT = 0.1
TARGET_PRESSURE = 0.1
WALL_MULT = 0.7

BGCOLOUR = (0, 0, 30)  #  RGB
SCREENSIZE = WIDTH, HEIGHT = (400, 400)  # (1000, 560)


def smoothing_function(distance):
    """the normalized smoothing kernal
    calculated values weighted by their distance
    the area of the function is always 1"""
    value = max((0, (SMOOTHING_RADIUS - distance) / SMOOTHING_RADIUS))
    value = value**3
    value *= 2 / SMOOTHING_RADIUS
    return value


def smoothing_derivative(distance):
    """derivative of the smoothing function"""
    value = -6 * (SMOOTHING_RADIUS - distance) ** 2
    value /= SMOOTHING_RADIUS**4
    return value


def calculate_distance(point1, point2):
    """calcualates the distance between 2 points using pythagoras"""
    return ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2) ** (1 / 2)


def calculate_pressure(point, positions, masses):
    """calculates the pressure using the smoothing funtion and iteration over all particles"""

    pressure = 0
    for i in range(NUM_PARTICLES):
        distance = calculate_distance(point, positions[i])
        pressure += smoothing_function(distance) * masses[i]

    return pressure


def update(initial_speeds, initial_positions, masses):
    """updates all particles to the next simulation frame"""

    accelerations = []

    predicted_positions = [
        [
            initial_positions[i][0] + initial_speeds[i][0],
            initial_positions[i][1] + initial_speeds[i][1],
        ]
        for i in range(NUM_PARTICLES)
    ]

    for i in range(NUM_PARTICLES):
        # Allows for all changes to the velocity to happen at the same time
        # This is so they do not interact
        # It is stored as acceleration and added at the end
        acceleration = [0, 0]
        # Applies gravity to each particle

        acceleration[1] += GRAVITY

        # applies the pressure force
        pressure_force = [0, 0]

        pressure = calculate_pressure(
            predicted_positions[i], predicted_positions, masses
        )

        for j in range(NUM_PARTICLES):
            if i != j:
                distance = calculate_distance(
                    predicted_positions[i], predicted_positions[j]
                )

                pressure_gradient = smoothing_derivative(distance) * masses[j]

                pressure_difference = TARGET_PRESSURE - pressure

                pressure_force[0] += (
                    ((predicted_positions[i][0] - predicted_positions[j][0]) / distance)
                    * pressure_gradient
                    * pressure_difference
                    * PRESSURE_FORCE_MULT
                )
                pressure_force[1] += (
                    ((predicted_positions[i][1] - predicted_positions[j][1]) / distance)
                    * pressure_gradient
                    * pressure_difference
                    * PRESSURE_FORCE_MULT
                )

        acceleration[0] += pressure_force[0] / pressure
        acceleration[1] += pressure_force[1] / pressure

        # savesacceleration for the particle to apply at the ends
        accelerations.append(acceleration)

    new_speeds = [[0, 0] for i in range(NUM_PARTICLES)]
    new_positions = [[0, 0] for i in range(NUM_PARTICLES)]

    for i in range(NUM_PARTICLES):
        # add the accelerations to each particles velocity
        new_speeds[i][0] = initial_speeds[i][0] + accelerations[i][0]
        new_speeds[i][1] = initial_speeds[i][1] + accelerations[i][1]

        # then add the new volocity to the location
        new_positions[i][0] = predicted_positions[i][0] + new_speeds[i][0]
        new_positions[i][1] = predicted_positions[i][1] + new_speeds[i][1]

        # generate the display size of the particle
        display_size = masses[i] ** (1 / 3) * PARTICLE_SIZE

        # then bounce the particles of the edge of the screen
        # in the x direction
        if new_positions[i][0] < 0 + display_size:
            new_positions[i][0] = 0 + display_size
            new_speeds[i][0] *= -WALL_MULT

        elif new_positions[i][0] > WIDTH - display_size:
            new_positions[i][0] = WIDTH - display_size
            new_speeds[i][0] *= -WALL_MULT

        # and the y direction
        if new_positions[i][1] < 0 + display_size:
            new_positions[i][1] = 0 + display_size
            new_speeds[i][1] *= -WALL_MULT

        elif new_positions[i][1] > HEIGHT - display_size:
            new_positions[i][1] = HEIGHT - display_size
            new_speeds[i][1] *= -WALL_MULT

    return new_speeds, new_positions


# main loop that displays particles and runs update
def main():
    running = True

    pygame.init()
    screen = pygame.display.set_mode(SCREENSIZE)
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Ariel", 18)

    speeds = [[0, 0] for i in range(NUM_PARTICLES)]
    masses = [1 for i in range(NUM_PARTICLES)]
    GRID_SIZE = round(
        NUM_PARTICLES ** (1 / 2)
    )  # size of the grid in number of particles per row
    GRID_AREA = 1 / 2  # area in the middle of the screen that the grid can take up
    positions = [
        [
            (i % GRID_SIZE) * WIDTH / GRID_SIZE * GRID_AREA
            + 1 / 2 * (1 - GRID_AREA) * WIDTH,
            (i // GRID_SIZE) * HEIGHT / GRID_SIZE * GRID_AREA
            + 1 / 2 * (1 - GRID_AREA) * HEIGHT,
        ]
        for i in range(NUM_PARTICLES)
    ]  # generates particles in a grid in the middle of the screen

    while running:
        speeds, positions = update(speeds, positions, masses)

        screen.fill(BGCOLOUR)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # displays the pressure at each point on the plane
        # for x in range(WIDTH):
        #     for y in range(HEIGHT):
        #         pressure = calculate_pressure((x, y), positions, masses)
        #         brightness = min(255, pressure / TARGET_PRESSURE * 255)
        #         pygame.draw.circle(
        #             screen, (brightness, brightness, brightness), (x, y), 1
        #         )

        # display each particle at its location with size relating to its mass
        for particle in range(NUM_PARTICLES):
            pygame.draw.circle(
                screen,
                (25, 255, 255),
                positions[particle],
                masses[particle] ** (1 / 3) * PARTICLE_SIZE,
            )

        # generate and display fps for performance monitoring
        clock.tick()
        framerate = clock.get_fps()
        screen.blit(
            font.render(f"FPS: {round(framerate)}", True, (255, 255, 255)), (0, 0)
        )

        pygame.display.flip()


if __name__ == "__main__":
    main()
