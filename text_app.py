from text_insights import TextInsight


def main():

    # creating a TextInsight object
    ti = TextInsight()

    # loading three different text files into the object
    ti.load_text('poe.txt', 'poe')
    ti.load_text('lovecraft.txt', 'lovecraft')
    ti.load_text('king.txt', 'king')

    # calling the sankey visualization method
    ti.wordcount_sankey()
    # calling the pie chart visualization method
    ti.pos_piecharts()
    # calling the line chart visualization method
    ti.top_word_percentage()


if __name__ == '__main__':
    main()

