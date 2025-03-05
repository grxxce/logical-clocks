import os
import shutil
import unittest
from unittest.mock import patch, MagicMock, call
import tempfile
import sys
import time
import threading

# Import the modules to test
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from simulations import handle_logfiles  # Import the specific function we're testing
from Client.main import Client

class TestSimulations(unittest.TestCase):
    
    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.logs_dir = os.path.join(self.test_dir, 'logs')
        self.results_dir = os.path.join(self.test_dir, 'results')
        
        # Save the original working directory
        self.original_dir = os.getcwd()
        # Change to the test directory
        os.chdir(self.test_dir)
        
    def tearDown(self):
        # Return to the original directory
        os.chdir(self.original_dir)
        # Clean up the test directory
        shutil.rmtree(self.test_dir)
    
    def test_handle_logfiles_creates_logs_dir_if_not_exists(self):
        """Test that handle_logfiles creates the logs directory if it doesn't exist."""
        # Ensure logs directory doesn't exist
        self.assertFalse(os.path.exists(self.logs_dir))
        
        # Call the function
        with patch('builtins.print') as mock_print:
            handle_logfiles(1)
            
        # Check that logs directory was created
        self.assertTrue(os.path.exists(self.logs_dir))
        mock_print.assert_any_call(f"Created logs directory: ./logs")
    
    def test_handle_logfiles_uses_existing_logs_dir(self):
        """Test that handle_logfiles uses the existing logs directory if it exists."""
        # Create logs directory
        os.makedirs(self.logs_dir)
        
        # Create a test log file
        test_log_path = os.path.join(self.logs_dir, 'logfile_vm1')
        with open(test_log_path, 'w') as f:
            f.write('Test log content')
        
        # Call the function
        with patch('builtins.print') as mock_print:
            handle_logfiles(1)
        
        # Check that the function didn't print about creating the directory
        for call in mock_print.call_args_list:
            self.assertNotIn("Created logs directory", call[0][0])
    
    def test_handle_logfiles_creates_results_dir(self):
        """Test that handle_logfiles creates the results directory structure."""
        # Call the function
        run_number = 42
        handle_logfiles(run_number)
        
        # Check that results directory was created with the correct run number
        expected_results_dir = os.path.join(self.results_dir, f'simulation_{run_number}')
        self.assertTrue(os.path.exists(expected_results_dir))
    
    def test_handle_logfiles_with_empty_logs_dir(self):
        """Test that handle_logfiles handles an empty logs directory correctly."""
        # Create an empty logs directory
        os.makedirs(self.logs_dir)
        
        # Call the function
        run_number = 10
        with patch('shutil.copy') as mock_copy:
            handle_logfiles(run_number)
            
            # Verify shutil.copy was not called
            mock_copy.assert_not_called()


