import os
import sys
import json
import time
import docker
import psutil

time_series_data = []

def calculate_cpu_percent(d):
    cpu_count = len(d["cpu_stats"]["cpu_usage"]["percpu_usage"])
    cpu_percent = 0.0
    cpu_delta = float(d["cpu_stats"]["cpu_usage"]["total_usage"]) - \
                float(d["precpu_stats"]["cpu_usage"]["total_usage"])
    system_delta = float(d["cpu_stats"]["system_cpu_usage"]) - \
                   float(d["precpu_stats"]["system_cpu_usage"])
    if system_delta > 0.0:
        cpu_percent = cpu_delta / system_delta * 100.0 * cpu_count
    return cpu_percent


def get_cpu_periods(d):
    return d['precpu_stats']['throttling_data']['periods']


def calculate_blkio_bytes(d):
    """
    :param d:
    :return: (read_bytes, wrote_bytes), ints
    """
    bytes_stats = graceful_chain_get(d, "blkio_stats", "io_service_bytes_recursive")
    if not bytes_stats:
        return 0, 0
    r = 0
    w = 0
    for s in bytes_stats:
        if s["op"] == "Read":
            r += s["value"]
        elif s["op"] == "Write":
            w += s["value"]
    return r, w


def calculate_network_bytes(d):
    """
    :param d:
    :return: (received_bytes, transceived_bytes), ints
    """
    networks = graceful_chain_get(d, "networks")
    if not networks:
        return 0, 0
    r = 0
    t = 0
    for if_name, data in networks.items():
        logger.debug("getting stats for interface %r", if_name)
        r += data["rx_bytes"]
        t += data["tx_bytes"]
    return r, t

def humanize_bytes(bytesize, precision=2):
    """
    Humanize byte size figures
    https://gist.github.com/moird/3684595
    """
    abbrevs = (
        (1 << 50, 'PB'),
        (1 << 40, 'TB'),
        (1 << 30, 'GB'),
        (1 << 20, 'MB'),
        (1 << 10, 'kB'),
        (1, 'bytes')
    )
    if bytesize == 1:
        return '1 byte'
    for factor, suffix in abbrevs:
        if bytesize >= factor:
            break
    if factor == 1:
        precision = 0
    return '%.*f %s' % (precision, bytesize / float(factor), suffix)

