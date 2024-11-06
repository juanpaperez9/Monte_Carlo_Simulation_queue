#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>

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

int main() {
    // Seed the random number generator
    srand(time(NULL));

    // Initialize and run the simulation
    simulateArrivals();
    simulateService();
    analyzeResults();

    return 0;
}

// Function to generate the next customer arrival time based on an exponential distribution
int getNextArrivalTime() {
    double lambda = 1.0 / ARRIVAL_RATE; // arrival rate (mean time between arrivals)
    return (int)(-log(1.0 - (double)rand() / RAND_MAX) / lambda);
}

// Simulate customer arrivals over the simulation period
void simulateArrivals() {
    int current_time = 0;

    // Generate customers until we reach the end of the simulation time
    while (current_time < TOTAL_SIMULATION_TIME && total_customers < MAX_CUSTOMERS) {
        int arrival_time = getNextArrivalTime();
        current_time += arrival_time;

        if (current_time >= TOTAL_SIMULATION_TIME) break;

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
    int tellers[NUM_TELLERS] = {0}; // Tracks when each teller will be free
    int queue[MAX_CUSTOMERS];       // Queue to hold waiting customers (store their indices)
    int queue_length = 0;
    int customers_served = 0;

    // Process each customer in the order they arrived
    for (int i = 0; i < total_customers; i++) {
        int arrival_time = customers[i].arrival_time;
        int service_time = customers[i].service_time;
        int teller_available = -1;

        // Check for an available teller
        for (int j = 0; j < NUM_TELLERS; j++) {
            if (tellers[j] <= arrival_time) { // Teller is free
                teller_available = j;
                break;
            }
        }

        if (teller_available != -1) {
            // Teller is available, serve the customer
            customers[i].start_service_time = arrival_time;
            customers[i].wait_time = 0;
            tellers[teller_available] = arrival_time + service_time; // Update teller's next available time
            customers_served++;
        } else {
            // No tellers are available, add customer to the queue
            queue[queue_length++] = i;
        }
    }

    // Process the queue once tellers become available
    for (int i = 0; i < queue_length; i++) {
        int customer_index = queue[i];
        int arrival_time = customers[customer_index].arrival_time;
        int service_time = customers[customer_index].service_time;
        int earliest_teller = 0;

        // Find the earliest available teller
        for (int j = 1; j < NUM_TELLERS; j++) {
            if (tellers[j] < tellers[earliest_teller]) {
                earliest_teller = j;
            }
        }

        // Assign customer to the earliest available teller
        customers[customer_index].start_service_time = tellers[earliest_teller];
        customers[customer_index].wait_time = tellers[earliest_teller] - arrival_time;
        tellers[earliest_teller] += service_time; // Update teller's next available time
        customers_served++;
    }

    printf("Total customers served: %d\n", customers_served);
    printf("Customers left in queue: %d\n", queue_length);
}

// Analyze the simulation results and calculate average wait time and other metrics
void analyzeResults() {
    int total_wait_time = 0;
    int served_customers = 0;

    for (int i = 0; i < total_customers; i++) {
        total_wait_time += customers[i].wait_time;
        if (customers[i].wait_time > 0 || customers[i].start_service_time != 0) {
            served_customers++;
        }
    }

    double average_wait_time = (double)total_wait_time / served_customers;
    printf("Average wait time for served customers: %.2f\n", average_wait_time);
    printf("Total customers served: %d\n", served_customers);
}
