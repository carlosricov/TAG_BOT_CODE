import csv

# Initialize the output file
def Initialize_Output_File(HitOutputFileName):
    hit_output_file = open(HitOutputFileName, "w")
    # print("Made File")
    hit_output_file.write("Current_Mode,Game_Number,Current_Game_Time,Score\n")
    return hit_output_file

# Writes the hit statistic to the output file
def Write_To_Output_File(hit_output_file, mode, game_num, game_time, score):
    hit_output_file.write(mode + "," + str(game_num) + "," + str(game_time) + ","+ str(score) + '\n')

def close_file(hit_output_file):
    hit_output_file.close()