import json

class ServerRequest:
    # Initialize a message from serialized data.
    # def __init__(self, data):
    #     self.data = data

    @staticmethod
    def serialize_to_str(version, op_code, arguments, isJSON=False):
        """TODO: add documentation"""
        if isJSON:
            operation_information = {
                "version": version,
                "length": len(op_code) + len(arguments),
                "opcode": op_code,
                "arguments": arguments
            }
            # Return as JSON string.
            print(operation_information)
            return json.dumps(operation_information)
        else:
            operation_specific = f"{op_code}"
            for arg in arguments:
                # If the argument is a dictionary or a list, then we must break it down.
                # This is only applicable to the sending of the list of users to the client,
                # which is denoted by the keyword "USERS".
                # if isinstance(arg, list):
                #     for item in arg:
                #         operation_specific += f"§{item}"
                # else:
                    operation_specific += f"§{arg}"
            return f"{version}§{len(operation_specific)}§{operation_specific}"

    @staticmethod
    def parse_serialized_data(data, isJSON=False):
        # Currently in byte strings & not decoded.
        try:
            message = {}
            # Decode our data from a byte string into a normal string.
            print(f"parsing!!! {data} {type(data)}")
            # Ensure we decode our byte string.
            if not isinstance(data, str):
                data = data.decode("utf-8")
            # decoded_data = data.outb.decode("utf-8")
            print("decoded data!", data)
            if isJSON:
                print("decoding JSON")
                json_obj = json.loads(data)
                print("json decoded and loaded as json", json_obj)
                message["version"] = json_obj["version"]
                message["length"] = json_obj["length"]
                message["opcode"] = json_obj["opcode"]
                # Handle arguments that contain lists.
                # This only applies to the initial list of users that is sent over to the user.
                if json_obj["opcode"] == "LOGIN_SUCCESS":
                    message["arguments"] = json_obj["arguments"][0:2]
                    message["arguments"] += json_obj["arguments"][2][0:]
                    print('done')
                else:
                    message["arguments"] = json_obj["arguments"]
            else:
                print("decoding custom", )
                delimiter = '§'
                split_data = data.split(delimiter)
                print("split data", split_data)
                message["version"] = split_data[0]
                message["length"] = split_data[1]
                message["opcode"] = split_data[2]
                message["arguments"] = split_data[3:]
                print("arguments custom:", split_data[3:])
            return message
        except Exception as e:
            # Let's not given an error right away!
            print(f"This value could not be parsed! Failed with error {e}")
            return ValueError
        
    @staticmethod
    def decode_multiple_json(data):
        """Handle multiple json objects sent via the wire."""
        decoder = json.JSONDecoder()
        pos = 0
        messages = []

        while pos < len(data):
            # Decode next JSON object
            obj, index = decoder.raw_decode(data, pos)  
            messages.append(json.dumps(obj))
            pos = index  # Move position to the next JSON object
        return messages

    # @staticmethod
    # def serialize(version, op_code, arguments):
    #     """TODO: add documentation"""
    #     operation_specific = f"{op_code}"
    #     for arg in arguments:
    #         operation_specific += f"§{arg}"
    #     return f"{version}§{len(operation_specific)}§{operation_specific}"

    # # TODO: see if this works!
    # @staticmethod
    # def serializeJSON(version, op_code, arguments):
    #     # Serialization function using JSON.
    #     operation_information = {
    #         "version": version,
    #         "opcode": op_code,
    #         "arguments": arguments
    #     }
    #     # Return as JSON string.
    #     return json.dumps(operation_information)
