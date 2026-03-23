# Forestry data API

## Cite ...
...

### Known Issues
...

### Installation Process
...

## Installation

### From GitHub:

1. Clone the repository
Begin by cloning the repository to your local machine using the following command: 
    >git clone ...
   > 
2. Switch to the TiMBA directory  
Navigate into the TiMBA project folder on your local machine.
   >cd ...
   >
3. Create a virtual environment  
It is recommended to set up a virtual environment for TiMBA to manage dependencies. The package is tested for 
   Python versions up to 3.11. With a newer Python version, we can not guarantee the full functionality of the package.
   Select the correct Python interpreter.   
   Show installed versions: 
   >py -0  
   >
   - If you have installed multiple versions of Python, activate the correct version using the py-Launcher.
   >py -3.11 -m venv venv 
   > 
   - If you are using only a single version of Python on your computer:
   >python -m venv venv
   >
4. Activate the virtual environment  
Enable the virtual environment to isolate TiMBA dependencies. 
   >venv\Scripts\activate
   >
5. Install TiMBA in the editable mode  
   >pip install -e .

    If the following error occurs: "ERROR: File "setup.py" or "setup.cfg" not found."
    you might need to update the pip version you use with: 
    >python.exe -m pip install --upgrade pip
   

### Double check installation and test suite
Double check if installation was successful by running following command from terminal:  
   >... --help

## Use ...
...

## ... extended model description 
...

## Roadmap and project status
...

## Contributing to the project
We welcome contributions, additions and suggestion to further develop or improve the code and the model. To check, discuss and include them into this project, we would like you to share your ideas with us so that we can agree on the requirements needed for accepting your contribution. 
You can contact us directly via GitHub by creating issues, or by writing an Email to:

[wf-timba@thuenen.de](mailto:wf-timba@thuenen.de)


## Authors
- [Christian Morland](https://www.thuenen.de/de/fachinstitute/waldwirtschaft/personal/wissenschaftliches-personal/ehemalige-liste/christian-morland-msc) [(ORCID 0000-0001-6600-570X)](https://orcid.org/0000-0001-6600-570X)

## Contribution statement
...

## License and copyright note

Licensed under the GNU AGPL, Version 3.0. 

Copyright ©, 2024, Thuenen Institute

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU Affero General Public License as
 published by the Free Software Foundation, either version 3 of the
 License, or (at your option) any later version.

 This program is distributed in the hope that it will be useful, but
 WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 Affero General Public License for more details.

 You should have received a copy of the GNU Affero General Public
 License along with this program.  If not, see
 <https://www.gnu.org/licenses/agpl-3.0.txt>.
