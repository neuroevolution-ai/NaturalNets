

def write_results_to_textfile(path, configuration, log, input_size, output_size, individual_size,
                              free_parameter_usage):

    def walk_dict(node, callback_node, depth=0):
        for key, item in node.items():
            if isinstance(item, dict):
                callback_node(key, item, depth, False)
                walk_dict(item, callback_node, depth + 1)
            else:
                callback_node(key, item, depth, True)

    with open(path, 'w') as write_file:

        def write(key, value, depth, is_leaf):
            pad = ""
            for x in range(depth):
                pad = pad + "\t"
            if is_leaf:
                write_file.write(pad + key + ": " + str(value))
            else:
                write_file.write(pad + key)
            write_file.write('\n')

        walk_dict(configuration, write)

        write_file.write("\n")
        write_file.write("Genome Size: {:d}\n".format(individual_size))
        write_file.write("Free Parameters: " + str(free_parameter_usage) + "\n")
        write_file.write("Inputs: {:s}\n".format(str(input_size)))
        write_file.write("Outputs: {:s}\n".format(str(output_size)))
        write_file.write('\n')
        dash = '-' * 90
        write_file.write(dash + '\n')
        write_file.write(
            '{:<8s}{:<14s}{:<14s}{:<14s}{:<14s}{:<14s}\n'.format('gen', 'min',
                                                                 'mean', 'max', 'best', 'elapsed time (s)'))
        write_file.write(dash + '\n')

        # Last element of log contains additional info like elapsed time for training
        log_info = log.pop()

        # Write data for each episode (ignore last list index of log since it is the elapsed training time)
        for line in log:
            write_file.write(
                '{:<8d}{:<14.2f}{:<14.2f}{:<14.2f}{:<14.2f}{:<14.2f}\n'.format(line['gen'], line['min'], line['mean'],
                                                                               line['max'], line['best'],
                                                                               line['elapsed_time']))

        # Write elapsed time
        write_file.write("\nElapsed time for training: %.2f seconds" % log_info["elapsed_time_training"])

        # Write CPU info
        write_file.write("\nCPU for training: " + log_info["cpu"])
