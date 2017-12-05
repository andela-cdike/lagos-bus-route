def check_if_dups_have_diffs():
    """
    I am not sure if I have updated this table since the first
    time I populated. This script is supposed to check if the
    duplicates have any meaningful difference so I can decide on
    how I will decide what duplicate to keep

    To be run from shell. This doesn't seem like it will be used
    enough times to warrant a special management command

    Result: After running this, I verified that there were no
    differences. Therefore, I can just clean all recent additions by
    clearing the routes db and running the fixture that started it all.
    """
    current_num_routes = 79
    issues = []
    for route_idx in xrange(1, current_num_routes + 1):
        num_dups = 4
        route = Route.objects.filter(route_id=route_idx)
        num_unique_nodes = route.count() / num_dups
        for node_position in xrange(1, num_unique_nodes + 1):
            # compare values in nodes
            fields = ('busstop', 'busstop_type', 'route_id', 'node_position')
            nodes = route.filter(node_position=node_position)
            for field in fields:
                if not (getattr(nodes[0], field) == getattr(nodes[1], field) ==
                        getattr(nodes[2], field) == getattr(nodes[3], field)):
                    msg = 'Node: {0}; Route: {1}'.format(
                        node_position, route_idx)
                    issues.append(msg)
    return issues
