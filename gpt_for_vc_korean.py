import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QVBoxLayout, QPushButton
import openai
from fpdf import FPDF
import datetime

#1. Question Maker   
def generate_questions(Industry, country, num_questions):
        system_message_01 = """
                            1. As an industry researcher in a pension fund, generate questions about the suggested industry in suggested country to maximize earnings.\n
                            2. I'm going to suggest this format (semiconductor, korea, 10)\n
                               then, you have to give me 10 questions about semiconductor in korea.\n
                            NOTE THAT!! Don't attach any additional comments excepet answer to the request! I will directly use it as prompt to other chat! Also, don't say 'I'm just AI model not analyst...'
                            """
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message_01},
                {"role": "user", "content": f"({Industry}, {country}, {num_questions})"}
            ],
            max_tokens=100 * num_questions
        )

        text = response.choices[0].message.content.strip()
        questions = text.split('\n')[:num_questions]
        return questions



# 2. Prompt Maker
def generate_prompt(questions):
    prompts = []
    for i in range(len(questions)):
            system_message_02 = """1. As a prompt engineer working for a pension fund analyst,
                                      generate a prompt for achieving good answer in order to maximize long-term investment earning rate.\n
                                      I know your not a prompt engineer, it's just assumption, role play.
                                      so don't say 'I'm not an prompt engimeer....'.
                                    2. NOTE THAT!!! Don't attach any additional replys including apologize except prompt about the question. I will directly use it as prompt to other chat!\n 
                                    3. Following below format (it's just an example)\n
                                      Example)
                                      Context: You are a researcher analyzing the value chain in the medical machine industry.\n
                                      Specific requirements: Please provide a comprehensive overview of the value chain in the medical machine industry. Include details about the various processes involved in creating value within this industry. Additionally, present the average operating profit margin for each layer within the value chain as a table format.\n
                                      Clarity and precision: Use clear language and industry-specific terminology to ensure accurate and concise responses.\n
                                      Additional instructions: Include specific numbers for the highest and lowest operating profit margins (OPM) and the highest and lowest volume of production or sales.\n
                                      Output Format: Please present the information in a structured manner with the average OPM table and clearly indicate the highest and lowest figures.\n
                                    \n
                                    NOTE: Please follow what I said strictly. please.....
                                    """
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                {"role": "system", "content": system_message_02},
                {"role": "user", "content": questions[i]}
                ],
                max_tokens=1000
                )
            prompt = response.choices[0].message.content.strip()
            prompts.append(prompt)
    return prompts




# 3. Final Answer
def generate_final_answers(prompts):
    final_answers = []
    for prompt in prompts:
            system_message_02 = """1. I will copy your answer directly to the research report,\n
                                      so don't add any reply such as 'sure. give me prompt' or 'sure. Here is answer'\n
                                   2. It's better not to attach 'Report', 'Introduction', 'Conclusion', unless these are neccesary
                                   """
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_message_02},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=1000
            )
            final_answer = response['choices'][0]['message']['content'].strip()
            final_answers.append(final_answer)
    return final_answers

def translator(contents) : 
    answers = []
    for content in contents:
            system_message_02 = """1. I will copy your answer directly to the research report,\n
                                      so don't add any reply such as 'sure. give me prompt' or 'sure. Here is answer'\n
                                   2. Just Translate it in Korean
                                   """
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_message_02},
                    {"role": "user", "content": content},
                ],
                max_tokens=1000
            )
            result_trans = response['choices'][0]['message']['content'].strip()
            answers.append(result_trans)
    return answers


##통합
def gpt_for_vc(Industry, country, num_questions) :
    Industry = Industry
    country = country
    num_questions = num_questions

    questions = generate_questions(Industry, country, num_questions)

    prompts = generate_prompt(questions)

    final_answers = translator(generate_final_answers(prompts))

    questions = translator(questions)

    return questions, final_answers


class ValueChainPDFApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Value Chain PDF Generator")
        self.layout = QVBoxLayout()

        self.api_key = QLabel("OpenAI API key:")
        self.key = QLineEdit()

        self.label_industry = QLabel("Industry:")
        self.input_industry = QLineEdit()

        self.label_country = QLabel("Country:")
        self.input_country = QLineEdit()

        self.label_num_questions = QLabel("Number of Questions:")
        self.input_num_questions = QLineEdit()

        self.button_generate_pdf = QPushButton("Generate PDF")
        self.button_generate_pdf.clicked.connect(self.generate_pdf)

        self.layout.addWidget(self.api_key)
        self.layout.addWidget(self.key)
        self.layout.addWidget(self.label_industry)
        self.layout.addWidget(self.input_industry)
        self.layout.addWidget(self.label_country)
        self.layout.addWidget(self.input_country)
        self.layout.addWidget(self.label_num_questions)
        self.layout.addWidget(self.input_num_questions)
        self.layout.addWidget(self.button_generate_pdf)

        self.setLayout(self.layout)

    def generate_pdf(self):
        openai.api_key = self.key.text()
        Industry = self.input_industry.text()
        country = self.input_country.text()
        num_questions = int(self.input_num_questions.text())

        final_answers = gpt_for_vc(Industry, country, num_questions)

        now = str(datetime.datetime.today())[:10]

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=20)
        pdf.add_page()

        
        pdf.add_font('ArialUnicodeMS', '', 'Arial_Unicode_MS.ttf', uni=True)
        pdf.set_font('ArialUnicodeMS', '', 11)

        pdf.set_font("ArialUnicodeMS", size= 15)
        pdf.set_text_color(0, 0, 255)
        pdf.cell(0, 10, f"{Industry} {country} {now}", align="C")
        pdf.ln(15)

        for i in range(len(final_answers[0])):
            pdf.set_font('ArialUnicodeMS', size=12)
            pdf.set_text_color(0, 0, 200)
            pdf.multi_cell(0, 10, final_answers[0][i])
            pdf.set_font("ArialUnicodeMS", size=11)
            pdf.set_text_color(0, 0, 0)
            pdf.multi_cell(0, 10, final_answers[1][i] + "\n\n")

        filename = f"{Industry} {country} {now}.pdf"
        pdf.output("./Generated_files/"+filename)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ValueChainPDFApp()
    window.show()
    sys.exit(app.exec_())