def humanize_time(value):
    abbrevs = (
        (1, "now"),
        (2, "{seconds} seconds ago"),
        (59, "{seconds} seconds ago"),
        (60, "{minutes} minute ago"),
        (119, "{minutes} minute ago"),
        (120, "{minutes} minutes ago"),
        (3599, "{minutes} minutes ago"),
        (3600, "{hours} hour ago"),
        (7199, "{hours} hour ago"),
        (86399, "{hours} hours ago"),
        (86400, "{days} day ago"),
        (172799, "{days} day ago"),
        (172800, "{days} days ago"),
        (172800, "{days} days ago"),
        (2591999, "{days} days ago"),
        (2592000, "{months} month ago"),
        (5183999, "{months} month ago"),
        (5184000, "{months} months ago"),
    )
    n = datetime.now()
    delta = n - value
    for guard, message in abbrevs:
        s = int(delta.total_seconds())
        if guard >= s:
            break
    return message.format(seconds=delta.seconds, minutes=int(delta.seconds // 60),
                          hours=int(delta.seconds // 3600), days=delta.days,
                          months=int(delta.days // 30))


#print(psutil.cpu_percent())
#print(psutil.virtual_memory())
#print('memory % used:', psutil.virtual_memory()[2])

print('-'*80)

secs_begin = time.time()

def plot_inc_cpu_over_time():
    import pandas as pd
    import numpy as np
    import matplotlib
    import matplotlib.pyplot as plt

    def normalize_booleans(value):
        return 1 if value else 0
    
    def normalize_secs(value, start_time, end_time):
        return (value - start_time) / (end_time - start_time)
    
    df = pd.DataFrame(time_series_data)
    print(df.head())
    df_d = df[["secs","is_increasing_cpu"]]
    df_d['n_is_increasing_cpu'] = df_d.apply(lambda row : normalize_booleans(row['is_increasing_cpu']), axis = 1)
    df_d['n_secs'] = df_d.apply(lambda row : normalize_secs(row['secs'], df_d['secs'].min(), df_d['secs'].max()), axis = 1)
    print(df_d.head())
    matplotlib.use( 'QtAgg' )
    plt.xlabel('time')
    plt.ylabel('n_is_increasing_cpu')
    plt.plot(df_d["n_secs"], df_d["n_is_increasing_cpu"])
    plt.show()

def plot_cpu_over_time():
    import pandas as pd
    import numpy as np
    import matplotlib
    import matplotlib.pyplot as plt

    def normalize_number(value, start_time, end_time):
        return (value - start_time) / (end_time - start_time)
    
    df = pd.DataFrame(time_series_data)
    print(df.head())
    df_d = df[["secs","cpu_pcent"]]
    df_d['n_secs'] = df_d.apply(lambda row : normalize_number(row['secs'], df_d['secs'].min(), df_d['secs'].max()), axis = 1)
    print(df_d.head())
    matplotlib.use( 'QtAgg' )
    plt.xlabel('time')
    plt.ylabel('cpu_pcent')
    plt.plot(df_d["n_secs"], df_d["cpu_pcent"])
    plt.show()

def plot_mem_over_time():
    import pandas as pd
    import numpy as np
    import matplotlib
    import matplotlib.pyplot as plt

    def normalize_number(value, start_time, end_time):
        return (value - start_time) / (end_time - start_time)
    
    df = pd.DataFrame(time_series_data)
    print(df.head())
    df_d = df[["secs","mem_usage"]]
    df_d['n_secs'] = df_d.apply(lambda row : normalize_number(row['secs'], df_d['secs'].min(), df_d['secs'].max()), axis = 1)
    print(df_d.head())
    matplotlib.use( 'QtAgg' )
    plt.xlabel('time')
    plt.ylabel('mem_usage')
    plt.plot(df_d["n_secs"], df_d["mem_usage"])
    plt.show()

one_gb_in_bytes = 1024 * 1024 * 1024

while (1):
    client = docker.DockerClient(base_url='unix:///var/run/docker.sock')
    for container in client.containers.list():
        doc = container.stats(decode=None, stream=False)
        cpu_pcent = calculate_cpu_percent(doc)
        cpu_periods = get_cpu_periods(doc)
        mem_usage = doc["memory_stats"]["usage"]
        mem_limit = doc["memory_stats"]["limit"]
        
        os_cpu_pcent = psutil.cpu_percent()
        os_memory_available = psutil.virtual_memory()[1]
        
        c_mem_usage_pcent = mem_usage / mem_limit
        
        is_increasing_cpu = (cpu_pcent > 80.0) and (cpu_pcent < 100.0) and (os_cpu_pcent < 80.0)
        is_decreasing_cpu = (cpu_pcent > 100.0)

        is_increasing_mem = (c_mem_usage_pcent > 0.8) and (os_memory_available > one_gb_in_bytes) and (mem_usage < (os_memory_available * 0.8))
        is_decreasing_mem = (c_mem_usage_pcent < 0.01)
        
        d = {}
        d["secs"] = time.time()
        d["container_id"] = container.id
        d["container_name"] = container.name
        d["cpu_pcent"] = cpu_pcent
        d["mem_usage"] = mem_usage
        d["mem_limit"] = mem_limit
        d["is_increasing_cpu"] = is_increasing_cpu
        d["is_increasing_mem"] = is_increasing_mem
        
        time_series_data.append(d)
        
        #print(json.dumps(doc, indent=4))
        print("Container Name: %s" % container.name)
        print("Container ID: %s" % container.id)
        print("CPU Percent: %s" % cpu_pcent)
        print("Memory Usage: %s" % humanize_bytes(mem_usage))
        print("Memory Limit: %s" % humanize_bytes(mem_limit))
        print("Is Increasing CPU: %s" % is_increasing_cpu)
        print("Is Increasing Memory: %s" % is_increasing_mem)
        print("Is Decreasing CPU: %s" % is_decreasing_cpu)
        print("Is Decreasing Memory: %s" % is_decreasing_mem)
        print()

        print("DEBUG: c_mem_usage_pcent: %s" % c_mem_usage_pcent)
        print('DEBUG: os_cpu_pcent: {}'.format(os_cpu_pcent))
        print('DEBUG: os_memory_available: {}'.format(os_memory_available))
        print()
        
        if (len(time_series_data) > 20):
            #plot_inc_cpu_over_time()
            #plot_cpu_over_time()
            #plot_mem_over_time()
            #sys.exit()
            pass
        
        if (is_increasing_mem or is_decreasing_mem or is_decreasing_cpu or is_increasing_cpu):
            print("Adjusting Container: %s" % container.name)
            if (is_increasing_mem):
                print("Adjusting Memory Up")
                container.update(mem_limit=mem_limit + one_gb_in_bytes)
            if (is_decreasing_mem):
                print("Adjusting Memory Down")
                container.update(mem_limit=mem_limit - one_gb_in_bytes)
            if (is_increasing_cpu):
                print("Adjusting CPU Up")
                container.update(cpu_periods=cpu_periods + 1000, cpu_quota=cpu_periods + 10000)
            if (is_decreasing_cpu):
                print("Adjusting CPU Down")
                container.update(cpu_periods=cpu_periods - 1000, cpu_quota=cpu_periods + 1000)
            print()
        print('-'*80)