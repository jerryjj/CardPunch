import _midgard as midgard, os

## This is a testing configuration, use MySQL or PostGreSQL for production

# Keep the connection and configuration as global variables
configuration = midgard.config()
configuration.dbtype = 'SQLite'
configuration.database = 'cardpunch'
#configuration.blobdir =  os.path.expanduser('~/.midgard2/blobs/' + configuration.database)
connection = midgard.connection()

class wrapper:
    """Wrap our storage logic to handier package, import this module and use storage.instance"""
    def __init__(self):
        # The classes we use, for these we create/update storage
        self.used_classes = [
            'cardpunch_exchange',
            'cardpunch_exchange_statistics',
            'cardpunch_exchange_contactinfo',
            'cardpunch_exchange_contactinfo_mvfield',
        ]
        self.person = None

        # Need to check this before opening the connection since that will create the file...
        self.dbpath = os.path.expanduser('~/.midgard2/data/' + configuration.database + '.db')
        self.db_exists = os.path.exists(self.dbpath)
        # Connection state tracking
        self.connected = False

    def connect(self):
        """Open connection to database or raise exception on failure"""
        self.connected = connection.open_config(configuration)
        if not self.connected:
            raise Exception('Could not open database connection, reason: %s' % midgard._connection.get_error_string())

    def initialize(self):
        if not self.connected:
            self.connect()
        self.initialize_db()

    def initialize_db(self):
        if not self.connected:
            self.connect()
        if self.db_exists:
            return
        if not midgard.storage.create_base_storage():
            raise Exception("create_base_storage() returned failure")
        
        for classname in self.used_classes:
            if not midgard.storage.create_class_storage(classname):
                raise Exception("create_class_storage(%s) returned failure" % classname)

# Use this instantiated wrapper object to access the base storage
instance = wrapper()
