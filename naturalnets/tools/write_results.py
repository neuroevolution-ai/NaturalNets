

def write_results_to_textfile(path, configuration, log, log_entry_keys, input_size, output_size, individual_size,
                              free_parameter_usage):

    def walk_dict(node, callback_node, depth=0):
        for key, item in node.items():
            if isinstance(item, dict):
                callback_node(key, item, depth, False)
                walk_dict(item, callback_node, depth + 1)
            else:
                callback_node(key, item, depth, True)

    with open(path, "w") as write_file:

        def write(key, value, depth, is_leaf):
            pad = ""
            for x in range(depth):
                pad = pad + "\t"
            if is_leaf:
                write_file.write(pad + key + ": " + str(value))
            else:
                write_file.write(pad + key)
            write_file.write("\n")

        walk_dict(configuration, write)

        write_file.write("\n")
        write_file.write(f"Genome Size: {individual_size}\n")
        write_file.write(f"Free Parameters: {free_parameter_usage}\n")
        write_file.write(f"Inputs: {input_size}\n")
        write_file.write(f"Outputs: {output_size}\n")
        write_file.write("\n")
        dash = "-" * 150
        write_file.write(dash + "\n")

        heading_line = "".join([f"{x:<14s}" for x in log_entry_keys])
        write_file.write(heading_line + "\n")

        write_file.write(dash + "\n")

        # Last element of log contains additional info like elapsed time for training
        log_info = log.pop()

        # Write data for each episode (ignore last list index of log since it is the elapsed training time)
        for line in log:
            log_line = ""

            for _key in log_entry_keys:
                log_line += f"{line[_key]:<14.2f}"

            write_file.write(log_line + "\n")

        # Write elapsed time
        write_file.write(f"Elapsed time for training: {log_info['elapsed_time_training']:.2f} seconds\n")

        # Write CPU info
        write_file.write(f"CPU for training: {log_info['cpu']}")
