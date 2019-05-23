import argparse
import os
import sys
import datetime

from qiskit import IBMQ, BasicAer

IBMQ_SIMULATOR = 'ibmq_qasm_simulator'
LOCAL_SIMULATOR = 'qasm_simulator'
SIMULATORS = [IBMQ_SIMULATOR, LOCAL_SIMULATOR]
MAX_JOBS_PER_ONE = 70
BACKENDS = BasicAer.backends() # In set_parameters() BACKENDS will be supplemented IBMQ.backends()


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


class DefaultArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_argument('-t', '--token', default=None, help='Specific token')
        self.add_argument('-b', '--backend', type=str, default=LOCAL_SIMULATOR,
                          help='Name of backend (default: %(default)s)')
        self.add_argument('-s', '--shots', type=int, default=8192,
                          help='Number of shots in experiment (default: %(default)s)')
        self.add_argument('--show-backends', action='store_true',
                          help='Show available backends(some backends might be on maintenance)')
        self.add_argument('-f', '--file', action='store_true',
                          help='Redirect output to file')


def set_parameters(description='Lloyd algorithm', parser_class=None, additional_argument_list=None):
    """
    :param additional_argument_list: list of (args, kwargs)
    """
    if parser_class is None:
        parser = DefaultArgumentParser(description=description)
    else:
        parser = parser_class(description=description)

    if additional_argument_list is not None:
        for additional_argument in additional_argument_list:
            parser.add_argument(*additional_argument[0], **additional_argument[1])

    args = parser.parse_args()

    try:
        from Qconfig import APItoken, config
        if args.token is not None:
            token = args.token
        else:
            token = APItoken

        IBMQ.enable_account(token, **config)
    except ImportError:
        pass

    global BACKENDS
    BACKENDS += IBMQ.backends()
    if args.show_backends:
        for backend in BACKENDS:
            print(backend.name())
        sys.exit()

    if args.file:
        exec_file = os.path.basename(sys.argv[0])[:-3]
        output_dir = 'outputs'
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        filename = f"{output_dir}/output_{exec_file}_" \
            f"{args.backend}_{description.lower().replace(' ', '-')}_" \
            f"{datetime.datetime.today().strftime('%Y_%m_%d')}"
        sys.stdout = open(filename, 'a')
        sys.stderr = open(filename, 'a')

    return {
        'backend_name': args.backend,
        'shots': args.shots,
        'args': args  # args can have additional field that isn't covered recently
    }
