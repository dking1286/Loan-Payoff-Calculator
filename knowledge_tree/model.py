import math

import knowledge_tree.constants as constants
import knowledge_tree.database as database
from knowledge_tree.financial_tools import time_until_zero_balance


class Model(object):
    """Contains the internal representations of the data to be displayed.
    
    Attributes:
        main (Main): A reference to the Main instance that contains the Model instance
        database (peewee database): A reference to the database the Model instance will
            read and write from
        interest_rate (float): The current interest rate being displayed. This value will be matched
            to the interest_rate_slider in the Controller instance.
        initial_balance (int): The current initial balance being displayed. This value will
            be matched to the initial_balance_slider in the Controller instance.
        payoff_times (dict<initial balance, dict<interest rate, dict<payment, payoff time>>>):
            A nested dictionary structure containing the data to be plotted.
            
    Public methods:
        Model(main=None)
        calculate_payoff_times()
        delete_payoff_times_from_database()
        load_payoff_times()
        get_time_vs_payment_data(Bo=0, r=0)
        get_payoff_time(Bo=0, r=0, p=0)
    """
    def __init__(self, main=None, db=None):    
        self.main = main
        self.database = db
        self.interest_rate = constants.interest_rate['default']
        self.initial_balance = constants.initial_balance['default']
        self.payoff_times = dict()
    
    def calculate_payoff_times(self):
        """Calculates payoff time data and stores the results in the database"""
        with self.database.transaction():
            current_id = 0
            for Bo in constants.initial_balance_range():
                for r in constants.interest_rate_range():
                    for p in constants.monthly_payment_range():
                        print("Calculating for initial balance {0}, rate {1}, monthly payment {2}".format(Bo, r, p))
                        t = time_until_zero_balance(r, Bo, p)
                        if t is not None:
                            database.create_point(current_id, Bo, r, p, t)
                        current_id += 1
                                
    def delete_payoff_times_from_database(self):
        """Generator function returning an iterator that deletes ALL of the data from the database.
        
        After each data point is deleted, the iterator yields the percent done with the process.
        """
        with self.database.transaction():
            points = database.DataPoint.select()
            num_points = points.count()
            i = 0
            for point in points:
                (Bo, r, p, t) = (point.Bo, point.r, point.p, point.t)
                print("Deleting point with (Bo, r, p, t) = ({0}, {1}, {2}, {3})".format(Bo, r, p, t)) 
                
                point.delete_instance()
                
                percent_done = math.floor(100 * i / num_points)
                yield percent_done
                i += 1
    
    def load_payoff_times(self):
        """Gets all of the data points from the database and loads them into memory as
        elements of the self.payoff_times dictionary"""
        with self.database.transaction():
            data = database.DataPoint.select()
            for point in data:
                Bo, r, p, t = point.Bo, point.r, point.p, point.t
                self.payoff_times[Bo] = self.payoff_times.get(Bo, {})
                self.payoff_times[Bo][r] = self.payoff_times[Bo].get(r, {})
                self.payoff_times[Bo][r][p] = t

    @staticmethod
    def get_time_vs_payment_data(Bo=0, r=0):
        """Gets the time vs. payment data for given values of Bo and r.
        """
        return database.get_time_vs_payment_data(Bo, r)

    @staticmethod
    def get_payoff_time(Bo=0, r=0, p=0):
        """Gets the payoff time for given values of Bo, r, and p."""
        try:
            print("In model,", database.get_payoff_time(Bo, r, p))
            return database.get_payoff_time(Bo, r, p)
        except ValueError:
            raise ValueError("No DataPoint was found with Bo={}, r={}, p={}".format(Bo, r, p))
