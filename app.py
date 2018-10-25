from flask import Flask, render_template, session, request, Response, jsonify
from pylti.flask import lti
from pylti.flask import LTI
import settings
import logging
import json
from logging.handlers import RotatingFileHandler
from rage import Rage

app = Flask(__name__)
app.secret_key = settings.secret_key
app.config.from_object(settings.configClass)

# ============================================
# Logging
# ============================================

formatter = logging.Formatter(settings.LOG_FORMAT)
handler = RotatingFileHandler(
    settings.LOG_FILE,
    maxBytes=settings.LOG_MAX_BYTES,
    backupCount=settings.LOG_BACKUP_COUNT
)
handler.setLevel(logging.getLevelName(settings.LOG_LEVEL))
handler.setFormatter(formatter)
app.logger.addHandler(handler)


# ============================================
# Utility Functions
# ============================================

def return_error(msg):
    return render_template('error.htm.j2', msg=msg)


def error(exception=None):
    app.logger.error("PyLTI error: {}".format(exception))
    return return_error('''Authentication error,
        please refresh and try again. If this error persists,
        please contact support.''')


# ============================================
# Web Views / Routes
# ============================================

# LTI Launch
@app.route('/launch', methods=['POST', 'GET'])
@lti(error=error, request='initial', role='any', app=app)
def launch(lti=lti):
    """
    Returns the launch page
    request.form will contain all the lti params
    """

    # Write the lti params to the console
    app.logger.info(json.dumps(request.form, indent=2))

    # example of getting lti data from the request
    # let's just store it in our session
    session['lis_person_name_full'] = request.form.get('lis_person_name_full')
    session['roles'] = request.form.get('roles')

    #
    # Render either the student view or the lecturer view
    #
    if LTI.is_role(lti, 'lecturer'):
        # TODO I'm hard coding a class here until new activities stop killing the server backend
        context = request.form.get('lis_course_section_sourcedid')
        rage = Rage()
        rage.login(settings.RAGE_USERNAME, settings.RAGE_PASSWORD)
        rage.setup_activity('Third Class')
        results = rage.get_results()
        return render_template('launch.htm.j2', lis_person_name_full=session['lis_person_name_full'],
                               rage_host=settings.RAGE_GAME_HOST,
                               rage_tracker_id=settings.RAGE_TRACKER_ID,
                               results=results,
                               rage_token=rage.the_token,
                               results_json=json.dumps(results),
                               class_name='Third Class',
                               roles=session['roles'])
    else:
        user_id = request.form.get('user_id')
        student_email_address = request.form.get('lis_person_contact_email_primary')
        rage = Rage()
        rage.login(settings.RAGE_USERNAME, settings.RAGE_PASSWORD)
        rage.setup_activity('Third Class')
        rage.add_student(user_id, student_email_address)
        rage.login(user_id, settings.RAGE_DEFAULT_STUDENT_PASSWORD)

        return render_template('student.htm.j2', lis_person_name_full=session['lis_person_name_full'],
                               rage_host=settings.RAGE_GAME_HOST,
                               rage_tracker_id=settings.RAGE_TRACKER_ID,
                               rage_token=rage.the_token,
                               send_results=send_results,
                               roles=session['roles'])


@app.route('/send', methods=['GET'])
@lti(error=error, request='session', app=app)
def send_results(lti=lti):
    score = request.args.get("score")
    ret = lti.post_grade(score)
    return jsonify("grade={}".format(ret))


# Home page
@app.route('/', methods=['GET'])
def index(lti=lti):
    return render_template('index.htm.j2')


# LTI XML Configuration
@app.route("/xml/", methods=['GET'])
def xml():
    """
    Returns the lti.xml file for the app.
    XML can be built at https://www.eduappcenter.com/
    """
    try:
        return Response(render_template(
            'lti.xml.j2'), mimetype='application/xml'
        )
    except:
        app.logger.error("Error with XML.")
        return return_error('''Error with XML. Please refresh and try again. If this error persists,
            please contact support.''')
