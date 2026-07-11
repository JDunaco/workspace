from simulation import Simulation

if __name__ == "__main__":
    print ("running software testing\n")

    # Create Simulation Class
    test_Simulation = Simulation()
    
    # Add driver cars to system (test_Simulation.new_car(id, location))
    test_Simulation.new_car(101, (1, 25))
    test_Simulation.new_car(102, (32, 2))
    test_Simulation.new_car(103, (4, 5))
    test_Simulation.new_car(104, (0, 50))
    test_Simulation.new_car(105, (10, 250))

    # Add riders to system (test_Simulation.new_rider(id, starting_location))
    test_Simulation.new_rider("\nR01", (100, 25), (25, 100))
    test_Simulation.new_rider("R02", (10, 50), (50, 10))
    test_Simulation.new_rider("R03", (30, 78), (78, 30))
    test_Simulation.new_rider("R04", (35, 6), (6, 35))
    test_Simulation.new_rider("R05", (1, 25), (25, 1))

    # See if all data added correctly
    test_Simulation.display_info()
