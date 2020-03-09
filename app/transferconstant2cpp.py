ifile = open("Constant.py")
for line in ifile:
    line = line.strip()
    if line.startswith("#"):
        continue
    if not line:
        continue
    print "const string "+ line +";"