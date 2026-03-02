print ("Welcome to my calculator!")

while True:
    # Ask for two numbers and an operation
    num1 = float(input("Enter a number: "))
    num2 = float(input("Enter another number: "))
    operation = input("Choose and operation (+, -, *, /): ")

    #Perform the calculation
    try:
        if operation == "+":
            result = num1 + num2
        elif operation == "-":
            result = num1 - num2
        elif operation == "*":
            result = num1 * num2
        elif operation == "/":
            result = num1 / num2
        else:
            print("Invalid operation")
                
    except ZeroDivisionError:
        print("You can't divide by zero!")
    except ValueError:
        print("Invalid input. Please enter a valid number.")
    else:
        print(f"{num1} {operation} {num2} = {result}")
        
    # Ask if the user wants to perform another calculation
    again = input("Do you want to perform another calculation? (y/n): ")
    if again.lower() == "n":
        break