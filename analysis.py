import argparse
import re
import matplotlib.pyplot as plt
import pandas as pd

"""
In this file, we perform analyses on the log data created through our simulations.
We start by handling and parsing our data, then we create plots of our results.
These plots do not capture all of the nuances of our data, as it is sometimes necessary
to reference multiple plots to "put the story together" in combination with the log files.
However, this gives a helpful overview of important pieces of information from our simulations.
"""

# MARK: Parse Log Data
def analyze_log_file(file_path):
    """ Analyzes a log file from our simulations and parses each line by calling `parse_log_line.` """
    with open(file_path, 'r') as file:
        log_data = []
        for line in file:
            result = parse_log_line(line.strip())
            if result:
                log_data.append(result)
        return log_data

def parse_log_line(log_line : str):
    """
    Given a line from our log data, parse it into a dictionary that can be easily
    understand and analyzed. We use regex patterns in order to match patterns and extract
    important pieces of information from our logs.

    Parameters:
        log_line (str): a single line from a process's log file

    Returns:
        A dictionary containing the following information, if available from the log_line
            - action (str): the action performed that led to the log
            - timestamp (str): the timestamp of the log in a string datetime format
            - global_time (float): the system time documented by the process
            - logical_clock (int): the counter of events/the clock updated by the client
            - local_clock (optional int): If the process has received an update from another process, it will
                                          get an update on the other process's logical clock state. This will be called
                                          the local_clock, local to the other process since it is not globally true.
                                          Otherwise, this value is None.
            - message_queue (optional int): If the process has received a message from another process, it will either
                                            add it to the queue or immediately handle it. If there are items in the queue,
                                            then the message_queue variable will document the number of "pending" messages.
                                            Otherwise, this value is None.
        
        If we are unable to pattern match a log_line, then we return None, signaling that no information can be extracted.
    """
    # For a client-specific log line, use the following regex pattern for matching and getting relevant information.
    pattern = r'(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - INFO - run_clock_cycle - (?P<action>.*?)\s+Global Time: (?P<global_time>[\d\.]+), Logical clock time: (?P<logical_clock>\d+)'
    match = re.match(pattern, log_line)

    # If we have documented a message from another client, handle it via a unique pattern to extract additional pieces of information.
    received_message_pattern = r"(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - INFO - run_clock_cycle - Received Message: the local clock time is (?P<local_clock>\d+), Global Time: (?P<global_time>[\d\.]+), Length of new message queue: (?P<message_queue>\d+), Logical clock time: (?P<logical_clock>\d+)"
    received_message_match = re.match(received_message_pattern, log_line)

    # Consider a normal match and extract important data.
    if match:
        action = match.group('action')
        timestamp = match.group('timestamp')
        # Global time refers to the system time of the client running.
        global_time = float(match.group('global_time'))
        # Logical clock keeps track of the events of the current client.
        logical_clock = int(match.group('logical_clock'))
        return {
            'action': action,
            'timestamp': timestamp,
            'global_time': global_time,
            'logical_clock': logical_clock,
            'local_clock': None,
            'message_queue': None
        }
    # Consider the case of receiving a message from another client.
    elif received_message_match:
        action = "Received Message"
        timestamp = received_message_match.group('timestamp')
        # Global time refers to the system time of the client running.
        global_time = float(received_message_match.group('global_time'))
        # Logical clock keeps track of the events of the current client.
        logical_clock = int(received_message_match.group('logical_clock'))
        # The local clock refers to the local clock of the client who sent the message.
        local_clock = int(received_message_match.group('local_clock'))
        # Message queue refers to the number of messages waiting to be handled by the client.
        message_queue = int(received_message_match.group('message_queue'))
        return {
            'action': action,
            'timestamp': timestamp,
            'global_time': global_time,
            'logical_clock': logical_clock,
            'local_clock': local_clock,
            'message_queue': message_queue
        }      
    return None


# MARK: Analyze Results

