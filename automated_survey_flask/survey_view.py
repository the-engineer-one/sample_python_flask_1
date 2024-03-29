from . import app
from .models import Survey
from flask import url_for, session
from twilio.twiml.voice_response import VoiceResponse
from twilio.twiml.messaging_response import MessagingResponse


@app.route('/voice')
# @app.route('/')
def voice_survey():
    response = VoiceResponse()
    survey = Survey.query.first()
    if survey_error(survey, response.say):
        return str(response)
    welcome_user(survey, response.say)
    redirect_to_first_question(response, survey)
    return str(response)


@app.route('/message')
def sms_survey():
    response = MessagingResponse()

    survey = Survey.query.first()
    if survey_error(survey, response.message):
        return str(response)

    if 'question_id' in session:
        response.redirect(url_for('answer',
                                  question_id=session['question_id']))
    else:
        welcome_user(survey, response.message)
        redirect_to_first_question(response, survey)
    return str(response)


def redirect_to_first_question(response, survey):
    first_question = survey.questions.order_by('id').first()
    first_question_url = url_for('question', question_id=first_question.id)
    response.redirect(url=first_question_url, method='GET')


def welcome_user(survey, send_function):
    welcome_text = 'Welcome to the %s , we will repeat question two times. Now you are going to Hear some questions, BEST OF LUCK.' % survey.title
    send_function(welcome_text, voice='alice', language='en-AU')


def survey_error(survey, send_function):
    if not survey:
        send_function('Sorry, but there are no surveys to be answered.')
        return True
    elif not survey.has_questions:
        send_function('Sorry, there are no questions for this survey.')
        return True
    return False
