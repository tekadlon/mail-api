from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from imapclient import IMAPClient

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MailRequest(BaseModel):
    email: str
    token: str

@app.post("/get-mails")
async def get_mails(req: MailRequest):
    try:
        with IMAPClient('outlook.office365.com', ssl=True) as client:
            client.oauth2_login(req.email, req.token)
            client.select_folder('INBOX')
            ids = client.search(['ALL'])
            messages = client.fetch(ids[-10:], ['ENVELOPE'])
            mails = [
                {
                    'subject': msg[b'ENVELOPE'].subject.decode(),
                    'from': f"{msg[b'ENVELOPE'].from_[0].mailbox.decode()}@{msg[b'ENVELOPE'].from_[0].host.decode()}",
                    'date': msg[b'ENVELOPE'].date.strftime("%Y-%m-%d %H:%M:%S")
                }
                for msg in messages.values()
            ]
            return {'mails': mails}
    except Exception as e:
        return {'error': str(e)}
