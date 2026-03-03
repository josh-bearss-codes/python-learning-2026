grades = []

print("Please enter the grades (one at a time). Enter done when ready to calculate")

#Enter Grade Loop
while True:
    grade = input()
    if 'done' not in grade:
        try:
            grades.append(abs(int(grade)))
        except: ValueError
    else: break
    
# Grading Scales
# 90-100 = A
# 80-90 = B
# 70-80 = C
# 60-70 = D
# 59 and below = F

average_grade = sum(grades) / len(grades)
grades.append(round(average_grade))

letter_grade = ''

for i, grade in enumerate(grades):
    if grade >= 90:
        letter_grade = 'A' 
    elif grade >= 80 and  grade < 90:
        letter_grade = 'B'
    elif grade >= 70 and grade < 80:
        letter_grade = 'C'
    elif grade >= 60 and grade < 70:
        letter_grade = 'D'
    elif grade <60 and grade > 0:
        letter_grade = 'F'
    else:
        print(f"{grade} is not a valid value")
        continue
    if i == len(grades) -1:
        print(f"Your average grade is a {letter_grade}: {grade}%")
    else:
        print(f"Your grade is a {letter_grade}: {grade}%")