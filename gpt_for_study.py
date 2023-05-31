import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QVBoxLayout, QPushButton
import openai
from fpdf import FPDF

key = input("Enter your OpenAI API key : ")

openai.api_key = key

topic = input("Enter the topic to study : ")
num_chapter = input("Enter the number of chapters want to study : ")
to_who = input("Enter reader : ")

def generate_chapter(topic = topic, num_chapter = num_chapter, to_who = to_who):
        system_message_01 = """I will give you specific format \n
                               input \n
                               ----------- \n
                               (Economics, 5, Entrepreneur) \n
                               ------------ \n
                               this means "'Economics 'textbook for 'entrepreneur' composed of '5' Chapter" \n

                               Then, assume you as  text book maker, make "'Economics 'textbook optimized to 'entrepreneur' composed of '5' Chapter" in this example with ordering \n

                               NOTE THAT | Don't add any comment. I will directly use it as prompt to other chat! Also, don't say 'I'm just AI model not analyst...'
                               
                               your output format

                               ------------ \n

                               1. ~~~~
                               2. ~~~~
                               ......
                               n. ~~~
                               """
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message_01},
                {"role": "user", "content": f"({topic}, {num_chapter}, {to_who})"}
            ],
            max_tokens=100 * num_chapter
        )

        text = response.choices[0].message.content.strip()
        chapters = text.split('\n')[:num_chapter]
        return chapters


def generate_outline(chapters, towho = to_who):
    outlines = []
    for i in range(len(chapters)):
            system_message_02 = """I'll give you input, then you have to follow the output type

                                   user input type :(Chapter name, For Who such as graduate students)

                                   your output type
                                   -------------- 
                                   1. ~~~~
                                     - 
                                   2. ~~~~
                                     - 
                                   ......
                                   n. ~~~
                                     -

                                   NOTE: Don't attach any additional replys such as "for who... understanding....", except outline. I will directly use it as outline to other chat!\n 
                                         Please follow what I said strictly. please.....
                                    """
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                {"role": "system", "content": system_message_02},
                {"role": "user", "content": f"({chapters[i]}, {towho})"}
                ],
                max_tokens=1000
                )
            outline = response.choices[0].message.content.strip()
            outlines.append(outline)
    return outlines


def generate_handbook(outlines):
    books = []
    for i in range(len(outlines)):
            system_message_02 = """I'll give you an outlne then you have to fill it.
                                   you must write full chapter! not just fill in outline.
                                   Don't reply anything except the result of filling
                                   NOTE: Don't attach any additional replys such as "for who... understanding....", except outline. I will directly use it as outline to other chat!\n 
                                         Please follow what I said strictly. please.....
                                    """
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                {"role": "system", "content": system_message_02},
                {"role": "user", "content": outlines[i]}
                ],
                max_tokens=1000
                )
            writing = response.choices[0].message.content.strip()
            books.append(writing)
    return books

generate_handbook(generate_outline(generate_chapter(topic = topic, num_chapter = num_chapter, to_who = to_who)))