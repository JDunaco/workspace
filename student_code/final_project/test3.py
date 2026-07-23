from simulation import Simulation

if __name__ == "__main__":
    print ("running software testing\n")

    # Create Simulation Class and load the map
    test_Simulation = Simulation('map.csv')
    test_Simulation.new_car(1,'A')
    test_Simulation.calculate_route(1,'D')

    car = test_Simulation.car_data['Car-1']
    print(car.route)
    print(car.route_time)
