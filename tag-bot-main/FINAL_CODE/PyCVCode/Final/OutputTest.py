HitOutputFileName = "Tag_Bot_Hits.csv"
hit_output_file = open(HitOutputFileName, "w")
print("Made File")
hit_output_file.write("Current_Mode,Game_Number,Current_Game_Time\n")
hit_output_file.close()