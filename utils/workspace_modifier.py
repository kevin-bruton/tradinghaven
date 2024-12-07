

base_dir = 'C:/_Workspaces/'
workspace = 'MDD_pt1_Tradestation_November24'

print('\nIn what directory is the workspace you want to modify?')
base_dir = input('[Default = ' + base_dir + ']: ') or base_dir
print('\nWhat workspace do you want to modify?')
workspace = input('[Default = ' + workspace + ']: ') or workspace
print('\nWhat do you want to set the TitanExportMode to?')
export_mode = input('0 = Disable export, 1 = Enable export: ')
new_workspace = workspace + '_Export' if export_mode == '1' else workspace + '_NoExport'

content = ''
with open(base_dir + workspace + '.wsp') as f:
  line = f.readline()
  content += line
  while line:
    if 'Input_TitanExportMode]' in line:
      for i in range(0, 5):
        line = f.readline()
        content += line
      line = f.readline()
      content += "  Value = '" + export_mode + "'\n"
    line = f.readline()
    content += line

workspace_path = base_dir + new_workspace + '.wsp'
with open(workspace_path, 'w') as f:
  f.write(content)

print('\nNew workspace saved to: ' + workspace_path)
