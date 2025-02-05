from openai import OpenAI
import json
import ast
client = OpenAI(api_key = "")


def generate_quiz():
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": "Generate a quiz with 5 multiple-choice questions about the book 'Mara' by Ioan Slavici. Each question should have 3 options, and clearly mark the correct answer in parentheses. Write just the questions and answers nothing more. Generate like a json file, every field will be like this : question<no_question> and if it's answer will be <no_question>answer<no_answer> and dont do the elements nested, also dont need to mark answers with A), or B), or C)."
            }
        ],
        temperature=0.1
    )

    generatedQuiz = completion.choices[0].message.content
    generatedNewQuiz = generatedQuiz[8:-4]
    quiz_dict = ast.literal_eval(generatedNewQuiz)
    #quiz_dict = json.loads(generatedNewQuiz)
    #print(quiz_dict)
    #print(generatedNewQuiz)
    
    return quiz_dict

# generate_quiz()



