# Tool-Calls
Make LLM search web, write and run python codes

this python code implement tool calls to make LLMs:
* search web and scrape relevant information
* fetch introduction from Wikipedia
* write and execute python codes and return results
⚠️ the python code that the LLM will run may affect your PC, it is not running in a closed environment. some modules like OS will return error for safety, and a 5 seconds timeout for infinite loops.

Make sure the server in lm studio in ON

Download the repo
```bash
git clone https://github.com/yossifibrahem/Tools.git
```
Run the code
```bash
python Tools\LM_tools.py
```
