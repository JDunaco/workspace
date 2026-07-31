Project Name : Jordan's RideShare Program

Purpose/Design : To create an app that can complete with Uber/Lyft in utility but provide more ease of use to the users and drivers. This is going to be achieved by a simplistic approach that'll allow users and 
drivers to easily find their next ride and provide clear data to both users on their client/driver.

How to run : Concurrently there is a test.py, test2.py, test3.py or test_quadtree files that contains initially testing, later down the road there will be a proper system that'll allow intuitive control in how to use the app. This will eventually be contained into a main program file, but for now it's testing based. Test 1 is for the overall dictionary testing, Test 2 is for the map layout using Graphs, Test 3 is for testing Dijsktra's algorithm being implented, while test_quadtree is to test quadtrees and how it'll possibly be implented withing my app.

Dependencies : N/A for this iteration

Map Data Format : 
    the map.csv file is where we store our road points. 
    They work with the process of two way street:
    (Intersection A (A), Intersection B (B), with the time to get there or the weight)
    (Intersection B (B), Intersection A (A), time to get there)
    One Way 
    (Intersection A (A), Intersetion C (C), time to get there)

Dijkkstra's Algorithm: 
    Dijkstra's Algoritm is used in this program as a baseline for how we will go about finding the shortest distance, with a few additions to the algoritm to match our needs, we plan on having a live updating map to have changing nodes to make sure we can adjust for construction and flow of traffic.

Quadtree Data Structure : 
    The Quadtree structure will be implemented with the purpose of locating the nearest driver when a rider requests a ride. We chose Quadtrees for it's efficiency for processing compared to other methods to allow our users the fastest response time. The current test script is ran with :
    cd (saved file path)/student_code/final_project then running python3 test_quadtree.py 
    This will showcase a random point getting chosen and how it compares to brute-forcing distance calculations. The reason it's faster is because of the node system it uses with breaking each section down into 4 quadrants and then keep breaking it down until we get our nodes within the shortest range and not having to calculate three other quadrants that would be outside of our scope unless there is no available driver within our immediate vicinity.