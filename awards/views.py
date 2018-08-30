from flask import render_template, current_app, request, redirect, url_for, session
from flask_classful import FlaskView
from flask_table import Table, Col
from awards import utils, db, models


class IndexView(FlaskView):
    route_base = '/'

    def index(self):
        if not session.get('logged_in'):
           return redirect(url_for('LoginView:get'), code=302)

        current_app.config['NAVBAR_BRAND'] = 'BSC Awards'

        return render_template('index.html')


class LoginView(FlaskView):
    def get(self):
        current_app.config['NAVBAR_BRAND'] = 'BSC Awards'

        logout = False
        if request.args.get('logout') == '1' and session.get('logged_in'):
            session['logged_in'] = False
            logout = True

        return render_template('security/login.html', valid=True, logout=logout)

    def post(self):
        if request.form.get('username') == current_app.config['USERNAME'] \
                and request.form.get('password') == current_app.config['PASSWORD']:
            session['logged_in'] = True
            return redirect(url_for('IndexView:index'), code=302)

        else:
            return render_template('security/login.html', valid=False, logout=False)


class LogoutView(FlaskView):
    def index(self):
        return redirect(url_for('LoginView:get') + '?logout=1')


class MainView(FlaskView):
    def index(self, year_level: int, group: int, page: int):
        if not session.get('logged_in'):
            return redirect(url_for('LoginView:get'), code=302)

        if int(year_level) not in current_app.config['YEAR_LEVELS']:
            return render_template('error/404.html'), 404

        gm = utils.GroupManager(year_level=[year_level])
        current_app.config['NAVBAR_BRAND'] = 'Year {}'.format(year_level)

        try:
            student_group = gm[int(group)]
        except IndexError:
            return render_template('main/completed.html')

        try:
            student = student_group[int(page)]
        except IndexError:
            return render_template('main/applause.html',
                                   year_level=year_level,
                                   group=group + 1,
                                   page=0)
        else:
            awards = utils.get_awards(student.student_id)
            return render_template('main/index.html',
                                   student=student,
                                   awards=awards,
                                   year_level=year_level,
                                   group=group,
                                   page=page + 1)


class AttendanceView(FlaskView):
    def get(self):
        if not session.get('logged_in'):
            return redirect(url_for('LoginView:get'))

        sm = utils.StudentManager()
        current_app.config['NAVBAR_BRAND'] = 'BSC Awards'

        student_id = request.args.get('studentID')
        valid = True
        if student_id is None:
            student = models.Student(student_id='', first_name='', last_name='', form_group='')
        else:
            student = sm.get(student_id)
            if student is None:
                valid = False
                student = models.Student(student_id=student_id, first_name='', last_name='', form_group='')

        return render_template('attendance/index.html',
                               valid=valid,
                               student=student)

    def post(self, student_id):
        if not session.get('logged_in'):
            return redirect(url_for('LoginView:get'), code=302)

        sm = utils.StudentManager()
        student = sm.get(student_id)
        if student is None:
            return redirect(url_for('AttendanceView:get'), code=302)

        if request.form.get('attending') == 'checked':
            student.attending = True
        else:
            student.attending = False

        db.session.commit()

        return redirect(url_for('AttendanceView:get'), code=302)


class AttendanceTable(Table):
    name = Col('Full Name')
    awards = NestedTableCol('Awards', )


class PrintView(FlaskView):
    def index(self):
        if not session.get('logged_in'):
            return redirect(url_for('LoginView:get'))

        sm = utils.StudentManager()

        rows = []

        for student in sm:
            name = '{} {}'.format(student.first_name, student.last_name)
            awards = [award.award_name for award in utils.get_awards(student.student_id)
            rows.append(dict(name=name, awards=awards))

        table = AttendanceTable(rows)

        return render_template('attendance/print.html', table=table)

