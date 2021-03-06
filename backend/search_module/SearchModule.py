"""
    The SearchModule class is responsible for formulating the responses from the question provided
    by QueryModule. It manages how each type of query should be responded and provides the final
    answer that is shown to user on UI. It manages Utility Module as well since some responses requires
    Utility Module to work.
"""
from database.DataBaseManager import DataBaseManager
from utility_module.UtilityModule import UtilityModule
from conf.Error import QueryError, ConsultationError
from conf.Response import FallbackResponse
from conf.Logger import Logger
import random

"""
    Logger setup
"""
logger = Logger(__name__).log


class SearchModule:
    def __init__(self, database_manager=DataBaseManager()):
        """
            Initialize the Response module class which act as a search engine as well.
            It contains a data base connection and query_map is responsible for handling different types
            of data retrieval functions. The keys inside query_map have to match an intent name on Dialogflow.
            It also instantiate a utility module class which will be responsible for queries that requires it.
            On each call, it uses its database instance to perform the query to database if required to get the answer.
        """
        self.database_manager = database_manager
        self.utility_module = UtilityModule(database_manager=self.database_manager)

        """
            Response function mapping
        """
        self.query_map = {
            'all_courses_queries': self.respond_to_all_courses_queries,
            'announcement_queries': self.respond_to_announcement_queries,
            'course_outline_queries': self.respond_to_course_outline_queries,
            'course_outline_queries_with_followup-user_input_course_code': self.respond_to_course_outline_queries,
            'course_fee_queries': self.respond_to_course_fee_queries,
            'course_fee_queries_with_followup-user_input_course_code': self.respond_to_course_fee_queries,
            'course_location_queries': self.respond_to_course_location_queries,
            'course_location_queries_with_followup-user_input_course_code': self.respond_to_course_location_queries,
            'indicative_hours_queries': self.respond_to_course_indicative_hours_queries,
            'indicative_hours_queries_with_followup-user_input_course_code': self.respond_to_course_indicative_hours_queries,
            'offering_term_queries': self.respond_to_course_offering_term_queries,
            'offering_term_queries_with_followup-user_input_course_code': self.respond_to_course_offering_term_queries,
            'prerequisites_queries': self.respond_to_course_prerequisites_queries,
            'prerequisites_queries_with_followup-user_input_course_code': self.respond_to_course_prerequisites_queries,
            'school_and_faculty_queries': self.respond_to_course_school_and_faculty_queries,
            'school_and_faculty_queries_with_followup-user_input_course_code': self.respond_to_course_school_and_faculty_queries,
            'send_outline_queries': self.respond_to_course_send_outline_queries,
            'send_outline_queries_with_followup-user_input_course_code': self.respond_to_course_send_outline_queries,
            'study_level_queries': self.respond_to_course_study_level_queries,
            'study_level_queries_with_followup-user_input_course_code': self.respond_to_course_study_level_queries,
            'consultation_booking': self.respond_to_course_consultation_booking,
            'consultation_booking_with_followup-user_input_course_code_with_followup-user_input_time_and_date': self.respond_to_course_consultation_booking,
            'consultation_booking_with_followup-user_input_time_and_date_with_followup-user_input_course_code': self.respond_to_course_consultation_booking,
            'consultation_cancel': self.respond_to_course_consultation_cancel,
            'wam_admin_queries': self.respond_to_wam_admin_queries,
            'wam_student_queries': self.respond_to_wam_student_queries,
            'rating_queries': self.response_to_rating_queries,
            'adk_course_queries': self.respond_to_course_isadk_queries,
            'consultation_view': self.respond_to_course_consultation_view,
            'course_timetable_queries': self.respond_to_timetable_queries
        }

    def respond(self, message):
        """ This function should be the entry point into SearchModule.
        Messages from the query module is passed into here for information search
        and responses.

        :param message: message from Dialogflow
        :type dict
        :return: response
        :rtype str
        """
        logger.info(
            'Response module recieved:\n\tIntent: {}\n\tFullfillment text: {}'.format(message.intent, message.message))
        # If fallback or welcome or followup, we don't need to do anything
        if message.intent == 'Default Welcome Intent' or \
                message.intent == 'Default Fallback Intent' or \
                message.intent.endswith('followup') or \
                isinstance(message, FallbackResponse):
            return message.message
        elif message.intent not in self.query_map.keys():
            return QueryError.UNKNOWN_QUERY_TYPE.value
        # Proceed to mapping
        return self.query_map[message.intent](message)

    def unpack_message(self, message, token=' @@@ '):
        """Unpack Dialogflow messages

        :param message: message to process.
        :param token: token to split by
        :type: str
        :return: processed message
        :rtype: list
        """
        return message.split(token)

    def respond_to_course_outline_queries(self, message):
        cid = message.message.upper()
        response = self.database_manager.get_course_outline(cid)
        if not response:
            return QueryError.NO_SUCH_COURSE.value
        return response[0][0]

    def respond_to_course_fee_queries(self, message):
        try:
            cid = message.message.upper()
            response = self.database_manager.get_tuition_fee(cid)
            if not response:
                return QueryError.NO_SUCH_COURSE.value
            return "Commonwealth student: {}\nDomestic student: {}\nInternational student: {}".format(response[0][0],
                                                                                                      response[0][1],
                                                                                                      response[0][2])
        except Exception as e:
            logger.error(str(e))
            return QueryError.UNKNOWN_QUERY_TYPE.value

    def respond_to_course_location_queries(self, message):
        try:
            cid = message.message.upper()
            campus = self.database_manager.get_location(cid)
            classroom = self.utility_module.class_room_finder.find_class_room(cid)
            if not campus and classroom:
                return QueryError.NO_SUCH_COURSE.value
            return "The location of {} is at {}{}".format(cid, classroom, campus[0][0])
        except Exception as e:
            logger.error(str(e))
            return QueryError.UNKNOWN_QUERY_TYPE.value

    def respond_to_course_indicative_hours_queries(self, message):
        try:
            cid = message.message.upper()
            response = self.database_manager.get_indicative_hours(cid)
            if not response:
                return QueryError.NO_SUCH_COURSE.value
            return '{} hours'.format(response[0][0])
        except Exception as e:
            logger.error(str(e))
            return QueryError.UNKNOWN_QUERY_TYPE.value

    def respond_to_course_offering_term_queries(self, message):
        try:
            cid = message.message.upper()
            response = self.database_manager.get_offer_term(cid)
            if not response:
                return QueryError.NO_SUCH_COURSE.value
            return response[0][0]
        except Exception as e:
            logger.error(str(e))
            return QueryError.UNKNOWN_QUERY_TYPE.value

    def respond_to_course_prerequisites_queries(self, message):
        try:
            cid = message.message.upper()
            response = self.database_manager.get_prerequisites(cid)
            if not response:
                return QueryError.NO_SUCH_COURSE.value
            if not response[0][0]:
                return "There is no prerequisite for this course, it is 0 level course"
            return response[0][0]
        except Exception as e:
            logger.error(str(e))
            return QueryError.UNKNOWN_QUERY_TYPE.value

    def respond_to_course_school_and_faculty_queries(self, message):
        try:
            cid = message.message.upper()
            response = self.database_manager.get_faculty(cid)
            if not response:
                return QueryError.NO_SUCH_COURSE.value
            responses = ["This course belongs to {}.".format(response[0][0]),
                         "This course is run by {}.".format(response[0][0]),
                         "{} manages this course.".format(response[0][0])]
            return random.choice(responses)
        except Exception as e:
            logger.error(str(e))
            return QueryError.UNKNOWN_QUERY_TYPE.value

    def respond_to_course_send_outline_queries(self, message):
        try:
            cid = message.message.upper()
            response = self.database_manager.get_pdf_url(cid)
            if not response:
                return QueryError.NO_SUCH_COURSE.value
            url = response[0][0]
            receiver = 'whatbot9900@gmail.com'  # set receiver to ourselves since in development, we don't have actual user emails.
            self.utility_module.emailer.send_outline('WhatBot: Your course outline information request', url, cid, receiver)
            return 'The course outline for {} has been sent to {}'.format(cid, receiver)
        except Exception as e:
            logger.error(str(e))
            return QueryError.UNKNOWN_QUERY_TYPE.value

    def respond_to_course_study_level_queries(self, message):
        try:
            cid = message.message.upper()
            cid = cid.upper()
            response = self.database_manager.get_course(cid)
            return '{} is a CSE course for postgraduate'.format(
                cid) if response else '{} is not a CSE postgraduate course'.format(cid)
        except Exception as e:
            logger.error(str(e))
            return QueryError.UNKNOWN_QUERY_TYPE.value

    def respond_to_course_isadk_queries(self, message):
        try:
            cid = message.message.upper()
            response = self.database_manager.get_course(cid)
            if not response:
                return QueryError.NO_SUCH_COURSE.value
            answer = "Yes, it is an ADK course" if response[0][3] else "This course is not an ADK course"
            return answer
        except Exception as e:
            logger.error(str(e))
            return QueryError.UNKNOWN_QUERY_TYPE.value

    def respond_to_course_consultation_booking(self, message):
        try:
            cid, time, date = self.unpack_message(message.message)
            sid = message.username
            cid = cid.upper()
            response = self.utility_module.consultation_manager.consultation_booking_query(cid, sid, time, date)
            if not response:
                return QueryError.NOT_AVAILABLE.value
            logger.debug(response)
            return response
        except Exception as e:
            logger.error(str(e))
            return QueryError.UNKNOWN_QUERY_TYPE.value

    def respond_to_course_consultation_cancel(self, message):
        try:
            cid, time, date = self.unpack_message(message.message)
            sid = message.username
            cid = cid.upper()
            response = self.utility_module.consultation_manager.delete_consultation(cid, sid, time, date)
            if not response:
                return QueryError.NOT_AVAILABLE.value
            elif response == ConsultationError.INVALID_COURSE.value:
                return response
            elif response == ConsultationError.INVALID_CANCEL.value:
                return response
            return "You have cancelled the booking at {} on {}".format(time, date)
        except Exception as e:
            logger.error(str(e))
            return QueryError.UNKNOWN_QUERY_TYPE.value

    def respond_to_course_consultation_view(self, message):
        try:
            sid = message.username
            response = self.utility_module.consultation_manager.view_my_consultation(sid)
            if not response:
                return QueryError.NO_CONSULTATION.value
            result = "The list of consultation bookings you’ve made are:\n"
            for cid, time, date in response:
                result += "{} on {} at {}\n".format(cid, date, time)
            return result
        except Exception as e:
            logger.error(str(e))
            return QueryError.UNKNOWN_QUERY_TYPE.value

    def respond_to_wam_admin_queries(self, message):
        try:
            sid = message.message
            response = self.utility_module.wam_calculator.calculate_wam(sid)
            if not len(response):
                return QueryError.NO_STUDENT.value
            return response
        except Exception as e:
            logger.error(str(e))
            return QueryError.UNKNOWN_QUERY_TYPE.value

    def respond_to_wam_student_queries(self, message):
        try:
            sid = message.username
            response = self.utility_module.wam_calculator.calculate_wam(sid)
            if not len(response):
                return QueryError.NO_STUDENT.value
            return response
        except Exception as e:
            logger.error(str(e))
            return QueryError.UNKNOWN_QUERY_TYPE.value

    def respond_to_announcement_queries(self, message):
        try:
            cid = message.message.upper()
            response = self.utility_module.announcement_getter.get_announcement(cid)
            if not len(response):
                return QueryError.NO_DATA.value
            return response
        except Exception as e:
            logger.error(str(e))
            return QueryError.UNKNOWN_QUERY_TYPE.value

    def respond_to_all_courses_queries(self, _):
        try:
            response = self.database_manager.get_all_courses()
            result = "The list of courses are:\n"
            for cid, cname in response:
                result += "{} - {}\n".format(cid, cname)
            return result
        except Exception as e:
            logger.error(str(e))
            return QueryError.UNKNOWN_QUERY_TYPE.value

    def respond_to_timetable_queries(self, message):
        try:
            cid = message.message.upper()
            response = self.utility_module.course_timetable_finder.get_course_timetable(cid)
            if not len(response):
                return QueryError.NO_SUCH_COURSE.value
            course, course_name, time= response[0][0], response[0][1], response[0][2]
            result = 'Timetable for {} - {} is:{}'.format(course, course_name, time)
            return result
        except Exception as e:
            logger.error(str(e))
            return QueryError.UNKNOWN_QUERY_TYPE.value

    def response_to_rating_queries(self, message):
        try:
            cid = message.message.upper()
            response = self.database_manager.get_rating(cid)
            result = "The rating of the course {} is {}/5".format(cid, response[0][0])
            return result
        except Exception as e:
            logger.error(str(e))
            return QueryError.UNKNOWN_QUERY_TYPE.value
