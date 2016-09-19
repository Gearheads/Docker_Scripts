import json
from docker import Client
cli = Client(base_url='unix://var/run/docker.sock')

list_containers = cli.containers(all=True)
json_name = "Names"
json_id = "Id"
cpu="cpu_stats"
memory="memory_stats"
precpu="precpu_stats"

for container in list_containers:
    print "Container ID and info:"
    container_id = container[json_id]
    print container_id
    # print json.dumps(container, sort_keys=True, indent=4, separators=(',',': '))
    container_name = container[json_name][0]
    print container_name
    print
    
    print "Container stats:"
    stats = cli.stats(container, stream=False)
    # print json.dumps(stats, sort_keys=True, indent=4, separators=(',',': '))
    print "CPU_STATS:"
    print json.dumps(stats[cpu], sort_keys=True, indent=4, separators=(',',': '))
    print "MEMORY_STATS:"
    print json.dumps(stats[memory], sort_keys=True, indent=4, separators=(',',': '))
    print "PRE_CPU_STATS:"
    print json.dumps(stats[precpu], sort_keys=True, indent=4, separators=(',',': '))
    print

    print "Container inspect:"
    inspect = cli.inspect_container(container_name)
    # print json.dumps(inspect, sort_keys=True, indent=4, separators=(',',': '))
    state = inspect["State"]
    print "State of container:"
    print json.dumps(state, sort_keys=True, indent=4, separators=(',',': '))
    print

    print "<metrictype=\"IntCounter\"name=\"Docker|RequestCounter:"+container_name+"\"value=\""+container_id+"\"/>"
    print
