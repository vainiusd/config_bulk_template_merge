import getopt, sys
import logging
import yaml
import jinja2
from os import listdir
from os.path import isfile, join, split

USAGE = '''
This scrpt merges a Jinja2 template file with configuration data provided in YAML files.
One configuration file generate for each yaml file.

 "-v"                     --> Verbose output
 "-h", "--help"           --> This menu
 "-t", "--template"       --> Template file
 "-c", "--config"         --> YAML file directory
 "-o", "--output"         --> Output configuration directory

Defaults:
    Template file   = './templates/template.j2'
    YAML file dir   = './yaml_configs/'
    Config file dir = './device_configs/'
'''


def main():
	# Defaults
    SEARCHPATH = './templates/'
    CONF_TEMPL = './templates/template.j2'
    YAML_PATH = './yaml_configs/'
    CONFIG_PATH = './device_configs/'
    try:
        opts, args = getopt.getopt(sys.argv[1:], "c:ho:t:v", 
            ["config=","help","output=","template="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err) # will print something like "option -a not recognized"
        print(USAGE)
        sys.exit(2)
    verbose = False
    for o, a in opts:
        if o == "-v":
            logging.basicConfig(level=logging.INFO)
        elif o in ("-h", "--help"):
            print(USAGE)
            sys.exit()
        elif o in ("-t", "--template"):
            CONF_TEMPL = a
        elif o in ("-c", "--config"):
            YAML_PATH = a
        elif o in ("-o", "--output"):
            CONFIG_PATH = a
        else:
            assert False, "unhandled option"

    # Find device configuration YAML files in YAML_PATH dir
    devices = [f for f in listdir(YAML_PATH) if isfile(join(YAML_PATH, f))]
    logging.info('Found device configuration files in dir ' + YAML_PATH)
    logging.info(devices)

    # Read Jinja2 template
    TEMPL_DIR = split(CONF_TEMPL)[0]
    TEMPL_FILE = split(CONF_TEMPL)[1]
    jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath=split(TEMPL_DIR)))
    jinja_env.trim_blocks = True
    jinja_env.lstrip_blocks = True
    template = jinja_env.get_template(TEMPL_FILE)
    logging.info('Using configuration template ' + CONF_TEMPL)

    # Generating configs
    for filename in devices:
        # Read yaml file to python data structure
        YAML_FILE = YAML_PATH + filename
        logging.info('Using device YAML configuration file ' + YAML_FILE)
        with open(YAML_FILE) as fp:
            info = yaml.safe_load(fp)
            logging.info('Generating configuration file for ' + info['hostname'])
            # Render template with data
            config = template.render(info)
            # Output to file
            CONFIG_FILE = CONFIG_PATH + info['hostname'] + '.ios'
            print(config, file=open(CONFIG_FILE,'w'))
            logging.info('Created device configuration file ' + CONFIG_FILE)

if __name__ == "__main__":
    main()