def analyze_logical_clock(p1_df, p2_df, p3_df, result_dirpath):
    """
    Plot a singular process's logical clock data. This should be a simple, monotonic graph.
    It will show which processes are faster or slower based on the slopes.
    
    Parameters:
        p1_df (DataFrame): the data frame for process 1's information
        p2_df (DataFrame): the data frame for process 2's information
        p3_df (DataFrame): the data frame for process 3's information
        result_dirpath (str): The directory path that the result should be placed into.

    Outcome:
        Creates a PNG plot using the data provided that is saved into the directory path
        inputted as a parameter.
    """        
    # Plot the logical clock for each series
    plt.figure(figsize=(10, 6))
    plt.plot(p1_df['global_time'], p1_df['logical_clock'], 'b-', label='Process 1', markersize=5, linestyle=' ', marker='o', color='blue')
    plt.plot(p2_df['global_time'], p2_df['logical_clock'], 'g-', label='Process 2', markersize=5, linestyle=' ', marker='o', color='green')
    plt.plot(p3_df['global_time'], p3_df['logical_clock'], 'r-', label='Process 3', markersize=5, linestyle=' ', marker='o', color='red')

    # Customize the plot with helpful information and sizing.
    plt.xlabel('Global Time')
    plt.ylabel('Logical Clock')
    plt.title('Logical Clock Over Time for Different Processes')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save figure into the given directory path
    result_path = f"{result_dirpath}/logical_clock_plot"
    plt.savefig(result_path)

def analyze_diff_systime_logtime(p1_df, p2_df, p3_df, result_dirpath):
    """
    Find the drift between the logical clock time and the system time. 
    We can do this by taking the difference of each process and their respective timings, and we should
    ideally see a constant line (the difference between them should be relatively identical). However,
    if we see a slope, then this indicates that the clock is drifting.
    """
    # Dividing by 1e9 converts our system time into seconds and avoids overflow.
    p1_df['drift'] = p1_df['logical_clock'] - p1_df['global_time'] / 1e9
    p2_df['drift'] = p2_df['logical_clock'] - p2_df['global_time'] / 1e9
    p3_df['drift'] = p3_df['logical_clock'] - p3_df['global_time'] / 1e9    

    # Plot the drifts for all machines with different colors
    plt.figure(figsize=(10, 6))
    plt.plot(p1_df['global_time'], p1_df['drift'], label='Process 1', markersize=5, color='b', linestyle=' ', marker='o')
    plt.plot(p2_df['global_time'], p2_df['drift'], label='Process 2', markersize=5, color='g', linestyle=' ', marker='o')
    plt.plot(p3_df['global_time'], p3_df['drift'], label='Process 3', markersize=5, color='r', linestyle=' ', marker='o')

    # Customize the plot
    plt.xlabel('Global Time')
    plt.ylabel('Drift (Logical Clock - System Time)')
    plt.title('Drift between Global Time and Logical Clocks')
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Save figure into the given directory path
    result_path = f"{result_dirpath}/drift_plot"
    plt.savefig(result_path)


def analyze_gaps(p1_df, p2_df, p3_df, result_dirpath):
    """Analyze the gaps between a process's logical clock and the local clock times that it receives from other processes."""

    # What is a gap? If I am Process #1 on my 100th logical clock tick, and I receive a message from Process #2 which is on its 120th clock tick,
    # that is a 20 point gap. We want to plot these gaps to see if any patterns may exist.
    # We only get these data points when we receive a message.

    # Filter out rows where 'local_clock' is None (or NaN)
    p1_df_filtered = p1_df[p1_df['local_clock'].notna()]
    p1_df_filtered.loc[:, 'gap'] = p1_df_filtered['logical_clock'] - p1_df_filtered['local_clock']
    # p1_df_filtered['gap'] = p1_df_filtered['logical_clock'] - p1_df_filtered['local_clock']

    p2_df_filtered = p2_df[p2_df['local_clock'].notna()]
    p2_df_filtered.loc[:, 'gap'] = p2_df_filtered['logical_clock'] - p2_df_filtered['local_clock']
    # p2_df_filtered['gap'] = p2_df_filtered['logical_clock'] - p2_df_filtered['local_clock']

    p3_df_filtered = p3_df[p3_df['local_clock'].notna()]
    p3_df_filtered.loc[:, 'gap'] = p3_df_filtered['logical_clock'] - p3_df_filtered['local_clock']
    # p3_df_filtered['gap'] = p3_df_filtered['logical_clock'] - p3_df_filtered['local_clock']

    # Plot the drifts for all machines with different colors
    plt.figure(figsize=(10, 6))
    plt.plot(p1_df_filtered['global_time'], p1_df_filtered['gap'], label='Process 1', markersize=5, color='b', linestyle=' ', marker='o')
    plt.plot(p2_df_filtered['global_time'], p2_df_filtered['gap'], label='Process 2', markersize=5, color='g', linestyle=' ', marker='o')
    plt.plot(p3_df_filtered['global_time'], p3_df_filtered['gap'], label='Process 3', markersize=5, color='r', linestyle=' ', marker='o')

    # Customize the plot
    plt.xlabel('Global Time')
    plt.ylabel('Gaps (Current Logical Clock - Other Process Local Clock)')
    plt.title('Gaps between Logical Clocks')
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Save figure into the given directory path
    result_path = f"{result_dirpath}/gap_plot"
    plt.savefig(result_path)


