# Tool-Calls
Make LLM search web and write and run python codes

this python code implement tool calls to make LLMs:
* search web and scrape relevant information
* fetch introduction from Wikipedia
* write and execute python codes and return results
:warning: the python code that the LLM will run may affect your PC, it is not running in a closed environment. some modules like OS will return error for safety, and a 5 seconds timeout for infinite loops.