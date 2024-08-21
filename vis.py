import numpy as np
import random
import math
import pygame
import time

# Problem instance
demands = [0, 5, 20, 10, 20, 85, 65, 30, 20, 70, 30]
original_demands = demands[:]
capacity = 100
num_vehicles = 6
num_customers = len(demands) - 1
distance_matrix = [
    [0, 13, 6, 55, 93, 164, 166, 168, 169, 241, 212],
    [13, 0, 11, 66, 261, 175, 177, 179, 180, 239, 208],
    [6, 11, 0, 60, 97, 128, 171, 173, 174, 239, 209],
    [55, 66, 60, 0, 82, 113, 115, 117, 117, 295, 265],
    [93, 261, 97, 82, 0, 113, 115, 117, 118, 333, 302],
    [164, 175, 168, 113, 113, 0, 6, 7, 2, 403, 374],
    [166, 177, 171, 115, 115, 6, 0, 8, 7, 406, 376],
    [168, 179, 173, 117, 117, 4, 8, 0, 3, 408, 378],
    [169, 180, 174, 117, 118, 3, 7, 3, 0, 409, 379],
    [241, 239, 239, 295, 333, 403, 406, 408, 409, 0, 46],
    [212, 208, 209, 265, 302, 374, 376, 378, 379, 46, 0]
]

# Seed the random number generator for reproducibility
random.seed(42)
np.random.seed(42)

# Initial solution: Greedy insertion
def initial_solution():
    routes = [[] for _ in range(num_vehicles)]
    remaining_customers = list(range(1, num_customers + 1))

    for customer in remaining_customers:
        for route in routes:
            if sum(demands[c] for c in route) + demands[customer] <= capacity:
                route.append(customer)
                break

    for route in routes:
        route.insert(0, 0)
        if route[-1] != 0:
            route.append(0)  # Ensure each route ends at the depot

    return routes

# Calculate the cost of the solution
def calculate_cost(routes):
    cost = 0
    for route in routes:
        for i in range(len(route) - 1):
            cost += distance_matrix[route[i]][route[i + 1]]
    return cost

# Calculate the load of each route
def calculate_load(route):
    return sum(demands[c] for c in route if c != 0)

# Generate a neighbor solution by swapping two customers within or between routes
def generate_neighbor(routes):
    new_routes = [route[:] for route in routes]

    if random.random() < 0.5:  # Swap within the same route
        route_idx = random.randint(0, num_vehicles - 1)
        route = new_routes[route_idx]
        if len(route) > 3:
            i, j = random.sample(range(1, len(route) - 1), 2)
            route[i], route[j] = route[j], route[i]
            if calculate_load(route) <= capacity:
                return new_routes  # Return if the swap is valid
    else:  # Swap between different routes
        route_idx1, route_idx2 = random.sample(range(num_vehicles), 2)
        route1, route2 = new_routes[route_idx1], new_routes[route_idx2]
        if len(route1) > 2 and len(route2) > 2:
            i = random.randint(1, len(route1) - 2)
            j = random.randint(1, len(route2) - 2)
            route1[i], route2[j] = route2[j], route1[i]
            if calculate_load(route1) <= capacity and calculate_load(route2) <= capacity:
                return new_routes  # Return if the swap is valid

    return routes  # Default return in case no valid swap is found

# Simulated Annealing algorithm
def simulated_annealing(initial_temp, cooling_rate, max_iterations, lower_limit_temp):
    temperature = initial_temp
    current_solution = initial_solution()
    current_cost = calculate_cost(current_solution)
    best_solution = current_solution
    best_cost = current_cost

    iteration = 0

    while temperature > lower_limit_temp and iteration < max_iterations:
        new_solution = generate_neighbor(current_solution)
        new_cost = calculate_cost(new_solution)
        cost_diff = new_cost - current_cost

        if cost_diff < 0 or random.random() < math.exp(-cost_diff / temperature):
            current_solution = new_solution
            current_cost = new_cost

        if current_cost < best_cost:
            best_solution = current_solution
            best_cost = current_cost

        temperature *= cooling_rate
        iteration += 1

        if iteration % 1000 == 0:
            print(f"Iteration {iteration}: Current Cost = {current_cost}, Best Cost = {best_cost}, Temperature = {temperature}")

    return best_solution, best_cost

