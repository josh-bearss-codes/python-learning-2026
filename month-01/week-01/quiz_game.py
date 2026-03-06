import json
import random

class Question:
    def __init__(self, question, options, answer):
        # store attributes
        self.question = question
        self.options = options
        self.answer = answer

    def display(self, number):
        # print the question number, question text, and numbered options
        print(f"{number}. {self.question}")
        for i, option in enumerate(self.options, 1):
            print(f"{i}. {option}")

    def check_answer(self, user_choice):
        # compare user's selected option to correct answer
        # return True/False
        return self.options[user_choice - 1] == self.answer

class Quiz:
    def __init__(self, filepath):
        self.questions = self.load_questions(filepath)
        self.score = 0

    def load_questions(self, filepath):
        # read JSON, create list of Question objects
        try:
            with open(filepath, 'r') as file:
                data = json.load(file)
                questions = []
                print(data)
                for item in data['questions']:
                    questions.append(Question(item['question'], item['options'], item['answer']))
                return questions
        except FileNotFoundError:
            print("Error: File not found.")
            return []
        except json.JSONDecodeError:
            print("Error: Invalid JSON format.")
            return []
        except KeyError as e:
            print(f"Error: Missing key in JSON data: {e}")
            return []

    def run(self):
        # shuffle questions (optional)
        random.shuffle(self.questions)
        # loop through questions with enumerate
        # display each, get user answer, check, update score
        for i, question in enumerate(self.questions, 1):
            print(f"Question {i}:")
            question.display(i) # Call display method
            user_answer = input("Your answer (1-4): ")
            if question.check_answer(int(user_answer)):
                print("Correct!")
                self.score += 1
            else:
                print("Wrong!")
                print(f"The correct answer was: {self.questions[i-1].answer}")

        print(f"Final score: {self.score}/{len(self.questions)}")
        if len(self.questions) > 0:
            percentage = (self.score / len(self.questions)) * 100
            print(f"Your percentage: {percentage:.1f}%")

    def show_results(self):
        # display final score with percentage
        # maybe show which questions were missed
        print(f"Final score: {self.score}/{len(self.questions)}")
        if len(self.questions) > 0:
            percentage = (self.score / len(self.questions)) * 100
            print(f"Your percentage: {percentage:.1f}%")

def main():
    quiz = Quiz("python_quiz.json")
    if quiz.questions:
        quiz.run()
        quiz.show_results()
    else:
        print("Error: No questions found in the quiz file")

if __name__ == "__main__":
    main()