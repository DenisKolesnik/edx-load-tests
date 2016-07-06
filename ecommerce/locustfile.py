import os

from locust import HttpLocust, TaskSet

from ecommerce.baskets import BasketsTasks
from ecommerce.coupon_offer import CouponOfferTasks
from ecommerce.payment import CybersourcePaymentTasks


class EcommerceTest(TaskSet):
    """Load test exercising ecommerce-related operations on the LMS and Otto.

    Execution probabilities are derived from a conservative estimate from
    marketing placing the percentage of paid enrollments at 2% of all
    enrollments.
    """
    tasks = {
        BasketsTasks: 50,
        CybersourcePaymentTasks: 1,
    }


class CouponsTest(TaskSet):
    """Load test excercising coupon-related operations on Otto."""
    tasks = [CouponOfferTasks]


class EcommerceUser(HttpLocust):
    """Representation of an HTTP "user".

    Defines how long a simulated user should wait between executing tasks, as
    well as which TaskSet class should define the user's behavior.
    """
    task_set = globals()[os.getenv('LOCUST_TASK_SET', 'EcommerceTest')]
    if os.getenv('COUPON_CODE'):
        task_set = CouponsTest
    min_wait = 3 * 1000
    max_wait = 5 * 1000
