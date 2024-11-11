#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>
#include <omp.h>

// Simulation constants
#define TOTAL_SIMULATION_TIME 480 // 8 hours in minutes
#define NUM_TELLERS 3             // Number of tellers in the bank
#define ARRIVAL_RATE 5            // Average time (in minutes) between arrivals
#define MAX_CUSTOMERS 1000        // Max number of customers that can arrive

// Customer structure to hold arrival and service times
typedef struct {
    int arrival_time;
    int service_time;
    int start_service_time;
    int wait_time;
} Customer;

Customer customers[MAX_CUSTOMERS];
int total_customers = 0;

// Function prototypes
int getNextArrivalTime();
void simulateArrivals();
void simulateService();
void analyzeResults();
void setSimulationParameters(int total_simulation_time, int num_tellers, int arrival_rate);

// Global parameters for simulation
int total_simulation_time = TOTAL_SIMULATION_TIME;
int num_tellers = NUM_TELLERS;
int arrival_rate = ARRIVAL_RATE;
int total_idle_time = 0;
int current_time = 0;
int total_queue_length = 0;
int max_queue_length = 0;

int main(int argc, char *argv[]) {
    // Parse command line arguments for different scenarios
    if (argc == 4) {
        total_simulation_time = atoi(argv[1]);
        num_tellers = atoi(argv[2]);
        arrival_rate = atoi(argv[3]);
    }

    // Seed the random number generator
    srand(time(NULL));

    // Measure start time
    double start_time = omp_get_wtime();

    // Initialize and run the simulation
    simulateArrivals();
    simulateService();
    analyzeResults();

    // Measure end time
    double end_time = omp_get_wtime();
    printf("Total execution time: %.2f seconds\n", end_time - start_time);

    return 0;
}

// Function to generate the next customer arrival time based on an exponential distribution
int getNextArrivalTime() {
    double lambda = 1.0 / arrival_rate; // arrival rate (mean time between arrivals)
    return (int)(-log(1.0 - (double)rand() / RAND_MAX) / lambda);
}

// Simulate customer arrivals over the simulation period
void simulateArrivals() {
    // Generate customers until we reach the end of the simulation time
    while (current_time < total_simulation_time && total_customers < MAX_CUSTOMERS) {
        int arrival_time = getNextArrivalTime();
        current_time += arrival_time;

        if (current_time >= total_simulation_time) break;

        customers[total_customers].arrival_time = current_time;
        customers[total_customers].service_time = rand() % 10 + 1; // Random service time between 1 and 10 minutes
        customers[total_customers].start_service_time = 0;
        customers[total_customers].wait_time = 0;
        total_customers++;
    }
    printf("Total customers generated: %d\n", total_customers);
}

// Simulate the service process for customers arriving at the bank
void simulateService() {
    int tellers[num_tellers];
    for (int i = 0; i < num_tellers; i++) tellers[i] = 0; // Tracks when each teller will be free
    int queue[MAX_CUSTOMERS];       // Queue to hold waiting customers (store their indices)
    int queue_length = 0;
    int customers_served = 0;

    // Process each customer in the order they arrived
    #pragma omp parallel for reduction(+:total_queue_length, customers_served) schedule(dynamic)
    for (int i = 0; i < total_customers; i++) {
        int arrival_time = customers[i].arrival_time;
        int service_time = customers[i].service_time;
        int teller_available = -1;
        int min_teller_time = total_simulation_time + 1;

        // Check for an available teller
        #pragma omp critical
        {
            for (int j = 0; j < num_tellers; j++) {
                if (tellers[j] <= arrival_time && tellers[j] < min_teller_time) {
                    min_teller_time = tellers[j];
                    teller_available = j;
                }
            }
        }
        
        if (teller_available != -1) {
            // Teller is available, serve the customer
            #pragma omp critical
            {
                customers[i].start_service_time = arrival_time;
                customers[i].wait_time = 0;
                tellers[teller_available] = arrival_time + service_time; // Update teller's next available time
                customers_served++;
            }
        } else {
            // No tellers are available, add customer to the queue
            #pragma omp critical
            {
                queue[queue_length++] = i;
            }
        }

        // Track total queue length for average calculation
        total_queue_length += queue_length;
        #pragma omp critical
        {
            if (queue_length > max_queue_length) {
                max_queue_length = queue_length;
            }
        }
    }

    // Process the queue once tellers become available
    while (queue_length > 0) {
        int customer_index = queue[0];
        int arrival_time = customers[customer_index].arrival_time;
        int service_time = customers[customer_index].service_time;
        int earliest_teller = 0;

        // Find the earliest available teller
        #pragma omp critical
        {
            for (int j = 1; j < num_tellers; j++) {
                if (tellers[j] < tellers[earliest_teller]) {
                    earliest_teller = j;
                }
            }
        }

        // Assign customer to the earliest available teller
        #pragma omp critical
        {
            customers[customer_index].start_service_time = tellers[earliest_teller];
            customers[customer_index].wait_time = tellers[earliest_teller] - arrival_time;
            tellers[earliest_teller] += service_time; // Update teller's next available time
            customers_served++;

            // Shift the queue
            for (int k = 1; k < queue_length; k++) {
                queue[k - 1] = queue[k];
            }
            queue_length--;

            // Track total queue length for average calculation
            total_queue_length += queue_length;
            if (queue_length > max_queue_length) {
                max_queue_length = queue_length;
            }
        }
    }

    // Calculate total idle time for all tellers
    #pragma omp parallel for reduction(+:total_idle_time)
    for (int i = 0; i < num_tellers; i++) {
        if (tellers[i] < total_simulation_time) {
            total_idle_time += (total_simulation_time - tellers[i]);
        }
    }

    printf("Total customers served: %d\n", customers_served);
    printf("Customers left in queue: %d\n", queue_length);
}

// Analyze the simulation results and calculate average wait time and other metrics
void analyzeResults() {
    int total_wait_time = 0;
    int served_customers = 0;
    int min_wait_time = MAX_CUSTOMERS;
    int max_wait_time = 0;

    #pragma omp parallel for reduction(+:total_wait_time, served_customers) reduction(min:min_wait_time) reduction(max:max_wait_time)
    for (int i = 0; i < total_customers; i++) {
        total_wait_time += customers[i].wait_time;
        if (customers[i].wait_time > 0 || customers[i].start_service_time != 0) {
            served_customers++;
        }
        if (customers[i].wait_time < min_wait_time && customers[i].wait_time > 0) {
            min_wait_time = customers[i].wait_time;
        }
        if (customers[i].wait_time > max_wait_time) {
            max_wait_time = customers[i].wait_time;
        }
    }

    double average_wait_time = (double)total_wait_time / served_customers;
    double average_queue_length = (double)total_queue_length / total_customers;
    double teller_utilization = 1.0 - ((double)total_idle_time / (num_tellers * total_simulation_time));

    printf("Average wait time for served customers: %.2f\n", average_wait_time);
    printf("Maximum wait time: %d\n", max_wait_time);
    printf("Minimum wait time: %d\n", min_wait_time == MAX_CUSTOMERS ? 0 : min_wait_time);
    printf("Average queue length: %.2f\n", average_queue_length);
    printf("Max queue length: %d\n", max_queue_length);
    printf("Teller utilization: %.2f%%\n", teller_utilization * 100);
    printf("Total customers served: %d\n", served_customers);
    
}
