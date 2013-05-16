def join_args(args, depth=2):
    return "\n".join(
        map(lambda y: "{0}{1};".format("\t" * depth, y), args)) + '\n'
