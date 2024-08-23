
# create-ivao-vmr
Create a vPilot VMR file from the IVAO MTL library.

## Usage
Requires [Python](https://www.python.org/).  
Make sure to [download](https://mtl.ivao.aero/installer), install, and index the IVAO MTL.  
Drop the `create_vmr.py` file in your `Packages/Community/IVAO_MTL` folder.  
Open a Windows Terminal and enter `python create_vmr.py`.  
Wait for the script to finish. It should only take a few seconds (less than two for me).  
The VMR file will be created as "ivaomtl.vmr" in the folder as the python script.  

### Options
`-d | --directory [path]`  
Specify a path where the script will look for the model files. The path specified should contain the `SimObjects/Airplanes` folder. Make sure to put the path in quotation marks.  
```bash
-o | --output [file]
# python create_vmr.py -o "C:\Users\mydir\Documents\vPilot Files/out.vmr"
# python create_vmr.py -o ivaomtl.vmr
```
Specify the output of the script. If you specify a directory, make sure to wrap it in quotation marks.  

`-v | -verbose`  
More verbose logging of what's going on. Get a real sense of speed. Makes you feel like your computer is super duper fast.

## I got an error when I ran the script!
### The error mentions an issue with "[VERSION]"
This error occurs due to a bug with the IVAO MTL installation. The `create_vmr.py` script will let you know what files had the bug. The rest of the VMR will still be created, but that aircraft type will be excluded.  
The error should look like this:  
![](https://i.imgur.com/PCx8Q4G.png)    
In this case, navigate to the file listed in the error. Open the file and scroll all the way to the bottom. Near the bottom, we see this:   
![](https://i.imgur.com/0EVfEq5.png)  
We can fix the problem by added the missing `[` to the beginning of where it says `VERSION]`. It should look like this:  
![](https://i.imgur.com/PZIfCds.png)  
Great! Now rerun the script with `python create_vmr.py`. This time there should be no errors.  

### I got a different error!
No problem! Head to the top of this page, click "Issues" and open a new issue.