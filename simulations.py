import subprocess
import time
import os
import signal
import argparse
import socket
import shutil

# MARK: Run Simulation

def run_simulation(ip, port, duration, runs):
    """
    Begin the simulation by creating 3 separate processes that run on the server.
    Handle starting the processes at the same time, allow them to run for a set duration,
    then shut down each process.

    Repeat these steps for the appropriate number of runs, moving the data such as log files
    into the result folder as they become available.
    
    Parameters:
        ip: the ip address that the server and clients should use
        port: the port that the server and clients should use
        duration (int): the time that each run of the simulation should take in seconds
        runs (int): the number of times the simulation should be run

    Outcome:
        In the results/ folder, each simulation should have its own unique log files from each process.
        These log files can be analyzed visually and in combination with our analysis file.
    """

    # List of commands to run the different processes
    commands = [
        f'python Client/main.py --ip {ip} --port {port} --id 1',
        f'python Client/main.py --ip {ip} --port {port} --id 2',
        f'python Client/main.py --ip {ip} --port {port} --id 3'
    ]

    # Start the server and wait for the server to begin.
    server_cmd = subprocess.Popen(f'python Server/main.py --ip {ip} --port {port}', shell=True)
    time.sleep(3)

    # We want the simulation to run for the inputted number of times.
    for run_number in range(runs):
        # Start the processes
        processes = []
        for cmd in commands:
            processes.append(subprocess.Popen(cmd, shell=True))

        # Wait for the inputted number of seconds
        time.sleep(duration)

        # Stop the clients by sending Ctrl+C (SIGINT)
        for p in processes:
            # Sends SIGINT which simulates Ctrl+C
            p.send_signal(signal.SIGINT)
        
        # Waits for the process to terminate
        for p in processes:
            p.wait()
        time.sleep(1)

        # Move the log files to organize results
        handle_logfiles(run_number)

        # Give a break in between the next run (for debugging purposes)
        print(f'Completed run number: {run_number}')
        time.sleep(3)

    # Kill the server to end the simulations.
    server_cmd.send_signal(signal.SIGINT)


def handle_logfiles(run_number):
    """
    Upon completion of a simulation, move the resulting log data from the temporary folder /logs/ into the results folder,
    symbolizing that the logging of the processes is complete and allowing for the next iteration of simulation to begin.
    
    Parameters:
        run_number (int): the number of times the simulation should be run

    Outcome:
        Moves the log data from ./logs into ./results
    """

    # Define the source and destination directories
    source_dir = './logs'
    if not os.path.exists(source_dir):
        os.makedirs(source_dir)
        print(f"Created logs directory: {source_dir}")

    destination_dir = f'./results/simulation_{run_number}'

    # Make sure the destination directory exists, create it if not
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    # Loop through all files in the source directory
    for filename in os.listdir(source_dir):
        file_path = os.path.join(source_dir, filename)
        
        # Check if it's a file (not a directory)
        if os.path.isfile(file_path):
            new_filename = f"simulation_{run_number}_{filename}"
            destination_path = os.path.join(destination_dir, new_filename)
            
            # Move and rename the log files
            shutil.move(file_path, destination_path)
            print(f"Moved and renamed {filename} to {new_filename}")


# MARK: Command-line arguments.
# Validate an IP address
def validate_ip(value):
    try:
        # Try to convert the value to a valid IP address using socket
        socket.inet_aton(value)  # This will raise an error if not a valid IPv4 address
        return value
    except socket.error:
        raise argparse.ArgumentTypeError(f"Invalid IP address: {value}")
    
def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Chat Client')

    # Add arguments
    parser.add_argument(
        '--ip',
        type=validate_ip,
        required=True,
        help='Server IP'    
    )

    parser.add_argument(
        '--port',
        type=int,
        default=5001,
        help='Server port (default: 5001)'    
    )

    parser.add_argument(
        '--duration',
        type=int,
        default=60,
        help='Duration of a single simulation (default: 60 seconds)'    
    )

    parser.add_argument(
        '--runs',
        type=int,
        default=5,
        help='Number of runs of the simulation (default: 5)'    
    )

    return parser.parse_args()

# MARK: MAIN
if __name__ == "__main__":
    # Set up arguments.
    args = parse_arguments()
    ip = args.ip
    port = args.port
    duration = args.duration
    runs = args.runs
    run_simulation(ip, port, duration, runs)

# Example Usage:
# python simulations.py --ip 127.0.0.1 --port 5001 --duration 90 --runs 5