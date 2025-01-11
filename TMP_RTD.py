'''===============================================
Traffic Mods Patcher for Real Traffic Density ETS2
================================================'''

import sys
import os
import re
import glob
import msvcrt
import subprocess
import fileinput
import shutil
from time import sleep
from pathlib import Path


#=============================
# Direct menu selection input.
#=============================
def direct_menu_input(accepted_characters):
    
    char_index = 0

    while True:
        valid = 0
        input_char = msvcrt.getwch()
   
        if input_char in accepted_characters:
            char_index = accepted_characters.index(input_char)
            valid += 1
        else:
            pass

        if valid == 1:            
            # If input characters is a digit return as int.
            if accepted_characters[char_index].isdigit():
                return int(accepted_characters[char_index]) 
            
            # If input is a unicode character, it will be returned as is.
            # Example: "\u001b" will be returned as "\u001b".
            else:
                return input_char


#===========================
# Search for available mods.
#===========================
def search_mods():

    files_found = {}
    id_val = int(0)
    dir_list = os.listdir()

    for file in dir_list:
        if re.findall('(?i)classic_cars_traffic_pack_by_TrafficManiac_v\d[.\d]*._base.scs$', file):
            id_val += 1
            files_found.update({id_val: [file,
                                         Path(file).stem + '/def/vehicle/traffic_storage_car.classic_tm.sii',
                                         Path(file).stem + '/def/vehicle/traffic_storage_classic.classic_tm.sii',
                                         Path(file).stem + '/def/vehicle/ai/tm',
                                         'No']})
            
        if re.findall('(?i)motorcycle_traffic_pack_by_Jazzycat_v\d[.\d]*.scs$', file):
            id_val += 1
            files_found.update({id_val: [file,
                                         Path(file).stem + '/def/vehicle/traffic_storage_car.jazzycat_moto.sii',
                                         Path(file).stem + '/def/vehicle/traffic_storage_moto.jazzycat_moto.sii',
                                         Path(file).stem + '/def/vehicle/ai/jazzycat',
                                         'No',
                                         '(Not recommended)']})
            
        if re.findall('(?i)painted_bdf_traffic_pack_by_Jazzycat_v\d[.\d]*.scs$', file):
            id_val += 1
            files_found.update({id_val: [file,
                                         Path(file).stem + '/def/vehicle/traffic_storage_truck.jazzycat_bdf.sii',
                                         Path(file).stem + '/def/vehicle/traffic_storage_truck_bdf.jazzycat_bdf.sii',
                                         Path(file).stem + '/def/vehicle/truck/',
                                         'No']})
            
        if re.findall('(?i)sport_cars_traffic_pack_by_TrafficManiac_v\d[.\d]*._base.scs$', file):
            id_val += 1
            files_found.update({id_val: [file,
                                         Path(file).stem + '/def/vehicle/traffic_storage_car.sport_tm.sii',
                                         Path(file).stem + '/def/vehicle/traffic_storage_sport.tm.sii',
                                         Path(file).stem + '/def/vehicle/ai/tm',
                                         'No']})            
        
    return files_found, id_val


#================
# Selection menu.
#================
def menu(files_found, id_val):

    options = {}
    for n in range(1, len(files_found) + 1):
        options.update({n: f'files_found[{n}][4]'})

    available_selection = [str(n) for n in range(1, len(files_found) + 1)] + ['\u001b'] + ['\u000d']
        
    while True:
        os.system("cls")
        print('--------------------------------------------------', 
              'Traffic Mods Patcher for Real Traffic Density ETS2',
              '--------------------------------------------------',
              'MODS founds:\n',
              sep=os.linesep)        

        for key, value in files_found.items():
            try:
                if files_found[key][5]: # If it has 5 values then it's motorcycle traffic pack.
                    if files_found[key][4] == 'Traffic behavior + parked vehicles':
                        print(f'[{key}] {value[0] : <65} {value[4]} (Not recommended)')
                    else:
                        print(f'[{key}] {value[0] : <65} {value[4]}')
            except IndexError:                
                print(f'[{key}] {value[0] : <65} {value[4]}')            
            
        print('\n[Numbers] select mod options, [Enter] apply patches, [Esc] exit.')
        
        get_opt = (lambda opt: 'Only traffic behavior' if opt == 'No'
                   else 'Traffic behavior + parked vehicles' if opt == 'Only traffic behavior'
                   else 'No')
        selection = direct_menu_input(available_selection)

        # Number pressed.
        if str(selection) in available_selection[0: -1]:
            options[selection] = get_opt(options[selection])
            files_found[selection][4] = get_opt(options[selection])
            
        # Return pressed.
        elif selection == '\u000d':
            if all(value[4] == 'No' for value in files_found.values()):
                continue
            else:
                return            
        
        # ESC pressed.
        elif selection == '\u001b':
            sys.exit()


#============
# Patch mods.
#============
def patch(files_found):

    for i in files_found:
        if files_found[i][4] != 'No':
            
            # Extract mod.
            print(f'\nExtracting mod {files_found[i][0]}...')
            subprocess.run(['scs_packer.exe', 'extract', files_found[i][0], '-root', Path(files_found[i][0]).stem])

            # Rename original file to .bak.
            print('Renaming original mod file to .bak...')
            try:
                os.rename(files_found[i][0], files_found[i][0] + '.bak')
            except FileExistsError:
                print('File already exist!')
                pass

            # Rename traffic file for RTD.
            print('Renaming traffic file for RTD...')
            if os.path.exists(files_found[i][2]):
                print('File already exist!')
            else:
                os.rename(files_found[i][1], files_found[i][2])
 
            # Add traffic to parkings.
            if files_found[i][4] == 'Traffic behavior + parked vehicles':
                print('Patch files for parked vehicles...')
                for file in glob.glob(files_found[i][3] + '/*.sui'):
                    with fileinput.FileInput(file, inplace=True) as vehicle_file:
                        for line in vehicle_file:
                            print(line.replace('allow_parked: false', 'allow_parked: true'), end='')
        
            # Repack_mods.
            print('Repacking mod...')
            subprocess.run(['scs_packer.exe', 'create', files_found[i][0], '-root', Path(files_found[i][0]).stem])
            
            # Delete work folders.        
            print('Removing working folder...')
            shutil.rmtree(Path(files_found[i][0]).stem)
            print('Done!')
    return


#======
# Main.
#======
def main():

    # Set console window size and buffer using Windows Powershell.
    os.system(f'powershell -command "[console]::WindowWidth=125; [console]::WindowHeight=30; [console]::BufferHeight=100"')
    
    if not os.path.exists('scs_packer.exe'):
        print('This program needs scs_packer.exe\nClosing...')
        sleep(4)
        sys.exit()    
    else:
        files_found, id_val = search_mods()
        if not files_found :
            print('No mod files found.\nClosing...')
            sleep(4)
            sys.exit()
        else:
            menu(files_found, id_val)
            patch(files_found)
            input('\nAll files patched! Press Enter to exit.')


if __name__ == "__main__":
    main()
