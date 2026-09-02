try:
    import pymysql

    pymysql.install_as_MySQLdb()

    from django.db.backends.mysql.base import DatabaseWrapper

    # Allow MySQL 8.0.x with Django 6.x
    DatabaseWrapper.check_database_version_supported = lambda self: None
except ImportError:
    pass
