# Sprint plan: account recovery & abuse protection

## Password reset
Users can request a password-reset email. The reset link contains a
single-use token that expires after 30 minutes.

## Login rate limiting
To slow credential stuffing, an IP may make at most 10 login attempts
per minute; further attempts get HTTP 429.
