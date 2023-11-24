# dfw_metroplex_vision_gpt
---------------
Wanted to play around with the new Vision feature that came out of the OpenAI developer day. 

![Terminator HUD](https://raw.githubusercontent.com/antoinesylvia/dfw_metroplex_vision_gpt/b45c39d55f501511b923a0e3763220e30466665e/zzDemo/Terminator_HUD.gif)

Instructions:
---------------
1. Fill out config.txt with your relevant data such as your OpenAI API key and custom prompt. This data will be tied to the constant values in the code. 

![Config Image](https://raw.githubusercontent.com/antoinesylvia/dfw_metroplex_vision_gpt/76360b295733e5bde2b7166cd6d8a6e9ad23b3d9/zzDemo/config.png)

2. Install the necessary requirements: pip install -r requirements.txt
3. If you have a screenshot application, point it at a subfolder in this directory once you clone this (BASE DIR > SCREENSHOTS > auto_scan). Only the latest file in directory dropped in will be scanned and output shown in the CLI.
4. If you want to manually move in images, drop them one at a time here: BASE DIR > SCREENSHOTS > manual_scan
5. Run app with --> python visiongpt.py

Other Notables:
---------------
- All processed items will have individual JSON logs capturing the filename, model, created timestamp for when item was logged, and content (output response from API):
![JSON Image](https://raw.githubusercontent.com/antoinesylvia/dfw_metroplex_vision_gpt/main/zzDemo/json.png)
- All processed items will have the same attributes captured in the JSON appended to a CSV, for each item processed a new row will be made:
  
![CSV Image](https://raw.githubusercontent.com/antoinesylvia/dfw_metroplex_vision_gpt/838ec956a0222b89c54a2e0ac66cf5b079261a88/zzDemo/csv.png)
- I've included some samples in the respective folders.

Demo
---------------
1. I screenshot an image of a Atari 2600, I have my system configured to save screenshots to the auto_scan directory. 

![Atari Image](https://raw.githubusercontent.com/antoinesylvia/dfw_metroplex_vision_gpt/2a00358b90a1994fe80f5460c7c4c822444f66f1/zzDemo/Atari.png)

2. Once it lands in the directory(auto_scan), it's presence is picked up and the data is sent to the API along with a customizable prompt, 'what's in this image?'.

![CLI Image](https://raw.githubusercontent.com/antoinesylvia/dfw_metroplex_vision_gpt/2a00358b90a1994fe80f5460c7c4c822444f66f1/zzDemo/CLI.png)

3. Response output is provided in the CLI, this is also saved to a JSON file per image processed and data output is appended to a CSV that captures all images processed.

4. App now waits to process the next image saved to auto_scan or manual_scan folders. 
