import sys
import os
import grpc
import threading
import logging
import argparse
import socket # Only for validating IP address inputted.
from datetime import datetime
# Import our proto materials
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from proto import service_pb2
from proto import service_pb2_grpc
import random
import time
import re


# MARK: Client Class
class Client:
    """
    The Client class controls the sending and receiving of messages from the other clients. 
    It also handles the controlling of a process's logical clock. 
    """
    def __init__(self, host, port, id, max_clock_rate, event_probability_upper_range):
        '''
        Initialization preamble that occurs before clock:
        (1) Create network queue
        (2) Set up virtual log
        (3) Start running clock 
        '''
        self.host = host
        self.port = port
        self.channel = grpc.insecure_channel(f'{host}:{port}')
        self.stub = service_pb2_grpc.MessageServerStub(self.channel)
        self.current_user = str(id)
        self.other_vms = ["1", "2", "3"]
        self.other_vms.remove(self.current_user)

        # (1) create network queue
        self.messageObservation = threading.Thread(target=self._monitor_messages, daemon=True)
        self.message_q = []

        # (2) create virtual log
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s',
            filename=f"./logs/logfile_vm{self.current_user}"
        )
        self.logger = logging.getLogger(__name__)

        # (3) start running clock
        # Clock rate defaults to have the upper range of 6
        self.clock_rate = random.randint(1, max_clock_rate)
        self.sleep_time = 1.0 / self.clock_rate
        self.logical_clock = 1
        self.running = True
        self.event_probability_upper_range = event_probability_upper_range
        self.run_clock_cycle()
        
        
    def run_clock_cycle(self):
        '''
        (1) Update local clock
        '''
        print("running clock now")
        while self.running:
            self._handle_get_inbox()

            # If there are messages in the queue: 
            if self.message_q:
                print("detected a message")
                message = self.message_q.pop(0)
                match = re.search(r"local clock time is (?P<local_clock>\d+)", message.message.message)
                if match:
                    local_clock_time = match.group('local_clock')
                    self.logical_clock = max(self.logical_clock, int(local_clock_time)) + 1

                self.logger.info(f"Received Message: {message.message.message}, Global Time: {time.time()}, Length of new message queue: {len(self.message_q)}, Logical clock time: {self.logical_clock}")
                
            # If no messages in queue, probabilistically take another action.
            else:
                print("Did not detect message. Creating an event.")
                self.logical_clock += 1
                # Default upper range is 10
                event = random.randint(1, self.event_probability_upper_range)
                match event:
                    case 1:
                        message =  f"the local clock time is {self.logical_clock}"
                        self._handle_send_message(self.other_vms[0], message)
                        self.logger.info(f"Sent Message: {message} to machine {self.other_vms[0]}, Global Time: {time.time()}, Logical clock time: {self.logical_clock}")
                    case 2:
                        message =  f"the local clock time is {self.logical_clock}"
                        self._handle_send_message(self.other_vms[1], message)
                        self.logger.info(f"Sent Message: {message} to machine {self.other_vms[1]}, Global Time: {time.time()}, Logical clock time: {self.logical_clock}")
                    case 3:
                        message =  f"the local clock time is {self.logical_clock}"
                        self._handle_send_message(self.other_vms[0], message)
                        self._handle_send_message(self.other_vms[1], message)
                        self.logger.info(f"Sent Message: {message} to machine {self.other_vms[0]} and {self.other_vms[1]}, Global Time: {time.time()}, Logical clock time: {self.logical_clock}")
                    case _:
                        self.logger.info(f"Internal Update. Global Time: {time.time()}, Logical clock time: {self.logical_clock}")

            time.sleep(self.sleep_time)

    def _handle_send_message(self, recipient, message):
        """Sends the server a message request and handles potential failures to deliver the message."""
        try: 
            print(f"Sending message request to {recipient} with message: {message}")
            message_request = service_pb2.Message(
                sender=self.current_user,
                recipient=recipient,
                message=message,
                timestamp=str(datetime.now())
            )
            response = self.stub.SendMessage(message_request)

            if response.status == service_pb2.MessageResponse.MessageStatus.SUCCESS:
                print(f"Message sent to {recipient} successfully")
            else:
                self.logger.error(f"Message failed to send to {recipient}")

        except Exception as e:
            self.logger.error(f"Message failed with error to send to {recipient} with error: {e}")
            sys.exit(1)
    
    def _monitor_messages(self):
        """
        Creates a request to the server to open a stream. This stream will yield messages that other clients
        are sending. When the user is supposed to receive a message, it will hear that message by iterating over
        the stream iterator provided as a response to the RPC call.
        """
        try:
            print(f"Starting message monitoring...")
            message_iterator = self.stub.MonitorMessages(service_pb2.MonitorMessagesRequest(username=self.current_user))
            while True:
                for message in message_iterator:
                    self.chat_ui.display_message(from_user=message.sender, message=message.message)

        except Exception as e:
            self.logger.error(f"Failed with error in monitor messages: {e}")
            sys.exit(1)

    def _handle_get_inbox(self):
        """
        Sends a request to the server to retrieve the process's pending messages.
        It handles these responses in the form of a stream of Messages.
        """
        try:
            print("Send request to get pending messages.")    
            responses = self.stub.GetPendingMessage(service_pb2.PendingMessageRequest(username=self.current_user))
            for response in responses:
                self.message_q.append(response)
            print(f"Retrieved pending messages: {self.message_q}")
        
        except Exception as e:
            print(f"Failed in handle get inbox with error: {e}")
            sys.exit(1)
    
    
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
        '--id',
        type=int,
        default=1,
        help='Server id (default: 1)'    
    )

    parser.add_argument(
        '--max_clock_rate',
        type=int,
        default=6,
        help='Max possible clock rate (default: 6)'  
    )

    parser.add_argument(
        '--event_probability_upper_range',
        type=int,
        default=10,
        help='Probability of sending a message as the upper range of the random prob. between 1 and this inputted number (default: 10)'  
    )

    return parser.parse_args()

# MARK: MAIN
if __name__ == "__main__":
    # Set up arguments.
    args = parse_arguments()
    port = args.port
    ip = args.ip
    id = args.id
    max_clock_rate = args.max_clock_rate
    event_prob = args.event_probability_upper_range
    client = Client(host=ip, port=port, id=id, max_clock_rate=max_clock_rate, event_probability_upper_range=event_prob)