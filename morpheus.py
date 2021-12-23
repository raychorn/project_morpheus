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

client = docker.DockerClient(base_url='unix:///var/run/docker.sock')
for containers in client.containers.list():
    doc = containers.stats(decode=None, stream=False)
    cpu_pcent = calculate_cpu_percent(doc)
    mem_usage = doc["memory_stats"]["usage"]
    mem_limit = doc["memory_stats"]["limit"]
    
    is_increasing_cpu = cpu_pcent < 80.0 #psutil.cpu_percent()
    is_increasing_mem = mem_usage < (psutil.virtual_memory()[1] * 0.8)
    
    d = {}
    d["secs"] = time.time()
    d["container_id"] = containers.id
    d["container_name"] = containers.name
    d["cpu_pcent"] = cpu_pcent
    d["mem_usage"] = mem_usage
    d["mem_limit"] = mem_limit
    d["is_increasing_cpu"] = is_increasing_cpu
    d["is_increasing_mem"] = is_increasing_mem
    
    time_series_data.append(d)
    
    #print(json.dumps(doc, indent=4))
    print("Container Name: %s" % containers.name)
    print("Container ID: %s" % containers.id)
    print("CPU Percent: %s" % cpu_pcent)
    print("Memory Usage: %s" % humanize_bytes(mem_usage))
    print("Memory Limit: %s" % humanize_bytes(mem_limit))
    print("Is Increasing CPU: %s" % is_increasing_cpu)
    print("Is Increasing Memory: %s" % is_increasing_mem)
    print('-'*80)
    
    if (len(time_series_data) > 20):
        import pandas as pd
        import numpy as np
        import matplotlib.pyplot as plt
        df = pd.DataFrame(time_series_data)
        df.head()
        df['Volume'].plot()