import shutil
import sys

import xmltodict
import json

from pathlib import Path


def transform(sip_dir, out_dir):
    """
        sip_name
        |   Metadata
            |   normalised DC.xml
        |   representations folder and sub folders
    """

    sip_name = sip_dir.stem.split(' ')[0]
    out_dir = out_dir / sip_name

    # Overwrite existing files
    if out_dir.is_dir():
        print(f"Overwriting {out_dir}")
        shutil.rmtree(out_dir)
        out_dir.mkdir(parents=True, exist_ok=False)

    # Copy representations folder(s)
    representations_path = sip_dir / "representations"
    if representations_path.exists():
        shutil.copytree(representations_path, out_dir / "representations")
    else:
        print('Representations directory not found.')
        print('Exiting.')
        sys.exit(1)

    # Extract and normalise dc.xml to metadata.json file
    sip_metadata_file = sip_dir / "metadata" / "descriptive" / "dc.xml"
    if sip_metadata_file.exists:
        try:
            (out_dir / "metadata").mkdir(parents=True, exist_ok=True)
        except OSError as e:
            print("Error creating metadata directory.")
            print(e.args)
        else:
            json_metadata = xml_to_json(sip_metadata_file)
            with open(out_dir / "metadata" / "metadata.json", "w") as json_file:
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
    if sip_dir.exists():
        if sip_dir.is_dir():
            if output_dir.exists():
                if output_dir.is_dir():
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
            print('Incorrect metadata format. Expected simpledc.')
        else:
            metadata_dict = {"filename": "object/representations"}
            for key in obj:
                if not key.startswith('@'):
                    metadata_dict["dc."+key] = obj[key]
            json_obj = json.dumps(metadata_dict, indent=4)
            return json_obj


if __name__ == '__main__':
    numArgs = len(sys.argv)
    if numArgs == 3:
        sip_directory = Path(get_arg(1))
        output_directory = Path(get_arg(2))
        if validate_directories(sip_directory, output_directory):
            transform(sip_directory, output_directory)
            print("Process Complete.")
        else:
            sys.exit(1)
    else:
        print("Error: Command should have the form:")
        print("python main.py <SIP Directory> <Output Directory>:")
        sys.exit(1)
