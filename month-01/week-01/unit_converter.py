def temp(x, y):
    # If the user input is in Fahrenheit, convert it to Celsius
    if y.lower() == 'f':
        return str((x - 32) * 5/9) + " C"
    # If the user input is in Celsius, convert it to Fahrenheit
    if y.lower() == 'c':
        return str((x * 9/5) + 32) + " F"
    else: 
        return None

def distance(x, y):
    # If the user input is in miles, convert it to kilometers
    if y.lower() == 'm' or y.lower() == 'miles':
        return str(x * 1.60934) + " kilometers"
    # If the user input is in kilometers, convert it to miles
    if y.lower() == 'k' or y.lower() == 'kilometers':
        return str(x / 1.60934) + " miles"
    else: 
        return None

def weight(x, y):
    # If the user input is in pounds, convert it to kilograms
    if y.lower() == 'lb':
        return str(x * 0.452592) + " kgs"
    # If the user input is in kilograms, convert it to pounds
    if y.lower() == 'kg':
        return str(x / 0.452592) + " lbs"
    
function_map = {
    'temp': temp,
    'distance': distance,
    'weight': weight
}

while True:
    user_choice = input("Enter the type of conversion you would like (temp, distance, weight)? ")
    function = function_map.get(user_choice)
    if function is None:
        print("Invalid conversion type")
        continue
        
    try:
        x = float(input("Enter the value to convert: "))
    except ValueError:
        print("Value entered is not a number")
        continue
        
    y = input("Enter the type of the value (F, C, Miles(M), Kilometers(K), Lbs(lb), Kgs(kg)): ")

    result = function(x, y)
    if result is not None:
        print(f"{x} {y} converts to {result}")
    else:
        print("Unable to convert due to Error")
    
    if input("Would you like to do another conversion (q to quit): ").lower() == 'q':
        break