import sys
sys.path.append('/usr/share/codio/assessments')
from lib.grade import send_partial_v2, FORMAT_V2_MD, FORMAT_V2_HTML, FORMAT_V2_TXT
import os
from exercise5 import Subway

points = 0
feedback = ""
test_subway = Subway()

boarding_test = False
fare_test = False
exit_test = False
distance_test = False
advance_test = False
change_fare_test = False

def check_boarding(subway, new_passengers):
  """Verify that passengers board as expected"""
  subway.board(new_passengers)
  if subway.passengers == new_passengers:
    # Boarding test passed
    points += 1
    return True
  else:
    # Boarding test feedback
    feedback += "<b>Boarding test did not pass</b>"
    return False

def check_fares(subway, total_passengers):
  """Verify that fares are being tallyed"""
  if subway.total_fares == total_passengers * Subway.fare:
    # Fare test passed
    points += 1
    return True
  else:
    # Fare test feedback
    feedback += "<b>Fare test did not pass</b>"
    return False

def check_exit(subway):
  """Verify that passengers are exiting as expected"""
  test1 = False
  test2 = False
  subway.disembark(75)
  if subway.passengers == 125:
    test1 = True
  subway.disembark(1000)
  if subway.passengers == 0:
    test2 = True
  if test1 and test2:
    # Disembark test passed
    points += 2
    return True
  else:
    # Disembark test feedback
    feedback += "<b>Disembark test did not pass</b>"
    return False

def check_distance(subway, desired_stop):
  """Verify that is being calculated as expected"""
  subway.current_stop = "Central"
  if subway.distance(desired_stop) == 3:
    # Distance test passed
    points += 3
    return True
  else:
    # Distance test feedback
    feedback += "<b>Distance test did not pass</b>"
    return False
  
def check_advance(subway):
  """Verify that the subway is advancing as expected"""
  test1 = False
  test2 = False
  subway.advance()
  if subway.current_stop == "Kendall" and subway.direction == "south":
    test1 = True
  subway.current_stop = "Alewife"
  subway.direction = "north"
  subway.advance()
  if subway.current_stop == "Davis" and subway.direction == "south":
    test2 = True
  if test1 and test2:
    # Advance test passed
    points += 3
    return True
  else:
    # Advance test feedback
    feedback += "<b>Advance test did not pass</b>"
    return False

def check_change_fare(subway, new_fare):
  """Verify that changing the fare affects all instances of the Subway class"""
  subway.change_fare(new_fare)
  if Subway.fare == new_fare:
    # Change fare test passed
    points += 12
    return True
  else:
    # Change fare test feedback
    feedback += "<b>Change fare test did not pass</b>"
    return False

boarding_test = check_boarding(test_subway, 200)
fare_test = check_fares(test_subway, 200)
exit_test = check_exit(test_subway)
distance_test = check_distance(test_subway, "Davis")
advance_test= check_advance(test_subway)
change_fare_test = check_change_fare(test_subway, 2.55)

# passing feedback
if feedback == "":
  feedback = "<h2>Test passed</h2>"

# send results to Codio
res = send_partial_v2(points, feedback, FORMAT_V2_HTML)
exit(0 if res else 1)