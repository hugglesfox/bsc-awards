from collections import namedtuple
import math
from awards import models, db, app


class StudentManager:
    """Manages student information.

    Args:
        year_level: A string to specify what year level to work with.
                    None for all (default).
    """

    def __init__(self, year_level=None):
        self.year_level = year_level

    def __enter__(self):
        return self

    def __exit__(self, *args):
        db.session.commit()

    def __len__(self):
        return len(models.Student.query.filter_by(year_level=self.year_level).all())

    def __getitem__(self, index):
        if index >= len(self):
            raise IndexError('Student index out of range.')
        return models.Student.query.filter_by(year_level=self.year_level).all()[index]

    def get(self, student_id):
        """Get a student via sudent_id.

        Returns None if the student doesn't exist.

        Args:
            student_id: A string of the id of the wanted student.

        Returns:
            A models student object of the wanted student.
        """
        return models.Student.query.filter_by(student_id=student_id, year_level=self.year_level).first()

    @property
    def attending(self):
        """A readonly int of the amount of students attending."""
        return len(models.Student.query.filter_by(year_level=self.year_level, attending=True).all())


def group_size(student_count=0):
    """Get the sizes of the award groups.

    Args:
        student_count: An interger of the amount of students attending.

    Returns:
        A namedtuple containing size (amount of students in one group),
        count (the amount of groups (excluding the last group))
        and last_size (the amount of students in the last group).
    """
    Groups = namedtuple('Groups', ['size', 'count', 'last_size'])
    for group_size in range(7, 10):
        if 10 > (student_count % group_size) > 4 or student_count % group_size == 0:
            groups = Groups(group_size,
                            math.floor(student_count / group_size),
                            student_count % group_size)

    if groups is None:
        # FIXME: Log level should be warn not info
        app.logging('Not enough students to create groups. \
                     Only creating one group.')
        groups = Groups(student_count, 1, 0)

    return groups


def get_awards(student_id):
    """Get all the awards for a student.

    Args:
        student_id: A string of the student id to get awards for.

    Returns:
        An array of all the models.Awards objects.
    """

    awards = []
    for recipient in models.AwardRecipients.query.filter_by(student_id=student_id).all():
        for award in models.Awards.query.filter_by(award_id=recipient.award_id).all():
            awards.append(award)

    return awards
