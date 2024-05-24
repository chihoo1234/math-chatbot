import sympy as sp
import random
import re
from flask import Flask, request, jsonify
import openai
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# OpenAI API 키 설정 (환경 변수로 관리하는 것이 좋음)
openai.api_key = os.getenv('OPENAI_API_KEY')

def set_coefficient_range(stage):
    if stage == 1:
        return (1, 10)
    elif stage == 2:
        return (-10, 10)
    elif stage == 3:
        return (-10, 100)
    elif stage == 4:
        return (-100, 100)
    elif stage == 5:
        return (-10000, 10000)
    else:
        return (-10000, 10000)  # 기본값

def generate_math_problem(stage):
    x = sp.symbols('x')
    a_range = set_coefficient_range(stage)
    b_range = set_coefficient_range(stage)
    c_range = set_coefficient_range(stage)

    a = random.randint(*a_range)
    b = random.randint(*b_range)
    c = random.randint(*c_range)

    operation = random.choice(['+', '-', '*', 'ln'])

    if operation == '+':
        problem = f"{a}*x + {b} = {c}"
    elif operation == '-':
        problem = f"{a}*x - {b} = {c}"
    elif operation == '*':
        problem = f"{a}*x * {b} = {c}"
    elif operation == 'ln':
        problem = f"ln(x) = {c}"

    return problem

def solve_math_problem(problem):
    try:
        if 'ln(x)' in problem:
            solution = sp.solve(sp.Eq(sp.log(sp.symbols('x')), sp.sympify(problem.split('=')[1])))
        else:
            solution = sp.solve(sp.Eq(sp.sympify(problem.split('=')[0]), sp.sympify(problem.split('=')[1])))
        return solution
    except Exception as e:
        return str(e)

def check_answer(correct_answer, user_answer):
    if correct_answer == "no solution":
        return user_answer == "no solution"
    else:
        correct_answer = correct_answer[0].evalf()
        user_answer = sp.Rational(user_answer).evalf()
        return correct_answer == user_answer

def validate_complex_number(problem):
    pattern = r"\b(\d+)i\*i\b"
    if re.search(pattern, problem):
        return True
    return False

@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.json
    user_message = data.get('message')
    
    if user_message:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=user_message,
            max_tokens=50
        )
        bot_message = response.choices[0].text.strip()
        return jsonify({"response": bot_message})
    else:
        return jsonify({"response": "Please provide a message."})

def main():
    while True:
        print("수학 문제 풀이 챗봇: 데이터 학습 또는 문제 풀기를 선택하세요.")
        print("1. 사용자가 문제를 내고 챗봇이 맞추는 모드")
        print("2. 챗봇이 문제를 내고 사용자가 맞추는 모드")
        print("3. 종료")
        choice = input("사용자: ")

        if choice == "1":
            print("수학 문제 풀이 챗봇: 수학 문제를 입력하세요.")
            print("수학 문제 풀이 챗봇: 종료하려면 '종료'를 입력하세요.")

            while True:
                problem = input("사용자: ")
                if problem.lower() == "종료":
                    print("수학 문제 풀이 챗봇: 문제 풀이를 종료합니다.")
                    break

                if validate_complex_number(problem):
                    print("수학 문제 풀이 챗봇: 복소수 형식은 '3*i'와 같이 입력해주세요.")
                    continue

                solution = solve_math_problem(problem)

                if isinstance(solution, list):
                    print("수학 문제 풀이 챗봇: 해답은", solution[0], "입니다.")
                else:
                    print("수학 문제 풀이 챗봇:", solution)

        elif choice == "2":
            print("수학 문제 풀이 챗봇: 난이도를 선택하세요 (1단계부터 5단계까지): ")
            stage = int(input("사용자: "))
            if stage < 1 or stage > 5:
                print("수학 문제 풀이 챗봇: 올바른 난이도를 선택하세요.")
                continue

            print("수학 문제 풀이 챗봇: 문제를 풀어보세요.")
            print("수학 문제 풀이 챗봇: 종료하려면 '종료'를 입력하세요.")

            while True:
                problem = generate_math_problem(stage)
                print("수학 문제 풀이 챗봇:", problem)

                if validate_complex_number(problem):
                    print("수학 문제 풀이 챗봇: 복소수 형식은 '3*i'와 같이 입력해주세요.")
                    continue

                solution = solve_math_problem(problem)

                user_answer = input("정답을 입력하세요: ")

                if user_answer.lower() == "종료":
                    print("수학 문제 풀이 챗봇: 문제 풀이를 종료합니다.")
                    break

                if check_answer(solution, user_answer):
                    print("수학 문제 풀이 챗봇: 정답입니다!")
                else:
                    print("수학 문제 풀이 챗봇: 오답입니다. 정답은", solution[0], "입니다.")

        elif choice == "3":
            print("수학 문제 풀이 챗봇: 프로그램을 종료합니다.")
            break

        else:
            print("수학 문제 풀이 챗봇: 올바른 옵션을 선택하세요.")

if __name__ == "__main__":
    main()
