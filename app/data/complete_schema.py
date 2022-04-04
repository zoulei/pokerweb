f = open("train_data_schema", "a")
for i in range(101):
    f.write("next_turn_winrate_" + str(i) + "\n")
f.close()