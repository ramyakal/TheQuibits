from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import pandas as pd
import io
import pickle
import joblib
from pydantic import BaseModel
from pymongo import MongoClient
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
from fastapi.responses import FileResponse
import openai 
app = FastAPI()
load_dotenv()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
api_key = os.getenv("OPENAI_API_KEY")
# MongoDB Atlas connection details
mongodb_url = os.getenv("MONGODB_URL")
client = MongoClient(mongodb_url)
db = client["zeroshield"]
users_collection = db["users"]

# User model
class User(BaseModel):
    username: str
    password: str

# User registration endpoint

@app.post("/")
def temp():
    print("Success!")


@app.post("/register")
def register(user: User):
    # print(user)
    existing_user = users_collection.find_one({"username": user.username})
    if existing_user:
        return {"message": False}
    else:
        users_collection.insert_one(user.dict())
        return {"message": True}

# User login endpoint
@app.post("/login")
def login(user: User):
    existing_user = users_collection.find_one({"username": user.username})
    if existing_user and existing_user["password"] == user.password:
        return {"username": user.username, "message": True}
    else:
        return {"message": False}



main_model = pickle.load(open('./Models/RandomForestmodel', 'rb'))
botmodel = pickle.load(open('./Models/bot_model.pkl', 'rb'))
XGB_model=pickle.load(open('./Models/XGB', 'rb'))
ddos_model = pickle.load(open('./Models/ddos_model.pkl', 'rb'))
ddoshulk_model = pickle.load(open('./Models/ddoshulk_model.pkl', 'rb'))
dos_goldeneye_model = pickle.load(open('./Models/dos_goldeneye_model.pkl', 'rb'))
dos_slowhttptest_model = pickle.load(open('./Models/dos_slowhttptest_model.pkl', 'rb'))
dos_slowloris_model = pickle.load(open('./Models/dos_slowloris_model.pkl', 'rb'))
ftppatator_model = pickle.load(open('./Models/FTP- PATATOR_model.pkl', 'rb'))
infiltration_model = pickle.load(open('./Models/infiltration_model.pkl', 'rb'))
ssh_patator_model = pickle.load(open('./Models/ssh_patator_model.pkl', 'rb'))
webattack_bruteforce_model = pickle.load(open('./Models/webattack_bruteforce_model.pkl', 'rb'))
webattack_sqlinjection_model = pickle.load(open('./Models/webattack_sqlinjection_model.pkl', 'rb'))
known_attack_models = {botmodel: "bot",ddos_model: "ddos", ddoshulk_model: "ddoshulk", dos_goldeneye_model: "ddosgoldeneye", dos_slowhttptest_model: "dosslowhttptest", dos_slowloris_model: "dosslowloris", ftppatator_model: "ftppatator", infiltration_model: "infiltration", ssh_patator_model: "sshpatator", webattack_bruteforce_model: "webattackbruteforce", webattack_sqlinjection_model: "webattacksqlinjection"}




