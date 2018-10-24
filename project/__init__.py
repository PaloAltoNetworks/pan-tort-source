import os
import logging
from flask import Flask
from elasticsearch import Elasticsearch, helpers
from logging.handlers import RotatingFileHandler

class logFormatter(logging.Formatter):
    width = 45
    datefmt='%Y-%m-%d %H:%M:%S'

    def format(self, record):
        cpath = f'{record.module}:{record.funcName}:[{record.lineno}]:{record.thread}'
        cpath = cpath[-self.width:].ljust(self.width)
        #record.message = record.getMessage()
        levelName = f"[{record.levelname}]"
        outputString = (f"{levelName:<10}: "
                       f"{self.formatTime(record, self.datefmt)} : {cpath} : "
                       f"{record.getMessage()}")

        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            if outputString[-1:] != "\n":
                outputString = outputString + "\n"
            outputString = outputString + record.exc_text
        return outputString

# Initialize the app for Flask
app = Flask(__name__)


# Set the configuration parameters that are used by the application.
# These values are overriden by the .panrc file located in the base directory
# for the application
#
# ---------- APPLICATION SETTINGS --------------
#
# Current version number of pan-tort
app.config['VERSION'] = "0.1-dev"
#
# When set to True, this slows down the logging by only processing 1 event at a
# time and allows us to see what is going on if there are bugs
app.config['DEBUG_MODE'] = False
#
# Flask setting for where session manager contains the info on the session(s)
app.config['SESSION_TYPE'] = "filesystem"
#
# Secret key needed by session setting above.
app.config['SECRET_KEY'] = "\xfd{H\xe5<\x95\xf9\xe3\x96.5\xd1\x01O<!\xd5"
#
# Sets the base directory for the application
app.config['BASE_DIR'] = os.path.abspath(os.path.dirname(__file__))
#
# This is an internal flag that will probably never show up in the .panrc file
# It is used to slow execution when it is True
app.config['AF_POINTS_MODE'] = False
#
# Number of AF points left to slow down processing so we don't run out of points
# When it reaches this point, it sets the AF_POINTS_MODE to True and it slows
# execution to 1 event at a time.
app.config['AF_POINTS_LOW'] = 5000
#
# Number of AF points left to stop processing all together
app.config['AF_POINT_NOEXEC'] = 500
#
# Number of seconds to wait when AF_POINT_NOEXEC gets triggered.  This stops all
# app execution and checks the AF points total at the specified interval.  When
# the points total is higher than AF_POINT_NOEXEC it resumes execution.
app.config['AF_NOEXEC_CKTIME'] = 3600
#
# Set the number of processes to simultaneously call AF.  This cannot be more 
# than 16 or it will kill the AF minute points.  The code will  take care of 
# cases where it is greater than 16 and this should only be adjusted down 
# (never up).
app.config['TORT_POOL_COUNT'] = 16
#

# ------------------------------- LOGGING --------------------------------------
#
# Log level for Flask
app.config['FLASK_LOGGING_LEVEL'] = "ERROR"
# Log level for the SafeNetworking application itself.  All files are written
# to log/tort.log
app.config['LOG_LEVEL'] = "INFO"
#
# Size of Log file before rotating - in bytes
app.config['LOG_SIZE'] = 10000000
#
# Number of log files to keep in log rotation
app.config['LOG_BACKUPS'] = 10
#
# ----------------------------- ELASTICSTACK -----------------------------------
#
# By default our ElasticStack is installed all on the same system
app.config['ELASTICSEARCH_HOST'] = "elasticsearch"
app.config['ELASTICSEARCH_PORT'] = "9200"
app.config['ELASTICSEARCH_HTTP_AUTH'] = ""
app.config['KIBANA_HOST'] = "kibana"
app.config['KIBANA_PORT'] = "5601"
app.config['ELASTICSTACK_VERSION'] = "6.4"


# ------------------------------ FLASK -----------------------------------------
#
# By default Flask listens to all ports - we will only listen to localhost
# for security reasons, but keep the default port of 5000
app.config['FLASK_HOST'] = "localhost"
app.config['FLASK_PORT'] = 5010
#
#
#
# ----------------------------- MISCELLANEOUS ----------------------------------
#
app.config['AUTOFOCUS_API_KEY'] = "NOT-SET"
app.config['AUTOFOCUS_HOSTNAME'] = "autofocus.paloaltonetworks.com"
app.config['AUTOFOCUS_SEARCH_URL'] = "https://autofocus.paloaltonetworks.com/api/v1.0/samples/search"
app.config['AUTOFOCUS_RESULTS_URL'] = "https://autofocus.paloaltonetworks.com/api/v1.0/samples/results/"
app.config['AUTOFOCUS_TAG_URL'] = "https://autofocus.paloaltonetworks.com/api/v1.0/tag/"



# Set instance config parameters
app.config.from_pyfile('.panrc')

# Add Elasticsearch object for our instance of ES
es = Elasticsearch(f"{app.config['ELASTICSEARCH_HOST']}:"
                   f"{app.config['ELASTICSEARCH_PORT']}")

# Set up logging for the application - we may want to revisit this
# see issue #10 in repo
handler = RotatingFileHandler(f"{app.config['BASE_DIR']}/../log/tort.log",
                            maxBytes=app.config['LOG_SIZE'],
                            backupCount=app.config['LOG_BACKUPS'])
tortFormatter = logFormatter()
handler.setLevel(app.config["LOG_LEVEL"])
handler.setFormatter(tortFormatter)
app.logger.addHandler(handler)
app.logger.info(f"INIT - Pan-Tort application initializing with log level of {app.config['LOG_LEVEL']}")
app.logger.info(f"ElasticSearch host is: {app.config['ELASTICSEARCH_HOST']}:{app.config['ELASTICSEARCH_PORT']}")

