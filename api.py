from fastapi import FastAPI, HTTPException, Depends
from pymongo import MongoClient
from pydantic import BaseModel
from bson import ObjectId
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import certify
from dotenv import load_dotenv
import os
import json
from extract import extract_text_from_pdf
import  boto3
load_dotenv()
username=os.getenv("MONGO_USER")
password=os.getenv("MONGO_PASS")

app = FastAPI()

# MongoDB setup
client = MongoClient(f"mongodb+srv://{username}:{password}@cluster0.mongodb.net/?retryWrites=true&w=majority",tlsCAFAile=certify.where())    


class MatchRequest(BaseModel):
    _id: str
    resumeId: str   


# AWS S3 Configuration
s3_client = boto3.client(
    "s3",
    aws_access_key_id="your-access-key",
    aws_secret_access_key="your-secret-key",
    region_name="your-region"
)

S3_BUCKET_NAME = "your-bucket-name"


def fetch_s3_file(s3_key):
    """Fetch file content from S3."""
    try:
        response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
        return response["Body"].read().decode("utf-8")  # Assuming it's a text-based file
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching file from S3: {str(e)}")



def get_score(jd_text, res_text):
    model = genai.GenerativeModel(model_name="gemini-2.0-flash-thinking-exp-01-21")
    
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
    
    final_score=0
    for key in jsoni:
        final_score+=jsoni[key]["score"]

    return{
        "score":final_score,
        "analysis":jsoni
    }







@app.post("/v1/ap/genai/initiateResumeMatch")
def process_match(data: MatchRequest):
    # fetch jd,resume from s3

    # extract text 

    # if pdf cannot extract text then use paddle ocr to extract text

    # call get_score function

    # save scores on mongo
    
