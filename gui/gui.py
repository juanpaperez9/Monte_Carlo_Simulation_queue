import subprocess
import pygame
import os
import time

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bank Queue Simulation")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Tellers and Queue positions
TELLER_WIDTH, TELLER_HEIGHT = 100, 50
CUSTOMER_SIZE = 20

# Initializing teller and queue display positions
tellers = [(100 + i * 150, 100) for i in range(3)]
queue_start = (50, 300)

# Function to run the C simulation and get the output
def run_simulation():
    try:
        result = subprocess.run(['./src/BankQueueSimulation'], capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running simulation: {e}")
        return None

# Function to parse the output and update the GUI
def parse_output(output):
    # Example parser for output like "Average wait time: 3.5\nCustomers served: 50\n"
    data = {}
    for line in output.splitlines():
        if "Average wait time" in line:
            data['average_wait_time'] = float(line.split(": ")[1])
        elif "Customers served" in line:
            data['customers_served'] = int(line.split(": ")[1])
    return data

# Function to draw the simulation environment
def draw_environment(customers, tellers_status, data=None):
    screen.fill(WHITE)

    # Draw tellers
    for i, teller_pos in enumerate(tellers):
        color = GREEN if tellers_status[i] == 'free' else RED
        pygame.draw.rect(screen, color, (*teller_pos, TELLER_WIDTH, TELLER_HEIGHT))
        font = pygame.font.Font(None, 30)
        text = font.render(f"Teller {i + 1}", True, BLACK)
        screen.blit(text, (teller_pos[0] + 10, teller_pos[1] + 10))

    # Draw customers in queue
    for i, customer in enumerate(customers):
        pygame.draw.circle(screen, BLUE, (queue_start[0] + i * (CUSTOMER_SIZE + 10), queue_start[1]), CUSTOMER_SIZE)

    # Display simulation data if available
    if data:
        font = pygame.font.Font(None, 36)
        avg_wait_text = font.render(f"Average Wait Time: {data.get('average_wait_time', 'N/A')} mins", True, BLACK)
        served_text = font.render(f"Customers Served: {data.get('customers_served', 'N/A')}", True, BLACK)
        screen.blit(avg_wait_text, (50, 450))
        screen.blit(served_text, (50, 500))

    pygame.display.flip()

# Main function to run the GUI
def main():
    running = True
    clock = pygame.time.Clock()

    # Run the simulation and get the output
    simulation_output = run_simulation()
    if simulation_output:
        data = parse_output(simulation_output)
    else:
        data = None

    # Placeholder data for tellers and customers (to replace with real data later)
    tellers_status = ['free', 'busy', 'free']
    customers = [1, 2, 3, 4, 5]

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update the environment with placeholder data
        draw_environment(customers, tellers_status, data)

        # Simulate processing (replace with real updates)
        time.sleep(1)

        clock.tick(60)  # Run at 60 frames per second

    pygame.quit()

if __name__ == "__main__":
    main()
