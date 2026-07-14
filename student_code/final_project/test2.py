from simulation import Simulation

if __name__ == "__main__":
    print ("running software testing\n")

    # Create Simulation Class and load the map
    test_Simulation = Simulation('map.csv')
    
    # Add nodes to the map
    test_Simulation.add_map_paths('F','G',10)
    test_Simulation.add_map_paths('G','F',10)
    test_Simulation.add_map_paths('A','G',15)
    test_Simulation.add_map_paths('B','G',7)
    test_Simulation.add_map_paths('C','G',13)
    test_Simulation.add_map_paths('G','A',15)

    # See if all data added correctly
    test_Simulation.display_info(2)