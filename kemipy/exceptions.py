class UndefinedEnvironmentVariable(Exception):
    """Exception raised when an environment varible is undefined

    Attributes:
        variable_name -- name of the undefined environment variable
    """

    def __init__(self, variable_name):
        self.variable_name = variable_name
        self.message = f"Environment variable {variable_name} is undefined"
        super().__init__(self.message)
