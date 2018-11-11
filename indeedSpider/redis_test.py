import redis

redis_cli = redis.StrictRedis()

redis_cli.incr("job_count")