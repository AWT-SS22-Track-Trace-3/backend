
# MongoDB datasource constants
MONGO = {
    'DATABASE': 'products',
    'HOST': 'localhost',
    'DOCKER': 'backend-mongo',
    'PORT': 27017,
    'USERNAME': 'root',
    'PASSWORD': 'SuperSecret',
    'AUTHENTICATION_SOURCE': 'admin'
}

JWT = {
    'SECRET_KEY': "610c6f6b5bfb43dc8f62aa9599062be51df1c1632550288b3d4472b95c399564",
    'SECRET_REFRESH_KEY': "f435e2e43fdfc4672da6e4f59568319ac45487832646e720d958367a96881750",
    'ALGORITHM': "HS256",
    'ACCESS_TOKEN_EXPIRE_MINUTES': 30,
    'REFRESH_TOKEN_EXPIRE_MINUTES': 60 * 24 * 7,
    'ACCESS_TOKEN_EXPIRE_SECONDS': 1
}
