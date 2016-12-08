
def forward_command(message):

def print_message(message):
    print(message)


available_commands = {
    'set_device': forward_command
    'success': print_message
}


def handle_command(message):
    if not 'command' in message:
        raise Exception("No command given")

    command_handler = available_commands.get(message['command'])
    if not command_handler:
        raise Exception("Unknown command {}".format(message['command']))

    return command_handler(message)
