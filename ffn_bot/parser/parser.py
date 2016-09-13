import bisect


class RequestParser(object):
    """
    A Parser extracts requests from the comment.
    """

    PARSERS = []

    def __init__(self):
        self.name = getattr(self, 'NAME', self.__class__.__name__)

    @classmethod
    def register(cls, priority, parser=None):
        """
        Registers a new RequestParser. If you directly pass a parser as the second argument, it will
        automatically register the parser, otherwise it will just act as a decorator generator registering
        new parsers.

        :param priority:  The priority of this parser
        :param parser:    The parser itself.
        :return: A decorator.
        """
        def _decorator(parser):
            bisect.insort(cls.PARSERS, (priority, parser))
            return parser

        if parser is not None:
            # If a parser has been passed to this function, immediately execute the decorator.
            return _decorator(parser)
        return _decorator

    @classmethod
    def get_parsers(cls):
        """
        Yields all parsers.
        :return: All parsers.
        """
        yield from (p for _, p in cls.PARSERS)

    def is_active(self, request):
        """
        Checks if this parser should be applied to this request.
        :param comment: true if this parser should be applied to the request.
        :return: true if this parser should be applied to the request.
        """
        return False

    def parse(self, request):
        """
        Applies this parser to this request.

        Modified state is directly applied to the request object.

        :param request: The request to parse.
        :return: False if parsing should end here a nonzero object otherwise.
        """
        return True

    def __cmp__(self, other):
        """
        A trick to make this code work with bisect.

        It uses a hash over itself to make the results reproducable.
        """
        return hash(self) - hash(other)


class parser(RequestParser):
    """
    A small decorator that creates a parser by taking a lambda for the is_active implementation
    and the function itself as the actual parser code itself.
    """

    def __init__(self, filter = None):
        self.filter = filter
        self.decorated = None

    def is_active(self, request):
        if filter is None:
            return True
        return self.filter(request)

    def parse(self, request):
        return self.decorated(request)

    def __call__(self, func):
        self.decorated = func
        return self


@RequestParser.register(-1)
@parser(lambda request: "ignore" in request.markers)
def ignore_request(request):
    return False