class TestClientLogicalClock(unittest.TestCase):
    
    def setUp(self):
        # Create a temporary directory for logs
        self.test_dir = tempfile.mkdtemp()
        self.logs_dir = os.path.join(self.test_dir, 'logs')
        os.makedirs(self.logs_dir)
        
        # Save original directory and change to test directory
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)
        
        # Mock gRPC channel and stub
        self.mock_channel = MagicMock()
        self.mock_stub = MagicMock()
        
        # Patch necessary components
        self.grpc_channel_patcher = patch('grpc.insecure_channel', return_value=self.mock_channel)
        self.stub_patcher = patch('proto.service_pb2_grpc.MessageServerStub', return_value=self.mock_stub)
        self.thread_patcher = patch.object(threading.Thread, 'start')
        self.run_clock_patcher = patch.object(Client, 'run_clock_cycle')
        
        # Start patchers
        self.grpc_channel_patcher.start()
        self.stub_patcher.start()
        self.thread_patcher.start()
        self.run_clock_patcher.start()
        
        # Create client instance with patched components
        self.client = Client(host='localhost', port=5001, id=1)
        
        # Reset the run_clock_cycle patch to test it
        self.run_clock_patcher.stop()
        
    def tearDown(self):
        # Stop all patchers
        self.grpc_channel_patcher.stop()
        self.stub_patcher.stop()
        self.thread_patcher.stop()
        
        # Return to original directory and clean up
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)
    
    def test_logical_clock_initialization(self):
        """Test that the logical clock is initialized correctly."""
        self.assertEqual(self.client.logical_clock, 1)
        self.assertTrue(1 <= self.client.clock_rate <= 6)
        self.assertEqual(self.client.sleep_time, 1.0 / self.client.clock_rate)
    
    @patch('time.sleep')
    @patch('random.randint')
    def test_logical_clock_increments(self, mock_randint, mock_sleep):
        """Test that the logical clock increments with each cycle."""
        # Set up mocks
        mock_randint.return_value = 7  # For internal event
        
        # Stop the clock after a few iterations
        def stop_after_iterations(*args, **kwargs):
            self.client.logical_clock += 1
            if self.client.logical_clock >= 5:
                self.client.running = False
        
        # Replace _handle_get_inbox with our test function
        self.client._handle_get_inbox = stop_after_iterations
        
        # Run the clock cycle for a few iterations
        with patch.object(self.client, '_handle_send_message'):
            self.client.run_clock_cycle()
        
        # Check that the logical clock was incremented
        self.assertEqual(self.client.logical_clock, 7)
    
    @patch('time.sleep')
    def test_logical_clock_updates_on_message_receipt(self, mock_sleep):
        """Test that the logical clock updates correctly when receiving messages."""
        # Create a mock message with a higher logical clock value
        mock_message = MagicMock()
        mock_message.message.message = "the local clock time is 10"
        
        # Add the message to the queue
        self.client.message_q = [mock_message]
        
        # Stop after processing one message
        def stop_after_message(*args, **kwargs):
            if not self.client.message_q:
                self.client.running = False
        
        # Replace _handle_get_inbox with our test function
        self.client._handle_get_inbox = stop_after_message
        
        # Initial clock value
        initial_clock = self.client.logical_clock
        
        # Run the clock cycle
        with patch.object(self.client.logger, 'info') as mock_logger:
            self.client.run_clock_cycle()
        
        # Check that the logical clock was incremented
        self.assertEqual(self.client.logical_clock, initial_clock +2)
    
    
    @patch('time.sleep')
    @patch('random.randint')
    def test_logical_clock_with_multiple_events(self, mock_randint, mock_sleep):
        """Test the logical clock behavior with multiple different events."""
        # Set up a sequence of events: internal, send to VM2, send to VM3, send to both
        mock_randint.side_effect = [5, 1, 2, 3, 5]
        
        # Count iterations and stop after a few
        self.iteration_count = 0
        def count_iterations(*args, **kwargs):
            self.iteration_count += 1
            if self.iteration_count >= 4:
                self.client.running = False
        
        # Replace _handle_get_inbox with our test function
        self.client._handle_get_inbox = count_iterations
        
        # Run the clock cycle
        with patch.object(self.client, '_handle_send_message') as mock_send, \
             patch.object(self.client.logger, 'info') as mock_logger:
            self.client.run_clock_cycle()
        
        # Check that the logical clock was incremented correctly
        self.assertEqual(self.client.logical_clock, 5)  # 1 (initial) + 4 iterations
        
        # Verify the correct sequence of calls
        expected_calls = [
            # First iteration: internal event (clock = 2)
            call(f"Internal Update. Global Time: {time.time()}, Logical clock time: 2"),
            
            # Second iteration: send to VM2 (clock = 3)
            call(f"Sent Message: the local clock time is 3 to machine {self.client.other_vms[0]}, "
                 f"Global Time: {time.time()}, Logical clock time: 3"),
            
            # Third iteration: send to VM3 (clock = 4)
            call(f"Sent Message: the local clock time is 4 to machine {self.client.other_vms[1]}, "
                 f"Global Time: {time.time()}, Logical clock time: 4"),
            
            # Fourth iteration: send to both (clock = 5)
            call(f"Sent Message: the local clock time is 5 to machine {self.client.other_vms[0]} and {self.client.other_vms[1]}, "
                 f"Global Time: {time.time()}, Logical clock time: 5")
        ]
        
        # Check that all expected log calls were made (ignoring exact time values)
        self.assertEqual(mock_logger.call_count, 4)
        for i, expected_call in enumerate(expected_calls):
            # Extract just the message part for comparison, ignoring the exact time values
            actual_msg = mock_logger.call_args_list[i][0][0]
            expected_msg = expected_call[0]
            
            # Compare the parts of the message that don't include the exact time
            self.assertIn(f"Logical clock time: {i+2}", actual_msg)
            if "Internal Update" in expected_msg:
                self.assertIn("Internal Update", actual_msg)
            elif "Sent Message" in expected_msg:
                self.assertIn("Sent Message", actual_msg)
                if "and" in expected_msg:
                    self.assertIn(f"to machine {self.client.other_vms[0]} and {self.client.other_vms[1]}", actual_msg)
                else:
                    recipient = self.client.other_vms[0] if "to machine 2" in expected_msg else self.client.other_vms[1]
                    self.assertIn(f"to machine {recipient}", actual_msg)


if __name__ == '__main__':
    unittest.main()