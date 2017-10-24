

def export_full_data(params):
    import tasks
    import time
    from .file import store_file

    timestamp = time.time()
    report = params['report']
    method_to_call = getattr(tasks, report)
    data = method_to_call(params)
    # data = method_to_call.delay(params)
    store_file(data, timestamp)

