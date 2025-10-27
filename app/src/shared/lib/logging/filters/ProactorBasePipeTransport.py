from logging import Filter

class ProactorBasePipeTransportFilter(Filter):
    def filter(self, record):
        return not ('ProactorBasePipeTransport' in record.getMessage()\
            and 'asyncio' in record.name\
            and record.levelname == 'ERROR') # замалчиваем проблемы, чтобы их не решать