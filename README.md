# MKS-TOOL
MKS TOOL is a tool that allows you to quickly modify the display UI and configuration files using a graphical interface (currently only supports MKS Robin series boards).

## Usage


1. Two ways:


 - Download the released installation file from [https://github.com/makerbase-mks/MKS-TOOL/releases](https://github.com/makerbase-mks/MKS-TOOL/releases) and then install it.(only supports Windows OS) 
 - Directly run the "mainFrame.py" with Python. This requires you to install Python2.7.x, and you must have some experience using Python, because you need to install some libraries halfway. 

2. Open the tool, choose the type of board+lcd and languagy and continue.![](https://github.com/makerbase-mks/MKS-TOOL/blob/master/Images/choose.png)
3. Now you can modify the images of each page or modify the configuration file.![](https://github.com/makerbase-mks/MKS-TOOL/blob/master/Images/step1.png)

### Modify images
 - It is recommended to load the factory image template first and modify it on this basis. Of cause, you can also import your current image folders("mks_pic" folder) by clicking "Import" to modify.
 - Select the page you want to modify in the left column, select the image you want to modify on the right, and then replace the pictures in the three "+" places below. Note that the pixels of the replacement image should meet the requirements. At present, the pixel requirement for the 2.4/2.8/3.2-inch screen is 78*104; for the 3.5-inch screen, the pixel is 117*140. Also, if the picture at the same position has serval state, you can modify different pictures for each state (so below are 3 "+", there are at most 3 states).![](https://github.com/makerbase-mks/MKS-TOOL/blob/master/Images/step2.png)
 - After modify finish, just click "Export", it will generate the mks_pic folder which can be copied to the sdcard for uploading.
### Modify configuration file
 - Just modify the parametres on the tools, and then click "Export configuration file", it will generate the configuration file automatically. You can copy the file to the sdcard for uploading.![](https://github.com/makerbase-mks/MKS-TOOL/blob/master/Images/step3.png)
 - You can also import your current configuration file by clicking the "Import configuration file" to modify.


