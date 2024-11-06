Objective: Simulate customer arrivals and service in a bank to analyze and optimize customer wait times and service efficiency.
Real-World Scenario: Model a bank with multiple tellers (service counters), each serving customers. Customers arrive randomly, and each customer requires a random amount of time to complete their service.
Metrics to Calculate:
Average Wait Time: The average time customers spend waiting to be served.
Queue Length: The number of customers waiting at any given time.
Resource Utilization: The proportion of time tellers are actively serving customers.

 **Simulation Flow**
Initialize the Simulation:
Set the total simulation time (e.g., simulate a bank operating for 8 hours).
Initialize a queue for waiting customers.
Set up service counters (tellers) based on the scenario.
Generate Customer Arrivals:
Use a loop to generate customers who arrive at random intervals, up to the total simulation time.
For each customer, generate an arrival time based on an exponential distribution.
Generate a random service time for each customer.
If a teller is available upon the customer’s arrival, the customer goes directly to service. If not, they enter the queue.
Simulate Service Process:
For each teller, keep track of their current status and the time they’ll be free.
If a teller is available when a customer arrives, assign them to the teller.
If all tellers are busy, add the customer to the queue and record their wait time until a teller is available.
Handle the Queue:
When a teller finishes serving a customer, check if there are customers waiting in the queue.
If so, assign the next customer in the queue to the teller, and update their wait time and service start time.
Track Key Metrics:
For each customer, record their wait time (arrival to service start).
Update the total queue length each time a new customer arrives or is served.
Calculate teller utilization by tracking the proportion of time each teller spends actively serving customers.
