import docker

client = docker.DockerClient(base_url='unix:///var/run/docker.sock')
for containers in client.containers.list():
    print(containers.stats(decode=None, stream = False))