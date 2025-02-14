import json
import logging

# Configure logging set-up. We want to log times & types of logs, as well as
# function names & the subsequent message.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s'
)

# Create a logger
logger = logging.getLogger(__name__)


class ServerRequest:
    """
    The ServerRequest class contains helpful functions to serialize and deserialize requests
    to the server, as well as responses from the server.
    """

    @staticmethod
    def serialize_to_str(version, op_code, arguments, isJSON=False):
        """
        Handles the translation of requests from the client into serialized messages
        that can be sent over the wire. This function handles our custom protocol with delimiters 
        and the JSON protocol, which is specified by when the server or client begins.

                Parameters:
                        version: an integer representing the current version the client is running
                        op_code: a string detailing the operation being requested
                        arguments: a list of applicable arguments to the operations
                        isJSON: a boolean state deciding whether to use the custom protocol or JSON protocol
                Returns:
                        a string containing the serialized request ready to be sent over the wire
        """
        if isJSON:
            operation_request = {
                "version": version,
                "length": len(op_code) + len(arguments),
                "opcode": op_code,
                "arguments": arguments
            }
            # Return as JSON string.
            logger.info(f"Client request serialized using JSON protocol as {operation_request}")
            return json.dumps(operation_request)
        else:
            operation_specific = f"{op_code}"
            for arg in arguments:
                    operation_specific += f"§{arg}"
            request = f"{version}§{len(operation_specific)}§{operation_specific}"
            logger.info(f"Client request serialized using custom protocol as {request}")
            return request


    @staticmethod
    def parse_serialized_data(data, isJSON=False):
        """
        Handles the translation of serialized data from the server into data that can be
        handled by the client. Outputs a dictionary containing a version, the length of the message,
        the operation code, and the arguments for the operation.

                Parameters:
                        data: a string or byte string of data passed by the server
                        isJSON: a boolean state deciding whether to use the custom protocol or JSON protocol
                Returns:
                        a dictionary with keys for the version, length, operation code, and arguments provided
                        by the server.
        """
        try:
            logger.info(f"Client parsing server response. Protocol isJSON: {isJSON}. Data being parsed is the following: {data}")
            # If we have not decoded the byte string into a normal string, ensure it is decoded.
            if not isinstance(data, str):
                data = data.decode("utf-8")
            
            message = {}
            if isJSON:
                # Create the appropriate JSON object from the string.
                json_obj = json.loads(data)
                # Parse the important information into an easy-to-use dictionary.
                message["version"] = json_obj["version"]
                message["length"] = json_obj["length"]
                message["opcode"] = json_obj["opcode"]
                # Handle arguments that contain lists.
                #       NOTE: This only applies to the initial list of users that the server 
                #       sends upon a successful login.
                if json_obj["opcode"] == "LOGIN_SUCCESS":
                    message["arguments"] = json_obj["arguments"][0:2]
                    message["arguments"] += json_obj["arguments"][2][0:]
                else:
                    message["arguments"] = json_obj["arguments"]
            else:
                # Using our custom protocol outlined in our documentation,
                # parse the data sent by the server by splitting at the delimiter.
                delimiter = '§'
                split_data = data.split(delimiter)
                message["version"] = split_data[0]
                message["length"] = split_data[1]
                message["opcode"] = split_data[2]
                message["arguments"] = split_data[3:]
            # Both JSON & the custom protocol yield the same parsed result.
            return message
        except Exception as e:
            # Handle parsing errors.
            logger.error(f"Client could not parse server response for data {data}. Failed with error {e}.")
            return ValueError


    @staticmethod
    def decode_multiple_json(data):
        """
        Handle multiple JSON objects sent via the wire. If multiple messages are sent together,
        then we must separate them properly. We can do so by decoding one JSON object at a time.

                Parameters:
                        data: a string or byte string of data passed by the server
                Returns:
                        a list of JSON objects parsed as strings
        """
        decoder = json.JSONDecoder()
        pos = 0
        messages = []
        while pos < len(data):
            # Decode JSON object, if possible.
            obj, index = decoder.raw_decode(data, pos)  
            messages.append(json.dumps(obj))
            # Detect next JSON object.
            pos = index  
        return messages