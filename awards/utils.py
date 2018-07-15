from collections import namedtuple
import math
from awards import models, db
import config


class StudentManager:
    """Manages student information.

    Args:
        year_levels: A array of integers to specify which year levels
                     to work with. None for all (default).
    """

    def __init__(self, year_level=None):
        self.year_levels = config.Config.YEAR_LEVELS
        if year_level is not None:
            self.year_levels = year_level

    def __enter__(self):
        return self

    def __exit__(self, *args):
        db.session.commit()

    def __len__(self):
        amount = 0
        for year in self.year_levels:
            amount += len(models.Student.query.filter_by(year_level=year).all())
        return amount

    def __getitem__(self, index):
        if index >= len(self):
            raise IndexError('Student index out of range.')

        result = []
        for year in self.year_levels:
            for student in models.Student.query.filter_by(year_level=year).all():
                result.append(student)
        return result[index]

    def get(self, student_id):
        """Get a student via sudent_id.

        Returns None if the student doesn't exist.

        Args:
            student_id: A string of the id of the wanted student.

        Returns:
            A models stself.year_leveludent object of the wanted student.
        """
        results = []
        for year in self.year_levels:
            results.append(models.Student.query.filter_by(student_id=student_id, year_level=year).first())

        for result in results:
            if result is not None:
                return result

    @property
    def attending(self):
        """A readonly int of the amount of students attending."""
        amount = 0
        for year in self.year_levels:
            amount += len(models.Student.query.filter_by(year_level=year, attending=True).all())
        return amount


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
        # FIXME: Raise a more suitable error
        raise NotImplementedError('Cannot calculate group size. Too few students.')

    return groups


def get_awards(student_id):
    """A generator that gets all the awards for a student.

    Args:
        student_id: A string of the student id to get awards for.
    """

    for recipient in models.AwardRecipients.query.filter_by(student_id=student_id).all():
        for award in models.Awards.query.filter_by(award_id=recipient.award_id).all():
            yield award
