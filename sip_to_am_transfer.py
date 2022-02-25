import getopt
import json
import shutil
import sys
import xmltodict
from pathlib import Path


def validate(sip_dir: Path, output_dir: Path) -> bool:
    if sip_dir.exists():
        if sip_dir.is_dir():
            if output_dir.exists():
                if output_dir.is_dir():
                    return True
                else:
                    print("Error: Output is not a directory")
            else:
                return True
        else:
            print("Error: Input is not a directory")
    else:
        print("Error: Input directory doesn't exit")
    return False


def dc_xml_to_json(dc_file):
    with open(dc_file) as xml:
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


# Create multiple transfer files for each representation
def transform(sip_dir: Path, output_dir: Path):

    sip_name = sip_dir.stem.split(' ')[0]
    sip_representations_dir = sip_dir / 'representations'

    dc_metadata_file = sip_dir / "metadata" / "descriptive" / "dc.xml"
    dc_json_data = ''
    if dc_metadata_file.is_file():
        dc_json_data = dc_xml_to_json(dc_metadata_file)

    for sip_rep_dir in sip_representations_dir.iterdir():
        if sip_rep_dir.stem.startswith('rep') and sip_rep_dir.is_dir():
            transfer_name = sip_name + '-' + sip_rep_dir.name
            transfer_output_dir = output_dir / transfer_name
            if transfer_output_dir.is_dir():
                print(f"Overwriting {transfer_output_dir}")
                shutil.rmtree(transfer_output_dir)
            transfer_output_dir.mkdir(parents=True, exist_ok=False)

            # Copy representations folder(s)
            shutil.copytree(sip_rep_dir, transfer_output_dir / "representations")

            # Write DC metadata json
            if dc_json_data != '':
                (transfer_output_dir / "metadata").mkdir(parents=False, exist_ok=False)
                with open(transfer_output_dir / "metadata" / "metadata.json", "w") as json_file:
                    json_file.write("["+dc_json_data+"]")

        else:
            print('Error in representations structure')


def main(argv):
    sip_dir = ''
    output_dir = ''
    try:
        opts, _ = getopt.getopt(argv,"hi:o:",["input=, output="])
    except getopt.GetoptError:
        print('metsgen.py -i <SIP directory> -o <Output Directory>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('metsgen.py -i <SIP Directory> -o <Output Directory>')
            sys.exit(2)
        elif opt in ("-i", "--input"):
            input_arg = Path(arg)
            if input_arg.is_dir() and (input_arg / 'representations').is_dir():
                sip_dir = input_arg
            else:
                print("Input is not a valid SIP directory")
                sys.exit(2)
        elif opt in ("-o", "--output"):
            output_arg = Path(arg)
            if not output_arg.is_dir():
                print("Creating output directoy:", output_arg)
                output_arg.mkdir(parents=True, exist_ok=False)
            output_dir = output_arg
    if sip_dir == '':
        print("No SIP given")
        sys.exit(2)
    if output_dir == '':
        print("No Output directory given")
        sys.exit(2)
    if validate(sip_dir, output_dir):
        transform(sip_dir, output_dir)


if __name__ == "__main__":
    main(sys.argv[1:])