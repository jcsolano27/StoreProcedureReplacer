import os


class ReplacerStoreProcedure:

    d = {}
    mapping_list = {}
    folders = ['etl', 'esd', 'gui']
    file_data = ''

    def replace_w_formats(self, old_table_name, new_table_name):
        old_table_bracket_parts = old_table_name.split('.')
        new_table_bracket_parts = new_table_name.split('.')

        old_table_bracket = f"[{old_table_bracket_parts[0]}].[{old_table_bracket_parts[1]}]"
        new_table_bracket = f"[{new_table_bracket_parts[0]}].[{new_table_bracket_parts[1]}]"

        count = self.file_data.count(old_table_name)+self.file_data.count(old_table_name.upper())+self.file_data.count(old_table_bracket)

        if count > 0:
            self.file_data = self.file_data.replace(old_table_bracket, new_table_bracket)
            self.file_data = self.file_data.replace(old_table_name, new_table_name)
            self.file_data = self.file_data.replace(old_table_name.upper(), new_table_name.upper())
            # self.file_data = self.file_data.replace(old_table_name[4:], new_table_name[4:])
            # self.file_data = self.file_data.replace(old_table_name[4:].upper(), new_table_name[4:].upper())

        return count

    def add_table_to_dictionary(self, old_table_name, new_table_name, filename, count):
        if old_table_name not in self.d.keys():
            self.d[old_table_name] = {}
            self.d[old_table_name]['new'] = new_table_name
            self.d[old_table_name]['packages'] = []
            self.d[old_table_name]['count'] = count

        if filename not in self.d[old_table_name]['packages']:
            self.d[old_table_name]['packages'].append(filename)

    def add_to_mapping_list(self, folder, old_filename):
        if old_filename not in self.mapping_list.keys():
            self.mapping_list[old_filename] = {}
            self.mapping_list[old_filename]['new_filename'] = self.rename_file(folder, old_filename)
            self.mapping_list[old_filename]['folder'] = folder

    def save_results(self):
        with open("results.csv", 'w') as results:
            results.write("Old Table Name,New Table Name,Modified Packages,Count\n")
            for k in self.d.keys():
                results.write(f"{k},{self.d[k]['new']},{'|'.join(self.d[k]['packages'])},{str(self.d[k]['count'])}\n")
        results.close()

    def save_new_file(self, filename):
        folder = self.mapping_list[filename]['folder']
        new_file_name = self.mapping_list[filename]['new_filename']
        if not os.path.exists(f'Output\\{folder}'):
            os.mkdir(f'Output\\{folder}')

        with open(f'Output\\{folder}\\{new_file_name}', 'w') as output:
            output.write(self.file_data)
        output.close()

    def process_file(self, filename, replace_lines, path, folder):
        with open(f'{path}\\{filename}', 'r') as data:
            self.file_data = data.read()
            for line in replace_lines:
                parts = line.split(",")
                old_table_name = parts[0].strip()
                new_table_name = parts[1].strip()

                if filename == 'UspBeginBatchRun.sql' and old_table_name == 'etl.UspBeginBatchRun':
                    print(filename)

                count = self.replace_w_formats(old_table_name, new_table_name)
                if count > 0:
                    self.add_table_to_dictionary(old_table_name, new_table_name, filename, count)
                    formatted_folder = f'{folder[0].upper()}{folder[1:]}'
                    for i in reversed(range(2, 5)):
                        repeated = (formatted_folder*i)
                        self.file_data = self.file_data.replace(repeated, formatted_folder)

                self.save_new_file(filename)

    @staticmethod
    def rename_file(folder, file):
        if file[:3] == 'Usp':
            if file[3:6].upper() == folder.upper():
                file_name = file
            else:
                file_name = f"{file[:3]}{folder[:1].upper()}{folder[1:]}{file[3:]}"
        elif file[:3].upper() == folder.upper():
            file_name = file
        else:
            file_name = f"{folder[:1].upper()}{folder[1:]}{file}"
        return file_name

    def process_path(self, renaming_list, path):
        with open(renaming_list, 'r') as f:
            replace_lines = f.readlines()
            for folder in self.folders:
                folder_path = f"{path}\\{folder}\\Stored Procedures\\"
                for file in os.listdir(folder_path):
                    if file[-4:] == '.sql':
                        print(f"Currently processing file: {folder}\\{file}")
                        self.add_to_mapping_list(folder, file)
                        self.process_file(file, replace_lines, folder_path, folder)
        self.save_results()

    def format_input_list(self, path):
        with open("formatted_list.csv", 'w') as f:
            f.write("Old Store Procedure name, New Store Procedure name\n")
            for folder in self.folders:
                folder_path = f"{path}\\{folder}\\Stored Procedures\\"
                for file in os.listdir(folder_path):
                    file_name = self.rename_file(folder, file)
                    f.write(f"{folder}.{file[:-4]}, dbo.{file_name[:-4]}\n")
        f.close()


if __name__ == '__main__':
    files_path = "C:\\Users\\jcsolano\\OneDrive - Intel Corporation\\Documents\\Engagements\\SvD\\Git\\frameworks.business.ssas.cubes.mpsrecon"
    renaming_input = "formatted_list.csv"
    replacer = ReplacerStoreProcedure()
    #replacer.format_input_list(files_path)
    replacer.process_path(renaming_input, files_path)
