@app.post("/upload")
async def upload_file(file: UploadFile = File(...), username: str = Form(...), fileType:str =Form(...)):
    if fileType=='ransomware':
        df = pd.read_csv(file.file, index_col=False,dtype='unicode')
        # Drop unnecessary columns
        cols_to_drop = ['FileName', 'md5Hash']
        df = df.drop(columns=cols_to_drop)
        columns = ["Machine", "DebugSize", "NumberOfSections", "SizeOfStackReserve", "MajorOSVersion", "BitcoinAddresses"]
        for col in columns:
            df[col] = df[col].astype('category')
            df[col] = df[col].cat.codes
        df = df.drop_duplicates(keep='last')
        num_features_used_for_training = 15  
        X = df.iloc[:, :num_features_used_for_training].values
        prediction = XGB_model.predict(X)
        count_0 = np.count_nonzero(test_pred == 0)
        count_1 = np.count_nonzero(test_pred == 1)

        if count_0 > count_1:  #BENIGN
            return {"Prediction": "Not Malicious",
                    "nonmal" : count_0,
                    "mali" : count_1,
                    "attack": "NA"}
        if count_1>count_0:  #MALICIOUS
            attack = "ransomware"
            print(attack)
            print(username)
            send_email(username, attack)
            # response = getchatgpt(type_of_the_attack
        # Display prediction results
            return {
                "Prediction": "malicious",
                "nonmal": count_0,
                "mali": count_1,
                "attack": ransomware}
    if fileType=='zero-day':
        df = pd.read_csv(file.file, index_col=False, dtype='unicode')

        df.dropna(inplace=True)
        df = df[~df.isin([np.nan, np.inf, -np.inf]).any(axis=1)]
        # colsfromindex = [' Subflow Bwd Bytes',' ECE Flag Count',' Fwd URG Flags',' Active Max','Init_Win_bytes_forward',' act_data_pkt_fwd',' Bwd Header Length',' min_seg_size_forward',' Fwd Header Length', ' Label']
        # df.drop(colsfromindex, axis=1, inplace=True)

        print("processing")
        # Replace infinite and large values with NaN
        df = df.apply(pd.to_numeric, errors='coerce')
        df.replace([np.inf, -np.inf], np.nan, inplace=True)
        df.fillna(0, inplace=True)  # Replace NaN with 0


        print("predicting")
        prediction = main_model.predict(df)
        prediction = (prediction > 0.5).astype(int)
        prediction = list(prediction)

        count_0, count_1 = prediction.count(0), prediction.count(1)

        if count_1 == 0:  #BENIGN
            return {"Prediction": "Not Malicious",
                    "nonmal" : count_0,
                    "mali" : count_1,
                    "attack": "NA"}
        else:  #MALICIOUS
            attack = ""
            foundornot = False
            no_of_records = len(df)

            l = []

            for model in known_attack_models:
                whichpred = model.predict(df)
                inliers = list(whichpred).count(1)
                l.append(inliers)
            
            # for i in l:
            #     if i != 0:
            #         foundornot = True
            # if foundornot == True:
            #     index = l.index(max(l))
            #     attack = list(known_attack_models.values())[index]
            # else:
            #     attack="Zero-day Attack"

            for i in known_attack_models:
                whichpred = i.predict(df)
                inliers = list(whichpred).count(1)
                if inliers > (no_of_records//2):
                    attack = known_attack_models[i]
                    break
            if attack=="":
                attack="zeroday"

            print(username)
            send_email(username, attack)
            # response = getchatgpt(type_of_the_attack
            print(attack)
            return {"Prediction": "malicious",
                    "nonmal" : count_0,
                    "mali" : count_1,
                    "attack": attack}



def send_email(email, attack):
    # Email configuration
    sender_email = "elsi22103@gmail.com"
    sender_password = "lisaEJ#22"

    subject = f"Urgent Security Alert: {attack} Attack Detected"
    message = f"""Subject: {subject}

Dear {email},
We have discovered some alarming findings. It appears that your network has been targeted and attacked by a malicious entity utilizing the {attack} method.

This type of attack can have severe consequences, ranging from data breaches to system malfunctions. To safeguard your network and protect your sensitive information, we strongly recommend taking immediate action.

We understand that this situation is concerning, but taking proactive measures is crucial for protecting your network from further harm.

Please do not hesitate to reach out if you require any assistance or guidance during this process. Our team is here to support you in any way we can.

Stay vigilant,

Team G70,
Detective Zero-day."""

    try:
        # Connect to SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)  
        server.ehlo()
        server.starttls()
        server.login(sender_email, sender_password)

        # Send email
        server.sendmail(sender_email, email, message)
        server.quit()

        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email. Error: {str(e)}")


def get_chat_gpt(attack):
    

# Now you can use the API key in your OpenAI calls
    openai.api_key = "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"
    # openai.api_key = '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'

    # Define your chat function
    def chat_with_gpt(prompt):
        response = openai.Completion.create(
            engine='text-davinci-003',  # Specify the GPT-3.5 engine
            prompt=prompt,
            max_tokens=200,  # Adjust the response length as needed
            n=1,  # Number of responses to generate
            stop=None,  # Optional stopping criteria
            temperature=0.7,  # Controls the randomness of the output
            timeout=10,  # Maximum time (in seconds) to wait for a response
        )

        if 'choices' in response and len(response['choices']) > 0:
            return response['choices'][0]['text'].strip()
        else:
            return None

    # Example usage
    prompt = f"Give information of the attack {attack} and suggestions"
    response = chat_with_gpt(prompt)
    return response

@app.post("/moreinfo")
async def more_info(attack: str):
    response = get_chat_gpt(attack)
    return {"info": response}

# Run the FastAPI server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


    