# Visualization function with car icons
def visualize_routes(routes):
    colors = ['red', 'black', 'blue', 'yellow']
    node_positions = {
        0: (400, 300),
        1: (400, 150),
        2: (550, 200),
        3: (600, 350),
        4: (550, 500),
        5: (400, 550),
        6: (250, 500),
        7: (200, 350),
        8: (250, 200),
        9: (450, 100),
        10: (350, 100)
    }

    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("CVRP Routes Visualization")
    car_images = {
        'red': pygame.transform.scale(pygame.image.load('red_car.png'), (50, 50)),
        'black': pygame.transform.scale(pygame.image.load('white_car.png'), (50, 50)),
        'blue': pygame.transform.scale(pygame.image.load('blue_car.png'), (50, 50)),
        'yellow': pygame.transform.scale(pygame.image.load('yellow_car.png'), (50, 50))
    }

    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)

    def draw_nodes():
        for node, position in node_positions.items():
            pygame.draw.circle(screen, (0, 0, 0), position, 15)
            text = font.render(f"{node} ({demands[node]})", True, (0, 0, 0))
            screen.blit(text, (position[0] - 40, position[1] - 40))

    def draw_routes():
        all_routes_completed = False
        for idx, route in enumerate(routes):
            if len(route) > 2:
                color = colors[idx % len(colors)]
                car_image = car_images[color]
                for i in range(len(route) - 1):
                    start_pos = node_positions[route[i]]
                    end_pos = node_positions[route[i + 1]]
                    steps = 50
                    for step in range(steps):
                        t = step / steps
                        x = start_pos[0] * (1 - t) + end_pos[0] * t
                        y = start_pos[1] * (1 - t) + end_pos[1] * t
                        screen.fill((255, 255, 255))
                        draw_nodes()
                        draw_routes_without_cars()
                        screen.blit(car_image, (x - 25, y - 25))  # Adjusted position for car centering
                        pygame.display.flip()
                        clock.tick(60)
                    # Update demand when a node is reached
                    if route[i + 1] != 0:
                        demands[route[i + 1]] = 0
                        if all(d == 0 for d in demands) or route[i + 1] == 0:
                            all_routes_completed = True
                            return all_routes_completed
        return all_routes_completed

    def draw_routes_without_cars():
        for idx, route in enumerate(routes):
            if len(route) > 2:
                color = colors[idx % len(colors)]
                for i in range(len(route) - 1):
                    start_pos = node_positions[route[i]]
                    end_pos = node_positions[route[i + 1]]
                    pygame.draw.line(screen, pygame.Color(color), start_pos, end_pos, 3)

    running = True
    routes_completed = False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((255, 255, 255))
        draw_nodes()
        if not routes_completed:
            routes_completed = draw_routes()
        else:
            for route in routes:
                if route[-1] != 0:
                    route.append(0)  # Ensure all routes end at the depot
            draw_routes_without_cars()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

    # Print final routes after visualization
    print("Final Routes:")
    for i, route in enumerate(routes):
        if len(route) > 2:
            print(f"Vehicle {i + 1}: Route: {route}, Load: {calculate_load(route)}, Cost: {calculate_cost([route])}")

# Parameters
initial_temp = 1000
cooling_rate = 0.995
max_iterations = 10000
lower_limit_temp = 1  # A lower limit for temperature

# Run the Simulated Annealing algorithm
best_routes, best_cost = simulated_annealing(initial_temp, cooling_rate, max_iterations, lower_limit_temp)

# Print results
print("Final Best Cost:", best_cost)
for i, route in enumerate(best_routes):
    if len(route) > 2:
        print(f"Vehicle {i + 1}: Route: {route}, Load: {calculate_load(route)}, Cost: {calculate_cost([route])}")

# Visualize the routes
visualize_routes(best_routes)
