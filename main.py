import argparse
import csv
from pathlib import Path
import asyncio

querrys = []
uniquefreq = []
freqprio = "MOD PCCFREQCFG:PCCDLEARFCN={},PREFERREDPCCPRIORITY={},NSAPCCANCHORINGPRIORITY={};{}"
cellprio = "MOD CELLRESEL:LOCALCELLID={},CELLRESELPRIORITY={};{}"
celltofreq = "MOD EUTRANINTERNFREQ:LOCALCELLID={},DLEARFCN={},CELLRESELPRIORITYCFGIND=CFG,CELLRESELPRIORITY={};{}"


async def main(input, celltemplateoutput, layerpriooutput):
    """Checks for correctness of provided path, changing .txt to .csv if applicable"""
    inputpath = Path(input)

    if inputpath.is_dir():
        raise IsADirectoryError("Directorys are not accepted")

    if inputpath.suffix != ".csv":
        print("{} is not a csv file, renaming...".format(input))
        inputpath = inputpath.rename(inputpath.with_suffix(".csv"))

    with open(inputpath, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            querrys.append(row)

    async with asyncio.TaskGroup() as tg:
        taskct = tg.create_task(createcelltemplate(celltemplateoutput))
        tasklp = tg.create_task(createlayerprio(layerpriooutput))
        print("async finished")

async def createcelltemplate(celltemplateoutput):
    """Creates the Cell template and appends it to celltemplateoutput, creating the file if it doesnt exist"""
    for entry in querrys:
        with open("data\Event_Script_4G_cell_Template_v02_1cell.txt", "r") as template:
            with open(celltemplateoutput, "a") as output:
                for line in template:
                    linefmt = line.format(
                        entry.get("LOCALCELLID"), neformat(entry.get("NE"))
                    )
                    output.write(linefmt)
                output.write("\n")
    print("finished Cell template!")


async def createlayerprio(layerpriooutput):
    """Creates the layerprio file and appends it to layerpriooutput, creating the file if it doesnt exist, based on Event_Script_4G_LayerPrio_Template.txt in /data"""
    getuniquefreq()
    with open(layerpriooutput, "a") as output:
        for freq in uniquefreq:
            if int(freq[0]) != 300 and int(freq[0]) != 1600 and int(freq[0]) != 3350:
                output.write(freqprio.format(freq[0], 2, 2, neformat(freq[1])) + "\n")
            else:
                output.write(freqprio.format(freq[0], 6, 6, neformat(freq[1])) + "\n")
        output.write("\n")
        for elem in querrys:
            dlearfcn = int(elem.get("DLEARFCN"))
            if dlearfcn != 300 and dlearfcn != 1600 and dlearfcn != 3350:
                output.write(
                    cellprio.format(
                        elem.get("LOCALCELLID"), 2, neformat(elem.get("NE")) + "\n"
                    )
                )
            else:
                output.write(
                    cellprio.format(
                        elem.get("LOCALCELLID"), 6, neformat(elem.get("NE")) + "\n"
                    )
                )
            if int(elem.get("LOCALCELLID")) % 10 == 3:
                output.write("\n")
        for elem in querrys:
            for freq in uniquefreq:
                if int(elem.get("DLEARFCN")) != int(freq[0]):
                    if (
                        int(freq[0]) != 300
                        and int(freq[0]) != 1600
                        and int(freq[0]) != 3350
                    ):
                        output.write(
                            celltofreq.format(
                                elem.get("LOCALCELLID"),
                                freq[0],
                                2,
                                neformat(elem.get("NE")),
                            )
                            + "\n"
                        )
                    else:
                        output.write(
                            celltofreq.format(
                                elem.get("LOCALCELLID"),
                                freq[0],
                                6,
                                neformat(elem.get("NE")),
                            )
                            + "\n"
                        )
            output.write("\n")
    print("finished layerPrio!")


def getuniquefreq():
    """create a array of unique frequencies of the input file"""
    for elem in querrys:
        dlearfcn = elem.get("DLEARFCN")
        ne = elem.get("NE")
        if [dlearfcn, ne] not in uniquefreq:
            uniquefreq.append([dlearfcn, ne])


def neformat(ne):
    """formats the NE to conform to the template"""
    return "{" + ne + "}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Description")
    parser.add_argument(
        "input", type=str, help="Input file, needs to be in a csv parsable format"
    )
    parser.add_argument(
        "celltemplateoutput", type=str, help="Output file for the Cell template"
    )
    parser.add_argument(
        "layerpriooutput", type=str, help="Output file for the layerPrio File"
    )
    parser.add_argument_group()

    args = parser.parse_args()

    values = vars(args)

    asyncio.run(
        main(
            values.get("input"),
            values.get("celltemplateoutput"),
            values.get("layerpriooutput"),
        )
    )
