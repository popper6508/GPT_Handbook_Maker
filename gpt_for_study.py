import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QVBoxLayout, QPushButton
import openai
from fpdf import FPDF

def generate_chapter(topic, num_chapter, to_who):
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


def generate_outline(chapters, towho):
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


def gpt_for_book(topic, num, forwho) :
    chapters = generate_chapter(topic, num, forwho)
    outlines = generate_outline(chapters, forwho)
    books = generate_handbook(outlines)
    return chapters, books
     

class ValueChainPDFApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Book Generator")
        self.layout = QVBoxLayout()

        self.api_key = QLabel("OpenAI API key:")
        self.key = QLineEdit()

        self.label_Topic = QLabel("Topic:")
        self.input_Topic = QLineEdit()

        self.label_Num_of_Chapter = QLabel("Number of Chapters:")
        self.input_Num_of_Chapter = QLineEdit()

        self.label_Make_for_Who = QLabel("Make for Who :")
        self.input_Make_for_Who = QLineEdit()

        self.button_generate_pdf = QPushButton("Generate Book")
        self.button_generate_pdf.clicked.connect(self.generate_pdf)

        self.layout.addWidget(self.api_key)
        self.layout.addWidget(self.key)
        self.layout.addWidget(self.label_Topic)
        self.layout.addWidget(self.input_Topic)
        self.layout.addWidget(self.label_Num_of_Chapter)
        self.layout.addWidget(self.input_Num_of_Chapter)
        self.layout.addWidget(self.label_Make_for_Who)
        self.layout.addWidget(self.input_Make_for_Who)
        self.layout.addWidget(self.button_generate_pdf)

        self.setLayout(self.layout)

    def generate_pdf(self):
        openai.api_key = self.key.text()
        Topic = self.input_Topic.text()
        Num_of_Chapter = self.input_Num_of_Chapter.text()
        Make_for_Who = int(self.input_Make_for_Who.text())

        final_answers = gpt_for_book(Topic, Num_of_Chapter, Make_for_Who)

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=20)
        pdf.add_page()

        pdf.set_font("Arial", "B", 15)
        pdf.set_text_color(0, 0, 255)
        pdf.cell(0, 10, f"{Topic} for {Make_for_Who}", align="C")
        pdf.ln(15)

        pdf.add_font('ArialUnicodeMS', '', 'Arial_Unicode_MS.ttf', uni=True)
        pdf.set_font('ArialUnicodeMS', '', 11)

        for i in range(len(final_answers[0])):
            pdf.set_font('Arial', 'B', 12)
            pdf.set_text_color(0, 0, 200)
            pdf.multi_cell(0, 10, final_answers[0][i])
            pdf.set_font("ArialUnicodeMS", size=11)
            pdf.set_text_color(0, 0, 0)
            pdf.multi_cell(0, 10, final_answers[1][i] + "\n\n")

        filename = f"{Topic} text book for {Make_for_Who}.pdf"
        pdf.output(filename)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ValueChainPDFApp()
    window.show()
    sys.exit(app.exec_())

