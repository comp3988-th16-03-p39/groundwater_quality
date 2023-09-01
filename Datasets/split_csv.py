#  USYD CODE CITATION ACKNOWLEDGEMENT
#  I declare that the following lines of code have been copiedyy from the
#  website MungingData and it is not my own work. 
 
#  Original URL
#  https://mungingdata.com/python/split-csv-write-chunk-pandas/
#  Last access August, 2023

chunk_size = 1000000
def write_chunk(path, part, lines, header):
    with open(path + '_'+ str(part) +'.csv', 'w') as f_out:
        f_out.write(header)
        f_out.writelines(lines)

def split_csv (path):
    with open(path + '.csv', "r") as f:
        count = 0
        header = f.readline()
        lines = []
        for line in f:
            count += 1
            lines.append(line)
            if count % chunk_size == 0:
                write_chunk(path,count // chunk_size, lines, header)
                lines = []
        # write remainder
        if len(lines) > 0:
            write_chunk(path,(count // chunk_size) + 1, lines, header)

split_csv ('ddw2020-present_2023-07-03')