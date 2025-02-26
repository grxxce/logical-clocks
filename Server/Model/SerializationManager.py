# import json
# import logging

# # Configure logging set-up. We want to log times & types of logs, as well as
# # function names & the subsequent message.
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s'
# )

# # Create a logger
# logger = logging.getLogger(__name__)

# class SerializationManager:
#     """
#     The SerializationManager class contains helpful functions to serialize responses to sent to the client,
#     and to parse and deserialize requests from the client.
#     """

#     @staticmethod
#     def serialize_to_str(version, op_code, arguments, isJSON=False):
#         """
#         Handles the translation of responses from the server into serialized messages
#         that can be sent over the wire. This function handles our custom protocol with delimiters 
#         and the JSON protocol, which is specified when the server or client begins.

#         Parameters:
#                 version: an integer representing the current version the server is running
#                 op_code: a string detailing the operation being responded to
#                 arguments: a list of applicable arguments to the operations
#                 isJSON: a boolean state deciding whether to use the custom protocol or JSON protocol
#         Returns:
#                 a string containing the serialized request ready to be sent over the wire
#         """
#         if isJSON:
#             operation_request = {
#                 "version": version,
#                 "length": len(op_code) + len(arguments),
#                 "opcode": op_code,
#                 "arguments": arguments
#             }
#             # Return as JSON string.
#             logger.info(f"Server response serialized using JSON protocol as {operation_request}")
#             return json.dumps(operation_request)
#         else:
#             operation_specific = f"{op_code}"
#             for arg in arguments:
#                 # If the argument is a dictionary or a list, then we must break it down.
#                 # This is only applicable to the sending of the list of users to the client,
#                 # which is denoted by the keyword "USERS".
#                 if isinstance(arg, list):
#                     for item in arg:
#                         operation_specific += f"§{item}"
#                 else:
#                     operation_specific += f"§{arg}"
#             response = f"{version}§{len(operation_specific)}§{operation_specific}∞"
#             logger.info(f"Server response serialized using custom protocol as {response}")
#             return response

#     @staticmethod
#     def parse_serialized_data(version, data, isJSON=False):
#         """
#         Handles the translation of serialized data from the client into data that can be
#         handled by the server. Outputs a dictionary containing a version, the length of the message,
#         the operation code, and the arguments for the operation.

#         Parameters:
#                 version: the server version
#                 data: a byte string
#                 isJSON: a boolean state deciding whether to use the custom protocol or JSON protocol
#         Returns:
#                 a dictionary with keys for the version, length, operation code, and arguments provided
#                 by the client.
#         """
#         try:
#             logger.info(f"Server parsing client response. Version is {version}. Protocol isJSON: {isJSON}. Data being parsed is the following: {data}")
#             # Decode our data from a byte string into a normal string.
#             decoded_data = data.outb.decode("utf-8")
#             message = {}
#             if isJSON:
#                 # Create the JSON object and the appropriate dictionary from it.
#                 json_obj = json.loads(decoded_data)
#                 message["version"] = json_obj["version"]
#                 message["length"] = json_obj["length"]
#                 message["opcode"] = json_obj["opcode"]
#                 message["arguments"] = json_obj["arguments"]
#             else:
#                 # Using our custom protocol outlined in our documentation,
#                 # parse the data sent by the server by splitting at the delimiter.
#                 delimiter = '§'
#                 split_data = decoded_data.split(delimiter)
#                 message["version"] = split_data[0]
#                 message["length"] = split_data[1]
#                 message["opcode"] = split_data[2]
#                 message["arguments"] = split_data[3:]
#             return message
#         except Exception as e:
#             # Handle parsing errors.
#             logger.error(f"Server could not parse client response for data {data}. Failed with error {e}.")
#             return ValueError