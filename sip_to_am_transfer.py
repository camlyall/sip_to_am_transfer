import getopt
import json
import shutil
import sys
import xmltodict
import logging
from pathlib import Path


def validate(sip_dir: Path, output_dir: Path) -> bool:
    if sip_dir.exists():
        if sip_dir.is_dir():
            if output_dir.exists():
                if output_dir.is_dir():
                    return True
                else:
                    logging.fatal("Error: Output is not a directory")
            else:
                return True
        else:
            logging.fatal("Error: Input is not a directory")
    else:
        logging.fatal("Error: Input directory doesn't exit")
    return False


def dc_xml_to_json(dc_file):
    with open(dc_file) as xml:
        try:
            obj = xmltodict.parse(xml.read())['simpledc']
        except KeyError:
            logging.error('Incorrect metadata format. Expected simpledc.')
            # print('Incorrect metadata format. Expected simpledc.')
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

    descriptive_metadata_dir = sip_dir / 'metadata' / 'descriptive'

    dc_metadata_file = ''
    dc_json_data = ''
    if (descriptive_metadata_dir / 'dc.xml').is_file():
        dc_metadata_file = descriptive_metadata_dir / 'dc.xml'
    elif (descriptive_metadata_dir / 'DC.xml').is_file():
        dc_metadata_file = descriptive_metadata_dir / 'DC.xml'
    else:
        logging.info('DC.xml metadata not found')

    if dc_metadata_file != '':
        logging.info(str(dc_metadata_file.stem) + ' metadata found')
        dc_json_data = dc_xml_to_json(dc_metadata_file)

    for sip_rep_dir in sip_representations_dir.iterdir():
        if sip_rep_dir.is_dir():
            transfer_name = sip_name + '-' + sip_rep_dir.name
            transfer_output_dir = output_dir / transfer_name
            if transfer_output_dir.is_dir():
                logging.info(f"Overwriting {transfer_output_dir}")
                shutil.rmtree(transfer_output_dir)
            transfer_output_dir.mkdir(parents=True, exist_ok=False)

            # Copy representations folder(s)
            shutil.copytree(sip_rep_dir, transfer_output_dir / "representation")
            logging.info('Representations copied')

            # Write DC metadata json
            if dc_json_data != '':
                (transfer_output_dir / "metadata").mkdir(parents=False, exist_ok=False)
                with open(transfer_output_dir / "metadata" / "metadata.json", "w") as json_file:
                    json_file.write("["+dc_json_data+"]")
                    logging.info('metadata.json written')
        else:
            logging.fatal('Warning: File found in representations')
            sys.exit(2)
    logging.info('COMPLETE!')


def main(argv):
    sip_dir = ''
    output_dir = ''
    try:
        opts, _ = getopt.getopt(argv,"hi:o:",["input=, output="])
    except getopt.GetoptError:
        logging.fatal('Incorrect script call format.')
        print("Error: Command should have the form:")
        print('python sip_to_am_transfer.py -i <SIP directory> -o <Output Directory>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('python sip_to_am_transfer.py -i <SIP Directory> -o <Output Directory>')
            sys.exit(2)
        elif opt in ("-i", "--input"):
            input_arg = Path(arg)
            if input_arg.is_dir() and (input_arg / 'representations').is_dir():
                sip_dir = input_arg
            else:
                logging.fatal('Invalid SIP')
                print("Input is not a valid SIP directory")
                sys.exit(2)
        elif opt in ("-o", "--output"):
            output_arg = Path(arg)
            if not output_arg.is_dir():
                logging.info('Creating output directory:' + str(output_arg))
                # print("Creating output directoy:", output_arg)
                output_arg.mkdir(parents=True, exist_ok=False)
            output_dir = output_arg
    if sip_dir == '':
        logging.fatal("No SIP given")
        sys.exit(2)
    if output_dir == '':
        logging.fatal("No output directory given")
        sys.exit(2)
    if validate(sip_dir, output_dir):
        transform(sip_dir, output_dir)


if __name__ == "__main__":
    Path("logs").mkdir(exist_ok=True)
    logging.basicConfig(level=logging.DEBUG, filemode='a', filename='logs/sip_to_am_transfer.log', format='%(asctime)s %(levelname)s: %(message)s')
    main(sys.argv[1:])
    
