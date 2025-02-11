# import spacy

# nlp = spacy.load('en_core_web_sm')
# with open('trc_ml.txt', 'r') as file:
#     text = file.read()

# doc = nlp(text)
# for ent in doc.ents:
#     print(ent.text, ent.label_)





import json
import streamlit as st
import chromadb
from pyresparser import ResumeParser
import os
import google.generativeai as genai
from extract import extract_text_from_pdf
from v2 import get_jd_details, get_resume_details,match
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import ollama

client = chromadb.Client()
collection_name = "resume_collection"
API_KEY ="AIzaSyBxtMRRQPVj6ViJqWl_SfcLuIP0-cwtCTQ"
genai.configure(api_key=API_KEY)

        

# client.delete_collection(name=collection_name)
collection = client.get_or_create_collection(name=collection_name) #,metadata={"hnsw:space": "cosine"}

st.sidebar.title("Job Description PDF Upload")
st.session_state.uploaded_file = st.sidebar.file_uploader("Choose a PDF file", type="pdf")
st.session_state.n=st.text_input("Enter the number of top resumes you want ")

if "skills" not in st.session_state:
    st.session_state.skills = None
if "n" not in st.session_state:
    st.session_state.n =    None

if st.session_state.uploaded_file and st.session_state.n :
    with open("/home/aryan/resume/sidebar/job_description.pdf", "wb") as f:
        f.write(st.session_state.uploaded_file.getbuffer())
    st.sidebar.success("File uploaded successfully")
    jd_data = ResumeParser('/home/aryan/resume/sidebar/job_description.pdf').get_extracted_data()
    skills = [skill.lower() for skill in jd_data['skills']]
    st.session_state.skills = skills
    st.sidebar.write("Skills extracted from the job description:")
    st.sidebar.write(skills)
    


