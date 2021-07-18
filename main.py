# coding=utf-8

import sys
import configparser
import os

from module import msg
from module import vision


# handle config
def set_config(home_dir):

    # set home dir as env
    os.environ['HOME_DIR'] = home_dir

    # read from config file
    parser = configparser.ConfigParser()
    parser.read(os.path.join(os.environ['HOME_DIR'], 'conf/config'))

    # set config as env
    for option in parser.options('ENV'):
        os.environ[option.upper()] = parser.get('ENV', option)

    # postprocessing
    os.environ['TMP_DIR'] = os.path.join(os.environ['HOME_DIR'], os.environ['TMP_DIR'])
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.join(os.environ['HOME_DIR'], os.environ['GOOGLE_APPLICATION_CREDENTIALS'])


# main
def main():
    # handle config
    if len(sys.argv) <= 1:
        print('[ERROR] HOME_DIR must be issued')
        sys.exit(1)
    print('[INFO] HOME_DIR=%s' % sys.argv[1])
    set_config(sys.argv[1])

    # watch directory
    for mail in os.listdir(os.environ['POOL_DIR']):

        # get images
        mail_path = os.path.join(os.environ['POOL_DIR'], mail)
        save_img_list = msg.get_img(mail_path)

        # call google vision api
        if os.environ['CALL_API'].lower() == 'true' and save_img_list:
            text_list = vision.GoogleVision(save_img_list).read()
            # reassemble message
            msg.reassemble(text_list, mail_path)

        # send message to local smtp
        send_result = msg.send(mail_path)
        print('[INFO] %s send result=%s' % (mail_path, send_result))
        if send_result:
            # delete message
            msg.delete(mail_path)


if __name__ == '__main__':
    main()



