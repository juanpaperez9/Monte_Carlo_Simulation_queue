import subprocess 
import pygame
import os
import time

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bank Queue Simulation")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 102, 102)
SOFT_RED = (255, 153, 153)
GREEN = (102, 255, 102)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)

# Fonts
font_large = pygame.font.Font(None, 42)
font_medium = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 24)

# Constants
PULSE_INCREMENT = 5
progress_bar_height = 10
CUSTOMER_SIZE = 30  # Increased size of customer circles
CUSTOMER_SPACING = 90  # Increased spacing between customers
queue_start = (50, 400)

# Function to run the C simulation and get the output
def run_simulation(simulation_type):
    try:
        # Set parameters for different scenarios
        if simulation_type == 'run_normal':
            parameters = ['480', '3', '5']
        elif simulation_type == 'run_rush_hour':
            parameters = ['120', '5', '2']
        elif simulation_type == 'run_off_peak':
            parameters = ['480', '2', '10']
        else:
            parameters = ['480', '3', '5']

        # Run the compiled C program directly
        result = subprocess.run(['.\BankQueueSimulation.exe'] + parameters, stdout=subprocess.PIPE, text=True, check=True)

        # Print the output to the terminal
        print(result.stdout)
        # Write output to a file for parsing
        with open('simulation_output.txt', 'w') as f:
            f.write(result.stdout)
        
        return result.stdout, int(parameters[1])  # Return number of tellers
    except subprocess.CalledProcessError as e:
        print(f"Error running simulation: {e}")
        return None, 3

# Function to parse the output and update the GUI
def parse_output(output):
    data = {}
    for line in output.splitlines():
        if "Total customers generated" in line:
            data['total_customers_generated'] = int(line.split(": ")[1])
        elif "Total customers served" in line and 'total_customers_served' not in data:
            data['total_customers_served'] = int(line.split(": ")[1])
        elif "Customers left in queue" in line:
            data['customers_left_in_queue'] = int(line.split(": ")[1])
        elif "Average wait time for served customers" in line:
            data['average_wait_time'] = float(line.split(": ")[1])
    return data

# Function to draw the simulation environment
def draw_environment(customers, tellers_status, progress_bars, data=None):
    screen.fill(WHITE)

    # Draw tellers
    for i, (teller_pos, teller_status) in enumerate(zip(tellers_status, progress_bars)):
        x, y, w, h = teller_pos
        color = GREEN if teller_status == 'free' else SOFT_RED
        # Pulse effect for available tellers
        if teller_status == 'free':
            glow = (PULSE_INCREMENT * (pygame.time.get_ticks() % 1000) // 500) % 10
            pygame.draw.rect(screen, color, (x - glow, y - glow, w + 2 * glow, h + 2 * glow), 3)
        pygame.draw.rect(screen, color, (x, y, w, h))
        text = font_medium.render(f"Teller {i + 1}", True, BLACK)
        screen.blit(text, (x + 10, y + 10))

        # Draw status icons (clock or check mark)
        if teller_status != 'free':
            pygame.draw.circle(screen, RED, (x + w - 30, y + 20), 10)
        else:
            pygame.draw.circle(screen, GREEN, (x + w - 30, y + 20), 10)

        # Draw progress bar for teller availability
        progress_width = int((teller_status / 100.0) * w) if isinstance(teller_status, int) else 0
        pygame.draw.rect(screen, GRAY, (x, y + h + 5, w, progress_bar_height))
        pygame.draw.rect(screen, BLUE, (x, y + h + 5, progress_width, progress_bar_height))

    # Draw customers in queue
    for i, customer in enumerate(customers):
        pygame.draw.circle(screen, BLACK, (queue_start[0] + i * CUSTOMER_SPACING, queue_start[1]), CUSTOMER_SIZE)

    # Display simulation data if available
    if data:
        stats_box_rect = pygame.Rect(50, 600, 1100, 180)
        pygame.draw.rect(screen, GRAY, stats_box_rect, border_radius=10)
        avg_wait_text = font_large.render(f"Average Wait Time: {data.get('average_wait_time', 'N/A')} mins", True, BLACK)
        served_text = font_large.render(f"Customers Served: {data.get('total_customers_served', 'N/A')}", True, BLACK)
        left_in_queue_text = font_medium.render(f"Customers Left in Queue: {data.get('customers_left_in_queue', 'N/A')}", True, BLACK)
        generated_text = font_medium.render(f"Total Customers Generated: {data.get('total_customers_generated', 'N/A')}", True, BLACK)
        screen.blit(avg_wait_text, (stats_box_rect.x + 20, stats_box_rect.y + 20))
        screen.blit(served_text, (stats_box_rect.x + 20, stats_box_rect.y + 70))
        screen.blit(left_in_queue_text, (stats_box_rect.x + 20, stats_box_rect.y + 120))
        screen.blit(generated_text, (stats_box_rect.x + 600, stats_box_rect.y + 120))

    # Draw buttons
    run_again_button = pygame.Rect(950, 300, 200, 60)
    draw_buttons(run_again_button)

    pygame.display.flip()

# Draw buttons with improved visibility
def draw_buttons(run_again_button):
    pygame.draw.rect(screen, RED, run_again_button)  # Changed button color to RED for better visibility
    
    # Button Text
    run_again_text = font_large.render("Run Again", True, WHITE)
    
    # Draw button text
    screen.blit(run_again_text, (run_again_button.x + 20, run_again_button.y + 10))

# Main function to run the GUI
def main():
    running = True
    clock = pygame.time.Clock()

    # Run the simulation and get the output
    current_simulation = 'run_rush_hour'  # Default scenario
    simulation_output, num_tellers = run_simulation(current_simulation)
    if simulation_output:
        data = parse_output(simulation_output)
    else:
        data = None

    # Define teller positions dynamically based on number of tellers
    tellers_status = []
    teller_width = WIDTH // (num_tellers + 1) - 20
    for i in range(num_tellers):
        x = (i + 1) * (WIDTH // (num_tellers + 1)) - teller_width // 2
        tellers_status.append((x, 100, teller_width, 100))

    # Placeholder data for customers
    customers = [1, 2, 3, 4, 5]
    progress_bars = ['free' for _ in range(num_tellers)]

    # Button
    run_again_button = pygame.Rect(950, 300, 200, 60)  # Placed in the middle right of the screen

    # Animation loop
    animation_step = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if run_again_button.collidepoint(event.pos):
                    # Run the simulation again with the same scenario
                    simulation_output, num_tellers = run_simulation(current_simulation)
                    if simulation_output:
                        data = parse_output(simulation_output)

        # Draw the environment with placeholder data
        draw_environment(customers[:animation_step % len(customers)], tellers_status, progress_bars, data)

        # Simulate processing (animate customer addition to queue)
        animation_step += 1
        time.sleep(0.5)  # Adjust speed for animation

        clock.tick(60)  # Run at 60 frames per second

    pygame.quit()

if __name__ == "__main__":
    main()
