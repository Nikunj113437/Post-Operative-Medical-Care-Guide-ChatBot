import openai
import threading
import ssl
import smtplib
import gradio as gr
from twilio.rest import Client
from email.message import EmailMessage


# Replace 'YOUR_OPENAI_API_KEY' with your actual API key
openai.api_key = 'YOUR-API-KEY'

# Replace 'YOUR_TWILIO_SID', 'YOUR_TWILIO_AUTH_TOKEN', and 'YOUR_TWILIO_PHONE_NUMBER' with your actual Twilio credentials
TWILIO_SID = 'YOUR-TWILIO-SID'
TWILIO_AUTH_TOKEN = 'YOUR-TWILIO-AUTH-TOKEN'
TWILIO_PHONE_NUMBER = 'YOUR-TWILIO-PHONE-NUMBER'


# Send SMS Reminder
def send_sms(phone_number, message):
    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
    try:
        message = client.messages.create(
            from_=TWILIO_PHONE_NUMBER, to=phone_number, body=message)
        print(f"SMS Reminder sent to {phone_number}. SID: {message.sid}")
    except Exception as e:
        print(f"Error sending SMS reminder to {phone_number}: {e}")


# Send E-mail Reminder
def send_email(email_address, subject, content):
    email_sender = "emailreminders123@gmail.com"
    email_password = "kgoirmnavtvqawjf"
    email_receiver = email_address

    subject = subject
    body = content
    try:
        em = EmailMessage()
        em['From'] = email_sender
        em['To'] = email_receiver
        em['Subject'] = subject
        em.set_content(body)

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.sendmail(email_sender, email_receiver, em.as_string())
            print(f"Email Reminder sent to: {email_address}")

    except Exception as e:
        print(f"Error sending email reminder to {email_address}: {e}")


# Scheduling Reminder through SMS and Email
def schedule_reminder(surgery_type, reminder_type, patient_email, patient_phone, interval):
    while True:
        if patient_email:
            send_email(patient_email, f"Reminder: {reminder_type} for {surgery_type} surgery",
                       f"Don't forget your {reminder_type} for {surgery_type} surgery.")
        if patient_phone:
            send_sms(
                "+91"+patient_phone, f"Reminder: Don't forget your {reminder_type} for {surgery_type} surgery.")
        # Wait for the specified interval before scheduling the next reminder
        threading.Event().wait(interval)


def start_reminder_scheduler(surgery_type, rem_type, rem_time, patient_email, patient_phone):

    # Schedule medication reminders every rem_time days
    if (rem_type == "Medication"):
        medication_thread = threading.Thread(target=schedule_reminder, args=(
            surgery_type, "Medication Reminder", patient_email, patient_phone, (1/rem_time) * 86400))
        medication_thread.start()

    # Schedule follow-up reminders every rem_time days
    if (rem_type == "Follow-up"):
        follow_up_thread = threading.Thread(target=schedule_reminder, args=(
            surgery_type, "Follow-up Appointment Reminder", patient_email, patient_phone, rem_time * 86400))
        follow_up_thread.start()

    # Schedule important recovery milestone reminders every rem_time days
    if (rem_type == "Recovery"):
        milestone_thread = threading.Thread(target=schedule_reminder, args=(
            surgery_type, "Important Recovery Milestone Reminder", patient_email, patient_phone, rem_time * 86400))
        milestone_thread.start()


# Providing ChatBot Role
messages = [{"role": "system", "content": "You are a Supertalented and Genius Post Operative \
            Medical Care Guide ChatBot that can guide patients through post-operative care \
            instructions after a surgery or medical procedure, providing information about wound \
            care, pain management, physical activity, diet, Personalized Recommendations based on \
            surgery type or medical procedure, medical schedule and Emergency \
            Situations by recognizing signs of complications or emergencies during recovery if \
            input by user, and instruct patients on when to seek immediate medical attention in \
            following format:\
            Instruction: \
            Wound Care: \
            Pain Management: \
            Physical Activity and Nutrition: \
            Diet: \
            Personalized Care Recommendations (Based on Surgery Type): \
            Medical Schedule: \
            Emergency Situations: "}]


def post_operative_care_guide(surgery_type, date_of_procedure, complications="",
                              medication_time=None, follow_up_time=None, recovery_time=None,
                              patient_email=None, patient_phone=None):

    # Foe Medication Reminder
    if medication_time:
        if patient_email or patient_phone:
            start_reminder_scheduler(
                surgery_type, "Medication", int(medication_time), patient_email, patient_phone)

    # For Follow-up Appointment Reminder
    if follow_up_time:
        if patient_email or patient_phone:
            start_reminder_scheduler(
                surgery_type, "Follow-up", int(follow_up_time), patient_email, patient_phone)

    # For Important Recovery Milestone Reminder
    if recovery_time:
        if patient_email or patient_phone:
            start_reminder_scheduler(
                surgery_type, "Recovery", int(recovery_time), patient_email, patient_phone)

    message = surgery_type+complications
    messages.append({"role": "user", "content": message})

    summary = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7
    )
    ChatGPT_reply = summary["choices"][0]["message"]["content"]
    messages.append({"role": "assistant", "content": ChatGPT_reply})
    return ChatGPT_reply


# Define the interface with inputs and outputs
iface = gr.Interface(
    fn=post_operative_care_guide,
    inputs=[
        gr.components.Textbox(label="Enter the type of Surgery you had:"),
        gr.components.Textbox(
            label="Enter the date of your Medical Procedure or Surgery (YYYY-MM-DD):"),
        gr.components.Textbox(
            label="Medical Sign of Complications Experienced during Recovery (If Any):"),
        gr.components.Dropdown(['2', '3', '4', '5'],
                               label="Select no. of times you take medicines in a Day: \
                                (Optional for Schedule Reminder)"),
        # gr.components.Textbox(
        #     label="Select no. of times you take medicines in a Day: \
        #         (Optional for scheduling Reminder)"),
        gr.components.Textbox(
            label="After how many days you visit doctor again for follow-up Appointment: \
                (Optional for scheduling Reminder)"),
        gr.components.Textbox(
            label="After how many days you wish to get Important Recovery Milestone Reminder: \
                (Optional for scheduling Reminder)"),
        gr.components.Textbox(
            label="Enter your Email Address for Scheduling Medication, Follow-up Appointments \
                and Important Recovery Milestone Reminders: (Optional)"),
        gr.components.Textbox(
            label="Enter your 10-digit Contact Number for Scheduling Medication, Follow-up Appointments \
                and Important Recovery Milestone Reminders: (Optional)"),
    ],
    outputs="text",
    title="RecoverEase - Your Personalized Post-Operative Guide",
    description="Your Personal Post-Operative Medical Guide Chatbot: Customized recovery instructions, \
                timely reminders, and expert advice tailored to your surgery. Stay on track and \
                ensure a smooth healing journey with our intelligent virtual assistant!",
)

if __name__ == "__main__":
    iface.launch(share=True)