if st.session_state.skills:
    


    st.title("Resume Data Extraction")
    resume_directory = "/home/aryan/resume/Resumes"
    resume_data = []

    page = st.radio("Select Page:", ["V0 (without LLM)", "V1 (llm, seperate skills, experience, projects)","V2 (direct prompt to gemini)"])
    
    if page=="V0 (without LLM)":
        if st.button("Extract Resume Data"):
            for filename in os.listdir(resume_directory):
                if filename.endswith(".pdf"):
                    file_path = os.path.join(resume_directory, filename)
                    data = ResumeParser(file_path).get_extracted_data()
                    
                    
                    skill_score = 0
                    exp_score=data["total_experience"]
                    
                    man_skills = [skill.lower() for skill in data["skills"]]
                    for skill in st.session_state.skills:
                        if skill in man_skills:
                            skill_score += 1
                    
                    # Initialize ChromaDB client
                    combined_text= extract_text_from_pdf(file_path)
                    embed_google = genai.embed_content(
                model="models/text-embedding-004",
                content=combined_text
            )
                    metas={"name":filename}
                    if data["experience"]:
                        metas["experience"]="\n".join(data["experience"])
                    if data["designation"]:
                        metas["designation"]="\n".join(data["designation"])
                    if data["degree"]:
                        metas["degree"]="\n".join(data["degree"])
                    if data["company_names"]:
                        metas["company"]="\n".join(data["company_names"])
                    if data["skills"]:
                        metas["skills"]= ",".join(man_skills)
                    metas["skills_score"]=skill_score
                    metas["experience_score"]=exp_score



                    collection.add(
                        documents=[combined_text],
                        embeddings=embed_google['embedding'],  #[embedding_vector],
                        metadatas=[metas],
                        ids=[str(filename)]
                    )
                
            # Step 2: Combine user query with their needs
            user_query = extract_text_from_pdf("/home/aryan/resume/sidebar/job_description.pdf")
     
            query_google = genai.embed_content(
                model="models/text-embedding-004",
                content=user_query
            )
      
            
            # Step 3: Perform semantic search in ChromaDB
            results = collection.query(
                query_embeddings=query_google['embedding'],  # [embedding_query]
                n_results=int(st.session_state.n)
            )
            
            
            top_resumes = [id for id in results["ids"]]
            st.write("Top Resumes:")
            rank=1
            ranked=[]
            for resume_id in top_resumes[0]:
                # st.title(f"Rank {rank}")
                # st.write(f"Displaying {resume_id} in PDF format:")
                # import fitz  # PyMuPDF

                # resume_path = os.path.join(resume_directory, resume_id)
                # pdf_document = fitz.open(resume_path)

                # for page_num in range(len(pdf_document)):
                #     page = pdf_document.load_page(page_num)
                #     pix = page.get_pixmap()
                #     img_path = f"/home/aryan/resume/temp_images/{resume_id}_page_{page_num}.png"
                #     os.makedirs(os.path.dirname(img_path), exist_ok=True)
                #     pix.save(img_path)
                #     st.image(img_path)


                data = collection.get(ids=[resume_id])
                # st.write(data)
                data=data["metadatas"][0]
                
                # st.write(f"Extracted data from {data['name']}:")
                # if data.get("skills"):
                #     st.write("Skills:")
                #     st.write(data["skills"])
                #     st.write("Skills Score:", data['skills_score'])
                # if data.get("experience"):
                #     st.write("Experience:")
                #     st.markdown(data['experience'])
                # if data.get("company"):
                #     st.write("Company:\n", data['company'])
                # if data.get("degree"):
                #     st.write("Degree:\n", data['degree'])
                # if data.get("Designation"):
                #     st.write("Designation:\n", data['designation'])
                # if data.get("experience_score"):
                #     st.write("years of experience:\n", data['experience_score'])
                
            
                # st.write(f"Semantic Score of :", results['distances'][0][rank-1])
                # st.write("________________________________________")

                

                # Normalize the skills score
                min_score = 0
                max_score = len(st.session_state.skills)
                normalized_skill_score = (data['skills_score'] - min_score) / (max_score - min_score) if max_score != min_score else 0

                # st.write("Normalized Skills Score:", normalized_skill_score)
                # st.write("final score:", normalized_skill_score - results['distances'][0][rank-1]+data['experience_score']/5)
                data["final_score"]=normalized_skill_score - results['distances'][0][rank-1]+data['experience_score']/5
                ranked.append((resume_id,data["final_score"]))





                
                rank+=1
            
            ranked.sort(key=lambda x: x[1], reverse=True)
            rank=1
            for res in ranked:
                st.title(f"Rank {rank}")
                resume_id=res[0]
                st.write(f"Displaying {resume_id} in PDF format:")
                
                import fitz  # PyMuPDF

                resume_path = os.path.join(resume_directory, resume_id)
                pdf_document = fitz.open(resume_path)

                for page_num in range(len(pdf_document)):
                    page = pdf_document.load_page(page_num)
                    pix = page.get_pixmap()
                    img_path = f"/home/aryan/resume/temp_images/{resume_id}_page_{page_num}.png"
                    os.makedirs(os.path.dirname(img_path), exist_ok=True)
                    pix.save(img_path)
                    st.image(img_path)


                data = collection.get(ids=[resume_id])
                # st.write(data)
                data=data["metadatas"][0]
                
                st.write(f"Extracted data from {data['name']}:")
                if data.get("skills"):
                    st.write("Skills:")
                    st.write(data["skills"])
                    st.write("Skills Score:", data['skills_score'])
                if data.get("experience"):
                    st.write("Experience:")
                    st.markdown(data['experience'])
                if data.get("company"):
                    st.write("Company:\n", data['company'])
                if data.get("degree"):
                    st.write("Degree:\n", data['degree'])
                if data.get("Designation"):
                    st.write("Designation:\n", data['designation'])
                if data.get("experience_score"):
                    st.write("years of experience:\n", data['experience_score'])
                
            
                st.write(f"Semantic Score of :", results['distances'][0][rank-1])
                st.write("________________________________________")

                st.write("Final Score:",res[1])
                rank+=1
            client.delete_collection(name=collection_name)
    

    elif page=="V1 (llm, seperate skills, experience, projects)":
        if st.button("Extract Resume Data"):
            jd_details=get_jd_details("/home/aryan/resume/sidebar/job_description.pdf")
            st.title("JD DETAILS")
            st.json(jd_details)
            for filename in os.listdir(resume_directory):
                if filename.endswith(".pdf"):
                    file_path = os.path.join(resume_directory, filename)
                    rd=get_resume_details(file_path)
                    st.title(f"Resume: {filename}")
                    st.json(rd)
                    m1=match(jd_details["requirements"],rd["experiences"])
                    m2=match(jd_details["skills"],rd["skills"])
                    m3=match(jd_details["responsibilities"],rd["projects"])
                    st.json({"name":filename,"experience":rd["experiences"],"skills":rd["skills"],"projects":rd["projects"],"match":m1+m2+m3})
                    st.write("scores:")
                    st.json({"experience":m1,"skills":m2,"projects":m3})
    else:
        if st.button("Extract Resume Data"):
            model = genai.GenerativeModel(model_name="gemini-2.0-flash-thinking-exp-01-21")
            jd_text=extract_text_from_pdf("/home/aryan/resume/sidebar/job_description.pdf")
            # jd_uploaded=genai.upload_file(path="/home/aryan/resume/sidebar/job_description.pdf",display_name="job_description")
            bp="""
    You are an expert hiring assistant tasked with evaluating a candidate's resume against a given job description. Your goal is to provide a detailed and fair assessment of the candidate's suitability for the role. Analyze the resume and job description carefully, and provide your evaluation in the form of a JSON output.

    The JSON output should contain the following structure:
    Each key in the JSON should represent a specific evaluation criteria ( 'Relevant Experience', 'Relevant Skills', 'Education', 'Achievements', 'Soft Skills').
    
    For each criteria, the value should be a JSON object with the following keys:
    positive_points: A string describing the positive aspects of the candidate's resume for this criteria.
    negative_points: A string describing the negative aspects or gaps in the candidate's resume for this criteria.
    score: A score out of 10, reflecting how well the candidate meets this criteria.
 
    Instructions:
    Carefully review the job description and the candidate's resume.
    For Relevant Experience, look for the number of years of experience, the relevance of the work to the job description, and the impact of the candidate's work.
    For Relevant Skills, look for the presence of the required skills in the resume and the depth of experience with those skills.
    For Education, don't decrease the score if candidate is currently persuing the degree. just look at the degree, college and associated details.
    For soft skills, don't look for keywords, instead analyse the soft skills on the basis of solid examples in the resume
    
    For each criteria, provide a detailed analysis of the candidate's strengths (positive_points) and weaknesses (negative_points).
    Assign a score out of 10 for each criteria based on how well the candidate matches the job requirements.

    Ensure the output is strictly in JSON format. No preambles and postambles.
    """
            for filename in os.listdir(resume_directory):
                file_path = os.path.join(resume_directory, filename)
                res_text=extract_text_from_pdf(file_path)
                # sample_file = genai.upload_file(path=file_path,display_name=filename,mime_type="application/pdf")
                st.write(f"Displaying {filename} in PDF format:")
                
                import fitz  # PyMuPDF

                
                pdf_document = fitz.open(file_path)

                for page_num in range(len(pdf_document)):
                    page = pdf_document.load_page(page_num)
                    pix = page.get_pixmap()
                    img_path = f"/home/aryan/resume/temp_images/{filename}_page_{page_num}.png"
                    os.makedirs(os.path.dirname(img_path), exist_ok=True)
                    pix.save(img_path)
                    st.image(img_path)
                print("Analysing resume ...")
                response = model.generate_content([bp+f"\nJOB DESCRIPTION :-\n{jd_text}\n\nRESUME :-{res_text}"],safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,

            },generation_config={"temperature": 1})
                
                # response = ollama.chat(
                #     model='deepseek-r1:8b',  # Change this to your preferred model
                #     messages=[
                #         {"role": "system", "content": bp},
                #         {"role": "user", "content":f"\nJOB DESCRIPTION :-\n{jd_text}\n\nRESUME :-{res_text}"}
                #     ]
                # )

                # print(response['message']['content'])  # Print the model's response

                print(response.text)
                
                jsoni=json.loads(response.text[7:-4])
                st.json(jsoni)
                final_score=0
                for key in jsoni:
                    final_score+=jsoni[key]["score"]

                st.write("Final Score gemini:",final_score)
                st.write("Final Score ollama:")




    # st.write("Top Resumes:")




# ResumeParser('/home/aryan/resume/sidebar/job_description.pdf').get_extracted_data()

# print(json.dumps(data, indent=2))





# from pyresumize import ResumeEngine    
# r_parser=ResumeEngine()    
# r_parser.set_custom_keywords_folder("data")    
# json=r_parser.process_resume("Aryan_Resume_latest (5).pdf")    
# print(json)