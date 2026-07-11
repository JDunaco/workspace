from math import pi

def circle_area(radius):
  if type(radius) not in [int, float]:
    raise TypeError("Radius must be a non-negative, real number.")
  if radius < 0:
    raise ValueError("Radius cannot be a negative number")
  return pi * radius ** 2