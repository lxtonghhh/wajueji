import csv


def write2csv(header, content, fname):
    with open(fname + '.csv', 'w') as f:
        f_csv = csv.writer(f)
        f_csv.writerow(header)
        f_csv.writerows(content)


class DataFrame(object):
    def __init__(self, header, content):
        """
        header-> 'code' 'open' 'close'
        content->[["sz000001",16.75,17.9],["sz000002",16.75,17.9]]
        """
        self.content = content
        self.header = header


if __name__ == "__main__":
    pass
