# dfw_metroplex_vision_gpt
---------------
Wanted to play around with the new Vision feature that came out of the OpenAI developer day. 

Instructions:
---------------
1. Fill out config.txt with your relevant data such as your OpenAI API key and custom prompt. This data will be tied to the constant values in the code. 
2. Install the necessary requirements: pip install -r requirements.txt
3a. If you have a screenshot application, point it at a subfolder in this directory once you clone this (BASE DIR > SCREENSHOTS > auto_scan). Only the latest file in directory dropped in will be scanned and output shown in the CLI.
3b. If you want to manually move in images, drop them one at a time here: BASE DIR > SCREENSHOTS > manual_scan
4. Run app with --> python visiongpt.py

Other Notables:
---------------
- All processed items will have individual JSON logs capturing the filename, model, created timestamp for when item was logged, and content (output response from API).
- All processed items will have the same attributes captured in the JSON appended to a CSV, for each item processed a new row will be made.
- I've included some samples in the respective folders. 
