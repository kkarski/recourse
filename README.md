# recourse

Philosophy:
- The product requirements are the prompt

Observed code gen behavior:
- The more detailed the prompt, the better the results
- LLMs do better when provided test cases up front
- LLMs make too convenient assumptions when not provided with all the constraints
- Code gen does much better with a planning phase
- LLMs make very bad assumptions about how something is supposed to work
- LLMs are bad at spotting their own mistakes or omissions, need to leverage multitude of models for feedback

Problems with the SDLC:
- Incomplete requirements which have to be clarified along the way during development
- Existing features or functionality which must interact or co-exist with new feature
- Undefined initial states or backwards compatibility issues which must be considered. I.e. need for a data transformation or migration of existing state to work with new feature
- Only high level definition of key algorithms
- Lacking input and data validation conditions
- Incomplete error conditions or handling of exceptions in user flow
- Late discovery of missing functionality assumed to exist or an incomplete implementation
- Use LLMs to probe for usage scenarios and see if requirements exist for these sets of conditions

Better Code Gen Planning:
- Start discovering what code will need to change earlier
- Continuously update the implementation plan as requirements change or the underlying code base changes

Test Planning:
- Test cases written for how the code works rather than how the feature is supposed to work
- No verification of the test cases by product manager, only developer or QA per how they interpreted the requirements
- Missing detailed assertions in test cases proving the code is correct
- Missing end to end test cases proving features work when integrated with one another
- Insufficient test coverage

Additional Reading:  
https://ordep.dev/posts/writing-code-was-never-the-bottleneck