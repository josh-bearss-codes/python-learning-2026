import random

number = random.randint(1, 100)

guesses = 0

while True:
    try:
        guess = int(input("Guess a number between 1 and 100: "))
    except:
        ValueError
    
    if guess > number:
        print("Too high!")
    elif guess < number:
        print("Too low")
    else:
        break
    
    guesses +=1

print(f"You got it in {guesses} guesses! The number was {number}.")