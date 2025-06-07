import smtplib
from typing import Dict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from interfaces import CommunicationInterface
from config.settings import SMTP_SERVER, SMTP_PORT, EMAIL_ADDRESS, EMAIL_PASSWORD

class CommunicationAgent(CommunicationInterface):
    
    def __init__(self, ar_requestor_email: str, recruiter_email: str):
        self.ar_requestor_email = ar_requestor_email
        self.recruiter_email = recruiter_email

    def send_email(self, recipient_email: str, subject: str, body: str) -> None:
        try:
            msg = MIMEMultipart()
            msg['From'] = EMAIL_ADDRESS
            msg['To'] = recipient_email
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                server.sendmail(EMAIL_ADDRESS, recipient_email, msg.as_string())
            print(f"Email sent successfully to {recipient_email}")
        except Exception as e:
            print(f"Error sending email to {recipient_email}: {e}")

    def notify(self, match_result: Dict) -> None:
        top_matches = match_result.get("matches", [])
        job_id = match_result.get("job_id", "N/A")
        timestamp = match_result.get("timestamp", "")

        if top_matches:
            self._send_success_notification(top_matches, job_id, timestamp)
        else:
            self._send_no_matches_notification(job_id, timestamp)

    def _send_success_notification(self, top_matches: list, job_id: str, timestamp: str) -> None:
        subject = f"Top Candidates for Job ID {job_id}"
        body = f"Hello,\n\nHere are the top {len(top_matches)} matching candidates for the job posting (Job ID: {job_id}):\n\n"
        
        for idx, profile in enumerate(top_matches, start=1):
            body += (
                f"{idx}. {profile['name']}\n"
                f"   Email: {profile['email']}\n"
                f"   Phone: {profile['phone']}\n"
                f"   Similarity Score: {profile['similarity_score']:.2f}\n"
                f"   Skills: {', '.join(profile['skills'])}\n"
                f"   Experience: {profile['experience']}\n"
                f"   Education: {profile['education']}\n"
                f"   Summary: {profile['summary']}\n\n"
            )
        
        body += f"Timestamp: {timestamp}\n\nRegards,\nRecruitment Matching System"
        self.send_email(self.ar_requestor_email, subject, body)

    def _send_no_matches_notification(self, job_id: str, timestamp: str) -> None:
        subject = f"No Matching Profiles for Job ID {job_id}"
        body = (
            f"Hello,\n\nNo suitable consultant profiles were found for the job posting (Job ID: {job_id}).\n"
            f"Please consider refining the job criteria or uploading more resumes.\n\n"
            f"Timestamp: {timestamp}\n\nRegards,\nRecruitment Matching System"
        )
        self.send_email(self.recruiter_email, subject, body)