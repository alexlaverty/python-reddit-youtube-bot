#!/bin/bash

# Needed to keep poetry happy
pip install --user --upgrade pip setuptools wheel

# Needed to keep imagemagick happy
sudo sed -i '/<policy domain="path" rights="none" pattern="@\*"/d' /etc/ImageMagick-6/policy.xml

# Install runtime dependencies
pip install --user -r requirements.txt

# Additional dependencies needed to develop the utility & maintain code
# quality.
pip install --user -r requirements-dev.txt

# Initialise playwright
playwright install-deps
playwright install firefox
