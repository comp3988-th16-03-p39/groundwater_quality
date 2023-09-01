import csv
import sys
import glob, os

#  USYD CODE CITATION ACKNOWLEDGEMENT
#  I declare that the following lines of code have been copied from the
#  website StackOverFlow and it is not my own work. 
 
#  Original URL
#  https://stackoverflow.com/questions/15063936/csv-error-field-larger-than-field-limit-131072
#  Last access Auguest, 2023.

maxInt = sys.maxsize

while True:
    # decrease the maxInt value by factor 10 
    # as long as the OverflowError occurs.
    try:
        csv.field_size_limit(maxInt)
        break
    except OverflowError:
        maxInt = int(maxInt/10)
#end of copied code

os.chdir("DP_GWDBQLD/")
for file in glob.glob("*.txt"):
    input_filename = str(file)
    output_filename = str(file).split(".")[0] + ".csv"

    # Read the contents of the txt file and write them to a csv file
    with open(input_filename, "r", encoding='utf-8', errors='replace') as txt_file, open(output_filename, "w", newline='', encoding='utf-8') as csv_file:
        reader = csv.reader(txt_file, delimiter='|')
        writer = csv.writer(csv_file, delimiter=',')

        for row in reader:
            writer.writerow(row)

    print(f"{input_filename} has been converted to {output_filename}.")