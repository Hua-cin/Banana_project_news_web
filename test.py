import os


def main():

    title_exclude_word_path = "{}/ref_data/title_exclude_word.txt".format(os.getcwd())
    itle_exclude_word = load_file_to_list(title_exclude_word_path))

def load_file_to_list(path):
    '''
    load file for list item
    :param path: file path
    :return: data list
    '''

    with open(path, 'r', encoding='utf-8') as f:
        temp = f.read()

    text = temp.split('\n')
    title_exclude_word = []

    for i in text:
        title_exclude_word.append(i)

    return title_exclude_word

if __name__ == "__main__":
    main()