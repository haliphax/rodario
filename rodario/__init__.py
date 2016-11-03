""" rodario - Simple, redis-backed Python actor framework """

# 3rd party
from redis import StrictRedis

get_redis_connection = StrictRedis  # pylint: disable=C0103
