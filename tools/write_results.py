

def write_results_to_textfile(path, log, individual_size, elapsed_time):

    with open(path, 'w') as write_file:

        write_file.write('\n')
        write_file.write('Genome Size: {:d}\n'.format(individual_size))
        # write_file.write('Inputs: {:d}\n'.format(input_size))
        # write_file.write('Outputs: {:d}\n'.format(output_size))
        write_file.write('\n')
        dash = '-' * 80
        write_file.write(dash + '\n')
        write_file.write(
            '{:<8s}{:<16s}{:<16s}{:<16s}{:<16s}\n'.format('gen', 'min', 'mean', 'max', 'elapsed time (s)'))
        write_file.write(dash + '\n')

        # Write data for each episode
        for line in log:
            write_file.write(
                '{:<8d}{:<16.2f}{:<16.2f}{:<16.2f}{:<16.2f}\n'.format(line['gen'], line['min'], line['mean'],
                                                                      line['max'], line['elapsed_time']))

        # Write elapsed time
        write_file.write("\nElapsed time for training: %.2f seconds" % elapsed_time)
