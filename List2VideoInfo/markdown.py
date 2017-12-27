#!/usr/bin/env python3

import csv
import sys, getopt, os

# port_csv.writerow(['title','p-title','link','aid', 'cid'])

def xtable_markdown(inputfile):
    outputfile = ''

    outputfile = os.path.splitext(inputfile)[0]
    f = open(outputfile + '.md','w')


    with open(inputfile,newline='') as csvfile:
        videoreader = csv.reader(csvfile,delimiter=',')
        next(videoreader, None) # skip header

        # table_header = '| 公演场次 | 分P | aid | cid |\n' + '|---|---|:--:|:--:|\n'
        table_header = '<table style="width:100%">\n'
        f.write(table_header)
        caption = '    <caption>' + inputfile + '</caption>\n'

        for row in videoreader:
            firstrow = 1
            table_row = ''
            link = '<a href="' + row[2] + '">' + row[1] + '</a>'

            if row[0]:
                span_row = '    <tr>\n'  \
                        + '        <th colspan="5">' + row[0] + '</th>\n' \
                        + '    </tr>\n'
                if firstrow == 1:
                    table_row = '    <tr>\n'
                else:
                    table_row = '    </tr>\n    <tr>\n'
                table_row = table_row + span_row

            table_row = table_row + '        <td>' +  link + '</td>\n'
            firstrow = 0
            f.write(table_row)

        table_end = '    </tr>\n</table>\n'

        f.write(table_end)

    f.close()

def table_markdown(inputfile):
    outputfile = ''

    outputfile = os.path.splitext(inputfile)[0]
    f = open(outputfile + '.md','w')


    with open(inputfile,newline='') as csvfile:
        videoreader = csv.reader(csvfile,delimiter=',')
        next(videoreader, None) # skip header

        table_header = '| 公演场次 | 分P | aid | cid |\n' + '|---|---|:--:|:--:|\n'
        f.write(table_header)

        for row in videoreader:
            table_row = ''
            link = '[' + row[1] + '](' + row[2] + ')'

            if row[0]:
                table_row = '| ' + row[0] + ' | ' + link + ' | ' + row[3] + ' | ' + row[4] + ' |\n'
            else:
                table_row = '| ' + row[0] + ' | ' + link + ' | ' + row[3] + ' | ' + row[4] + ' |\n'
            f.write(table_row)

    f.close()


def simple_markdown(inputfile):
    outputfile = ''

    outputfile = os.path.splitext(inputfile)[0]
    f = open(outputfile + '.md','w')


    with open(inputfile,newline='') as csvfile:
        f.write('# %s' % outputfile)
        videoreader = csv.reader(csvfile,delimiter=',')
        next(videoreader, None) # skip header

        for row in videoreader:
            if row[0]:
                line = '\n\n## ' + row[0] + '\n'
                f.write(line)

            vline = '\n[' + row[1] + '](' + row[2] + ')' + ' '
            f.write(vline)

    f.close()

def main(argv):
    inputfile = str(sys.argv[1])
    xtable_markdown(inputfile)


if __name__ == '__main__':
    main(sys.argv[1:])
