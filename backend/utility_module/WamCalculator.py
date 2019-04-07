from database.DataBaseManager import DataBaseManager
import pandas as pd

class WamCalculator:
    def __init__(self):
        """Initialise the WamCalculator with list of dict of
        [{course_name: string, number_of_credits: int, score: float}]

        :param courses: list of courses with their score and number of credits as shown above
        :type list of dict
        """
        self.data_base_manager = DataBaseManager()
        self.data = None

    def add_mark(self, sid, cid, mark):
        """Update the mark of a course for a student in the databse

        :param sid: student ID
        :type: str
        :param cid: course code
        :type: str
        :param mark: result of that course
        :type: float
        :return: database operation result
        :rtype: str
        """
        query = "INSERT INTO wam(sid, cid, mark, credit) VALUES (%s, %s, %s, %s)"
        inputs = (sid, cid, mark, credit, )
        return self.data_base_manager.execute_query(query, inputs)

    def delete_sid(self, sid):
        query = "DELETE FROM wam WHERE sid = %s"
        inputs = (sid, )
        return self.data_base_manager.execute_query(query, inputs)

    def get_student_wam(self, sid):
        query = "SELECT * from wam where sid = %s"
        inputs = (sid, )
        result = self.data_base_manager.execute_query(query, inputs)
        df = pd.DataFrame(data=result, columns=['sid', 'cid', 'mark', 'credit'])
        self.data = df
        return df

    def calculate_wam(self, sid):
        """Calculate wam using the preloaded data from self.courses and
        give a result string which is a summary of their course results and
        final calculated WAM

        :return: result summary string
        :rtype: str
        """
        if self.data is None:
            self.get_student_wam(sid)
        wam, total_credits = 0, 0
        result_string = ''
        for index, row in self.data.iterrows():
            course_name, num_of_credits, mark = row['cid'], row['credit'], row['mark']
            result_string += 'Course name: {}\nNumber of credits: {}\nResult: {}\n'.format(course_name,
                                                                                           num_of_credits,
                                                                                           round(float(mark), 1))
            wam += float(row['mark'])*int(row['credit'])
            total_credits += int(row['credit'])
        wam /= total_credits
        result_string += 'Wam is: {}\nGrade is: {}'.format(round(wam, 1), self.determine_grade(wam))
        #print(result_string)
        return result_string

    def determine_grade(self, wam):
        wam = float(wam)
        if wam > 90:
            return 'HD'
        if wam > 75:
            return 'D'
        if wam > 65:
            return 'CR'
        if wam > 50:
            return 'P'
        return 'F'


if __name__ == '__main__':
    wam_finder = WamCalculator()
    #result = wam_finder.add_mark("z8888888", "COMP9511", "74", "6")
    #result = wam_finder.get_student_wam("z1234567")
    result = wam_finder.calculate_wam("z8888888")
    print(result)
