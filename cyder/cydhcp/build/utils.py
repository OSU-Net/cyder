def join_args(args, depth=2):
    build_str = ""
    for arg in args:
        build_str += "{0}{1}\n".format(depth*'\t', arg)
    return build_str
