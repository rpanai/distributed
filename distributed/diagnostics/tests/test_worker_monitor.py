from distributed.diagnostics.worker_monitor import (resource_profile_plot,
        resource_profile_update)
from distributed.diagnostics.scheduler import workers, tasks
from distributed.utils_test import gen_cluster

from collections import deque
import datetime
from tornado import gen


@gen_cluster()
def test_resource_monitor_plot(s, a, b):
    while any('last-seen' not in v for v in s.host_info.values()):
        yield gen.sleep(0.01)

    times_buffer = deque([datetime.datetime(2016, 3, 23, 14, 31, 4, 426461),
                          datetime.datetime(2016, 3, 23, 14, 31, 5, 430657),
                          datetime.datetime(2016, 3, 23, 14, 31, 6, 432290)],
                          maxlen=1000)
    workers_buffer = deque([{},
                            {'10.10.20.86': {'cpu': 15.9, 'memory-percent': 63.0}},
                            {'10.10.20.86': {'cpu': 14.9, 'memory-percent': 64.0},
                             '10.10.20.87': {'cpu': 13.9, 'memory-percent': 64.0}}],
                             maxlen=1000)

    source, plot = resource_profile_plot()
    resource_profile_update(source, workers_buffer, times_buffer)

    assert source.data['workers'] == ['10.10.20.86', '10.10.20.87']
    assert len(source.data['cpu']) == 2
    assert source.data['cpu'][0] == ['null', 15.9, 14.9]
    assert source.data['cpu'][1] == ['null', 'null', 13.9]

    assert source.data['times'][0] == ['null',
                                       datetime.datetime(2016, 3, 23, 14, 31, 5, 430657),
                                       datetime.datetime(2016, 3, 23, 14, 31, 6, 432290)]
    assert source.data['times'][1] == ['null',
                                       'null',
                                       datetime.datetime(2016, 3, 23, 14, 31, 6, 432290)]
    assert len(source.data['times']) == 2
    assert len(source.data['memory-percent']) == 2