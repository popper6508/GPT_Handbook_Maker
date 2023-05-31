import openai
from fpdf import FPDF
import datetime

key = input("Please enter your OpenAI API key: ")
openai.api_key = key

#1. Question Maker   
def generate_questions(Industry, country, num_questions):
        openai.api_key = key
        system_message_01 = """As an industry researcher in a pension fund, generate questions about the suggested industry in suggested country to maximize earnings.\n
                            I'm going to suggest this format (semiconductor, korea, 10)\n
                            then, you have to give me 10 questions about semiconductor in korea.\n
                            NOTE THAT!! Don't attach any additional comments excepet answer to the request! I will directly use it as prompt to other chat! Also, don't say 'I'm just AI model not analyst...'
                            """
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message_01},
                {"role": "user", "content": f"{Industry}, {country}, {num_questions}"}
            ],
            max_tokens=100 * num_questions
        )

        text = response.choices[0].message.content.strip()
        questions = text.split('\n')[:num_questions]
        return questions


# 2. Prompt Maker
def generate_prompt(questions):
    openai.api_key = key
    prompts = []
    for i in range(len(questions)):
            system_message_02 = """As a prompt engineer working for a pension fund analyst,
                                    generate a prompt for achieving good answer in order to maximize long-term investment earning rate.\n
                                    I know your just LLM, this is just an assumption, so don't say 'I'm not an prompt engimeer....'.
                                    Following below format (it's just an example)
                                    Example)
                                    Context: You are a researcher analyzing the value chain in the medical machine industry.\n
                                    Specific requirements: Please provide a comprehensive overview of the value chain in the medical machine industry. Include details about the various processes involved in creating value within this industry. Additionally, present the average operating profit margin for each layer within the value chain as a table format.\n
                                    Clarity and precision: Use clear language and industry-specific terminology to ensure accurate and concise responses.\n
                                    Additional instructions: Include specific numbers for the highest and lowest operating profit margins (OPM) and the highest and lowest volume of production or sales.\n
                                    Output Format: Please present the information in a structured manner with the average OPM table and clearly indicate the highest and lowest figures.\n
                                    Do your best for me to get greatest answer for maximizing our fund's long-term earning by investment decision making from your prompt
                                    \n
                                    NOTE THAT!!! Don't attach any additional comments except prompt to the question. I will directly use it as prompt to other chat!\n
                                    Only show your prompt 
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
    openai.api_key = key
    final_answers = []
    for prompt in prompts:
            system_message_02 = """I will copy all of your answer directly, and paste it other paper,\n
                                   so don't add any reply such as 'sure. give me prompt'
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



##통합
def gpt_for_vc(Industry, country, num_questions) :
    Industry = Industry
    country = country
    num_questions = num_questions
    openai.api_key = key

    questions = generate_questions(Industry, country, num_questions)

    prompts = generate_prompt(questions)

    final_answers = generate_final_answers(prompts)

    return questions, final_answers


##pdf 파일 제작
def making_valuechain_pdf() :
    Industry = input("What industry do you want to research? : ")
    country = input("What country do you want to research? : ")
    num_questions = int(input("How many questions do you want to create? : "))

    final_answers = gpt_for_vc(Industry, country, num_questions)

    now = str(datetime.datetime.today())[:10]

    from fpdf import FPDF

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    pdf.set_font("Arial", "B", 15)
    pdf.set_text_color(0, 0, 255)
    pdf.cell(0, 10, f"{Industry} {country} {now}", align="C")
    pdf.ln(15)

    pdf.add_font('ArialUnicodeMS', '', 'Arial_Unicode_MS.ttf', uni=True)
    pdf.set_font('ArialUnicodeMS', '',11)

    for i in range(len(final_answers[0])):
        pdf.set_font('Arial', 'B',12)
        pdf.set_text_color(0,0,200)
        pdf.multi_cell(0, 10, final_answers[0][i])
        pdf.set_font("ArialUnicodeMS", size=11)
        pdf.set_text_color(0,0,0)
        pdf.multi_cell(0, 10, final_answers[1][i] + "\n\n")

    filename = f"{Industry}_{country}_{now}.pdf"
    pdf.output(filename)


making_valuechain_pdf()