import ollama
from extract import extract_text_from_pdf
from dotenv import load_dotenv
from groq import Groq
import json
# prompt=extract_text_from_pdf("/home/aryan/resume/Resumes/shreyanshResume.pdf")
# print(prompt)
# Generate embedding for some text
# response = ollama.embeddings(
#     model='nomic-embed-text',
#     prompt=prompt
# )
# embedding = response.get('embedding')  
# print(embedding)
load_dotenv()
groq = Groq()


def get_jd_details(path):
    jd=extract_text_from_pdf(path)


    jd_prompt="""FROM THE GIVEN JOB DESCRIPTION, EXTRACT THE RELEVANT REQUIREMENTS (experiences, degree, research), SKILLS (technologies and frameworks required, certifications), AND RESPONSIBILITIES (work to do in the job, working hours, shifts, etc.) 
    Return a json with keys as requirements, skills, and responsibilities and values as lists of extracted requirements, skills, and responsibilities respectively. No preambles and postambles, only return the json. enclose strings in double quotes.
    """

    chat_completion = groq.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": jd_prompt                          

                    },
                    {
                        "role": "user",
                        "content": f"JOB DESCRIPTION :-\n {jd}",
                    },
                ],
                model="llama-3.3-70b-versatile",                       
                temperature=0,    
                # Streaming is not supported in JSON mode
                stream=False,
                # Enable JSON mode by setting the response format
            )
    
    print(chat_completion.choices[0].message.content,"\n")
    if chat_completion.choices[0].message.content[0]=='`':
        to_ret=json.loads(chat_completion.choices[0].message.content[10:-4])
    else:
        to_ret=json.loads(chat_completion.choices[0].message.content)
    return to_ret





def get_resume_details(path):
    resume=extract_text_from_pdf(path)
    resume_prompt="""Act as a hiring manager. FROM THE GIVEN RESUME, EXTRACT THE RELEVANT EXPERIENCES (experiences, companies worked for, work and impact, degrees, research papers), SKILLS (technologies and frameworks worked on and certifications), AND PROJECTS (Competitions, Projects, Hackathons, etc.) 
    Return a json with keys as experiences, skills, and projects , values as lists of extracted experiences, skills, and projects respectively. Extract all information and keep it detailed. No preambles and postambles, only return the json. response should start with { and end with }.
    """
    chat_completion = groq.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": resume_prompt                          

                    },
                    {
                        "role": "user",
                        "content": f"RESUME :-\n {resume}",
                    },
                ],
                model="llama-3.3-70b-versatile",                       
                temperature=0,    
                # Streaming is not supported in JSON mode
                stream=False,
                # Enable JSON mode by setting the response format
            )
    # print(chat_completion)
    print(chat_completion.choices[0].message.content,"\n")
    if chat_completion.choices[0].message.content[0]=='`':
        try:
            to_ret=json.loads(chat_completion.choices[0].message.content[10:-4])
        except:
            to_ret=json.loads(chat_completion.choices[0].message.content[6:-4])
    else:
        to_ret=json.loads(chat_completion.choices[0].message.content)
    return to_ret


def match(jd, resume):
    match_prompt=f"""
Act as a hiring team member of a company and give a rating to the given person out of 10 based on his details and company requirements. The rating should be based on how will the person details and works make him a good fit for the company requirements.
\n only return a number between 0 and 10. no preambles or postambles
""" 
    chat_completion = groq.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": match_prompt                          

                    },
                    {
                        "role": "user",
                        "content": f"""COMPANY REQUIREMENTS:-
{jd}\n
PERSON DETAILS:-
{resume}""",
                    },
                ],
                model="llama-3.3-70b-versatile",                       
                temperature=0,    
                # Streaming is not supported in JSON mode
                stream=False,
                # Enable JSON mode by setting the response format
            )
    # print(chat_completion)
    print("MATCH",chat_completion.choices[0].message.content,"\n")
    return int(chat_completion.choices[0].message.content)
    



# response = ollama.chat(
#     model='deepseek-r1:8b',  # Change this to your preferred model
#     messages=[
#         {"role": "system", "content": jd_prompt},
#         {"role": "user", "content":f"JOB DESCRIPTION :-\n {jd}"}
#     ]
# )

# print(response['message']['content'])  # Print the model's response
