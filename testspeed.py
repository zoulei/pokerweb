sum = 0
for card1 in range(2, 15):
    for card2 in range(card1, 15):
        for card3 in range(card2, 15):
            sum += 1
print sum
