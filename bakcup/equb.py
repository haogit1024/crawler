import ebooklib
from ebooklib import epub


def test_epub():
    book = epub.read_epub(r'F:\test\test.epub')
    for image in book.get_items_of_type(ebooklib.ITEM_IMAGE):
        print(image)


if __name__ == '__main__':
    test_epub()
