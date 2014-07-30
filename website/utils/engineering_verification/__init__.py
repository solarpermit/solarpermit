import nec2014

def pass_fail(func):
    def testcase(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except ValidationError as e:
            return (False, func.__name__, e.args[0])
        except Exception as e:
            return (False, func.__name__, "Unknown Error")
        return (True, func.__name__)
