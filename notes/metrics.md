**TTFT**  
time to first token = T(arrival) - t(request)

**total latency**  
time from request sent to outpute received

**output throughput / tokens per second**  
output tokens generated per second, can be per request or aggregate across all concurrent requests (we will only measure the formoer of course)

**input tokens**  
tokens sent to the model from prompt, instructions, conversation history, skills, etc

**output tokens**  
tokens genreated and returned including not just the final answer but reasoning tokens as well.

**input $/1M tokens**  
price charged per million input tokens

**output $/1M tokens**  
price chargerd per million output tokens, always higher than input

**request cost**  
total dollar cost of a single inference call

**HTTP/API error**  
rate limits, auth failures, overloads, server errors, etc. the numerator in success rate equation (with total requests as denominator)

**provider/model metadata**  
descriptive attributes belonging to a model endpoint including name/id, pricing, rate limits, region, version, context window, provider, etc.
