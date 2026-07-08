# SPECZ: spz-auth-bz

MAX_FAILURES = 3
LOCK_MINUTES = 15


def login(user, password):
    """Authenticate a user with email and password."""
    if verify(user, password):
        user.failures = 0
        return issue_session(user)
    record_failure(user)
    return None


# SPECZ: spz-auth-bz, spz-sec-k9
def record_failure(user):
    user.failures += 1
    if user.failures >= MAX_FAILURES:
        lock_account(user, minutes=LOCK_MINUTES)
