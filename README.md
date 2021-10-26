# Extract raster stats using polygons
Script to get raster stats using polygons

## Steps to execute:
1. Open terminal
2. Clone Repo
3. Go into /extract
4. Create a virtualenv (python 3.9.5) and activate   
5. Install the requirements packages (requirements.txt)
6. Create folder /outputs, /precipitacao, /temperatura, /uso_solo inside of /extract
7. Input rasters dataset inside of /precipitacao, /temperatura, /uso_solo

**Note: Datasets of precipitacao and temperatura (src 4326), inputs and uso_solo (src 31981)
## Codes
```
git clone https://github.com/newmarwegner/stats_automate.git
cd /extract
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt