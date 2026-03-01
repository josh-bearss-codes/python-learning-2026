try:
    # Ask for the bill amount
    bill_amount = float(input("Enter the bill amount: "))
except ValueError:
    print("Invalid bill amount. Please enter a valid number.")

try:
    # Ask for the number of people splitting the bill
    num_people = int(input("How many people are splitting the bill? "))
except ValueError:
    print("Invalid number of people. Please enter a valid number.")

try:
    # Ask for the desired tip percentage
    tip_percentage = float(input("What percentage tip would you like to leave? "))
except ValueError:
    print("Invalid tip percentage. Please enter a valid number.")
    
try:
    # Calculate the tip amount and total with tip
    tip_amount = (bill_amount * tip_percentage) / 100
    total_with_tip = bill_amount + tip_amount

    # Calculate each person's share
    person_share = total_with_tip / num_people
    
except ZeroDivisionError:
    print("You can't divide by zeron!")
    
else:
    # Format all money output to 2 decimal places
    bill_amount_formatted = "${:.2f}".format(bill_amount)
    tip_amount_formatted = "${:.2f}".format(tip_amount)
    total_with_tip_formatted = "${:.2f}".format(total_with_tip)
    person_share_formatted = "${:.2f}".format(person_share)

    # Print the results
    print("Bill amount:", bill_amount_formatted)
    print("Tip percentage:", tip_percentage, "%")
    print("Tip amount:", tip_amount_formatted)
    print("Total with tip:", total_with_tip_formatted)
    print("Each person's share:", person_share_formatted)