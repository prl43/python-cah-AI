from urllib.request import urlopen
import os


def fetch_card_list(url):
    start_delete_str = 'cards='

    data = str(urlopen(url).read().decode('utf-8'))
    start_index = data.find(start_delete_str) + len(start_delete_str)
    data = data[start_index:]
    return data


def write_file(overwrite, file_name, urls):
    if (not overwrite) and os.path.isfile(os.path.join(os.path.dirname(__file__), file_name)):
        return None
    with open(os.path.join(os.path.dirname(__file__), file_name), "w") as f:
        for u in urls:
            f.write(fetch_card_list(u))


def download(overwrite=False):
    write_file(overwrite, "bin/answer.txt", ["http://www.cardsagainsthumanity.com/wcards.txt"])

    write_file(overwrite, "bin/question.txt", ["http://www.cardsagainsthumanity.com/bcards.txt",
                                               "http://www.cardsagainsthumanity.com/bcards1.txt",
                                               "http://www.cardsagainsthumanity.com/bcards2.txt"])

if __name__ == "__main__":
    download(True)
