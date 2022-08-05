import os
import glob
import json
from tabnanny import check

main_folder = '/home/aviralkumar/hdd/'
which_day = 'awbc_bcinit'
cmd_file = 'scp_cmd.sh'
output_dir = '/raid/asap7772/awbc_bcinit/'

# which_checkpoints=[80000, 100000, 120000, 140000, 160000, 180000, 240000]
which_checkpoints=[120000, 180000, 320000, 360000, 440000, 480000]

check_json=dict(
    #  target_dataset={'toykitchen6_knife_in_pot'},
)
check_train_json=dict(
   
)

sub_path=os.path.join(main_folder, which_day)

all_dirs = set()
for root, dirs, files in os.walk(sub_path, topdown=False):
   for name in files:
      f_name = os.path.join(root, name)
      if 'checkpoint' in f_name:
        all_dirs.add(f_name.split('checkpoint')[0])

output_file = open(f'{main_folder}/{cmd_file}', 'w')

i=0
for dir in all_dirs:
    conf = f'{dir}config.json'
    try:
        with open(conf) as f:
            data = json.load(f)
    except:
        continue
    
    things_to_print=dict()

    filter=False
    for x in check_json:
        if x in data and data[x] not in check_json[x]:
            filter=True
    for x in check_train_json:
        things_to_print[x] = data['train_kwargs'][x]
        if x in data['train_kwargs'] and data['train_kwargs'][x] not in check_train_json[x]:
            filter=True

    if not filter:
        print(i, dir)
        i += 1

        for x in things_to_print:
            print(x, things_to_print[x]) 

        print()
        
        output_file.write(f"echo 'Copying {dir}' \n")
        folder_to_make = f'{output_dir}/{dir.split(sub_path)[-1]}'
        mkdir_command = f"ssh ada 'mkdir -p {folder_to_make}' \n"
        output_file.write(mkdir_command)

        fi='config.json'
        scp_command = f'rsync -vae ssh {dir}/{fi} ada:{folder_to_make} \n'
        output_file.write(scp_command)

        for fi in os.listdir(dir):
            if 'checkpoint' in fi and fi != 'checkpointtmp':
                which = int(fi.split('checkpoint')[-1])
                if which in which_checkpoints or which % 100000 == 0:
                    print(f'added scp command for {which}')

                    scp_command = f'rsync -vae ssh {dir}/{fi} ada:{folder_to_make} \n'
                    output_file.write(scp_command)
                    # print(scp_command)      
        
        output_file.write('\n')
        
        print()
        print(data['train_kwargs'])
        print()
    # print(x.split('/')[-2])
    # print()

print(f'total={i}')
print(output_file)
output_file.close()
