# -*- coding: utf-8 -*-

# Standard imports
from json import (
    dump as json_dump,
    load as json_load)
from json.decoder import JSONDecodeError
from os import (
    listdir,
    makedirs,
    remove as os_remove,
    rename as os_rename,
    scandir,
    walk as os_walk)
from os.path import (
    exists as os_path_exists,
    isdir,
    isfile)
from pathlib import PurePath
from shutil import (
    copy2 as shutil_copy2,
    copytree,
    make_archive,
    rmtree)
from time import perf_counter as time_perf_counter

# 3rd party imports
from PIL import Image

# CatppuccinColors classes
from catppuccincolors import (
    CatppuccinAccentColors,
    CatppuccinFlavors,
    get_flavor_colors)


def main():
    templates_folder = PurePath('template')

    while True:
        template_version = input(
            '-----------------------------------------------------------------------\n'
            'Enter which template version to use. Use names of the template folders.\n')

        if not template_version:
            continue

        template_folder = PurePath(templates_folder, template_version)

        if isdir(template_folder) and any(scandir(template_folder)):
            output_folder = PurePath('output', template_version)
            break
        elif isdir(templates_folder) and any(scandir(templates_folder)):
            templates = listdir(templates_folder)
            if '1.9-1.10.2' in templates:
                templates.remove('1.9-1.10.2')
                templates.insert(0, '1.9-1.10.2')
            if '1.6.1-1.8.9' in templates:
                templates.remove('1.6.1-1.8.9')
                templates.insert(0, '1.6.1-1.8.9')
            templates = '\n'.join(templates)
            print(
                f'No template folder found for \'{template_version}\'!\n'
                f'Try to use one of these:\n{templates}')
        else:
            print('No templates folder found.')

    # Start to count the time it takes to run this script.
    starting_time = int(time_perf_counter())
    temporary_files_dir = PurePath('temp', template_version)

    # Get resource pack version from version file.
    if isfile(PurePath('version.txt')):
        with open(PurePath('version.txt'), 'r') as version_file:
            pack_version = version_file.readline()

    # Delete the temporary files folder if it exists.
    # This is here just in case something goes wrong.
    # Temporary files folder will always be deleted before new files are started to get created.
    if isdir(temporary_files_dir):
        rmtree(temporary_files_dir)

    # Create temporary files folder.
    if not isdir(temporary_files_dir):
        makedirs(temporary_files_dir)

    # Check if the template language file exists for Minecraft.
    mc_lang_folder = PurePath(template_folder, 'assets', 'minecraft', 'lang')
    if isdir(mc_lang_folder) and any(scandir(mc_lang_folder)):
        for file in listdir(mc_lang_folder):
            if 'template' in file:
                template_lang_file = PurePath(mc_lang_folder, file)
                break
        try:
            template_lang_file
        except UnboundLocalError:
            print(
                f'ERROR: No template language file found for Minecraft in template {template_version}.\n'
                f'You\'ll have to add one with the name \'template\'.')
            return
    else:
        print(f'ERROR: No template language folder found at path:\n{mc_lang_folder}')
        return
    
    # Check if language files exist for the latest version that the current template supports.
    mc_versions = template_version.split()[-1].strip()
    if '-' in mc_versions:
        lang_version = mc_versions.split('-', 1)[1]
    else:
        lang_version = mc_versions
    language_files_folder = PurePath('lang', 'output')
    if not template_lang_file.name.startswith('$'):
        folder_name = lang_version
        lang_folder = PurePath(language_files_folder, folder_name, 'minecraft')
    else:
        folder_name = template_lang_file.name.split('$', 1)[1].split('$', 1)[0]
        lang_folder = PurePath(language_files_folder, folder_name, 'minecraft')

    if (isdir(lang_folder) and any(scandir(lang_folder))):
        # Try to load template language file in assets/minecraft/lang.
        with open(template_lang_file, 'r') as template_file:
            if template_lang_file.suffix == '.json':
                try:
                    template = json_load(template_file)
                except JSONDecodeError as e:
                    print(
                        'ERROR: Unable to load the template language file of minecraft.\n'
                        'Reason: ', e)
                    return
                
            elif template_lang_file.suffix == '.lang':
                template_language_dict = {}
                for line in template_file:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        template_language_dict[key] = value
                template = template_language_dict
    else:
        print(
            f'Language files not found for version {lang_version}!\n'
            f'You can add language files by executing the '
            f'\'import_language_files.py\' script in the \'lang\' folder.')
        return

    # Start to generate different flavors and accent colors from the template.
    for flavor in CatppuccinFlavors.all():
        print(f'\nStarting to create flavor {flavor} from template {template_version}!\n')
        
        # Get correct color values depending on flavor.
        flavor_colors = get_flavor_colors(flavor)
        # Create color map for current flavor.
        color_map = {
            (17, 17, 27): flavor_colors.crust,
            (24, 24, 37): flavor_colors.mantle,
            (30, 30, 46): flavor_colors.base,
            (49, 50, 68): flavor_colors.surface0,
            (69, 71, 90): flavor_colors.surface1,
            (88, 91, 112): flavor_colors.surface2,
            (108, 112, 134): flavor_colors.overlay0,
            (127, 132, 156): flavor_colors.overlay1,
            (147, 153, 178): flavor_colors.overlay2,
            (166, 173, 200): flavor_colors.subtext0,
            (186, 194, 222): flavor_colors.subtext1,
            (205, 214, 244): flavor_colors.text,
            (180, 190, 254): flavor_colors.lavender,
            (137, 180, 250): flavor_colors.blue,
            (116, 199, 236): flavor_colors.sapphire,
            (137, 220, 235): flavor_colors.sky,
            (148, 226, 213): flavor_colors.teal,
            (166, 227, 161): flavor_colors.green,
            (249, 226, 175): flavor_colors.yellow,
            (250, 179, 135): flavor_colors.peach,
            (235, 160, 172): flavor_colors.maroon,
            (243, 139, 168): flavor_colors.red,
            (181, 103, 125): flavor_colors.red2,
            (203, 166, 247): flavor_colors.mauve,
            (245, 194, 231): flavor_colors.pink,
            (242, 205, 205): flavor_colors.flamingo,
            (245, 224, 220): flavor_colors.rosewater}

        # Creating a temporary template for each flavor which is used later on just to change the accent colors.
        print(f'Starting to create a temporary template for {flavor}!\n')
        temporary_template_folder = PurePath(temporary_files_dir, flavor)
        copytree(template_folder, temporary_template_folder)

        # Create a temporary template for each flavor which is used later on just to change the accent colors.
        for dirpath, _, filenames in os_walk(temporary_template_folder):
            for filename in filenames:
                # Copy file from another template if filename starts with '$1'
                if '$1' in filename and 'template.json' not in filename and 'template.lang' not in filename:
                    texture_template_version = filename.split('$', 1)[1].split('$', 1)[0]
                    path_list = list(PurePath(dirpath).parts)
                    path_list[path_list.index('temp')] = 'template'
                    path_list[path_list.index(template_version)] = texture_template_version
                    path_list.remove(flavor)

                    old_filename = filename
                    filename = filename.replace(f'${texture_template_version}$', '').replace('$flavor$', f'${flavor.lower()}$')

                    # Check if template has specific texture for current flavor.
                    # For example: '$latte$filename.png'.
                    if '$flavor$' not in old_filename and isfile(PurePath(*path_list, f'${flavor.lower()}${filename}')):
                        filename = f'${flavor.lower()}${filename}'
                    
                    texture_path = PurePath(*path_list, filename)
                    if isfile(texture_path):
                        # Copy texture file from other template to temporary template.
                        shutil_copy2(texture_path, PurePath(dirpath, filename))
                        os_remove(PurePath(dirpath, old_filename))
                    elif '$accent_color$' in filename:
                        for accent in CatppuccinAccentColors.all():
                            new_filename = filename.replace('$accent_color$', f'${accent.lower()}$')
                            texture_path = PurePath(*path_list, new_filename)
                            if isfile(texture_path):
                                # Copy texture file from other template to temporary template.
                                shutil_copy2(texture_path, PurePath(dirpath, new_filename.replace(f'${flavor.lower()}$', '')))
                        os_remove(PurePath(dirpath, old_filename))
                        continue
                    else:
                        print(f'ERROR: File \'{filename}\' not found in path:\n{texture_path}')
                        return
                
                # If file has '$current_flavor$' prefix
                # remove the prefix so textures inside file will work in the pack.
                if filename.startswith(f'${flavor.lower()}$'):
                    filenameNoFlavorPrefix = filename.replace(f'${flavor.lower()}$', '')
                    fileNoFlavorPrefix = PurePath(dirpath, filenameNoFlavorPrefix)
                    # Remove file without flavor prefix so the one with flavor prefix can be renamed.
                    if isfile(fileNoFlavorPrefix):
                        os_remove(fileNoFlavorPrefix)
                        filenames.remove(filenameNoFlavorPrefix)
                    os_rename(
                        PurePath(dirpath, filename),
                        PurePath(dirpath, filename.replace(f'${flavor.lower()}$', '')))
                    continue

                # Replace the correct colors for each image.
                if filename.endswith('.png') and not filename.startswith('$'):
                    # Skip creating textures for temporary template of Mocha since
                    #  textures in the template already use colors of flavor Mocha.
                    if flavor == 'Mocha':
                        continue

                    image_path = PurePath(dirpath, filename)
                    with Image.open(str(image_path)) as image:
                        image = image.convert('RGBA')
                        width, height = image.size

                    # Process all pixels
                    for x in range(0, width):
                        for y in range(0, height):
                            r, g, b, a = image.getpixel((x, y))
                            # Skip empty pixels
                            if (r, g, b, a) == (0, 0, 0, 0):
                                continue

                            for template_color, new_color in color_map.items():
                                new_color_with_alpha = new_color + (a,)
                                if (r, g, b) == template_color:
                                    image.putpixel((x, y), new_color_with_alpha)
                                    continue
                    image.save(str(image_path), 'PNG')

                # Create language files for Minecraft and mods that have language files.
                elif dirpath.endswith('lang') and 'template' in filename:
                    path_list = PurePath(dirpath).parts
                    mod_name = path_list[-2]
                    # Check if mod has language files.
                    if not filename.startswith('$'):
                        folder_name = lang_version
                        lang_folder = PurePath(language_files_folder, folder_name, mod_name)
                    else:
                        folder_name = filename.split('$', 1)[1].split('$', 1)[0]
                        lang_folder = PurePath(language_files_folder, folder_name, mod_name)
                    # Check if mod has language files.
                    if isdir(lang_folder) and any(scandir(lang_folder)):
                        all_language_files = listdir(lang_folder)
                        mod_lang_files_folder = lang_folder
                    else:
                        print(f'No language files found for mod \'{mod_name}\'!\n'
                              f'Add language files or fix template language file prefix.')
                        return

                    # Load the template language file.
                    template_language_file = PurePath(dirpath, filename)
                    with open(template_language_file, 'r') as template_file:
                        if template_language_file.suffix == '.json':
                            try:
                                template = json_load(template_file)
                            except JSONDecodeError as e:
                                print(
                                    f'ERROR: Unable to load template language file at path: '
                                     f'{template_language_file}\nReason: ', e)
                                return
                        elif template_language_file.suffix == '.lang':
                            template_language_dict = {}
                            for line in template_file:
                                if '=' in line:
                                    key, value = line.strip().split('=', 1)
                                    template_language_dict[key] = value
                            template = template_language_dict

                    # Create language files for every language available.
                    print(
                        f'Template language file found for {mod_name}! '
                        f'Starting to create language files of {mod_name} for flavor {flavor}!\n')
                    # Loop over all available language files.
                    for lang in sorted(all_language_files):
                        lang_dict = {}
                        # Load each language file correctly depending on game version.
                        with open(PurePath(
                                mod_lang_files_folder, lang), 'r', encoding='utf-8') as lang_file:
                            if lang.endswith('.json'):
                                try:
                                    lang_dict = json_load(lang_file)
                                except JSONDecodeError as e:
                                    print(
                                        f'ERROR: Unable to load language file at path: '
                                        f'{lang_file}\nReason: ', e)
                                    return
                            elif lang.endswith('.lang'):
                                temporary_language_dict = {}
                                for line in lang_file:
                                    if '=' in line:
                                        key, value = line.strip().split('=', 1)
                                        temporary_language_dict[key] = value
                                lang_dict = temporary_language_dict

                        # Create a copy of the template with correct translations
                        #   from the original language file.
                        template_copy = template.copy()

                        # If the original language file doesn't have a certain translation
                        #   it'll be removed from template_copy.
                        #   Minecraft then just automatically uses en_us translations as a fallback.
                        for key in list(template_copy.keys()):
                            if key not in lang_dict:
                                del template_copy[key]

                        # Set correct colors and translations for each key in template_copy.
                        for key, value in lang_dict.items():
                            if key in template_copy:
                                template_value = template_copy[key]
                                if '<value>' in template_value:
                                    if '<text_color>' in template_value:
                                        template_value = template_value.replace(
                                            '<text_color>', flavor_colors.text_color)
                                    elif '<green_text_color>' in template_value:
                                        template_value = template_value.replace(
                                            '<green_text_color>', flavor_colors.green_text_color)
                                    elif '<yellow_text_color>' in template_value:
                                        template_value = template_value.replace(
                                            '<yellow_text_color>', flavor_colors.yellow_text_color)
                                    elif '<purple_text_color>' in template_value:
                                        template_value = template_value.replace(
                                            '<purple_text_color>', flavor_colors.purple_text_color)
                                    template_copy[key] = template_value.replace('<value>', value)
                                else:
                                    template_copy[key] = ''

                        # Save the updated template_copy as a new file.
                        new_file_name = PurePath(
                            temporary_files_dir, flavor, 'assets', mod_name, 'lang', lang)
                        shutil_copy2(template_language_file, new_file_name)

                        with open(new_file_name, 'w', encoding='utf-8') as new_file:
                            if lang.endswith('.json'):
                                json_dump(template_copy, new_file, indent=4, ensure_ascii=False)
                            elif lang.endswith('.lang'):
                                for key, value in template_copy.items():
                                    new_file.write(f'{key}={value}\n')

                    print(
                        f'Language files of {mod_name} ready for the '
                        f'temporary template of flavor {flavor}!\n')

                # Delete file if it doesn't have '$ignore$' prefix. This removes all files that are either not needed
                # anymore (template language files) or files that are only used by other flavors than current.
                elif not filename.startswith('$ignore$') and filename != 'pack.mcmeta':
                    os_remove(PurePath(dirpath, filename))
                    continue

        print(f'Temporary template for flavor {flavor} is ready!\n')

        # Generate resource packs for each accent color from the temporary template of flavor created earlier.
        for color in CatppuccinAccentColors.all():
            print(f'Starting to create flavor {flavor} with accent color {color}!')

            version_folder = PurePath(output_folder, f'Catppuccin {flavor} {color}')

            # Create color map for current accent color.
            if color == CatppuccinAccentColors.lavender:
                accent_color = flavor_colors.lavender
            elif color == CatppuccinAccentColors.blue:
                accent_color = flavor_colors.blue
            elif color == CatppuccinAccentColors.sapphire:
                accent_color = flavor_colors.sapphire
            elif color == CatppuccinAccentColors.sky:
                accent_color = flavor_colors.sky
            elif color == CatppuccinAccentColors.teal:
                accent_color = flavor_colors.teal
            elif color == CatppuccinAccentColors.green:
                accent_color = flavor_colors.green
            elif color == CatppuccinAccentColors.yellow:
                accent_color = flavor_colors.yellow
            elif color == CatppuccinAccentColors.peach:
                accent_color = flavor_colors.peach
            elif color == CatppuccinAccentColors.maroon:
                accent_color = flavor_colors.maroon
            elif color == CatppuccinAccentColors.red:
                accent_color = flavor_colors.red
            elif color == CatppuccinAccentColors.mauve:
                accent_color = flavor_colors.mauve
            elif color == CatppuccinAccentColors.pink:
                accent_color = flavor_colors.pink
            elif color == CatppuccinAccentColors.flamingo:
                accent_color = flavor_colors.flamingo
            else:
                accent_color = flavor_colors.rosewater

            accent_color_map = {(255, 0, 0): accent_color}

            # Delete version_folder if it exists so a new one can be created.
            if os_path_exists(version_folder):
                rmtree(version_folder)

            # Copy the temporary template to the final location
            #   and then update the accent color for each texture.
            copytree(temporary_template_folder, version_folder)
            for dirpath, _, filenames in os_walk(version_folder):
                for filename in filenames:
                    # If file has '$current_accent_color$' prefix
                    #   remove the prefix so textures inside file will work in the pack.
                    if filename.startswith(f'${color.lower()}$'):
                        os_rename(
                            PurePath(dirpath, filename),
                            PurePath(dirpath, filename.replace(f'${color.lower()}$', '')))
                        continue

                    # Remove '$ignore$' prefix if file has it.
                    elif filename.startswith('$ignore$'):
                        os_rename(
                            PurePath(dirpath, filename),
                            PurePath(dirpath, filename.replace('$ignore$', '')))
                        continue

                    # Update accent color for all textures.
                    if filename.endswith('.png') and not filename.startswith('$'):
                        image_path = PurePath(dirpath, filename)
                        with Image.open(str(image_path)) as image:
                            image = image.convert('RGBA')
                            width, height = image.size

                        # Process all pixels
                        for x in range(0, width):
                            for y in range(0, height):
                                r, g, b, a = image.getpixel((x, y))
                                # Skip empty pixels
                                if (r, g, b, a) == (0, 0, 0, 0):
                                    continue

                                for template_color, new_color in accent_color_map.items():
                                    new_color_with_alpha = new_color + (a,)
                                    if (r, g, b) == template_color:
                                        image.putpixel((x, y), new_color_with_alpha)
                                        continue
                        image.save(str(image_path), 'PNG')

                    # Update pack description.
                    elif filename == 'pack.mcmeta':
                        file_path = PurePath(dirpath, filename)
                        with open(file_path, 'r') as mcmeta:
                            try:
                                pack_mcmeta = json_load(mcmeta)
                            except JSONDecodeError as e:
                                print(
                                    f'ERROR: Unable to load pack.mcmeta file at path: '
                                    f'{mcmeta}\nReason: ', e)
                                return

                        pack_mcmeta['pack']['description'] = (
                            pack_mcmeta['pack']['description']
                            .replace('<pack_version>', pack_version)
                            .replace('<mc_version>', mc_versions))

                        with open(file_path, 'w') as mcmeta:
                            json_dump(pack_mcmeta, mcmeta, indent=4)

                    # Delete files of other accent colors than the current accent color.
                    elif filename.startswith(f'$') and not filename.startswith(f'${color.lower()}$'):
                        os_remove(PurePath(dirpath, filename))

            make_archive(str(version_folder), 'zip', str(version_folder))
            rmtree(version_folder)
        print(f'\nFlavor {flavor} is ready for every accent color!')

    # Delete the temporary files folder.
    if isdir(temporary_files_dir):
        rmtree(temporary_files_dir)

    # Calculate the time it took to run this script.
    ending_time = int(time_perf_counter())
    total_time = ending_time - starting_time
    minutes, seconds = divmod(total_time, 60)

    print(
        f'\nEverything done!\n'
        f'Completed in {minutes} minutes and {seconds} seconds.\n'
        f'You may close this window now!')
    return


if __name__ == '__main__':
    main()
    input()
