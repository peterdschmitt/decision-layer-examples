"""Send this example's sample input to the API and print the queue.

    python3 run.py --dry-run   # print the request, send nothing
    python3 run.py             # needs TYPESAFE_API_KEY in your environment
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))

from common.jev_client import main  # noqa: E402
from request import build_body  # noqa: E402
from route import route  # noqa: E402

if __name__ == "__main__":
    main(build_body, route, os.path.join(HERE, "sample_input.txt"))
