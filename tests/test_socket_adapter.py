import struct
from unittest.mock import Mock
from core.socket_adapter import recieve_signal

def test_recieve_signal()->None:
    # input_nums = (1.0, 2.0, 3.0, 4.0)
    input_nums = (1, 2, 3, 4)
    size = len(input_nums)
    binary_size = struct.pack('!I', size)
    binary_nums = struct.pack(f'!{size}q', *input_nums)
    mock_socket = Mock()
    mock_socket.recv.side_effect = [
        binary_size,
        binary_nums,
    ]
    nums = recieve_signal(mock_socket)
    assert input_nums == nums