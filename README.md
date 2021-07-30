# MKS-TOOL
MKS developed the MKS TOOL series to make it more convenient for users to use 3d printer motherboards. We have developed the installed version and the online version of the webpage. The webpage online version will be the main development later. Now MKS TOOL has been implemented:
- Online configuration of touch screen display pictures and styles (for MKS Robin series boards and MKS TFT series boards)
- Modify configuration parameters (for Marlin and MKS firmware)
- Compile Marlin V2.X firmware online
More features will be developed....

Now there are two versions of MKS TOOL, one is for installing in windows, the other is web version. 

## For Webpage Online Version Usage
Webpage version is independent with OS, so no matter you use Windows, Ubuntu, MacOS, you can use the web version throught the browser.
There are two part of tool now on the Web version:
1. Online configuration of touch screen display pictures and styles (for MKS Robin series boards and MKS TFT series boards)  
  1.1 Visit the address with a browser: https://baizhongyun.cn/home/mkstoolview  
  1.2 According to the wizard, select the board you use, the firmware you use...  
  1.3 From the ui interface, you can modify the configuration files, modify the display icons, export the files to flash...  
2. Compile Marlin V2.X firmware online  
 It solves the difficulty of installing VScode and PlatformIO when some users use Marlin 2.X firmware.  
  2.1 Visit the address with a browser: https://baizhongyun.cn/home/mkscompileview  
  2.2 Import the Marlin souce package (.zip file)  
  2.3 Choose the mainboard you use. Make sure the board type in the configuration file before importing is consistent with the current selection, otherwise, the compilation will not succeed.  
  2.4 Leave the mail box address which will receive the comiple result. The compiled information and files will be sent to the filled email address.   
  2.5 Click Online Compile. Large files will take some time to upload. Please pay attention to your email after the upload is successful. Compilation takes about 3 to 6 minutes. 


## For Installed Version Usage(No longer maintained)

1. Two ways:
 - Download the released installation file from [https://github.com/makerbase-mks/MKS-TOOL/releases](https://github.com/makerbase-mks/MKS-TOOL/releases) and then install it.(only supports Windows OS) 
 - Directly run the "mainFrame.py" with Python. This requires you to install Python2.7.x, and you must have some experience using Python, because you need to install some libraries halfway. 
2. Open the tool, choose the type of board+lcd and language and continue.

![](https://github.com/makerbase-mks/MKS-TOOL/blob/master/Images/choose.png)

3. Now you can modify the images of each page or modify the configuration file.![](https://github.com/makerbase-mks/MKS-TOOL/blob/master/Images/step1.png)

### Modify images
 - It is recommended to load the factory image template first and modify it on this basis. Of cause, you can also import your current image folders("mks_pic" folder) by clicking "Import" to modify.
 - Select the page you want to modify in the left column, select the image you want to modify on the right, and then replace the pictures in the three "+" places below. Note that the pixels of the replacement image should meet the requirements. At present, the pixel requirement for the 2.4/2.8/3.2-inch screen is 78x104; for the 3.5-inch screen, the pixel is 117x140. Also, if the picture at the same position has serval state, you can modify different pictures for each state (so below are 3 "+", there are at most 3 states).
 
 ![](https://github.com/makerbase-mks/MKS-TOOL/blob/master/Images/step2.png)
 - After modify finish, just click "Export", it will generate the mks_pic folder which can be copied to the sdcard for uploading.
### Modify configuration file
 - Just modify the parametres on the tools, and then click "Export configuration file", it will generate the configuration file automatically. You can copy the file to the sdcard for uploading.
 
 ![](https://github.com/makerbase-mks/MKS-TOOL/blob/master/Images/step3.png)
 - You can also import your current configuration file by clicking the "Import configuration file" to modify.


