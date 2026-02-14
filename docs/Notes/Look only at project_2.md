Look only at project_2
Based on the current architecture, proposed the followings:
1. add a mqtt client that subscribe to the topic which defined in os.env called "topic_for_iot" to a mqtt server.  which collects the iot devices status as a json in memory as a global variable that can be accessed by other modules.  
2. add a new MCP tool named `get_smart_home_status` that can access the json data which has  iot devices status described above.  prompt it to gemini, collect the answer from gemini and eventually return to end user.


Deliverables:
- Tool interface/schema
- Where it should be registered
- What files should be modified

Do not write code yet.
Do not propose changes yet.