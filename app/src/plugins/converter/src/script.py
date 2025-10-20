from ..models import ConverterParams
from ..objects._types import message_callback, raw_progress_callback
from ..objects.fast_table import FastTable
from ..objects.optimized_table import OptimizedTable
import orjson

def text_to_text_convert(params: ConverterParams, msg_cb: message_callback, done_cb, progress_cb: raw_progress_callback):
    if params.source_type == 'csv':
        data = params.source_text.splitlines()
    elif params.source_type == 'json':
        data = orjson.loads(params.source_text)
    table = FastTable.read(data, params.source_type, params.splitter, msg_cb)
    result = table.save(None, params.target_type, params.splitter, msg_cb)
    params.target_text =result
    done_cb()

def optimized_convert(params: ConverterParams, msg_cb: message_callback, done_cb, progress_cb: raw_progress_callback):
    table = OptimizedTable.read(params.source_path, params.source_type, params.splitter, msg_cb, progress_cb)
    table.save(params.target_path, params.target_type, params.splitter, msg_cb)
    done_cb()

def fast_convert(params: ConverterParams, msg_cb: message_callback, done_cb, progress_cb: raw_progress_callback):
    table = FastTable.read(params.source_path, params.source_type, params.splitter, msg_cb)
    table.save(params.target_path, params.target_type, params.splitter, msg_cb)
    done_cb()

def main(params: ConverterParams, msg_cb: message_callback, done_cb, progress_cb: raw_progress_callback):
    if params.type.lower() == 'быстрый':
        if params.source_text:
            return text_to_text_convert(params, msg_cb, done_cb, progress_cb)
        return fast_convert(params, msg_cb, done_cb, progress_cb)
    else:
        return optimized_convert(params, msg_cb, done_cb, progress_cb)