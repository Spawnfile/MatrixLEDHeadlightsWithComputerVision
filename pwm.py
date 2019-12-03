import UDPLibrary

"""
Some setup things for raspbery.

"""
bounding_boxes_coordinates = UDP.Receive()
def generate_pwm(bounding_boxes_coordinates):
	print("Generate PWM signals to related pins")
