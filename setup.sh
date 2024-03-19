#!/bin/bash

# Create and activate virtual environment
python -m venv venv
source ./venv/bin/activate

# Install dependencies
pip install -r requirements.txt

touch youtube-links.txt

echo ""
echo "Setup is complete. Please input the YouTube links you wish to add to the backlog, one link per line, into the file named youtube-links.txt"
echo "then run"
echo "python main.py --load"
echo ""
echo "for more information on other operations such as download, run"
echo "python main.py -h"