def analyze_message_queues(p1_df, p2_df, p3_df, result_dirpath):
    """Analyze the messages queues of each process"""
    
    # Filter out rows where 'message_queue' is None (or NaN)
    p1_df_filtered = p1_df[p1_df['message_queue'].notna()]
    p2_df_filtered = p2_df[p2_df['message_queue'].notna()]
    p3_df_filtered = p3_df[p3_df['message_queue'].notna()]

    # Plot the drifts for all machines with different colors
    plt.figure(figsize=(10, 6))
    plt.plot(p1_df_filtered['global_time'], p1_df_filtered['message_queue'], label='Process 1', markersize=5, color='b', linestyle=' ', marker='o')
    plt.plot(p2_df_filtered['global_time'], p2_df_filtered['message_queue'], label='Process 2', markersize=5, color='g', linestyle=' ', marker='o')
    plt.plot(p3_df_filtered['global_time'], p3_df_filtered['message_queue'], label='Process 3', markersize=5, color='r', linestyle=' ', marker='o')

    # Customize the plot
    plt.xlabel('Global Time')
    plt.ylabel('Message Queue Count (# of Pending Messages)')
    plt.title('Message Queue Count across Clients')
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Save figure into the given directory path
    result_path = f"{result_dirpath}/message_queue_plot"
    plt.savefig(result_path)


# MARK: Parse Arguments
def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Chat Client')

    # Add arguments
    parser.add_argument(
        '--runs',
        type=int,
        default=5,
        help='Number of runs of simulation - must match the simulation number of runs (default: 5)'    
    )
    return parser.parse_args()

# MARK: Main
if __name__ == "__main__":
    # Get the number of runs to analyze
    args = parse_arguments()
    runs = args.runs
    
    # Analyze each simulation separately
    for i in range(runs):
        p1_path = f"./results/simulation_{i}/simulation_{i}_logfile_vm1"
        p2_path = f"./results/simulation_{i}/simulation_{i}_logfile_vm2"
        p3_path = f"./results/simulation_{i}/simulation_{i}_logfile_vm3"

        # Parse data from log files
        parsed_p1 = analyze_log_file(p1_path)
        parsed_p2 = analyze_log_file(p2_path)
        parsed_p3 = analyze_log_file(p3_path)

        # Create DataFrames for each of the parsed data to make it easier to handle.
        p1_df = pd.DataFrame(parsed_p1)
        p2_df = pd.DataFrame(parsed_p2)
        p3_df = pd.DataFrame(parsed_p3)

        # For each simulation, we want to analyze the following 4 characteristics:
        #       Logical clock time per process with varying speeds
        #       Drift between real clock time and logical clock time within a process
        #       Analyze the size of jumps and gaps between process clock times
        #       Analyze the length of message queues

        result_dirpath = f"./results/simulation_{i}"
        analyze_logical_clock(p1_df, p2_df, p3_df, result_dirpath)
        analyze_diff_systime_logtime(p1_df, p2_df, p3_df, result_dirpath)
        analyze_gaps(p1_df, p2_df, p3_df, result_dirpath)
        analyze_message_queues(p1_df, p2_df, p3_df, result_dirpath)