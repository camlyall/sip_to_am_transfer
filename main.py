import os.path
import shutil
import sys

import xmltodict
import json


def transform(sip_dir, out_dir):
    """
        sip_name
        |   Metadata
            |   normalised DC.xml
        |   representations folder and sub folders
    """

    sip_name = os.path.basename(os.path.normpath(sip_dir)).split(' ')[0]
    out_dir = os.path.join(out_dir, sip_name)

    # Overwrite existing files
    if os.path.isdir(out_dir):
        print(f"Overwriting {out_dir}")
        shutil.rmtree(out_dir)
        os.makedirs(os.path.join(out_dir))

    # Copy representations folder(s)
    representations_path = os.path.join(sip_dir, "representations")
    if os.path.exists(representations_path):
        shutil.copytree(os.path.join(representations_path), os.path.join(out_dir, "representations"))
    else:
        print('Representations directory not found.')
        print('Exiting.')
        sys.exit(1)

    # Extract and normalise dc.xml to metadata.json file
    sip_metadata_file = os.path.join(sip_dir, "metadata", "descriptive", "dc.xml")
    if os.path.exists(sip_metadata_file):
        try:
            os.makedirs(os.path.join(out_dir, "metadata"), exist_ok=True)
        except OSError as e:
            print("Error creating metadata directory.")
            print(e.args)
        else:
            json_metadata = xml_to_json(sip_metadata_file)
            with open(os.path.join(out_dir, "metadata", "metadata.json"), "w") as json_file:
                json_file.write(json_metadata)
    else:
        print('metadata/descriptive/dc.xml not found')


def get_arg(index):
    try:
        sys.argv[index]
    except IndexError:
        return None
    else:
        return sys.argv[index]


def validate_directories(sip_dir, output_dir):
    if os.path.exists(sip_dir):
        if os.path.isdir(sip_dir):
            if os.path.exists(output_dir):
                if os.path.isdir(output_dir):
                    return True
                else:
                    print("Error: Output is not a directory")
            else:
                print("Error: Output directory doesn't exit")
        else:
            print("Error: Input is not a directory")
    else:
        print("Error: Input directory doesn't exit")
    return False


def xml_to_json(file):
    with open(file) as xml:
        try:
            obj = xmltodict.parse(xml.read())['simpledc']
        except KeyError:
            print('Incorrect metadata format. Expected simpledc')
        else:
            metadata_dict = {"filename": "object/representations"}
            for key in obj:
                if not key.startswith('@'):
                    metadata_dict["dc."+key] = obj[key]
            json_obj = json.dumps(metadata_dict, indent=4)
            print(json_obj)
            return json_obj


if __name__ == '__main__':
    numArgs = len(sys.argv)
    if numArgs == 3:
        sip_directory = get_arg(1)
        output_directory = get_arg(2)
        if validate_directories(sip_directory, output_directory):
            # TODO: Validate folder structure?
            transform(sip_directory, output_directory)
        else:
            sys.exit(1)
    else:
        print("Error: Command should have the form:")
        print("python main.py <SIP Directory> <Output Directory>:")
        sys.exit(1)
